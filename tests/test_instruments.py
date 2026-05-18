"""
Pruebas para los módulos de instrumentos de UniLab.

Cubre:
- InstrumentBase: validación de construcción.
- MockInstrument: conexión, mediciones, comandos, historial.
- SerialJsonInstrument: manejo sin pyserial, errores de conexión.
- Esp32Instrument: delegación al receiver, manejo de errores.
"""

import pytest

from unilab.contracts.models import Command, CommandStatus
from unilab.modules.instruments.base import InstrumentBase
from unilab.modules.instruments.esp32 import Esp32Instrument
from unilab.modules.instruments.mock import MockInstrument
from unilab.modules.instruments.serial_json import SerialJsonInstrument


# =============================================================================
# InstrumentBase: validación de construcción
# =============================================================================

class TestInstrumentBaseValidation:
    def test_empty_instrument_id_raises(self):
        with pytest.raises(ValueError, match="instrument_id"):
            MockInstrument(instrument_id="", name="sensor")

    def test_blank_instrument_id_raises(self):
        with pytest.raises(ValueError, match="instrument_id"):
            MockInstrument(instrument_id="   ", name="sensor")

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="nombre"):
            MockInstrument(instrument_id="sensor_01", name="")

    def test_valid_construction(self):
        instrument = MockInstrument(instrument_id="sensor_01", name="Sensor de Prueba")
        assert instrument.instrument_id == "sensor_01"
        assert instrument.name == "Sensor de Prueba"
        assert not instrument.is_connected()


# =============================================================================
# MockInstrument
# =============================================================================

class TestMockInstrument:
    def setup_method(self):
        self.instrument = MockInstrument(
            instrument_id="mock_01",
            name="Mock Sensor",
            config={
                "variable": "temperature",
                "unit": "C",
                "base_value": 25.0,
                "noise": 0.0,
            },
        )

    def test_connect_disconnects_correctly(self):
        assert not self.instrument.is_connected()
        self.instrument.connect()
        assert self.instrument.is_connected()
        self.instrument.disconnect()
        assert not self.instrument.is_connected()

    def test_get_measurement_requires_connection(self):
        with pytest.raises(RuntimeError, match="conectado"):
            self.instrument.get_measurement()

    def test_get_measurement_returns_correct_values(self):
        self.instrument.connect()
        measurement = self.instrument.get_measurement()

        assert measurement.source == "mock_01"
        assert measurement.variable == "temperature"
        assert measurement.value == 25.0
        assert measurement.unit == "C"

    def test_measurement_with_noise(self):
        instrument = MockInstrument(
            instrument_id="noisy",
            name="Noisy Sensor",
            config={"base_value": 100.0, "noise": 5.0},
        )
        instrument.connect()

        values = [instrument.get_measurement().value for _ in range(20)]
        assert any(v != 100.0 for v in values), "El noise debería producir variación"
        assert all(85.0 <= v <= 115.0 for v in values), "Los valores deberían estar dentro del rango"

    def test_send_command_requires_connection(self):
        command = Command(target="mock_01", action="reset")
        with pytest.raises(RuntimeError, match="conectado"):
            self.instrument.send_command(command)
        assert command.status == CommandStatus.FAILED

    def test_send_command_marks_sent(self):
        self.instrument.connect()
        command = Command(target="mock_01", action="reset")
        self.instrument.send_command(command)
        assert command.status == CommandStatus.SENT

    def test_command_history(self):
        self.instrument.connect()
        cmd1 = Command(target="mock_01", action="start")
        cmd2 = Command(target="mock_01", action="stop")
        self.instrument.send_command(cmd1)
        self.instrument.send_command(cmd2)

        history = self.instrument.get_command_history()
        assert len(history) == 2
        assert history[0].action == "start"
        assert history[1].action == "stop"

    def test_get_last_command(self):
        self.instrument.connect()
        assert self.instrument.get_last_command() is None

        command = Command(target="mock_01", action="calibrate")
        self.instrument.send_command(command)
        assert self.instrument.get_last_command().action == "calibrate"

    def test_set_base_value(self):
        self.instrument.connect()
        self.instrument.set_base_value(50.0)
        measurement = self.instrument.get_measurement()
        assert measurement.value == 50.0

    def test_read_status(self):
        status = self.instrument.read_status()
        assert status["instrument_id"] == "mock_01"
        assert status["variable"] == "temperature"
        assert status["unit"] == "C"

    def test_setup_and_shutdown(self):
        self.instrument.setup()
        assert self.instrument._is_setup

        self.instrument.connect()
        self.instrument.shutdown()
        assert not self.instrument.is_connected()
        assert not self.instrument._is_setup

    def test_get_status(self):
        status = self.instrument.get_status()
        assert status["instrument_id"] == "mock_01"
        assert status["type"] == "MockInstrument"
        assert "connected" in status


# =============================================================================
# SerialJsonInstrument: sin pyserial disponible
# =============================================================================

class TestSerialJsonInstrumentNoSerial:
    """
    Prueba el comportamiento cuando pyserial no está disponible.
    """

    def test_connect_raises_when_serial_not_available(self, monkeypatch):
        import unilab.modules.instruments.serial_json as module
        monkeypatch.setattr(module, "SERIAL_AVAILABLE", False)

        instrument = SerialJsonInstrument(
            instrument_id="serial_01",
            name="Serial Sensor",
            config={"port": "/dev/ttyUSB0"},
        )

        with pytest.raises(RuntimeError, match="pyserial"):
            instrument.connect()

    def test_construction_always_works(self):
        instrument = SerialJsonInstrument(
            instrument_id="serial_01",
            name="Serial Sensor",
        )
        assert instrument.instrument_id == "serial_01"
        assert not instrument.is_connected()


# =============================================================================
# Esp32Instrument: con MockReceiver
# =============================================================================

class MockReceiver:
    """Receptor simulado para pruebas de Esp32Instrument."""

    def __init__(self, packets=None):
        self._packets = packets or []
        self._index = 0
        self.setup_called = False
        self.start_called = False
        self.shutdown_called = False
        self.name = "mock_receiver"

    def setup(self):
        self.setup_called = True

    def start(self):
        self.start_called = True

    def shutdown(self):
        self.shutdown_called = True

    def read_packet(self):
        if self._index >= len(self._packets):
            return None
        packet = self._packets[self._index]
        self._index += 1
        return packet

    def get_status(self):
        return {"type": "MockReceiver"}


class TestEsp32Instrument:
    def setup_method(self):
        from unilab.contracts.models import Measurement, TelemetryPacket
        self.packet = TelemetryPacket(
            source="esp32_01",
            measurements=[
                Measurement(source="esp32_01", variable="temperature", value=24.5, unit="C"),
                Measurement(source="esp32_01", variable="humidity", value=65.0, unit="%"),
            ],
        )
        self.receiver = MockReceiver(packets=[self.packet])
        self.instrument = Esp32Instrument(
            instrument_id="esp32_01",
            name="ESP32 Lab",
            receiver=self.receiver,
        )

    def test_requires_receiver(self):
        with pytest.raises(ValueError, match="receiver"):
            Esp32Instrument(instrument_id="esp32", name="ESP32", receiver=None)

    def test_connect_calls_receiver_setup_and_start(self):
        self.instrument.connect()
        assert self.receiver.setup_called
        assert self.receiver.start_called
        assert self.instrument.is_connected()

    def test_disconnect_calls_receiver_shutdown(self):
        self.instrument.connect()
        self.instrument.disconnect()
        assert self.receiver.shutdown_called
        assert not self.instrument.is_connected()

    def test_get_measurement_returns_first_measurement(self):
        self.instrument.connect()
        measurement = self.instrument.get_measurement()
        assert measurement.variable == "temperature"
        assert measurement.value == 24.5

    def test_get_measurement_requires_connection(self):
        with pytest.raises(RuntimeError, match="conectado"):
            self.instrument.get_measurement()

    def test_get_measurement_no_data_raises(self):
        receiver = MockReceiver(packets=[])  # sin datos
        instrument = Esp32Instrument(
            instrument_id="esp32_02",
            name="ESP32 Sin Datos",
            receiver=receiver,
        )
        instrument.connect()
        with pytest.raises(RuntimeError):
            instrument.get_measurement()

    def test_send_command_raises_not_implemented(self):
        self.instrument.connect()
        command = Command(target="esp32_01", action="reset")
        with pytest.raises(NotImplementedError):
            self.instrument.send_command(command)

    def test_get_last_packet(self):
        self.instrument.connect()
        self.instrument.get_measurement()
        packet = self.instrument.get_last_packet()
        assert packet is not None
        assert len(packet.measurements) == 2

    def test_read_status(self):
        self.instrument.connect()
        status = self.instrument.read_status()
        assert status["instrument_id"] == "esp32_01"
        assert status["connected"] is True
