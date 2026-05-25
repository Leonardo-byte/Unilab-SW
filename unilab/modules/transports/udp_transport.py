"""
Transporte UDP para UniLab.

Abre un socket UDP y recibe datagramas.
No interpreta el contenido: solo entrega bytes crudos.

Usado por UdpJsonReceiver para recibir datos de un ESP32 u otro dispositivo.
"""

import socket
from typing import Any

from unilab.modules.transports.base import TransportBase


class UdpTransport(TransportBase):
    """
    Transporte UDP sin conexión para recepción de datagramas.

    Configuración esperada:

    {
        "host": "0.0.0.0",   # Dirección de escucha
        "port": 5005,          # Puerto UDP
        "timeout": 0.1         # Timeout de recepción en segundos
    }
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config=config)

        self._host: str = self.config.get("host", "0.0.0.0")
        self._port: int = int(self.config.get("port", 5005))
        self._timeout: float = float(self.config.get("timeout", 0.1))
        self._socket: socket.socket | None = None
        self._last_address: tuple[str, int] | None = None

    def open(self) -> None:
        """
        Crea el socket UDP y lo enlaza al host y puerto configurados.

        Raises:
            RuntimeError: Si el socket no se puede abrir.
        """
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.bind((self._host, self._port))
            self._socket.settimeout(self._timeout)
            self._is_open = True
        except OSError as error:
            self._is_open = False
            raise RuntimeError(
                f"No se pudo abrir el socket UDP en {self._host}:{self._port}: {error}"
            ) from error

    def close(self) -> None:
        """
        Cierra el socket UDP.
        """
        if self._socket is not None:
            self._socket.close()
            self._socket = None
        self._is_open = False

    def receive(self, buffer_size: int = 1024) -> bytes | None:
        """
        Espera un datagrama UDP y retorna los bytes crudos.

        Retorna:
            bytes: Si llegó un datagrama.
            None: Si el timeout expiró sin datos.

        Raises:
            RuntimeError: Si el socket no está abierto.
        """
        if self._socket is None or not self._is_open:
            raise RuntimeError("El transporte UDP no está abierto.")

        try:
            data, address = self._socket.recvfrom(buffer_size)
            self._last_address = address
            return data
        except socket.timeout:
            return None

    def get_last_address(self) -> tuple[str, int] | None:
        """
        Retorna la dirección del último remitente (IP, puerto).
        """
        return self._last_address

    def get_status(self) -> dict[str, Any]:
        status = super().get_status()
        status.update({
            "host": self._host,
            "port": self._port,
            "timeout": self._timeout,
            "last_address": self._last_address,
        })
        return status
