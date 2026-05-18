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

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from unilab.modules.storage import MemoryStorage


TEMPLATES_DIR = Path(__file__).parent / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def create_app(storage: MemoryStorage | None = None) -> FastAPI:
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

        return {
            "available": True,
            "packet": _to_dict(packet),
        }

    @app.get("/api/recent-packets")
    def get_recent_packets(limit: int = 10) -> dict[str, Any]:
        """
        Retorna los últimos paquetes de telemetría almacenados.
        """
        current_storage: MemoryStorage = app.state.storage
        packets = current_storage.get_recent_packets(limit=limit)

        return {
            "count": len(packets),
            "packets": [_to_dict(packet) for packet in packets],
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

    return app


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
