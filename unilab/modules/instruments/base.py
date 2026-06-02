"""
Clase base para instrumentos de UniLab.

Todo instrumento, ya sea real o simulado, debe heredar de InstrumentBase
e implementar los métodos abstractos definidos aquí.

Esto garantiza que el core, el scheduler, safety y el resto del sistema
puedan trabajar con cualquier instrumento de la misma manera,
sin importar si es un ESP32, un Arduino, un mock o un dispositivo serial.
"""

from abc import ABC, abstractmethod
from typing import Any

from unilab.contracts.models import Command, CommandStatus, Measurement


class InstrumentBase(ABC):
    """
    Clase base abstracta para todos los instrumentos de UniLab.

    Un instrumento puede ser:
    - Un dispositivo físico real (ESP32, Arduino, sensor serial).
    - Un instrumento simulado (mock).
    - Un adaptador de protocolo (SiLA, MODBUS, etc.).

    La interfaz es siempre la misma para el resto del sistema.
    """

    def __init__(self, instrument_id: str, name: str, config: dict[str, Any] | None = None) -> None:
        if not instrument_id or not instrument_id.strip():
            raise ValueError("El instrument_id no puede estar vacío.")
        if not name or not name.strip():
            raise ValueError("El nombre del instrumento no puede estar vacío.")

        self.instrument_id = instrument_id
        self.name = name
        self.config = config or {}
        self._connected = False
        self._is_setup = False

    def setup(self) -> None:
        """
        Prepara el instrumento para su uso.
        Puede sobrescribirse para inicializar recursos.
        """
        self._is_setup = True

    def shutdown(self) -> None:
        """
        Libera los recursos del instrumento.
        Si está conectado, lo desconecta primero.
        """
        if self._connected:
            self.disconnect()
        self._is_setup = False

    @abstractmethod
    def connect(self) -> None:
        """
        Establece la conexión con el instrumento.
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """
        Cierra la conexión con el instrumento.
        """
        raise NotImplementedError

    def is_connected(self) -> bool:
        """
        Retorna True si el instrumento está conectado.
        """
        return self._connected

    @abstractmethod
    def read_status(self) -> dict[str, Any]:
        """
        Lee el estado actual del instrumento.
        Puede incluir firmware, modo de operación, errores, etc.
        """
        raise NotImplementedError

    @abstractmethod
    def send_command(self, command: Command) -> None:
        """
        Envía un comando al instrumento.
        Debe actualizar el status del comando a SENT o FAILED.
        """
        raise NotImplementedError

    @abstractmethod
    def get_measurement(self) -> Measurement:
        """
        Obtiene una medición individual desde el instrumento.
        """
        raise NotImplementedError

    def get_status(self) -> dict[str, Any]:
        """
        Retorna el estado general del instrumento para diagnóstico.
        """
        return {
            "instrument_id": self.instrument_id,
            "name": self.name,
            "type": self.__class__.__name__,
            "connected": self._connected,
            "is_setup": self._is_setup,
            "config": self.config,
        }

    def _mark_command_sent(self, command: Command) -> None:
        command.status = CommandStatus.SENT

    def _mark_command_failed(self, command: Command) -> None:
        command.status = CommandStatus.FAILED
