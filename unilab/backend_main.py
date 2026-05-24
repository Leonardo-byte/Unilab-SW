"""
Entry point para el backend UniLab en Docker.

Este archivo solo arranca el runtime.
La orquestación de módulos se delega a UniLabApp y al core.
"""

import threading
import time
from typing import cast

import uvicorn

from unilab.core.app import UniLabApp
from unilab.modules.acquisition import UdpJsonReceiver
from unilab.modules.safety import SafetyManager
from unilab.modules.storage import MemoryStorage
from unilab.modules.web.api import create_app


UDP_HOST = "0.0.0.0"
UDP_PORT = 5005

WEB_HOST = "0.0.0.0"
WEB_PORT = 8000

UDP_RECEIVER_NAME = "udp_receiver"
SAFETY_MANAGER_NAME = "safety_manager"
MEMORY_STORAGE_NAME = "memory_storage"


def build_runtime() -> UniLabApp:
    """
    Construye UniLabApp y registra los módulos principales del backend.
    """
    unilab_app = UniLabApp()

    receiver_config = {
        "host": UDP_HOST,
        "port": UDP_PORT,
        "buffer_size": 1024,
        "timeout": 0.1,
    }

    receiver = UdpJsonReceiver(
        name=UDP_RECEIVER_NAME,
        config=receiver_config,
    )

    safety = SafetyManager(name=SAFETY_MANAGER_NAME)
    storage = MemoryStorage(name=MEMORY_STORAGE_NAME)

    unilab_app.register_module(UDP_RECEIVER_NAME, receiver)
    unilab_app.register_module(SAFETY_MANAGER_NAME, safety)
    unilab_app.register_module(MEMORY_STORAGE_NAME, storage)

    return unilab_app


def acquisition_loop(unilab_app: UniLabApp) -> None:
    """
    Bucle principal de adquisición.

    Obtiene los módulos desde UniLabApp, lee paquetes UDP,
    valida mediciones y guarda paquetes/eventos.
    """
    receiver = cast(
        UdpJsonReceiver,
        unilab_app.get_module(UDP_RECEIVER_NAME),
    )

    safety = cast(
        SafetyManager,
        unilab_app.get_module(SAFETY_MANAGER_NAME),
    )

    storage = cast(
        MemoryStorage,
        unilab_app.get_module(MEMORY_STORAGE_NAME),
    )

    print("[UniLab Backend] Bucle de adquisición iniciado.")

    while receiver.is_running():
        try:
            packet = receiver.read_packet()

            if packet is None:
                continue

            events = safety.validate_packet(packet)

            storage.register_device(
                device_id=packet.source,
                protocol="udp",
            )

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
    Inicializa UniLab, adquisición UDP y API web.
    """
    print("[UniLab Backend] Iniciando...")

    unilab_app = build_runtime()

    try:
        unilab_app.setup()

        receiver = cast(
            UdpJsonReceiver,
            unilab_app.get_module(UDP_RECEIVER_NAME),
        )

        print(
            f"[UniLab Backend] UdpJsonReceiver configurado en "
            f"{UDP_HOST}:{UDP_PORT}"
        )

        receiver.start()


        # Crea aplicacion
        app = create_app(unilab_app=unilab_app)

        acquisition_thread = threading.Thread(
            target=acquisition_loop,
            args=(unilab_app,),
            daemon=True,
        )

        acquisition_thread.start()
        print("[UniLab Backend] Thread de adquisición iniciado.")

        print(f"[UniLab Backend] Uvicorn servidor en {WEB_HOST}:{WEB_PORT}")

        uvicorn.run(
            app,
            host=WEB_HOST,
            port=WEB_PORT,
            log_level="info",
        )

    finally:
        print("[UniLab Backend] Apagando servicios...")
        unilab_app.shutdown()


if __name__ == "__main__":
    main()