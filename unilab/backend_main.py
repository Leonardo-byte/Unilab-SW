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
from unilab.modules.acquisition import (
    UdpJsonReceiver,
    TcpJsonReceiver,
    SerialJsonReceiver,
)

from unilab.modules.safety import SafetyManager
from unilab.modules.storage import MemoryStorage
from unilab.modules.web.api import create_app

#autenticacion
from unilab.modules.auth import AuthManager



UDP_HOST = "0.0.0.0"
UDP_PORT = 5005

TCP_HOST = "0.0.0.0"
TCP_PORT = 5005

SERIAL_PORT = "/dev/ttyUSB0"
SERIAL_BAUDRATE = 115200
SERIAL_RECEIVER_NAME = "serial_receiver"

WEB_HOST = "0.0.0.0"
WEB_PORT = 8000

UDP_RECEIVER_NAME = "udp_receiver"
TCP_RECEIVER_NAME = "tcp_receiver"

SAFETY_MANAGER_NAME = "safety_manager"
MEMORY_STORAGE_NAME = "memory_storage"
#autenticacion
AUTH_MANAGER_NAME = "auth_manager"


def build_runtime() -> UniLabApp:
    """
    Construye UniLabApp y registra los módulos principales del backend.
    """
    unilab_app = UniLabApp()

    udp_receiver_config = {
        "host": UDP_HOST,
        "port": UDP_PORT,
        "buffer_size": 1024,
        "timeout": 0.1,
    }

    tcp_receiver_config = {
        "host": TCP_HOST,
        "port": TCP_PORT,
        "buffer_size": 1024,
        "timeout": 0.1,
    }

    udp_receiver = UdpJsonReceiver(
        name=UDP_RECEIVER_NAME,
        config=udp_receiver_config,
    )

    tcp_receiver = TcpJsonReceiver(
    name=TCP_RECEIVER_NAME,
    config=tcp_receiver_config,
    )

    serial_receiver_config = {
        "port": SERIAL_PORT,
        "baudrate": SERIAL_BAUDRATE,
        "timeout": 1.0,
    }

    serial_receiver = SerialJsonReceiver(
        name=SERIAL_RECEIVER_NAME,
        config=serial_receiver_config,
    )

    safety = SafetyManager(name=SAFETY_MANAGER_NAME)
    storage = MemoryStorage(name=MEMORY_STORAGE_NAME)
    #autenticacion
    auth = AuthManager(name=AUTH_MANAGER_NAME)

    unilab_app.register_module(UDP_RECEIVER_NAME, udp_receiver)
    unilab_app.register_module(TCP_RECEIVER_NAME, tcp_receiver)
    unilab_app.register_module(SERIAL_RECEIVER_NAME, serial_receiver)
    unilab_app.register_module(SAFETY_MANAGER_NAME, safety)
    unilab_app.register_module(MEMORY_STORAGE_NAME, storage)
    #
    unilab_app.register_module(AUTH_MANAGER_NAME, auth)

    return unilab_app


def acquisition_loop(
    unilab_app: UniLabApp,
    receiver_name: str,
    protocol: str,
) -> None:
    receiver = unilab_app.get_module(receiver_name)

    safety = cast(
        SafetyManager,
        unilab_app.get_module(SAFETY_MANAGER_NAME),
    )

    storage = cast(
        MemoryStorage,
        unilab_app.get_module(MEMORY_STORAGE_NAME),
    )

    print(f"[UniLab Backend] Bucle de adquisición {protocol.upper()} iniciado.")

    while receiver.is_running():
        try:
            packet = receiver.read_packet()

            if packet is None:
                continue

            storage.register_device(
                device_id=packet.source,
                protocol=protocol,
            )

            if not storage.is_device_connected(packet.source):
                print(
                    f"[Backend] Dispositivo detectado pero no conectado: "
                    f"{packet.source}"
                )
                continue

            events = safety.validate_packet(packet)

            storage.save_packet(packet)
            storage.save_events(events)

            print(f"[Backend][{protocol.upper()}] Paquete recibido desde: {packet.source}")

            for measurement in packet.measurements:
                print(
                    f" - {measurement.variable}: "
                    f"{measurement.value} {measurement.unit}"
                )

            for event in events:
                print(f"[Safety] {event.event_type}: {event.message}")

        except KeyboardInterrupt:
            break

        except Exception as error:
            print(f"[Backend][{protocol.upper()}] Error en adquisición: {error}")

        time.sleep(0.01)


def main() -> None:
    """
    Inicializa UniLab, adquisición UDP y API web.
    """
    print("[UniLab Backend] Iniciando...")

    unilab_app = build_runtime()

    try:
        unilab_app.setup()

        udp_receiver = cast(
            UdpJsonReceiver,
            unilab_app.get_module(UDP_RECEIVER_NAME),
        )

        tcp_receiver = cast(
            TcpJsonReceiver,
            unilab_app.get_module(TCP_RECEIVER_NAME),
        )

        serial_receiver = cast(
            SerialJsonReceiver,
            unilab_app.get_module(SERIAL_RECEIVER_NAME),
        )

        print(
            f"[UniLab Backend] UdpJsonReceiver configurado en "
            f"{UDP_HOST}:{UDP_PORT}"
        )

        print(
            f"[UniLab Backend] TcpJsonReceiver configurado en "
            f"{TCP_HOST}:{TCP_PORT}"
        )

        print(
            f"[UniLab Backend] SerialJsonReceiver configurado en "
            f"{SERIAL_PORT} a {SERIAL_BAUDRATE} baud"
        )

        udp_receiver.start()
        tcp_receiver.start()
        serial_receiver.start()


        # Crea aplicacion
        app = create_app(unilab_app=unilab_app)

        udp_thread = threading.Thread(
            target=acquisition_loop,
            args=(unilab_app, UDP_RECEIVER_NAME, "udp"),
            daemon=True,
        )

        tcp_thread = threading.Thread(
            target=acquisition_loop,
            args=(unilab_app, TCP_RECEIVER_NAME, "tcp"),
            daemon=True,
        )

        serial_thread = threading.Thread(
            target=acquisition_loop,
            args=(unilab_app, SERIAL_RECEIVER_NAME, "serial"),
            daemon=True,
        )

        udp_thread.start()
        tcp_thread.start()
        serial_thread.start()

        print("[UniLab Backend] Threads de adquisición UDP, TCP y Serial iniciados.")
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