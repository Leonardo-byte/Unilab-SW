"""
Clases base para los módulos de adquisición de UniLab.

Este archivo define una estructura común mínima para los módulos de adquisición.
Las implementaciones concretas podrán adquirir datos desde UDP, TCP, Serial,
MQTT, HTTP, archivos o fuentes simuladas.

Ejemplos de módulos concretos:
- UdpJsonReceiver
- SerialJsonReceiver
- TcpJsonReceiver
- CsvFileReceiver
"""

from abc import ABC, abstractmethod
from typing import Any

from unilab.contracts.models import TelemetryPacket


class AcquisitionBase(ABC):
    """
    Clase base para todos los módulos de adquisición.

    Un módulo de adquisición se encarga de recibir datos externos y convertirlos
    a los contratos comunes de UniLab, principalmente TelemetryPacket.

    Esta clase base no sabe si los datos vienen de:
    - ESP32 por UDP
    - ESP32 por TCP
    - Arduino por Serial
    - Un archivo CSV
    - Una fuente simulada

    Ese detalle pertenece a cada implementación concreta.
    """

    def __init__(self, name: str, config: dict[str, Any] | None = None) -> None:
        if not name or not name.strip():
            raise ValueError("El nombre del módulo de adquisición no puede estar vacío.")

        self.name = name
        self.config = config or {}
        self._is_setup = False
        self._is_running = False

    def setup(self) -> None:
        """
        Prepara el módulo de adquisición.

        Las clases concretas pueden sobrescribir este método si necesitan abrir
        sockets, puertos seriales, archivos u otros recursos externos.
        """
        self._is_setup = True

    def start(self) -> None:
        """
        Inicia la adquisición.

        El módulo debe haber sido configurado antes de iniciar.
        """
        if not self._is_setup:
            raise RuntimeError(
                f"El módulo de adquisición '{self.name}' debe ejecutar setup() antes de iniciar."
            )

        self._is_running = True

    def stop(self) -> None:
        """
        Detiene la adquisición.
        """
        self._is_running = False

    def shutdown(self) -> None:
        """
        Detiene el módulo y libera recursos.

        Las clases concretas pueden sobrescribir este método si necesitan cerrar
        sockets, puertos seriales, archivos o tareas en segundo plano.
        """
        self.stop()
        self._is_setup = False

    @abstractmethod
    def read_packet(self) -> TelemetryPacket | None:
        """
        Lee un paquete de telemetría.

        Retorna:
            TelemetryPacket:
                Cuando se recibió y convirtió correctamente un paquete válido.

            None:
                Cuando todavía no hay datos disponibles.
        """
        raise NotImplementedError

    def is_running(self) -> bool:
        """
        Retorna si el módulo de adquisición está ejecutándose.
        """
        return self._is_running

    def is_setup(self) -> bool:
        """
        Retorna si el módulo de adquisición ya fue configurado.
        """
        return self._is_setup

    def get_status(self) -> dict[str, Any]:
        """
        Retorna un diccionario simple con el estado del módulo.

        Esto es útil para depuración, dashboards y pruebas de integración.
        """
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "is_setup": self._is_setup,
            "is_running": self._is_running,
            "config": self.config,
        }
