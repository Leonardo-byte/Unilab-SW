"""
Receptor UDP JSON para módulos de adquisición de UniLab.

Este módulo permite recibir telemetría enviada por un dispositivo externo,
por ejemplo un ESP32, usando paquetes UDP en formato JSON.

La responsabilidad de esta clase es:

1. Abrir un socket UDP.
2. Esperar mensajes JSON.
3. Convertir esos mensajes a Measurement.
4. Agrupar las mediciones en un TelemetryPacket.

Este archivo pertenece a Persona 2 y se construye encima de la base ya creada
por Persona 1, sin modificar contracts/, core/ ni config/.
"""

import json
import socket
from typing import Any

from unilab.contracts.models import Measurement, TelemetryPacket
from unilab.modules.acquisition.base import AcquisitionBase


class UdpJsonReceiver(AcquisitionBase):
    """
    Receptor de telemetría por UDP usando JSON.

    Ejemplo de JSON esperado desde un ESP32:

    {
        "device_id": "esp32_01",
        "measurements": [
            {
                "variable": "temperature",
                "value": 24.8,
                "unit": "C"
            },
            {
                "variable": "humidity",
                "value": 68.2,
                "unit": "%"
            }
        ]
    }

    También se acepta un formato más simple:

    {
        "device_id": "esp32_01",
        "temperature": 24.8,
        "humidity": 68.2
    }
    """

    def __init__(self, name: str, config: dict[str, Any] | None = None) -> None:
        super().__init__(name=name, config=config)

        self.host: str = self.config.get("host", "0.0.0.0")
        self.port: int = int(self.config.get("port", 5005))
        self.buffer_size: int = int(self.config.get("buffer_size", 1024))
        self.timeout: float = float(self.config.get("timeout", 0.1))

        self._socket: socket.socket | None = None

    def setup(self) -> None:
        """
        Crea y configura el socket UDP.

        El socket queda escuchando en la dirección y puerto indicados en config.
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((self.host, self.port))
        self._socket.settimeout(self.timeout)

        self._is_setup = True

    def shutdown(self) -> None:
        """
        Detiene la adquisición y cierra el socket UDP.
        """
        self.stop()

        if self._socket is not None:
            self._socket.close()
            self._socket = None

        self._is_setup = False

    def read_packet(self) -> TelemetryPacket | None:
        """
        Lee un paquete UDP y lo convierte a TelemetryPacket.

        Retorna:
            TelemetryPacket:
                Si llegó un JSON válido con mediciones.

            None:
                Si no llegó ningún dato durante el tiempo de espera.
        """
        if not self._is_running:
            raise RuntimeError(
                f"El módulo de adquisición '{self.name}' debe estar iniciado antes de leer datos."
            )

        if self._socket is None:
            raise RuntimeError(
                f"El módulo de adquisición '{self.name}' no tiene un socket UDP activo."
            )

        try:
            raw_data, _address = self._socket.recvfrom(self.buffer_size)
        except socket.timeout:
            return None

        try:
            decoded_data = raw_data.decode("utf-8")
            json_data = json.loads(decoded_data)
        except UnicodeDecodeError as error:
            raise ValueError("El paquete UDP recibido no está codificado en UTF-8.") from error
        except json.JSONDecodeError as error:
            raise ValueError("El paquete UDP recibido no contiene un JSON válido.") from error

        return self._json_to_packet(json_data)

    def _json_to_packet(self, json_data: dict[str, Any]) -> TelemetryPacket:
        """
        Convierte un diccionario JSON a TelemetryPacket.
        """
        device_id = json_data.get("device_id", "unknown_device")
        measurements = self._extract_measurements(
            json_data=json_data,
            source=device_id,
        )

        return TelemetryPacket(
            source=device_id,
            measurements=measurements,
        )

    def _extract_measurements(self, json_data: dict[str, Any], source: str,) -> list[Measurement]:
        """
        Extrae mediciones desde el JSON recibido.
        """
        if "measurements" in json_data:
            return self._extract_measurements_from_list(
                data=json_data["measurements"],
                source=source,
            )

        return self._extract_measurements_from_simple_json(
            json_data=json_data,
            source=source,
        )


    def _extract_measurements_from_list(self,data: Any,source: str,) -> list[Measurement]:
        """
        Extrae mediciones desde una lista de diccionarios.
        """
        if not isinstance(data, list):
            raise ValueError("El campo 'measurements' debe ser una lista.")

        measurements: list[Measurement] = []

        for item in data:
            if not isinstance(item, dict):
                raise ValueError("Cada medición dentro de 'measurements' debe ser un objeto JSON.")

            measurement = Measurement(
                source=source,
                variable=item["variable"],
                value=item["value"],
                unit=item.get("unit", "raw"),
            )

            measurements.append(measurement)

        return measurements


    def _extract_measurements_from_simple_json(self,json_data: dict[str, Any],source: str,) -> list[Measurement]:
        """
        Extrae mediciones desde un JSON plano.

        Se ignoran campos de identificación o metadatos.
        """
        ignored_fields = {
            "device_id",
            "timestamp",
            "status",
            "type",
        }

        measurements: list[Measurement] = []

        for key, value in json_data.items():
            if key in ignored_fields:
                continue

            if isinstance(value, int | float):
                measurement = Measurement(
                    source=source,
                    variable=key,
                    value=value,
                    unit="raw",
                )

                measurements.append(measurement)

        if not measurements:
            raise ValueError("El JSON recibido no contiene mediciones válidas.")

        return measurements

