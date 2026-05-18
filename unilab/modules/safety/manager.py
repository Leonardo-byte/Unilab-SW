"""
Gestor de seguridad mínimo para UniLab.

Este módulo valida paquetes de telemetría usando reglas simples de límites
mínimos y máximos.

La idea es que Safety no dependa de cómo llegaron los datos. No le importa si
la telemetría vino por UDP, Serial, TCP, MQTT o desde un archivo. Solo recibe
un TelemetryPacket y revisa sus Measurement.

Este archivo forma parte de la demo vertical mínima:

ESP32
  ↓ UDP JSON
UdpJsonReceiver
  ↓
TelemetryPacket
  ↓
SafetyManager
  ↓
Storage / Dashboard
"""

from typing import Any

from unilab.contracts.events import Event, EventType, FaultEvent, Severity
from unilab.contracts.models import Measurement, TelemetryPacket


class SafetyManager:
    """
    Gestor de seguridad básico.

    Permite definir límites por nombre de medición.

    Ejemplo de configuración:

    {
        "temperature": {
            "min": 0,
            "max": 60
        },
        "humidity": {
            "min": 20,
            "max": 90
        }
    }

    Si una medición está fuera de rango, se genera un FaultEvent.
    Si todas las mediciones son válidas, se genera un Event normal.
    """

    def __init__(self, limits: dict[str, dict[str, float]] | None = None) -> None:
        self.limits = limits or {}

    def validate_packet(self, packet: TelemetryPacket) -> list[Event]:
        """
        Valida todas las mediciones de un paquete de telemetría.

        Retorna:
            list[Event]:
                Lista de eventos generados por la validación.

                - Si todo está correcto, retorna un evento informativo.
                - Si hay mediciones fuera de rango, retorna eventos de falla.
        """
        events: list[Event] = []

        for measurement in packet.measurements:
            event = self.validate_measurement(
                measurement=measurement,
                source=packet.source,
            )

            if event is not None:
                events.append(event)

        return events

    def validate_measurement(
        self,
        measurement: Measurement,
        source: str = "unknown_source",
    ) -> Event | None:
        """
        Valida una medición individual.

        Retorna:
            FaultEvent:
                Si la medición está fuera de los límites definidos.

            None:
                Si la medición es válida o no tiene límites configurados.
        """
        measurement_limits = self.limits.get(measurement.variable)

        if measurement_limits is None:
            return None

        min_value = measurement_limits.get("min")
        max_value = measurement_limits.get("max")

        if min_value is not None and measurement.value < min_value:
            return self._build_fault_event(
                measurement=measurement,
                source=source,
                message=(
                    f"La medición '{measurement.variable}' está por debajo del límite mínimo. "
                    f"Valor recibido: {measurement.value}. Límite mínimo: {min_value}."
                ),
            )

        if max_value is not None and measurement.value > max_value:
            return self._build_fault_event(
                measurement=measurement,
                source=source,
                message=(
                    f"La medición '{measurement.variable}' está por encima del límite máximo. "
                    f"Valor recibido: {measurement.value}. Límite máximo: {max_value}."
                ),
            )

        return None

    def update_limits(self, limits: dict[str, dict[str, float]]) -> None:
        """
        Actualiza todos los límites de seguridad.
        """
        self.limits = limits

    def set_limit(
        self,
        measurement_name: str,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> None:
        """
        Define o actualiza el límite de una medición específica.
        """
        if not measurement_name or not measurement_name.strip():
            raise ValueError("El nombre de la medición no puede estar vacío.")

        self.limits[measurement_name] = {}

        if min_value is not None:
            self.limits[measurement_name]["min"] = min_value

        if max_value is not None:
            self.limits[measurement_name]["max"] = max_value

    def get_limits(self) -> dict[str, dict[str, float]]:
        """
        Retorna los límites configurados.
        """
        return self.limits

    def get_status(self) -> dict[str, Any]:
        """
        Retorna el estado general del gestor de seguridad.
        """
        return {
            "type": self.__class__.__name__,
            "limits_count": len(self.limits),
            "limits": self.limits,
        }

    def _build_fault_event(
        self,
        measurement: Measurement,
        source: str,
        message: str,
    ) -> FaultEvent:
        """
        Construye un evento de falla para una medición fuera de rango.
        """
        return FaultEvent(
            source="SafetyManager",
            event_type=EventType.SAFETY_WARNING,
            severity=Severity.WARNING,
            message=message,
            fault_code=f"{source}.{measurement.variable}.out_of_range",
            details={
                "source": source,
                "measurement": measurement.variable,
                "value": measurement.value,
                "unit": measurement.unit,
            },
        )
