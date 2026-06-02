"""
Pruebas para los módulos de adquisición de UniLab.

Cubre:
- AcquisitionBase: ciclo de vida (setup, start, stop, shutdown).
- UdpJsonReceiver: parseo de JSON, manejo de errores, formato plano y estructurado.
- FileReceiver: lectura de JSONL, JSON array, CSV, manejo de errores.
- TcpJsonReceiver y SerialJsonReceiver: construcción y validación básica.
"""

import json
import socket
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from unilab.modules.acquisition.base import AcquisitionBase
from unilab.modules.acquisition.file_receiver import FileReceiver
from unilab.modules.acquisition.tcp_json_receiver import TcpJsonReceiver
from unilab.modules.acquisition.udp_json_receiver import UdpJsonReceiver


# =============================================================================
# AcquisitionBase: ciclo de vida
# =============================================================================

class ConcreteReceiver(AcquisitionBase):
    """Implementación concreta mínima para probar la base."""

    def read_packet(self):
        return None


class TestAcquisitionBase:
    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="vacío"):
            ConcreteReceiver(name="")

    def test_blank_name_raises(self):
        with pytest.raises(ValueError, match="vacío"):
            ConcreteReceiver(name="   ")

    def test_initial_state(self):
        receiver = ConcreteReceiver(name="test")
        assert not receiver.is_setup()
        assert not receiver.is_running()

    def test_start_requires_setup(self):
        receiver = ConcreteReceiver(name="test")
        with pytest.raises(RuntimeError, match="setup"):
            receiver.start()

    def test_setup_start_stop_cycle(self):
        receiver = ConcreteReceiver(name="test")
        receiver.setup()
        assert receiver.is_setup()

        receiver.start()
        assert receiver.is_running()

        receiver.stop()
        assert not receiver.is_running()

    def test_shutdown_resets_state(self):
        receiver = ConcreteReceiver(name="test")
        receiver.setup()
        receiver.start()
        receiver.shutdown()
        assert not receiver.is_setup()
        assert not receiver.is_running()

    def test_get_status(self):
        receiver = ConcreteReceiver(name="mi_receptor", config={"port": 5005})
        status = receiver.get_status()
        assert status["name"] == "mi_receptor"
        assert status["type"] == "ConcreteReceiver"
        assert not status["is_setup"]
        assert not status["is_running"]


# =============================================================================
# UdpJsonReceiver: parseo JSON
# =============================================================================

class TestUdpJsonReceiverParsing:
    """
    Pruebas del parseo JSON de UdpJsonReceiver sin abrir sockets reales.
    Accedemos directamente a los métodos privados de conversión.
    """

    def setup_method(self):
        self.receiver = UdpJsonReceiver(name="udp_test", config={"port": 5005})

    def test_structured_format_single_measurement(self):
        data = {
            "device_id": "esp32_01",
            "measurements": [
                {"variable": "temperature", "value": 24.8, "unit": "C"}
            ],
        }
        packet = self.receiver._json_to_packet(data)
        assert packet.source == "esp32_01"
        assert len(packet.measurements) == 1
        assert packet.measurements[0].variable == "temperature"
        assert packet.measurements[0].value == 24.8
        assert packet.measurements[0].unit == "C"

    def test_structured_format_multiple_measurements(self):
        data = {
            "device_id": "esp32_01",
            "measurements": [
                {"variable": "temperature", "value": 24.8, "unit": "C"},
                {"variable": "humidity", "value": 68.2, "unit": "%"},
                {"variable": "pressure", "value": 1013.0, "unit": "hPa"},
            ],
        }
        packet = self.receiver._json_to_packet(data)
        assert len(packet.measurements) == 3
        variables = [m.variable for m in packet.measurements]
        assert "temperature" in variables
        assert "humidity" in variables
        assert "pressure" in variables

    def test_flat_format(self):
        data = {
            "device_id": "esp32_02",
            "temperature": 22.5,
            "humidity": 70.0,
        }
        packet = self.receiver._json_to_packet(data)
        assert packet.source == "esp32_02"
        assert len(packet.measurements) == 2
        variables = {m.variable for m in packet.measurements}
        assert variables == {"temperature", "humidity"}

    def test_flat_format_ignores_metadata_fields(self):
        data = {
            "device_id": "esp32_03",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "ok",
            "type": "sensor",
            "temperature": 30.0,
        }
        packet = self.receiver._json_to_packet(data)
        assert len(packet.measurements) == 1
        assert packet.measurements[0].variable == "temperature"

    def test_flat_format_uses_raw_unit(self):
        data = {"device_id": "esp32_04", "voltage": 3.3}
        packet = self.receiver._json_to_packet(data)
        assert packet.measurements[0].unit == "raw"

    def test_missing_device_id_uses_unknown(self):
        data = {"temperature": 25.0}
        packet = self.receiver._json_to_packet(data)
        assert packet.source == "unknown_device"

    def test_measurements_not_a_list_raises(self):
        data = {"device_id": "esp32", "measurements": "not_a_list"}
        with pytest.raises(ValueError, match="lista"):
            self.receiver._json_to_packet(data)

    def test_flat_format_no_numeric_values_raises(self):
        data = {"device_id": "esp32", "mode": "auto", "status": "ok"}
        with pytest.raises(ValueError, match="mediciones"):
            self.receiver._json_to_packet(data)

    def test_source_is_set_on_measurements(self):
        data = {
            "device_id": "my_device",
            "measurements": [
                {"variable": "temp", "value": 20.0, "unit": "C"}
            ],
        }
        packet = self.receiver._json_to_packet(data)
        assert packet.measurements[0].source == "my_device"


class TestUdpJsonReceiverSocket:
    """
    Pruebas del receptor UDP con socket mockeado.
    """

    def test_read_packet_requires_start(self):
        receiver = UdpJsonReceiver(name="udp", config={"port": 5099})
        receiver.setup()
        with pytest.raises(RuntimeError, match="iniciado"):
            receiver.read_packet()

    def test_read_packet_returns_none_on_timeout(self):
        receiver = UdpJsonReceiver(name="udp", config={"port": 5099})

        with patch("socket.socket") as mock_socket_class:
            mock_sock = MagicMock()
            mock_socket_class.return_value = mock_sock
            mock_sock.recvfrom.side_effect = socket.timeout

            receiver.setup()
            receiver.start()
            result = receiver.read_packet()
            assert result is None

    def test_read_packet_parses_valid_json(self):
        receiver = UdpJsonReceiver(name="udp", config={"port": 5099})

        payload = json.dumps({
            "device_id": "esp32_test",
            "measurements": [
                {"variable": "temperature", "value": 23.5, "unit": "C"}
            ],
        }).encode("utf-8")

        with patch("socket.socket") as mock_socket_class:
            mock_sock = MagicMock()
            mock_socket_class.return_value = mock_sock
            mock_sock.recvfrom.return_value = (payload, ("192.168.1.10", 5005))

            receiver.setup()
            receiver.start()
            packet = receiver.read_packet()

        assert packet is not None
        assert packet.source == "esp32_test"
        assert packet.measurements[0].value == 23.5

    def test_read_packet_invalid_json_raises(self):
        receiver = UdpJsonReceiver(name="udp", config={"port": 5099})

        with patch("socket.socket") as mock_socket_class:
            mock_sock = MagicMock()
            mock_socket_class.return_value = mock_sock
            mock_sock.recvfrom.return_value = (b"not valid json", ("192.168.1.10", 5005))

            receiver.setup()
            receiver.start()
            with pytest.raises(ValueError, match="JSON"):
                receiver.read_packet()

    def test_shutdown_closes_socket(self):
        receiver = UdpJsonReceiver(name="udp", config={"port": 5099})

        with patch("socket.socket") as mock_socket_class:
            mock_sock = MagicMock()
            mock_socket_class.return_value = mock_sock

            receiver.setup()
            receiver.shutdown()
            mock_sock.close.assert_called_once()
            assert not receiver.is_setup()


# =============================================================================
# FileReceiver
# =============================================================================

class TestFileReceiver:
    def test_requires_filepath_in_config(self):
        with pytest.raises(ValueError, match="filepath"):
            FileReceiver(name="files", config={})

    def test_setup_raises_if_file_not_found(self):
        receiver = FileReceiver(name="files", config={"filepath": "/no/existe.jsonl"})
        with pytest.raises(FileNotFoundError):
            receiver.setup()

    def test_read_jsonl_file(self, tmp_path):
        filepath = tmp_path / "data.jsonl"
        packets = [
            {"device_id": "dev_01", "temperature": 20.0},
            {"device_id": "dev_01", "temperature": 21.5},
            {"device_id": "dev_01", "temperature": 22.0},
        ]
        filepath.write_text("\n".join(json.dumps(p) for p in packets), encoding="utf-8")

        receiver = FileReceiver(name="files", config={"filepath": str(filepath)})
        receiver.setup()
        receiver.start()

        result = []
        while receiver.has_more():
            packet = receiver.read_packet()
            if packet:
                result.append(packet)

        assert len(result) == 3
        assert result[0].measurements[0].value == 20.0
        assert result[1].measurements[0].value == 21.5

    def test_read_json_array_file(self, tmp_path):
        filepath = tmp_path / "data.json"
        packets = [
            {"device_id": "dev_01", "measurements": [{"variable": "temp", "value": 10.0, "unit": "C"}]},
            {"device_id": "dev_01", "measurements": [{"variable": "temp", "value": 11.0, "unit": "C"}]},
        ]
        filepath.write_text(json.dumps(packets), encoding="utf-8")

        receiver = FileReceiver(name="files", config={"filepath": str(filepath), "format": "json"})
        receiver.setup()
        receiver.start()

        p1 = receiver.read_packet()
        p2 = receiver.read_packet()
        p3 = receiver.read_packet()

        assert p1.measurements[0].value == 10.0
        assert p2.measurements[0].value == 11.0
        assert p3 is None

    def test_read_csv_file(self, tmp_path):
        filepath = tmp_path / "data.csv"
        content = "variable,value,unit\ntemperature,25.0,C\nhumidity,60.0,%\n"
        filepath.write_text(content, encoding="utf-8")

        receiver = FileReceiver(name="files", config={"filepath": str(filepath), "format": "csv"})
        receiver.setup()
        receiver.start()

        p1 = receiver.read_packet()
        p2 = receiver.read_packet()

        assert p1.measurements[0].variable == "temperature"
        assert p1.measurements[0].value == 25.0
        assert p2.measurements[0].variable == "humidity"

    def test_returns_none_when_exhausted(self, tmp_path):
        filepath = tmp_path / "data.jsonl"
        filepath.write_text(json.dumps({"device_id": "d", "temp": 10.0}), encoding="utf-8")

        receiver = FileReceiver(name="files", config={"filepath": str(filepath)})
        receiver.setup()
        receiver.start()

        receiver.read_packet()
        assert receiver.read_packet() is None

    def test_reset_allows_re_reading(self, tmp_path):
        filepath = tmp_path / "data.jsonl"
        filepath.write_text(json.dumps({"device_id": "d", "temp": 10.0}), encoding="utf-8")

        receiver = FileReceiver(name="files", config={"filepath": str(filepath)})
        receiver.setup()
        receiver.start()

        p1 = receiver.read_packet()
        receiver.reset()
        p2 = receiver.read_packet()

        assert p1 is not None
        assert p2 is not None
        assert p1.measurements[0].value == p2.measurements[0].value

    def test_total_packets(self, tmp_path):
        filepath = tmp_path / "data.jsonl"
        lines = [json.dumps({"device_id": "d", "temp": float(i)}) for i in range(5)]
        filepath.write_text("\n".join(lines), encoding="utf-8")

        receiver = FileReceiver(name="files", config={"filepath": str(filepath)})
        receiver.setup()
        assert receiver.total_packets() == 5

    def test_read_requires_start(self, tmp_path):
        filepath = tmp_path / "data.jsonl"
        filepath.write_text(json.dumps({"device_id": "d", "temp": 10.0}), encoding="utf-8")

        receiver = FileReceiver(name="files", config={"filepath": str(filepath)})
        receiver.setup()

        with pytest.raises(RuntimeError, match="iniciado"):
            receiver.read_packet()

    def test_get_status(self, tmp_path):
        filepath = tmp_path / "data.jsonl"
        filepath.write_text(json.dumps({"device_id": "d", "temp": 10.0}), encoding="utf-8")

        receiver = FileReceiver(name="files", config={"filepath": str(filepath)})
        receiver.setup()

        status = receiver.get_status()
        assert status["total_packets"] == 1
        assert status["format"] == "jsonl"
        assert "filepath" in status

    def test_unsupported_format_raises(self, tmp_path):
        filepath = tmp_path / "data.xml"
        filepath.touch()

        with pytest.raises(ValueError, match="soportado"):
            FileReceiver(name="files", config={"filepath": str(filepath), "format": "xml"})


# =============================================================================
# TcpJsonReceiver: construcción básica
# =============================================================================

class TestTcpJsonReceiverConstruction:
    def test_construction_valid(self):
        receiver = TcpJsonReceiver(name="tcp_test", config={"port": 5006})
        assert receiver.name == "tcp_test"
        assert not receiver.is_setup()
        assert not receiver.is_running()

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            TcpJsonReceiver(name="")
