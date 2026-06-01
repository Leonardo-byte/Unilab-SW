"""
Instrumento serial JSON para UniLab.

Este módulo representa un dispositivo físico conectado por puerto serial
que intercambia mensajes en formato JSON.

Ejemplo de mensaje esperado desde el dispositivo:

    {"variable": "temperature", "value": 24.8, "unit": "C"}

El instrumento usa pyserial para la comunicación.
Es robusto ante timeouts, respuestas vacías y JSON malformado.
"""

import json
from typing import Any

from unilab.contracts.models import Command, Measurement
from unilab.modules.instruments.base import InstrumentBase

try:
    import serial  # type: ignore
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


class SerialJsonInstrument(InstrumentBase):
    """
    Instrumento conectado por puerto serial que usa JSON como protocolo.

    Configuración esperada:

    {
        "port": "/dev/ttyUSB0",       # Puerto serial
        "baudrate": 115200,            # Velocidad de comunicación
        "timeout": 1.0,               # Timeout de lectura en segundos
        "variable": "temperature",    # Variable principal que mide
        "unit": "C"                   # Unidad de la variable principal
    }
    """

    def __init__(
        self,
        instrument_id: str,
        name: str,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(instrument_id=instrument_id, name=name, config=config)

        self._port: str = self.config.get("port", "/dev/ttyUSB0")
        self._baudrate: int = int(self.config.get("baudrate", 115200))
        self._timeout: float = float(self.config.get("timeout", 1.0))
        self._variable: str = self.config.get("variable", "value")
        self._unit: str = self.config.get("unit", "raw")
        self._serial: Any = None  # serial.Serial cuando esté conectado

    def connect(self) -> None:
        """
        Abre el puerto serial y establece la conexión.

        Raises:
            RuntimeError: Si pyserial no está instalado.
            RuntimeError: Si el puerto no se puede abrir.
        """
        if not SERIAL_AVAILABLE:
            raise RuntimeError(
                "pyserial no está instalado. "
                "Ejecuta: pip install pyserial"
            )

        try:
            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                timeout=self._timeout,
            )
            self._connected = True
        except serial.SerialException as error:
            self._connected = False
            raise RuntimeError(
                f"No se pudo abrir el puerto serial '{self._port}': {error}"
            ) from error

    def disconnect(self) -> None:
        """
        Cierra el puerto serial.
        """
        if self._serial is not None and self._serial.is_open:
            self._serial.close()
        self._serial = None
        self._connected = False

    def read_status(self) -> dict[str, Any]:
        """
        Retorna el estado actual del puerto serial.
        """
        if self._serial is None or not self._serial.is_open:
            return {
                "instrument_id": self.instrument_id,
                "connected": False,
                "port": self._port,
            }

        return {
            "instrument_id": self.instrument_id,
            "connected": True,
            "port": self._serial.port,
            "baudrate": self._serial.baudrate,
            "timeout": self._serial.timeout,
            "in_waiting": self._serial.in_waiting,
        }

    def send_command(self, command: Command) -> None:
        """
        Serializa el comando a JSON y lo envía por el puerto serial.

        El mensaje enviado tiene el formato:
            {"action": "...", "params": {...}}

        Raises:
            RuntimeError: Si el instrumento no está conectado.
            RuntimeError: Si ocurre un error al escribir en el puerto.
        """
        if not self._connected or self._serial is None:
            self._mark_command_failed(command)
            raise RuntimeError(
                f"El instrumento '{self.name}' no está conectado."
            )

        try:
            payload = json.dumps({
                "action": command.action,
                "params": command.params,
            })
            self._serial.write((payload + "\n").encode("utf-8"))
            self._mark_command_sent(command)

        except Exception as error:
            self._mark_command_failed(command)
            raise RuntimeError(
                f"Error al enviar comando al instrumento '{self.name}': {error}"
            ) from error

    def get_measurement(self) -> Measurement:
        """
        Lee una línea del puerto serial y la convierte a Measurement.

        El dispositivo debe responder con JSON en el formato:
            {"variable": "temperature", "value": 24.8, "unit": "C"}

        Raises:
            RuntimeError: Si el instrumento no está conectado.
            TimeoutError: Si no llegan datos en el tiempo configurado.
            ValueError: Si el JSON recibido no es válido o le faltan campos.
        """
        if not self._connected or self._serial is None:
            raise RuntimeError(
                f"El instrumento '{self.name}' no está conectado."
            )

        try:
            raw_line = self._serial.readline()
        except Exception as error:
            raise RuntimeError(
                f"Error al leer del puerto serial '{self._port}': {error}"
            ) from error

        if not raw_line:
            raise TimeoutError(
                f"El instrumento '{self.name}' no respondió dentro del timeout de {self._timeout}s."
            )

        try:
            decoded = raw_line.decode("utf-8").strip()
            data = json.loads(decoded)
        except UnicodeDecodeError as error:
            raise ValueError(
                f"El mensaje del instrumento '{self.name}' no está en UTF-8."
            ) from error
        except json.JSONDecodeError as error:
            raise ValueError(
                f"El instrumento '{self.name}' envió un JSON inválido: '{decoded}'"
            ) from error

        return self._parse_measurement(data)

    def _parse_measurement(self, data: dict[str, Any]) -> Measurement:
        """
        Convierte un diccionario JSON a Measurement.

        Acepta el formato completo:
            {"variable": "temperature", "value": 24.8, "unit": "C"}

        O el formato simple (usa la variable y unidad de config):
            {"value": 24.8}
        """
        if "value" not in data:
            raise ValueError(
                f"El JSON del instrumento '{self.name}' no contiene el campo 'value'."
            )

        value = data["value"]
        if not isinstance(value, int | float):
            raise ValueError(
                f"El campo 'value' del instrumento '{self.name}' debe ser numérico. "
                f"Se recibió: {type(value).__name__}"
            )

        variable = data.get("variable", self._variable)
        unit = data.get("unit", self._unit)

        return Measurement(
            source=self.instrument_id,
            variable=variable,
            value=float(value),
            unit=unit,
        )
