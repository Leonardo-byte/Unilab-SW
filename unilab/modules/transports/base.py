"""
Clase base para transportes de UniLab.

Un transporte es la capa de comunicación de bajo nivel.
Se encarga únicamente de enviar y recibir bytes crudos.
No sabe nada de JSON, TelemetryPacket ni Measurement.

Los módulos de adquisición (UdpJsonReceiver, TcpJsonReceiver, etc.)
usan un transporte para obtener los bytes y luego los parsean.

Esto separa claramente:
- Transporte: abrir/cerrar conexión, enviar/recibir bytes.
- Adquisición: interpretar bytes y convertirlos a contratos de UniLab.
"""

from abc import ABC, abstractmethod
from typing import Any


class TransportBase(ABC):
    """
    Interfaz común para todos los transportes de UniLab.

    Un transporte puede ser UDP, TCP, Serial, HTTP, MQTT u otro.
    La interfaz siempre es la misma: open, close, send, receive.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._is_open = False

    @abstractmethod
    def open(self) -> None:
        """
        Abre la conexión o socket del transporte.
        """
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """
        Cierra la conexión o socket del transporte.
        """
        raise NotImplementedError

    @abstractmethod
    def receive(self, buffer_size: int = 1024) -> bytes | None:
        """
        Recibe datos crudos del transporte.

        Retorna:
            bytes: Si llegaron datos.
            None: Si no hay datos disponibles (timeout).
        """
        raise NotImplementedError

    def send(self, data: bytes) -> None:
        """
        Envía datos crudos por el transporte.

        Por defecto no implementado. Solo los transportes bidireccionales
        como TCP y Serial lo implementan.
        """
        raise NotImplementedError(
            f"El transporte '{self.__class__.__name__}' no soporta envío de datos."
        )

    def is_open(self) -> bool:
        """
        Retorna True si el transporte está activo.
        """
        return self._is_open

    def get_status(self) -> dict[str, Any]:
        """
        Retorna el estado del transporte.
        """
        return {
            "type": self.__class__.__name__,
            "is_open": self._is_open,
            "config": self.config,
        }
