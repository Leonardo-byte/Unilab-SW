"""
Receptor TCP JSON para UniLab.

Recibe paquetes de telemetría enviados por un dispositivo (ESP32, Arduino)
usando una conexión TCP. Los mensajes deben ser JSON terminados en newline.

Formato esperado (igual que UdpJsonReceiver):

    {"device_id": "esp32_01", "measurements": [
        {"variable": "temperature", "value": 24.8, "unit": "C"}
    ]}

O formato plano:

    {"device_id": "esp32_01", "temperature": 24.8, "humidity": 68.2}
"""

import json
from typing import Any

from unilab.contracts.models import Measurement, TelemetryPacket
from unilab.modules.acquisition.base import AcquisitionBase
from unilab.modules.transports.tcp_transport import TcpTransport


class TcpJsonReceiver(AcquisitionBase):
    """
    Receptor de telemetría por TCP usando JSON.

    Actúa como servidor: espera que el ESP32 (cliente) se conecte
    y luego lee líneas JSON de la conexión.

    Configuración esperada:

    {
        "host": "0.0.0.0",
        "port": 5006,
        "timeout": 1.0
    }
    """

    def __init__(self, name: str, config: dict[str, Any] | None = None) -> None:
        super().__init__(name=name, config=config)
        self._transport = TcpTransport(config=self.config)

    def setup(self) -> None:
        """
        Abre el servidor TCP y espera la conexión del cliente.
        """
        self._transport.open()
        self._is_setup = True

    def shutdown(self) -> None:
        """
        Detiene la adquisición y cierra la conexión TCP.
        """
        self.stop()
        self._transport.close()
        self._is_setup = False

    def read_packet(self) -> TelemetryPacket | None:
        """
        Lee una línea JSON de la conexión TCP y la convierte a TelemetryPacket.

        Retorna:
            TelemetryPacket: Si llegó un JSON válido.
            None: Si no hay datos disponibles (timeout).

        Raises:
            RuntimeError: Si el módulo no está iniciado.
            ValueError: Si el JSON recibido no es válido.
        """
        if not self._is_running:
            raise RuntimeError(
                f"El receptor TCP '{self.name}' debe estar iniciado antes de leer datos."
            )

        raw_data = self._transport.receive()

        if raw_data is None:
            return None

        try:
            decoded = raw_data.decode("utf-8").strip()
            json_data = json.loads(decoded)
        except UnicodeDecodeError as error:
            raise ValueError("El mensaje TCP recibido no está en UTF-8.") from error
        except json.JSONDecodeError as error:
            raise ValueError(f"El mensaje TCP no contiene JSON válido: '{decoded}'") from error

        return self._json_to_packet(json_data)

    def _json_to_packet(self, json_data: dict[str, Any]) -> TelemetryPacket:
        device_id = json_data.get("device_id", "tcp_device")
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
            raise ValueError("El JSON TCP no contiene mediciones válidas.")
        return measurements
