"""
Entry point para el backend UniLab en Docker.

Inicia:
1. UdpJsonReceiver (escucha datos del ESP32)
2. SafetyManager (valida datos)
3. MemoryStorage (almacena datos)
4. Uvicorn server (sirve API en puerto 8000)
"""

import threading
import time
from typing import Any

import uvicorn

from unilab.modules.acquisition import UdpJsonReceiver
from unilab.modules.safety import SafetyManager
from unilab.modules.storage import MemoryStorage
from unilab.modules.web.api import create_app


# Configuración
UDP_HOST = "0.0.0.0"
UDP_PORT = 5005

WEB_HOST = "0.0.0.0"
WEB_PORT = 8000


def acquisition_loop(
    receiver: UdpJsonReceiver,
    safety: SafetyManager,
    storage: MemoryStorage,
) -> None:
    """
    Bucle principal de adquisición.

    Lee paquetes UDP, valida las mediciones con SafetyManager
    y guarda paquetes/eventos en MemoryStorage.
    """
    print("[UniLab Backend] Bucle de adquisición iniciado.")

    while receiver.is_running():
        try:
            packet = receiver.read_packet()

            if packet is None:
                continue

            events = safety.validate_packet(packet)

            storage.save_packet(packet)
            storage.save_events(events)

            print(f"[Backend] Paquete recibido desde: {packet.source}")

            for measurement in packet.measurements:
                print(
                    f"  - {measurement.variable}: "
                    f"{measurement.value} {measurement.unit}"
                )

            for event in events:
                print(f"[Safety] {event.event_type}: {event.message}")

        except KeyboardInterrupt:
            break

        except Exception as error:
            print(f"[Backend] Error en adquisición: {error}")

        time.sleep(0.01)


def main() -> None:
    """
    Función principal que inicia todos los servicios.
    """
    print("[UniLab Backend] Iniciando...")

    # Crear instancias compartidas
    storage = MemoryStorage()
    safety = SafetyManager()
    
    # Configurar UdpJsonReceiver con config dict
    receiver_config = {
        "host": UDP_HOST,
        "port": UDP_PORT,
        "buffer_size": 1024,
        "timeout": 0.1,
    }
    receiver = UdpJsonReceiver(name="udp_receiver", config=receiver_config)

    print(f"[UniLab Backend] UdpJsonReceiver configurado en {UDP_HOST}:{UDP_PORT}")

    # Setup del receiver (abre socket)
    receiver.setup()
    receiver.start()

    # Crear app FastAPI con las instancias compartidas
    app = create_app(storage=storage, safety=safety)

    # Iniciar bucle de adquisición en thread separado
    acquisition_thread = threading.Thread(
        target=acquisition_loop,
        args=(receiver, safety, storage),
        daemon=True,
    )
    acquisition_thread.start()
    print("[UniLab Backend] Thread de adquisición iniciado.")

    # Iniciar servidor Uvicorn
    print(f"[UniLab Backend] Uvicorn servidor en {WEB_HOST}:{WEB_PORT}")
    uvicorn.run(
        app,
        host=WEB_HOST,
        port=WEB_PORT,
        log_level="info",
    )


if __name__ == "__main__":
    main()
