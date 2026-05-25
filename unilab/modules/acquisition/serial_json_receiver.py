"""
Receptor serial JSON para UniLab.

Recibe paquetes de telemetría desde un dispositivo conectado por puerto serial
que envía líneas JSON terminadas en newline.

Formato esperado:

    {"device_id": "arduino_01", "temperature": 24.8, "unit": "C"}

O formato con lista de mediciones:

    {"device_id": "arduino_01", "measurements": [
        {"variable": "temperature", "value": 24.8, "unit": "C"}
    ]}
"""

import json
from typing import Any

from unilab.contracts.models import Measurement, TelemetryPacket
from unilab.modules.acquisition.base import AcquisitionBase
from unilab.modules.transports.serial_transport import SerialTransport


class SerialJsonReceiver(AcquisitionBase):
    """
    Receptor de telemetría por puerto serial usando JSON.

    Configuración esperada:

    {
        "port": "/dev/ttyUSB0",
        "baudrate": 115200,
        "timeout": 1.0
    }
    """

    def __init__(self, name: str, config: dict[str, Any] | None = None) -> None:
        super().__init__(name=name, config=config)
        self._transport = SerialTransport(config=self.config)

    def setup(self) -> None:
        """
        Abre el puerto serial.
        """
        self._transport.open()
        self._is_setup = True

    def shutdown(self) -> None:
        """
        Detiene la adquisición y cierra el puerto serial.
        """
        self.stop()
        self._transport.close()
        self._is_setup = False

    def read_packet(self) -> TelemetryPacket | None:
        """
        Lee una línea JSON del puerto serial y la convierte a TelemetryPacket.

        Retorna:
            TelemetryPacket: Si llegó un JSON válido.
            None: Si no hay datos (timeout).

        Raises:
            RuntimeError: Si el receptor no está iniciado.
            ValueError: Si el mensaje no es JSON válido.
        """
        if not self._is_running:
            raise RuntimeError(
                f"El receptor serial '{self.name}' debe estar iniciado antes de leer datos."
            )

        raw_data = self._transport.receive()

        if raw_data is None or raw_data == b"":
            return None

        try:
            decoded = raw_data.decode("utf-8").strip()
            json_data = json.loads(decoded)
        except UnicodeDecodeError as error:
            raise ValueError("El mensaje serial no está en UTF-8.") from error
        except json.JSONDecodeError as error:
            raise ValueError(f"El mensaje serial no contiene JSON válido: '{decoded}'") from error

        return self._json_to_packet(json_data)

    def _json_to_packet(self, json_data: dict[str, Any]) -> TelemetryPacket:
        device_id = json_data.get("device_id", "serial_device")
        measurements = self._extract_measurements(json_data=json_data, source=device_id)
        return TelemetryPacket(source=device_id, measurements=measurements)

    def _extract_measurements(self, json_data: dict[str, Any], source: str) -> list[Measurement]:
        if "measurements" in json_data:
            return self._from_list(json_data["measurements"], source)
        return self._from_flat(json_data, source)

    def _from_list(self, data: Any, source: str) -> list[Measurement]:
        if not isinstance(data, list):
            raise ValueError("El campo 'measurements' debe ser una lista.")
        return [
            Measurement(
                source=source,
                variable=item["variable"],
                value=item["value"],
                unit=item.get("unit", "raw"),
            )
            for item in data
            if isinstance(item, dict) and "variable" in item and "value" in item
        ]

    def _from_flat(self, json_data: dict[str, Any], source: str) -> list[Measurement]:
        ignored = {"device_id", "timestamp", "status", "type"}
        measurements = [
            Measurement(source=source, variable=key, value=float(value), unit="raw")
            for key, value in json_data.items()
            if key not in ignored and isinstance(value, int | float)
        ]
        if not measurements:
            raise ValueError("El JSON serial no contiene mediciones válidas.")
        return measurements
