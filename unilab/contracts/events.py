from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Event:
    event_type: str
    source: str
    timestamp: datetime
    payload: dict[str, Any]


@dataclass
class FaultEvent(Event):
    severity: str = "warning"

    