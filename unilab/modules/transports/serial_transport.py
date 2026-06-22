"""
Transporte serial para UniLab.

Abre un puerto serial y lee líneas de texto crudo.
No interpreta el contenido: solo entrega bytes crudos.

Usado por SerialJsonReceiver para recibir datos de un Arduino, ESP32 serial u otro.
"""

from typing import Any

from unilab.modules.transports.base import TransportBase

try:
    import serial  # type: ignore
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


class SerialTransport(TransportBase):
    """
    Transporte serial (UART) para UniLab.

    Configuración esperada:

    {
        "port": "/dev/ttyUSB0",  # Puerto serial
        "baudrate": 115200,       # Velocidad de comunicación
        "timeout": 1.0            # Timeout de lectura en segundos
    }
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config=config)

        self._port: str = self.config.get("port", "/dev/ttyUSB0")
        self._baudrate: int = int(self.config.get("baudrate", 115200))
        self._timeout: float = float(self.config.get("timeout", 1.0))
        self._serial: Any = None

    def open(self) -> None:
        """
        Abre el puerto serial.

        Raises:
            RuntimeError: Si pyserial no está instalado.
            RuntimeError: Si el puerto no se puede abrir.
        """
        if not SERIAL_AVAILABLE:
            raise RuntimeError(
                "pyserial no está instalado. Ejecuta: pip install pyserial"
            )

        try:
            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                timeout=self._timeout,
            )
            self._is_open = True
        except serial.SerialException as error:
            self._is_open = False
            raise RuntimeError(
                f"No se pudo abrir el puerto serial '{self._port}': {error}"
            ) from error

    def close(self) -> None:
        """
        Cierra el puerto serial.
        """
        if self._serial is not None and self._serial.is_open:
            self._serial.close()
        self._serial = None
        self._is_open = False

    def receive(self, buffer_size: int = 1024) -> bytes | None:
        """
        Lee una línea del puerto serial.

        Retorna:
            bytes: La línea leída (sin newline).
            None: Si no llegaron datos en el timeout.

        Raises:
            RuntimeError: Si el puerto no está abierto.
        """
        if self._serial is None or not self._is_open:
            raise RuntimeError("El transporte serial no está abierto.")

        try:
            line = self._serial.readline()
            return line.rstrip(b"\r\n") if line else None
        except Exception as error:
            raise RuntimeError(
                f"Error al leer del puerto serial '{self._port}': {error}"
            ) from error

    def send(self, data: bytes) -> None:
        """
        Envía bytes por el puerto serial.

        Raises:
            RuntimeError: Si el puerto no está abierto.
        """
        if self._serial is None or not self._is_open:
            raise RuntimeError("El transporte serial no está abierto.")

        self._serial.write(data)
        self._serial.flush()

    def get_status(self) -> dict[str, Any]:
        status = super().get_status()

        try:
            in_waiting = self._serial.in_waiting if self._serial else 0
            serial_is_open = self._serial.is_open if self._serial else False
        except Exception:
            in_waiting = 0
            serial_is_open = False

        status.update(
            {
                "port": self._port,
                "baudrate": self._baudrate,
                "timeout": self._timeout,
                "is_open": self._is_open,
                "serial_is_open": serial_is_open,
                "in_waiting": in_waiting,
            }
        )

        return status
    
    def send_line(self, data: bytes) -> None:
        if not data.endswith(b"\n"):
            data += b"\n"
        self.send(data)
