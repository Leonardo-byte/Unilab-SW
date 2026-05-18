"""
API web mínima para UniLab.

Este módulo expone una API usando FastAPI para consultar la telemetría,
eventos y estado general del sistema.

No se encarga de recibir datos UDP directamente. Esa responsabilidad pertenece
a UdpJsonReceiver.

Flujo esperado de la demo:

ESP32
  ↓ UDP JSON
UdpJsonReceiver
  ↓
TelemetryPacket
  ↓
SafetyManager
  ↓
MemoryStorage
  ↓
FastAPI / Dashboard
"""

from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, Request
from unilab.modules.safety import SafetyManager
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from unilab.modules.storage import MemoryStorage


TEMPLATES_DIR = Path(__file__).parent / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

def create_app(
    storage: MemoryStorage | None = None,
    safety: SafetyManager | None = None,
) -> FastAPI:
    
    """
    Crea la aplicación FastAPI de UniLab.

    Args:
        storage:
            Instancia de MemoryStorage usada para consultar paquetes y eventos.
            Si no se entrega una instancia, se crea una por defecto.

    Returns:
        FastAPI:
            Aplicación web lista para ejecutarse con uvicorn.
    """
    app = FastAPI(
        title="UniLab Demo API",
        description="API mínima para visualizar telemetría de UniLab.",
        version="0.1.0",
    )

    app.state.storage = storage or MemoryStorage()
    app.state.safety = safety or SafetyManager()

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request) -> HTMLResponse:
        """
        Muestra el dashboard HTML principal.
        """
        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {
                "title": "UniLab Dashboard",
            },
    )

    @app.get("/api/status")
    def get_status() -> dict[str, Any]:
        """
        Retorna el estado general del almacenamiento usado por la API.
        """
        current_storage: MemoryStorage = app.state.storage

        return {
            "api": "running",
            "storage": current_storage.get_status(),
        }

    @app.get("/api/latest-packet")
    def get_latest_packet() -> dict[str, Any]:
        """
        Retorna el último paquete de telemetría recibido.
        """
        current_storage: MemoryStorage = app.state.storage
        packet = current_storage.get_latest_packet()

        if packet is None:
            return {
                "available": False,
                "packet": None,
            }

        packet_dict = _to_dict(packet)
        packet_dict = _filter_packet_dict(
            packet_dict=packet_dict,
            visible_variables=current_storage.get_visible_variables_filter(),
        )

        return {
            "available": True,
            "packet": packet_dict,
        }
    

    @app.get("/api/recent-packets")
    def get_recent_packets(limit: int = 10) -> dict[str, Any]:
        """
        Retorna los últimos paquetes de telemetría almacenados.
        """
        current_storage: MemoryStorage = app.state.storage
        packets = current_storage.get_recent_packets(limit=limit)

        visible_variables = current_storage.get_visible_variables_filter()

        filtered_packets = [
            _filter_packet_dict(
                packet_dict=_to_dict(packet),
                visible_variables=visible_variables,
            )
            for packet in packets
        ]

        return {
            "count": len(filtered_packets),
            "packets": filtered_packets,
        }

    @app.get("/api/recent-events")
    def get_recent_events(limit: int = 10) -> dict[str, Any]:
        """
        Retorna los últimos eventos almacenados.
        """
        current_storage: MemoryStorage = app.state.storage
        events = current_storage.get_recent_events(limit=limit)

        return {
            "count": len(events),
            "events": [_to_dict(event) for event in events],
        }

    @app.post("/api/clear")
    def clear_storage() -> dict[str, Any]:
        """
        Limpia los paquetes y eventos almacenados en memoria.
        """
        current_storage: MemoryStorage = app.state.storage
        current_storage.clear()

        return {
            "message": "Almacenamiento limpiado correctamente.",
            "storage": current_storage.get_status(),
        }
    
    @app.get("/api/variables")
    def get_variables() -> dict[str, Any]:
        """
        Retorna las variables disponibles según la telemetría recibida.
        """
        current_storage: MemoryStorage = app.state.storage
        packets = current_storage.get_recent_packets(limit=100)

        variables: set[str] = set()

        for packet in packets:
            for measurement in packet.measurements:
                variables.add(measurement.variable)

        return {
            "count": len(variables),
            "variables": sorted(variables),
        }


    @app.get("/api/visible-variables")
    def get_visible_variables() -> dict[str, Any]:
        """
        Retorna las variables seleccionadas por el usuario para visualizar.
        """
        current_storage: MemoryStorage = app.state.storage

        return {
            "configured": current_storage.is_visible_variables_configured(),
            "variables": current_storage.get_visible_variables(),
        }


    @app.post("/api/visible-variables")
    def set_visible_variables(
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        """
        Actualiza las variables visibles seleccionadas por el usuario.
        """
        current_storage: MemoryStorage = app.state.storage
        variables = payload.get("variables", [])

        if not isinstance(variables, list):
            raise ValueError("El campo 'variables' debe ser una lista.")

        current_storage.set_visible_variables(variables)

        return {
            "message": "Variables visibles actualizadas correctamente.",
            "variables": current_storage.get_visible_variables(),
        }


    @app.get("/api/safety/limits")
    def get_safety_limits() -> dict[str, Any]:
        """
        Retorna los rangos de seguridad configurados.
        """
        current_safety: SafetyManager = app.state.safety

        return {
            "limits": current_safety.get_limits(),
        }


    @app.post("/api/safety/limits")
    def set_safety_limit(
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        """
        Actualiza el rango de seguridad de una variable.
        """
        current_safety: SafetyManager = app.state.safety

        variable = payload.get("variable")
        min_value = payload.get("min")
        max_value = payload.get("max")

        if not variable:
            raise ValueError("El campo 'variable' es obligatorio.")

        current_safety.set_limit(
            measurement_name=variable,
            min_value=min_value,
            max_value=max_value,
        )

        return {
            "message": "Límite actualizado correctamente.",
            "limits": current_safety.get_limits(),
        }


    @app.get("/api/notes")
    def get_notes() -> dict[str, Any]:
        """
        Retorna las notas registradas por el usuario.
        """
        current_storage: MemoryStorage = app.state.storage
        notes = current_storage.get_notes()

        return {
            "count": len(notes),
            "notes": notes,
        }


    @app.post("/api/notes")
    def add_note(
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        """
        Registra una nota manual del usuario.
        """
        current_storage: MemoryStorage = app.state.storage

        message = payload.get("message")
        variable = payload.get("variable")
        note_type = payload.get("note_type", "general")

        note = current_storage.add_note(
            message=message,
            variable=variable,
            note_type=note_type,
        )

        return {
            "message": "Nota registrada correctamente.",
            "note": note,
        }


    return app


def _filter_packet_dict(
    packet_dict: dict[str, Any],
    visible_variables: list[str] | None,
) -> dict[str, Any]:
    """
    Filtra las mediciones de un paquete según las variables visibles.

    Reglas:
    - None: el usuario todavía no configuró nada, se muestran todas.
    - []: el usuario deseleccionó todas, no se muestra ninguna.
    - ["temperature", "ph"]&#58; se muestran solo esas variables.
    """
    if visible_variables is None:
        return packet_dict

    visible_set = set(visible_variables)

    packet_dict["measurements"] = [
        measurement
        for measurement in packet_dict.get("measurements", [])
        if measurement.get("variable") in visible_set
    ]

    return packet_dict


def _to_dict(data: Any) -> dict[str, Any]:
    """
    Convierte modelos de Pydantic o dataclasses simples a diccionarios.

    Esto permite que FastAPI pueda devolver Measurement, TelemetryPacket,
    Event y FaultEvent como JSON.
    """
    if hasattr(data, "model_dump"):
        return data.model_dump(mode="json")

    if hasattr(data, "dict"):
        return data.dict()

    if hasattr(data, "__dict__"):
        return data.__dict__

    return {"value": str(data)}


app = create_app()
