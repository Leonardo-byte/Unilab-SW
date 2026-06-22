from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ExperimentStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    FINISHED = "finished"
    FAILED = "failed"


class CommandStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"


class Measurement(BaseModel):
    """
    Representa una medición individual producida por un instrumento,
    simulador, módulo de adquisición o fuente externa.
    """

    source: str = Field(
        ...,
        min_length=1,
        description="Nombre o identificador de la fuente que produjo la medición.",
    )

    variable: str = Field(
        ...,
        min_length=1,
        description="Nombre de la variable medida, por ejemplo: temperatura, corriente, voltaje.",
    )

    value: float = Field(
        ...,
        description="Valor numérico de la medición.",
    )

    unit: str = Field(
        ...,
        min_length=1,
        description="Unidad física de la medición, por ejemplo: C, A, V, uT.",
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Marca de tiempo UTC en la que se generó la medición.",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Información adicional opcional asociada a la medición.",
    )


class Command(BaseModel):
    """
    Representa un comando enviado a un instrumento, simulador o módulo interno.
    """

    target: str = Field(
        ...,
        min_length=1,
        description="Módulo o dispositivo destino que debe recibir el comando.",
    )

    action: str = Field(
        ...,
        min_length=1,
        description="Acción que debe ejecutar el destino.",
    )

    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Parámetros requeridos por el comando.",
    )

    command_id: str | None = Field(
        default=None,
        description="Identificador opcional del comando.",
    )

    status: CommandStatus = Field(
        default=CommandStatus.PENDING,
        description="Estado actual del comando.",
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Marca de tiempo UTC en la que se creó el comando.",
    )


class ExperimentConfig(BaseModel):
    """
    Configuración general de un experimento.
    """

    experiment_id: str = Field(
        ...,
        min_length=1,
        description="Identificador único del experimento.",
    )

    name: str = Field(
        ...,
        min_length=1,
        description="Nombre legible del experimento.",
    )

    description: str | None = Field(
        default=None,
        description="Descripción opcional del experimento.",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Marca de tiempo UTC en la que se creó la configuración del experimento.",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadatos opcionales de configuración.",
    )


class ExperimentState(BaseModel):
    """
    Representa el estado de ejecución de un experimento.
    """

    experiment_id: str = Field(
        ...,
        min_length=1,
        description="Identificador del experimento.",
    )

    status: ExperimentStatus = Field(
        default=ExperimentStatus.CREATED,
        description="Estado actual del experimento.",
    )

    started_at: datetime | None = Field(
        default=None,
        description="Marca de tiempo UTC en la que inició el experimento.",
    )

    finished_at: datetime | None = Field(
        default=None,
        description="Marca de tiempo UTC en la que finalizó el experimento.",
    )

    error_message: str | None = Field(
        default=None,
        description="Mensaje de error si el experimento falló.",
    )


class TelemetryPacket(BaseModel):
    """
    Representa un conjunto de mediciones recibidas juntas.
    Es útil para adquisición, almacenamiento y APIs web.
    """

    source: str = Field(
        ...,
        min_length=1,
        description="Fuente que generó el paquete de telemetría.",
    )

    measurements: list[Measurement] = Field(
        default_factory=list,
        description="Lista de mediciones incluidas en el paquete.",
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Marca de tiempo UTC en la que se creó el paquete.",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Información adicional opcional del paquete.",
    )

# ---------------------------------------------------------------------------
# Autenticación (agregado para la funcionalidad de login)
# ---------------------------------------------------------------------------
 
 
class User(BaseModel):
    """
    Representa un usuario del sistema.
 
    Nunca incluye la contraseña ni su hash: este modelo es seguro
    para devolver al cliente en respuestas de la API.
    """
 
    username: str = Field(
        ...,
        min_length=3,
        description="Nombre de usuario único (no distingue mayúsculas/minúsculas).",
    )
 
    email: str | None = Field(
        default=None,
        description="Correo electrónico opcional del usuario.",
    )
 
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Marca de tiempo UTC en la que se creó el usuario.",
    )
 
 
class UserCredentials(BaseModel):
    """
    Credenciales enviadas por el cliente para iniciar sesión o registrarse.
    """
 
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
 
 
class LoginResponse(BaseModel):
    """
    Respuesta enviada al cliente tras un login exitoso.
    """
 
    token: str = Field(..., description="Token de sesión a usar en el header Authorization.")
    expires_at: datetime = Field(..., description="Momento UTC en que expira el token.")
    user: User