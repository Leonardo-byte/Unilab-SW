from datetime import datetime
from unilab.contracts.models import Measurement, Command, ExperimentConfig
from unilab.contracts.events import Event


def test_measurement_model():
    measurement = Measurement(
        source="mock_sensor",
        variable="temperature",
        value=25.5,
        unit="C",
        timestamp=datetime.now()
    )

    assert measurement.source == "mock_sensor"
    assert measurement.variable == "temperature"
    assert measurement.value == 25.5


def test_command_model():
    command = Command(
        target="coil_x",
        action="set_current",
        params={"current": 1.5}
    )

    assert command.target == "coil_x"
    assert command.action == "set_current"
    assert command.params["current"] == 1.5


def test_event_model():
    event = Event(
        event_type="experiment.started",
        source="core",
        timestamp=datetime.now(),
        payload={"experiment_id": "exp001"}
    )

    assert event.event_type == "experiment.started"
    assert event.source == "core"
