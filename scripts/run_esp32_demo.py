"""
Demo mínima ESP32 → UniLab → Dashboard.

Este script integra:

- UdpJsonReceiver
- SafetyManager
- MemoryStorage
- FastAPI Dashboard

Flujo:

ESP32 o simulador Python
  ↓ UDP JSON
UdpJsonReceiver
  ↓ TelemetryPacket
SafetyManager
  ↓ Event / FaultEvent
MemoryStorage
  ↓
FastAPI / Dashboard

Ejecutar desde la raíz del proyecto:

python scripts/run_esp32_demo.py

Luego abrir en el navegador:

http://127.0.0.1:8000
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import threading
import time
from typing import Any

import uvicorn

from unilab.modules.acquisition import UdpJsonReceiver
from unilab.modules.safety import SafetyManager
from unilab.modules.storage import MemoryStorage
from unilab.modules.web.api import create_app


UDP_HOST = "0.0.0.0"
UDP_PORT = 5005

WEB_HOST = "127.0.0.1"
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
    print("[UniLab] Bucle de adquisición iniciado.")

    while receiver.is_running():
        try:
            packet = receiver.read_packet()

            if packet is None:
                continue

            events = safety.validate_packet(packet)

            storage.save_packet(packet)
            storage.save_events(events)

            print(f"[UniLab] Paquete recibido desde: {packet.source}")

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
            print(f"[UniLab] Error en adquisición: {error}")

        time.sleep(0.01)

    print("[UniLab] Bucle de adquisición detenido.")


def create_demo_components() -> tuple[UdpJsonReceiver, SafetyManager, MemoryStorage]:
    """
    Crea los componentes principales de la demo.
    """
    receiver = UdpJsonReceiver(
        name="esp32_udp_receiver",
        config={
            "host": UDP_HOST,
            "port": UDP_PORT,
            "buffer_size": 1024,
            "timeout": 0.1,
        },
    )

    safety = SafetyManager(
        limits={
            "temperature": {
                "min": 0,
                "max": 60,
            },
            "humidity": {
                "min": 20,
                "max": 90,
            },
            "ph": {
                "min": 4,
                "max": 9,
            },
            "ec": {
                "min": 0,
                "max": 5,
            },
        }
    )

    storage = MemoryStorage(
        max_packets=100,
        max_events=100,
    )

    return receiver, safety, storage


def print_demo_info() -> None:
    """
    Muestra información útil para ejecutar la demo.
    """
    print("")
    print("====================================")
    print(" UniLab ESP32 UDP Demo")
    print("====================================")
    print(f"UDP escuchando en: {UDP_HOST}:{UDP_PORT}")
    print(f"Dashboard web en: http://{WEB_HOST}:{WEB_PORT}")
    print("")
    print("Formato JSON explícito esperado:")
    print(
        """
{
  "device_id": "esp32_01",
  "measurements": [
    {"variable": "temperature", "value": 25.5, "unit": "C"},
    {"variable": "humidity", "value": 70.0, "unit": "%"}
  ]
}
"""
    )
    print("Formato JSON simple también aceptado:")
    print(
        """
{
  "device_id": "esp32_01",
  "temperature": 25.5,
  "humidity": 70.0
}
"""
    )
    print("Presiona Ctrl+C para detener.")
    print("")


def main() -> None:
    """
    Punto de entrada principal de la demo.
    """
    receiver, safety, storage = create_demo_components()

    receiver.setup()
    receiver.start()

    acquisition_thread = threading.Thread(
        target=acquisition_loop,
        args=(receiver, safety, storage),
        daemon=True,
    )

    acquisition_thread.start()

    app = create_app(storage=storage)

    print_demo_info()

    try:
        uvicorn.run(
            app,
            host=WEB_HOST,
            port=WEB_PORT,
            log_level="info",
        )

    except KeyboardInterrupt:
        print("[UniLab] Deteniendo demo...")

    finally:
        receiver.shutdown()
        print("[UniLab] Demo detenida correctamente.")


if __name__ == "__main__":
    main()

