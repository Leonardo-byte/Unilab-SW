from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """
    Tipos generales de eventos que pueden ocurrir dentro del sistema UniLab.
    """

    SYSTEM_STARTED = "system.started"
    SYSTEM_STOPPED = "system.stopped"

    MODULE_REGISTERED = "module.registered"
    MODULE_LOADED = "module.loaded"
    MODULE_ERROR = "module.error"

    EXPERIMENT_CREATED = "experiment.created"
    EXPERIMENT_STARTED = "experiment.started"
    EXPERIMENT_PAUSED = "experiment.paused"
    EXPERIMENT_STOPPED = "experiment.stopped"
    EXPERIMENT_FINISHED = "experiment.finished"
    EXPERIMENT_FAILED = "experiment.failed"

    INSTRUMENT_CONNECTED = "instrument.connected"
    INSTRUMENT_DISCONNECTED = "instrument.disconnected"
    INSTRUMENT_ERROR = "instrument.error"

    TELEMETRY_RECEIVED = "telemetry.received"

    SAFETY_WARNING = "safety.warning"
    SAFETY_FAULT = "safety.fault"


class Severity(str, Enum):
    """
    Nivel de severidad asociado a eventos de advertencia, falla o error.
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Event(BaseModel):
    """
    Representa un evento general generado por cualquier parte del sistema.

    Un evento puede provenir del core, un instrumento, un módulo de adquisición,
    el scheduler, safety, storage, web u otro componente.
    """

    event_type: EventType | str = Field(
        ...,
        min_length=1,
        description="Tipo de evento generado por el sistema.",
    )

    source: str = Field(
        ...,
        min_length=1,
        description="Módulo, servicio o componente que generó el evento.",
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Marca de tiempo UTC en la que se generó el evento.",
    )

    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Datos adicionales asociados al evento.",
    )


class FaultEvent(Event):
    """
    Representa un evento de falla, advertencia o condición anómala.

    Este tipo de evento se puede usar cuando un módulo detecta un error,
    una condición insegura, pérdida de comunicación o un valor fuera de rango.
    """

    severity: Severity = Field(
        default=Severity.WARNING,
        description="Nivel de severidad de la falla o advertencia.",
    )

    fault_code: str | None = Field(
        default=None,
        description="Código opcional para identificar la falla.",
    )

    message: str | None = Field(
        default=None,
        description="Mensaje descriptivo de la falla.",
    )