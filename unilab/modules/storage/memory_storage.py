"""
Almacenamiento en memoria para UniLab.

Este módulo guarda temporalmente paquetes de telemetría y eventos generados
durante la ejecución de una demo o prueba de integración.

No usa base de datos. Toda la información se pierde cuando se detiene el
programa.

Este archivo forma parte de la demo vertical mínima:

ESP32
  ↓ UDP JSON
UdpJsonReceiver
  ↓
TelemetryPacket
  ↓
SafetyManager
  ↓
MemoryStorage
  ↓
Dashboard / API
"""

from typing import Any

from unilab.contracts.events import Event
from unilab.contracts.models import TelemetryPacket


class MemoryStorage:
    """
    Almacenamiento temporal en memoria.

    Guarda:

    - Paquetes de telemetría recibidos.
    - Eventos generados por SafetyManager u otros módulos.

    Este módulo es útil para una demo mínima porque permite consultar los datos
    más recientes desde una API o dashboard sin implementar todavía una base de
    datos real.
    """

    def __init__(self, max_packets: int = 100, max_events: int = 100) -> None:
        if max_packets <= 0:
            raise ValueError("max_packets debe ser mayor que cero.")

        if max_events <= 0:
            raise ValueError("max_events debe ser mayor que cero.")

        self.max_packets = max_packets
        self.max_events = max_events

        self._packets: list[TelemetryPacket] = []
        self._events: list[Event] = []

    def save_packet(self, packet: TelemetryPacket) -> None:
        """
        Guarda un paquete de telemetría en memoria.

        Si se supera el número máximo de paquetes, se elimina el más antiguo.
        """
        self._packets.append(packet)

        if len(self._packets) > self.max_packets:
            self._packets.pop(0)

    def save_event(self, event: Event) -> None:
        """
        Guarda un evento en memoria.

        Si se supera el número máximo de eventos, se elimina el más antiguo.
        """
        self._events.append(event)

        if len(self._events) > self.max_events:
            self._events.pop(0)

    def save_events(self, events: list[Event]) -> None:
        """
        Guarda una lista de eventos en memoria.
        """
        for event in events:
            self.save_event(event)

    def get_latest_packet(self) -> TelemetryPacket | None:
        """
        Retorna el último paquete de telemetría recibido.

        Retorna None si todavía no se guardó ningún paquete.
        """
        if not self._packets:
            return None

        return self._packets[-1]

    def get_latest_event(self) -> Event | None:
        """
        Retorna el último evento guardado.

        Retorna None si todavía no se guardó ningún evento.
        """
        if not self._events:
            return None

        return self._events[-1]

    def get_packets(self) -> list[TelemetryPacket]:
        """
        Retorna todos los paquetes almacenados en memoria.
        """
        return self._packets

    def get_events(self) -> list[Event]:
        """
        Retorna todos los eventos almacenados en memoria.
        """
        return self._events

    def get_recent_packets(self, limit: int = 10) -> list[TelemetryPacket]:
        """
        Retorna los últimos paquetes almacenados.

        Args:
            limit:
                Número máximo de paquetes a retornar.
        """
        if limit <= 0:
            raise ValueError("limit debe ser mayor que cero.")

        return self._packets[-limit:]

    def get_recent_events(self, limit: int = 10) -> list[Event]:
        """
        Retorna los últimos eventos almacenados.

        Args:
            limit:
                Número máximo de eventos a retornar.
        """
        if limit <= 0:
            raise ValueError("limit debe ser mayor que cero.")

        return self._events[-limit:]

    def clear(self) -> None:
        """
        Limpia todos los paquetes y eventos almacenados.
        """
        self._packets.clear()
        self._events.clear()

    def get_status(self) -> dict[str, Any]:
        """
        Retorna el estado general del almacenamiento en memoria.
        """
        return {
            "type": self.__class__.__name__,
            "packets_count": len(self._packets),
            "events_count": len(self._events),
            "max_packets": self.max_packets,
            "max_events": self.max_events,
        }
