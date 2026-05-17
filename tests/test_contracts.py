from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from unilab.contracts.models import (
    Measurement,
    Command,
    ExperimentConfig,
    ExperimentState,
    ExperimentStatus,
    CommandStatus,
    TelemetryPacket,
)

from unilab.contracts.events import (
    Event,
    FaultEvent,
    EventType,
    Severity,
)

from unilab.contracts.protocols import (
    ModuleProtocol,
    InstrumentProtocol,
    AcquisitionProtocol,
    SimulationProtocol,
    StorageProtocol,
    SafetyProtocol,
)


def test_measurement_model():
    measurement = Measurement(
        source="mock_sensor",
        variable="temperature",
        value=25.5,
        unit="C",
    )

    assert measurement.source == "mock_sensor"
    assert measurement.variable == "temperature"
    assert measurement.value == 25.5
    assert measurement.unit == "C"
    assert measurement.timestamp is not None
    assert measurement.metadata == {}


def test_measurement_rejects_empty_source():
    with pytest.raises(ValidationError):
        Measurement(
            source="",
            variable="temperature",
            value=25.5,
            unit="C",
        )


def test_command_model():
    command = Command(
        target="coil_x",
        action="set_current",
        params={"current": 1.5},
    )

    assert command.target == "coil_x"
    assert command.action == "set_current"
    assert command.params["current"] == 1.5
    assert command.status == CommandStatus.PENDING
    assert command.timestamp is not None


def test_experiment_config_model():
    config = ExperimentConfig(
        experiment_id="exp001",
        name="Test experiment",
        description="Basic test",
    )

    assert config.experiment_id == "exp001"
    assert config.name == "Test experiment"
    assert config.description == "Basic test"
    assert config.created_at is not None
    assert config.metadata == {}


def test_experiment_state_model():
    state = ExperimentState(
        experiment_id="exp001",
        status=ExperimentStatus.CREATED,
    )

    assert state.experiment_id == "exp001"
    assert state.status == ExperimentStatus.CREATED
    assert state.started_at is None
    assert state.finished_at is None
    assert state.error_message is None


def test_telemetry_packet_model():
    packet = TelemetryPacket(
        source="mock_receiver",
        measurements=[
            Measurement(
                source="mock_sensor",
                variable="temperature",
                value=25.5,
                unit="C",
            )
        ],
    )

    assert packet.source == "mock_receiver"
    assert len(packet.measurements) == 1
    assert packet.measurements[0].variable == "temperature"
    assert packet.timestamp is not None


def test_event_model():
    event = Event(
        event_type=EventType.EXPERIMENT_STARTED,
        source="core",
        payload={"experiment_id": "exp001"},
    )

    assert event.event_type == EventType.EXPERIMENT_STARTED
    assert event.source == "core"
    assert event.payload["experiment_id"] == "exp001"
    assert event.timestamp is not None


def test_fault_event_model():
    fault = FaultEvent(
        event_type=EventType.SAFETY_FAULT,
        source="safety.manager",
        severity=Severity.CRITICAL,
        fault_code="LIMIT_EXCEEDED",
        message="Valor fuera del límite permitido.",
        payload={"value": 10.5, "limit": 8.0},
    )

    assert fault.event_type == EventType.SAFETY_FAULT
    assert fault.source == "safety.manager"
    assert fault.severity == Severity.CRITICAL
    assert fault.fault_code == "LIMIT_EXCEEDED"
    assert fault.message == "Valor fuera del límite permitido."
    assert fault.payload["value"] == 10.5


class DummyModule:
    name = "dummy_module"

    def setup(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_status(self) -> dict:
        return {"status": "ok"}


class DummyInstrument:
    name = "dummy_instrument"
    instrument_id = "inst_001"

    def setup(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_status(self) -> dict:
        return {"status": "ok"}

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def is_connected(self) -> bool:
        return True

    def read_status(self) -> dict:
        return {"connected": True}

    def send_command(self, command: Command) -> None:
        pass

    def get_measurement(self) -> Measurement:
        return Measurement(
            source="dummy_instrument",
            variable="temperature",
            value=25.0,
            unit="C",
            timestamp=datetime.now(timezone.utc),
        )


class DummyAcquisition:
    name = "dummy_acquisition"
    source = "udp_mock"

    def setup(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_status(self) -> dict:
        return {"status": "ok"}

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def read_packet(self) -> TelemetryPacket:
        return TelemetryPacket(source="udp_mock")


class DummySimulation:
    name = "dummy_simulation"
    model_name = "simple_model"

    def setup(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_status(self) -> dict:
        return {"status": "ok"}

    def reset(self) -> None:
        pass

    def step(self, dt: float) -> TelemetryPacket:
        return TelemetryPacket(source="simple_model")


class DummyStorage:
    name = "dummy_storage"

    def setup(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_status(self) -> dict:
        return {"status": "ok"}

    def save_measurement(self, measurement: Measurement) -> None:
        pass

    def save_telemetry_packet(self, packet: TelemetryPacket) -> None:
        pass

    def save_event(self, event) -> None:
        pass


class DummySafety:
    name = "dummy_safety"

    def setup(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_status(self) -> dict:
        return {"status": "ok"}

    def check(self, packet: TelemetryPacket) -> bool:
        return True

    def get_faults(self) -> list:
        return []


def test_dummy_module_implements_module_protocol():
    module = DummyModule()

    assert isinstance(module, ModuleProtocol)


def test_dummy_instrument_implements_instrument_protocol():
    instrument = DummyInstrument()

    assert isinstance(instrument, InstrumentProtocol)


def test_dummy_acquisition_implements_acquisition_protocol():
    acquisition = DummyAcquisition()

    assert isinstance(acquisition, AcquisitionProtocol)


def test_dummy_simulation_implements_simulation_protocol():
    simulation = DummySimulation()

    assert isinstance(simulation, SimulationProtocol)


def test_dummy_storage_implements_storage_protocol():
    storage = DummyStorage()

    assert isinstance(storage, StorageProtocol)


def test_dummy_safety_implements_safety_protocol():
    safety = DummySafety()

    assert isinstance(safety, SafetyProtocol)