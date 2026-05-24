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
        self._notes.clear()

    def get_status(self) -> dict[str, Any]:
        """Retorna el estado general del almacenamiento en memoria."""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "is_setup": self._is_setup,
            "packets_count": len(self._packets),
            "events_count": len(self._events),
            "max_packets": self.max_packets,
            "max_events": self.max_events,
            "notes_count": len(self._notes),
            "visible_variables": self.get_visible_variables(),
            "visible_variables_configured": self.is_visible_variables_configured(),
        }
    

    def set_visible_variables(self, variables: list[str]) -> None:
        """
        Define qué variables desea visualizar el usuario.

        Si se guarda una lista vacía, se interpreta como no mostrar ninguna variable.
        Si nunca se configuró esta opción, UniLab muestra todas las variables.
        """
        self._visible_variables = {
            variable for variable in variables
            if variable and variable.strip()
        }


    def get_visible_variables(self) -> list[str]:
        """
        Retorna las variables seleccionadas por el usuario.

        Si todavía no se configuró la selección, retorna una lista vacía.
        """
        if self._visible_variables is None:
            return []

        return sorted(self._visible_variables)


    def get_visible_variables_filter(self) -> list[str] | None:
        """
        Retorna el filtro real de variables visibles.

        None significa que el usuario todavía no configuró nada,
        por lo tanto se deben mostrar todas las variables.

        Lista vacía significa que el usuario deseleccionó todas las variables.
        """
        if self._visible_variables is None:
            return None

        return sorted(self._visible_variables)


    def is_visible_variables_configured(self) -> bool:
        """
        Indica si el usuario ya configuró manualmente las variables visibles.
        """
        return self._visible_variables is not None


    def add_note(
    self,
    message: str,
    variable: str | None = None,
    note_type: str = "general",) -> dict[str, Any]:
        """
        Registra una nota manual del usuario.

        La nota puede ser general o estar asociada a una variable y a una condición.
        """
        if not message or not message.strip():
            raise ValueError("La nota no puede estar vacía.")

        allowed_note_types = {
            "general",
            "below_min",
            "above_max",
        }

        if note_type not in allowed_note_types:
            raise ValueError("El tipo de nota no es válido.")

        note = {
            "message": message.strip(),
            "variable": variable,
            "note_type": note_type,
        }

        self._notes.append(note)

        return note


    def get_notes(self) -> list[dict[str, Any]]:
        """
        Retorna todas las notas registradas.
        """
        return self._notes
    
    def setup(self) -> None:
        """Inicializa el almacenamiento en memoria."""
        self._is_setup = True

    def shutdown(self) -> None:
        """Apaga el almacenamiento en memoria."""
        self._is_setup = False
