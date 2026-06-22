"""
Pruebas para la API web mínima de UniLab.

Estas pruebas verifican que FastAPI pueda consultar datos desde MemoryStorage.
"""

from fastapi.testclient import TestClient

from unilab.contracts.models import Measurement, TelemetryPacket
from unilab.modules.safety import SafetyManager
from unilab.modules.storage import MemoryStorage
from unilab.modules.web.api import create_app
from unilab.core.app import UniLabApp


def create_test_app(
    storage: MemoryStorage | None = None,
    safety: SafetyManager | None = None,
):
    storage = storage or MemoryStorage()
    safety = safety or SafetyManager()

    unilab_app = UniLabApp()

    unilab_app.register_module("memory_storage", storage)
    unilab_app.register_module("safety_manager", safety)

    return create_app(unilab_app)

def test_api_status_endpoint_returns_running():
    """
    Verifica que el endpoint de estado de la API responda correctamente.
    """
    storage = MemoryStorage()
    app = create_test_app(storage=storage)
    client = TestClient(app)

    response = client.get("/api/status")

    assert response.status_code == 200
    assert response.json()["api"] == "running"


def test_api_status_returns_storage_status():
    """
    Verifica que /api/status retorne el estado de la API y del almacenamiento.
    """
    storage = MemoryStorage()
    app = create_test_app(storage=storage)
    client = TestClient(app)

    response = client.get("/api/status")
    data = response.json()

    assert response.status_code == 200
    assert data["api"] == "running"
    assert data["storage"]["type"] == "MemoryStorage"
    assert data["storage"]["packets_count"] == 0
    assert data["storage"]["events_count"] == 0


def test_api_latest_packet_returns_no_data_when_storage_is_empty():
    """
    Verifica que /api/latest-packet indique que no hay datos cuando
    MemoryStorage está vacío.
    """
    storage = MemoryStorage()
    app = create_test_app(storage=storage)
    client = TestClient(app)

    response = client.get("/api/latest-packet")
    data = response.json()

    assert response.status_code == 200
    assert data["available"] is False
    assert data["packet"] is None


def test_api_latest_packet_returns_saved_packet():
    """
    Verifica que /api/latest-packet retorne el último paquete guardado.
    """
    storage = MemoryStorage()

    packet = TelemetryPacket(
        source="esp32_01",
        measurements=[
            Measurement(source="esp32_01", variable="temperature", value=25.5, unit="C"),
            Measurement(source="esp32_01", variable="humidity", value=70.0, unit="%"),
        ],
    )

    storage.save_packet(packet)

    app = create_test_app(storage=storage)
    client = TestClient(app)

    response = client.get("/api/latest-packet")
    data = response.json()

    assert response.status_code == 200
    assert data["available"] is True
    assert data["packet"]["source"] == "esp32_01"
    assert len(data["packet"]["measurements"]) == 2

    assert data["packet"]["measurements"][0]["variable"] == "temperature"
    assert data["packet"]["measurements"][0]["value"] == 25.5
    assert data["packet"]["measurements"][0]["unit"] == "C"


def test_api_recent_events_returns_saved_safety_events():
    """
    Verifica que /api/recent-events retorne eventos generados por SafetyManager.
    """
    storage = MemoryStorage()

    packet = TelemetryPacket(
        source="esp32_01",
        measurements=[
            Measurement(source="esp32_01", variable="temperature", value=80, unit="C"),
        ],
    )

    safety = SafetyManager(
        limits={
            "temperature": {
                "min": 0,
                "max": 60,
            },
        }
    )

    events = safety.validate_packet(packet)

    storage.save_packet(packet)
    storage.save_events(events)

    app = create_test_app(storage=storage)
    client = TestClient(app)

    response = client.get("/api/recent-events")
    data = response.json()

    assert response.status_code == 200
    assert data["count"] == 1
    assert "temperature" in data["events"][0]["message"]
    assert "80.0" in data["events"][0]["message"]


def test_api_clear_removes_packets_and_events():
    """
    Verifica que /api/clear elimine paquetes y eventos almacenados.
    """
    storage = MemoryStorage()

    packet = TelemetryPacket(
        source="esp32_01",
        measurements=[
            Measurement(source="esp32_01", variable="temperature", value=25.5, unit="C"),
        ],
    )

    storage.save_packet(packet)

    app = create_test_app(storage=storage)
    client = TestClient(app)

    response = client.post("/api/clear")
    data = response.json()

    assert response.status_code == 200
    assert data["storage"]["packets_count"] == 0
    assert data["storage"]["events_count"] == 0

    response = client.get("/api/latest-packet")
    data = response.json()

    assert data["available"] is False
    assert data["packet"] is None



def test_api_visible_variables_can_be_updated():
    """
    Verifica que el usuario pueda seleccionar variables visibles.
    """
    storage = MemoryStorage()
    app = create_test_app(storage=storage)
    client = TestClient(app)

    response = client.post(
        "/api/visible-variables",
        json={
            "variables": ["temperature", "ph"],
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["variables"] == ["ph", "temperature"]

    response = client.get("/api/visible-variables")
    data = response.json()

    assert data["variables"] == ["ph", "temperature"]


def test_api_safety_limits_can_be_updated():
    """
    Verifica que el usuario pueda modificar rangos de seguridad.
    """
    storage = MemoryStorage()
    safety = SafetyManager()

    app = create_test_app(storage=storage, safety=safety)
    client = TestClient(app)

    response = client.post(
        "/api/safety/limits",
        json={
            "variable": "temperature",
            "min": 10,
            "max": 35,
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["limits"]["temperature"]["min"] == 10
    assert data["limits"]["temperature"]["max"] == 35


def test_api_notes_can_be_created():
    """
    Verifica que el usuario pueda registrar notas.
    """
    storage = MemoryStorage()
    app = create_test_app(storage=storage)
    client = TestClient(app)

    response = client.post(
        "/api/notes",
        json={
            "variable": "temperature",
            "message": "Se acercó una fuente de calor al sensor.",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["note"]["variable"] == "temperature"
    assert data["note"]["message"] == "Se acercó una fuente de calor al sensor."

    response = client.get("/api/notes")
    data = response.json()

    assert data["count"] == 1

def test_api_status_endpoint_exists():
    storage = MemoryStorage()
    app = create_test_app(storage=storage)
    client = TestClient(app)

    response = client.get("/api/status")

    assert response.status_code == 200
    assert response.json()["api"] == "running"