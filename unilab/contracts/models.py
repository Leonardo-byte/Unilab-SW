from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Measurement:
    source: str
    variable: str
    value: float
    unit: str
    timestamp: datetime


@dataclass
class Command:
    target: str
    action: str
    params: dict[str, Any]


@dataclass
class ExperimentConfig:
    experiment_id: str
    name: str
    description: str | None = None

    