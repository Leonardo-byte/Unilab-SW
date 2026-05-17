from typing import Protocol, Any
from unilab.contracts.models import Measurement, Command


class InstrumentProtocol(Protocol):
    def connect(self) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def read_status(self) -> dict[str, Any]:
        ...

    def send_command(self, command: Command) -> None:
        ...

    def get_measurement(self) -> Measurement:
        ...


class ModuleProtocol(Protocol):
    name: str

    def setup(self) -> None:
        ...

    def shutdown(self) -> None:
        ...