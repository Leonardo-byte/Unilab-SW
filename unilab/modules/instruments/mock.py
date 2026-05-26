"""
Instrumento mock para UniLab.

Este instrumento no se conecta a ningún hardware real.
Su propósito es permitir el desarrollo, pruebas y simulaciones
sin necesidad de un dispositivo físico.

Genera mediciones con valores predefinidos o aleatorios según la configuración.
"""

import random
from typing import Any

from unilab.contracts.models import Command, CommandStatus, Measurement
from unilab.modules.instruments.base import InstrumentBase


class MockInstrument(InstrumentBase):
    """
    Instrumento simulado que genera datos ficticios.

    Útil para:
    - Pruebas unitarias e integración.
    - Desarrollo sin hardware real.
    - Demostrar el flujo completo del sistema.

    Ejemplo de configuración:

    {
        "variable": "temperature",
        "unit": "C",
        "base_value": 25.0,
        "noise": 0.5
    }

    Si noise > 0, el valor generado tendrá variación aleatoria.
    """

    def __init__(
        self,
        instrument_id: str,
        name: str,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(instrument_id=instrument_id, name=name, config=config)

        self._variable: str = self.config.get("variable", "mock_variable")
        self._unit: str = self.config.get("unit", "raw")
        self._base_value: float = float(self.config.get("base_value", 0.0))
        self._noise: float = float(self.config.get("noise", 0.0))
        self._last_command: Command | None = None
        self._command_history: list[Command] = []

    def connect(self) -> None:
        """
        Simula la conexión con el instrumento.
        Siempre tiene éxito en el mock.
        """
        self._connected = True

    def disconnect(self) -> None:
        """
        Simula la desconexión del instrumento.
        """
        self._connected = False

    def read_status(self) -> dict[str, Any]:
        """
        Retorna el estado simulado del instrumento.
        """
        return {
            "instrument_id": self.instrument_id,
            "connected": self._connected,
            "firmware": "mock-v1.0.0",
            "mode": "simulation",
            "variable": self._variable,
            "unit": self._unit,
            "base_value": self._base_value,
            "noise": self._noise,
        }

    def send_command(self, command: Command) -> None:
        """
        Registra el comando recibido y lo marca como enviado.

        En el mock no se envía ningún mensaje real,
        pero se actualiza el estado del comando.
        """
        if not self._connected:
            self._mark_command_failed(command)
            raise RuntimeError(
                f"El instrumento '{self.name}' no está conectado. "
                "No se puede enviar el comando."
            )

        self._mark_command_sent(command)
        self._last_command = command
        self._command_history.append(command)

    def get_measurement(self) -> Measurement:
        """
        Genera una medición simulada.

        Si noise > 0, agrega variación aleatoria al valor base.
        """
        if not self._connected:
            raise RuntimeError(
                f"El instrumento '{self.name}' no está conectado. "
                "No se puede obtener una medición."
            )

        value = self._base_value
        if self._noise > 0:
            value += random.uniform(-self._noise, self._noise)

        return Measurement(
            source=self.instrument_id,
            variable=self._variable,
            value=round(value, 4),
            unit=self._unit,
            metadata={"instrument_type": "mock"},
        )

    def get_last_command(self) -> Command | None:
        """
        Retorna el último comando recibido.
        Útil para verificar en pruebas.
        """
        return self._last_command

    def get_command_history(self) -> list[Command]:
        """
        Retorna todos los comandos recibidos.
        """
        return list(self._command_history)

    def set_base_value(self, value: float) -> None:
        """
        Actualiza el valor base del mock en tiempo de ejecución.
        Útil para simular cambios de condición durante pruebas.
        """
        self._base_value = value

    def get_status(self) -> dict[str, Any]:
        status = super().get_status()
        status.update({
            "last_command": self._last_command.action if self._last_command else None,
            "commands_received": len(self._command_history),
        })
        return status
