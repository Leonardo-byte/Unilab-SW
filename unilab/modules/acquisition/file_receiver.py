"""
Receptor de archivos para UniLab.

Permite leer telemetría desde archivos en lugar de una red o puerto serial.
Útil para pruebas, replay de experimentos y desarrollo offline.

Formatos soportados:
- JSON Lines (.jsonl): una medición o paquete JSON por línea.
- JSON Array (.json): lista de paquetes en un archivo JSON.
- CSV (.csv): columnas como variables, filas como mediciones.

El receptor lee el archivo línea por línea (o fila por fila en CSV)
y entrega un TelemetryPacket por llamada a read_packet().
"""

import csv
import json
from io import StringIO
from pathlib import Path
from typing import Any

from unilab.contracts.models import Measurement, TelemetryPacket
from unilab.modules.acquisition.base import AcquisitionBase


class FileReceiver(AcquisitionBase):
    """
    Receptor de telemetría desde archivos.

    Itera el archivo en cada llamada a read_packet(), entregando
    un paquete por vez. Cuando el archivo se agota, retorna None.

    Configuración esperada:

    {
        "filepath": "datos/experimento_01.jsonl",  # Ruta al archivo
        "source": "file_replay",                    # Nombre de la fuente
        "format": "jsonl"                           # "jsonl", "json" o "csv"
    }
    """

    SUPPORTED_FORMATS = {"jsonl", "json", "csv"}

    def __init__(self, name: str, config: dict[str, Any] | None = None) -> None:
        super().__init__(name=name, config=config)

        filepath = self.config.get("filepath")
        if not filepath:
            raise ValueError(
                f"El FileReceiver '{self.name}' requiere 'filepath' en su configuración."
            )

        self._filepath = Path(filepath)
        self._source: str = self.config.get("source", self._filepath.stem)
        self._format: str = self.config.get("format", self._detect_format()).lower()

        if self._format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Formato '{self._format}' no soportado. "
                f"Formatos válidos: {self.SUPPORTED_FORMATS}"
            )

        self._packets: list[TelemetryPacket] = []
        self._index: int = 0

    def setup(self) -> None:
        """
        Lee y parsea el archivo completo en memoria.

        Raises:
            FileNotFoundError: Si el archivo no existe.
            ValueError: Si el formato no es válido.
        """
        if not self._filepath.exists():
            raise FileNotFoundError(
                f"El archivo '{self._filepath}' no existe."
            )

        if self._format == "jsonl":
            self._packets = self._load_jsonl()
        elif self._format == "json":
            self._packets = self._load_json_array()
        elif self._format == "csv":
            self._packets = self._load_csv()

        self._index = 0
        self._is_setup = True

    def shutdown(self) -> None:
        """
        Libera los datos cargados en memoria.
        """
        self.stop()
        self._packets = []
        self._index = 0
        self._is_setup = False

    def read_packet(self) -> TelemetryPacket | None:
        """
        Retorna el siguiente paquete del archivo.

        Retorna:
            TelemetryPacket: El siguiente paquete disponible.
            None: Si el archivo ya fue consumido completamente.
        """
        if not self._is_running:
            raise RuntimeError(
                f"El FileReceiver '{self.name}' debe estar iniciado antes de leer datos."
            )

        if self._index >= len(self._packets):
            return None

        packet = self._packets[self._index]
        self._index += 1
        return packet

    def has_more(self) -> bool:
        """
        Retorna True si quedan paquetes por leer.
        """
        return self._index < len(self._packets)

    def reset(self) -> None:
        """
        Reinicia el cursor al inicio del archivo.
        """
        self._index = 0

    def total_packets(self) -> int:
        """
        Retorna el total de paquetes cargados desde el archivo.
        """
        return len(self._packets)

    def get_status(self) -> dict[str, Any]:
        status = super().get_status()
        status.update({
            "filepath": str(self._filepath),
            "format": self._format,
            "total_packets": len(self._packets),
            "current_index": self._index,
            "has_more": self.has_more(),
        })
        return status

    # -------------------------------------------------------------------------
    # Loaders internos
    # -------------------------------------------------------------------------

    def _load_jsonl(self) -> list[TelemetryPacket]:
        """
        Carga un archivo JSON Lines: un JSON por línea.
        Cada línea puede ser un paquete completo o una medición simple.
        """
        packets = []
        with open(self._filepath, encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    packets.append(self._dict_to_packet(data))
                except (json.JSONDecodeError, ValueError) as error:
                    raise ValueError(
                        f"Error en línea {line_number} de '{self._filepath}': {error}"
                    ) from error
        return packets

    def _load_json_array(self) -> list[TelemetryPacket]:
        """
        Carga un archivo JSON con un array de paquetes.
        """
        with open(self._filepath, encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(
                f"El archivo JSON '{self._filepath}' debe contener un array de paquetes."
            )

        return [self._dict_to_packet(item) for item in data]

    def _load_csv(self) -> list[TelemetryPacket]:
        """
        Carga un archivo CSV donde cada fila es una medición.

        Columnas esperadas: variable, value, unit (unit es opcional).
        La fuente se toma de la configuración.

        Si hay una columna 'device_id', se usa como source por fila.
        """
        packets = []
        with open(self._filepath, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row_number, row in enumerate(reader, start=2):
                try:
                    source = row.get("device_id", self._source)
                    variable = row["variable"]
                    value = float(row["value"])
                    unit = row.get("unit", "raw")

                    measurement = Measurement(
                        source=source,
                        variable=variable,
                        value=value,
                        unit=unit,
                    )
                    packet = TelemetryPacket(
                        source=source,
                        measurements=[measurement],
                    )
                    packets.append(packet)
                except (KeyError, ValueError) as error:
                    raise ValueError(
                        f"Error en fila {row_number} de '{self._filepath}': {error}"
                    ) from error
        return packets

    def _dict_to_packet(self, data: dict[str, Any]) -> TelemetryPacket:
        """
        Convierte un diccionario JSON a TelemetryPacket.
        Soporta el mismo formato que UdpJsonReceiver y TcpJsonReceiver.
        """
        source = data.get("device_id", self._source)

        if "measurements" in data:
            measurements = [
                Measurement(
                    source=source,
                    variable=item["variable"],
                    value=item["value"],
                    unit=item.get("unit", "raw"),
                )
                for item in data["measurements"]
                if isinstance(item, dict) and "variable" in item and "value" in item
            ]
        else:
            ignored = {"device_id", "timestamp", "status", "type"}
            measurements = [
                Measurement(source=source, variable=key, value=float(val), unit="raw")
                for key, val in data.items()
                if key not in ignored and isinstance(val, int | float)
            ]

        if not measurements:
            raise ValueError(f"El paquete del archivo no contiene mediciones: {data}")

        return TelemetryPacket(source=source, measurements=measurements)

    def _detect_format(self) -> str:
        """
        Detecta el formato del archivo a partir de su extensión.
        """
        suffix = self._filepath.suffix.lower()
        if suffix == ".jsonl":
            return "jsonl"
        elif suffix == ".json":
            return "json"
        elif suffix == ".csv":
            return "csv"
        return "jsonl"
