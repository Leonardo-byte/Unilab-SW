"""
Pruebas para UdpJsonReceiver.

Estas pruebas verifican que el módulo de adquisición pueda recibir un paquete
UDP en formato JSON y convertirlo correctamente a TelemetryPacket.
"""

import json
import socket

from unilab.modules.acquisition import UdpJsonReceiver


def test_udp_json_receiver_reads_explicit_measurements_format():
    """
    Verifica que UdpJsonReceiver pueda leer el formato explícito:

    {
        "device_id": "esp32_01",
        "measurements": [
            {"variable": "temperature", "value": 25.5, "unit": "C"}
        ]
    }
    """
    receiver = UdpJsonReceiver(
        name="test_udp_receiver",
        config={
            "host": "127.0.0.1",
            "port": 0,
            "buffer_size": 1024,
            "timeout": 0.5,
        },
    )

    receiver.setup()
    receiver.start()

    try:
        assert receiver._socket is not None
        host, port = receiver._socket.getsockname()

        message = {
            "device_id": "esp32_01",
            "measurements": [
                {
                    "variable": "temperature",
                    "value": 25.5,
                    "unit": "C",
                },
                {
                    "variable": "humidity",
                    "value": 70.0,
                    "unit": "%",
                },
            ],
        }

        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sender.sendto(json.dumps(message).encode("utf-8"), (host, port))
        sender.close()

        packet = receiver.read_packet()

        assert packet is not None
        assert packet.source == "esp32_01"
        assert len(packet.measurements) == 2

        assert packet.measurements[0].variable == "temperature"
        assert packet.measurements[0].value == 25.5
        assert packet.measurements[0].unit == "C"

        assert packet.measurements[1].variable == "humidity"
        assert packet.measurements[1].value == 70.0
        assert packet.measurements[1].unit == "%"

    finally:
        receiver.shutdown()


def test_udp_json_receiver_reads_simple_json_format():
    """
    Verifica que UdpJsonReceiver pueda leer el formato simple:

    {
        "device_id": "esp32_01",
        "temperature": 24.8,
        "humidity": 68.2
    }
    """
    receiver = UdpJsonReceiver(
        name="test_udp_receiver",
        config={
            "host": "127.0.0.1",
            "port": 0,
            "buffer_size": 1024,
            "timeout": 0.5,
        },
    )

    receiver.setup()
    receiver.start()

    try:
        assert receiver._socket is not None
        host, port = receiver._socket.getsockname()

        message = {
            "device_id": "esp32_01",
            "temperature": 24.8,
            "humidity": 68.2,
        }

        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sender.sendto(json.dumps(message).encode("utf-8"), (host, port))
        sender.close()

        packet = receiver.read_packet()

        assert packet is not None
        assert packet.source == "esp32_01"
        assert len(packet.measurements) == 2

        measurement_variables = [measurement.variable for measurement in packet.measurements]
        measurement_values = [measurement.value for measurement in packet.measurements]

        assert "temperature" in measurement_variables
        assert "humidity" in measurement_variables
        assert 24.8 in measurement_values
        assert 68.2 in measurement_values

    finally:
        receiver.shutdown()


def test_udp_json_receiver_returns_none_when_no_data_is_available():
    """
    Verifica que read_packet retorne None si no llega ningún paquete UDP
    durante el tiempo de espera.
    """
    receiver = UdpJsonReceiver(
        name="test_udp_receiver",
        config={
            "host": "127.0.0.1",
            "port": 0,
            "buffer_size": 1024,
            "timeout": 0.1,
        },
    )

    receiver.setup()
    receiver.start()

    try:
        packet = receiver.read_packet()

        assert packet is None

    finally:
        receiver.shutdown()


