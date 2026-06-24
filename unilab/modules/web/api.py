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
from typing import Any, cast

from fastapi import Body, FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse

from unilab.core.app import UniLabApp
from unilab.modules.safety import SafetyManager
from unilab.modules.storage import MemoryStorage

# nuevo modulo 
from unilab.modules.auth import AuthManager


SAFETY_MANAGER_NAME = "safety_manager"
MEMORY_STORAGE_NAME = "memory_storage"
AUTH_MANAGER_NAME = "auth_manager" # 
TEMPLATE_FILE = Path(__file__).resolve().parent / "templates" / "dashboard.html"


def create_app(
    unilab_app: UniLabApp | None = None,
    storage: MemoryStorage | None = None,
    safety: SafetyManager | None = None,
) -> FastAPI:
    """
    Crea la aplicación FastAPI de UniLab usando UniLabApp como fuente
    de módulos registrados.
    """
    app = FastAPI(
        title="UniLab Demo API",
        description="API mínima para visualizar telemetría de UniLab.",
        version="0.1.0",
    )

    app.state.unilab_app = unilab_app

    if unilab_app is not None:
        app.state.unilab_app = unilab_app
    else:
        if storage is None:
            storage = MemoryStorage()
        if safety is None:
            safety = SafetyManager()

        app.state.unilab_app = UniLabApp()
        app.state.unilab_app.register_module(MEMORY_STORAGE_NAME, storage)
        app.state.unilab_app.register_module(SAFETY_MANAGER_NAME, safety)

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request) -> Any:
        with TEMPLATE_FILE.open("r", encoding="utf-8") as template_file:
            html = template_file.read()

        return HTMLResponse(content=html, status_code=200)

    @app.get("/api/status")
    def get_status(request: Request) -> dict[str, Any]:
        """
        Retorna el estado general del sistema usado por la API.
        """
        current_storage = get_storage(request)
        current_safety = get_safety(request)

        return {
            "api": "running",
            "storage": current_storage.get_status(),
            "safety": current_safety.get_status(),
        }

    @app.get("/api/latest-packet")
    def get_latest_packet(request: Request) -> dict[str, Any]:
        """
        Retorna el último paquete de telemetría recibido.
        """
        current_storage = get_storage(request)
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
    def get_recent_packets(
        request: Request,
        limit: int = 10,
    ) -> dict[str, Any]:
        """
        Retorna los últimos paquetes de telemetría almacenados.
        """
        current_storage = get_storage(request)
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
    def get_recent_events(
        request: Request,
        limit: int = 10,
    ) -> dict[str, Any]:
        """
        Retorna los últimos eventos almacenados.
        """
        current_storage = get_storage(request)
        events = current_storage.get_recent_events(limit=limit)

        return {
            "count": len(events),
            "events": [_to_dict(event) for event in events],
        }

    @app.post("/api/clear")
    def clear_storage(request: Request) -> dict[str, Any]:
        """
        Limpia los paquetes y eventos almacenados en memoria.
        """
        current_storage = get_storage(request)
        current_storage.clear()

        return {
            "message": "Almacenamiento limpiado correctamente.",
            "storage": current_storage.get_status(),
        }

    @app.get("/api/variables")
    def get_variables(request: Request) -> dict[str, Any]:
        """
        Retorna las variables disponibles según la telemetría recibida.
        """
        current_storage = get_storage(request)
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
    def get_visible_variables(request: Request) -> dict[str, Any]:
        """
        Retorna las variables seleccionadas por el usuario para visualizar.
        """
        current_storage = get_storage(request)

        return {
            "configured": current_storage.is_visible_variables_configured(),
            "variables": current_storage.get_visible_variables(),
        }

    @app.post("/api/visible-variables")
    def set_visible_variables(
        request: Request,
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        """
        Actualiza las variables visibles seleccionadas por el usuario.
        """
        current_storage = get_storage(request)
        variables = payload.get("variables", [])

        if not isinstance(variables, list):
            raise ValueError("El campo 'variables' debe ser una lista.")

        current_storage.set_visible_variables(variables)

        return {
            "message": "Variables visibles actualizadas correctamente.",
            "variables": current_storage.get_visible_variables(),
        }

    @app.get("/api/safety/limits")
    def get_safety_limits(request: Request) -> dict[str, Any]:
        """
        Retorna los rangos de seguridad configurados.
        """
        current_safety = get_safety(request)

        return {
            "limits": current_safety.get_limits(),
        }

    @app.post("/api/safety/limits")
    def set_safety_limit(
        request: Request,
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        """
        Actualiza el rango de seguridad de una variable.
        """
        current_safety = get_safety(request)

        variable = payload.get("variable")
        min_value = payload.get("min")
        max_value = payload.get("max")

        comment_below = payload.get("comment_below")
        comment_above = payload.get("comment_above")

        if not variable:
            raise ValueError("El campo 'variable' es obligatorio.")

        current_safety.set_limit(
            measurement_name=variable,
            min_value=min_value,
            max_value=max_value,
            comment_below=comment_below,
            comment_above=comment_above,
        )

        return {
            "message": "Límite actualizado correctamente.",
            "limits": current_safety.get_limits(),
        }

    @app.get("/api/notes")
    def get_notes(request: Request) -> dict[str, Any]:
        """
        Retorna las notas registradas por el usuario.
        """
        current_storage = get_storage(request)
        notes = current_storage.get_notes()

        return {
            "count": len(notes),
            "notes": notes,
        }

    @app.post("/api/notes")
    def add_note(
        request: Request,
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        """
        Registra una nota manual del usuario.
        """
        current_storage = get_storage(request)

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
    
    @app.get("/api/modules")
    def get_modules(request: Request) -> dict[str, Any]:
        """
        Retorna los módulos registrados en UniLabApp.
        """
        unilab_app = get_unilab_app(request)

        return {
            "app": unilab_app.get_status(),
            "modules": unilab_app.get_modules_status(),
        }

    # ------------------------------------------------------------------
    # Autenticación
    # ------------------------------------------------------------------

    @app.post("/api/auth/login")
    def login(
        request: Request,
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        current_auth = get_auth(request)
        username = (payload.get("username") or "").strip()
        password = payload.get("password") or ""

        if not username or not password:
            raise HTTPException(status_code=400, detail="Usuario y contraseña son obligatorios.")

        user = current_auth.authenticate(username=username, password=password)

        if user is None:
            raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")

        token, expires_at = current_auth.create_session(user)

        return {
            "token": token,
            "expires_at": expires_at.isoformat(),
            "user": {"username": user.username, "email": user.email},
        }

    @app.post("/api/auth/register")
    def register(
        request: Request,
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        current_auth = get_auth(request)
        username = (payload.get("username") or "").strip()
        password = payload.get("password") or ""
        email = payload.get("email")

        if not username or not password:
            raise HTTPException(status_code=400, detail="Usuario y contraseña son obligatorios.")

        if len(password) < 6:
            raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres.")

        try:
            user = current_auth.register_user(username=username, password=password, email=email)
        except ValueError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

        return {
            "message": "Usuario registrado correctamente.",
            "user": {"username": user.username, "email": user.email},
        }

    @app.post("/api/auth/logout")
    def logout(
        request: Request,
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        current_auth = get_auth(request)
        token = payload.get("token") or ""
        current_auth.revoke_session(token)
        return {"message": "Sesión cerrada correctamente."}

    @app.get("/api/auth/me")
    def me(request: Request) -> dict[str, Any]:
        current_auth = get_auth(request)
        token = _extract_bearer_token(request)

        if not token:
            raise HTTPException(status_code=401, detail="No autenticado.")

        user = current_auth.get_user_from_token(token)

        if user is None:
            raise HTTPException(status_code=401, detail="Sesión inválida o expirada.")

        return {"username": user.username, "email": user.email}

    return app


def get_unilab_app(request: Request) -> UniLabApp:
    """
    Obtiene la instancia UniLabApp asociada a FastAPI.
    """
    return cast(UniLabApp, request.app.state.unilab_app)


def get_storage(request: Request) -> MemoryStorage:
    """
    Obtiene el módulo MemoryStorage desde el core.
    """
    unilab_app = get_unilab_app(request)

    return cast(
        MemoryStorage,
        unilab_app.get_module(MEMORY_STORAGE_NAME),
    )


def get_safety(request: Request) -> SafetyManager:
    """
    Obtiene el módulo SafetyManager desde el core.
    """
    unilab_app = get_unilab_app(request)

    return cast(
        SafetyManager,
        unilab_app.get_module(SAFETY_MANAGER_NAME),
    )

#autenticacion
def get_auth(request: Request) -> AuthManager:
    """
    Obtiene el módulo AuthManager desde el core.
    """
    unilab_app = get_unilab_app(request)

    return cast(
        AuthManager,
        unilab_app.get_module(AUTH_MANAGER_NAME),
    )

def _extract_bearer_token(request: Request) -> str | None:
    """
    Extrae el token del header 'Authorization: Bearer <token>'.
    """
    auth_header = request.headers.get("Authorization", "")

    if auth_header.startswith("Bearer "):
        return auth_header[len("Bearer ") :]

    return None

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