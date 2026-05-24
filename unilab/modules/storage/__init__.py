from unilab.modules.storage.memory_storage import MemoryStorage

def __init__(
    self,
    max_packets: int = 100,
    max_events: int = 100,
    name: str = "memory_storage",
) -> None:
    if max_packets <= 0:
        raise ValueError("max_packets debe ser mayor que cero.")
    if max_events <= 0:
        raise ValueError("max_events debe ser mayor que cero.")

    self.name = name
    self._is_setup = False

    self.max_packets = max_packets
    self.max_events = max_events
    self._packets: list[TelemetryPacket] = []
    self._events: list[Event] = []
    self._visible_variables: set[str] | None = None
    self._notes: list[dict[str, Any]] = []
