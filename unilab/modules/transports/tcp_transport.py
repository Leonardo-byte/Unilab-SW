"""
Transporte TCP para UniLab.

Funciona como servidor TCP: acepta una conexión de un cliente (ESP32)
y lee datos en forma de líneas terminadas en newline.

No interpreta el contenido: solo entrega bytes crudos por línea.
"""

import socket
from typing import Any

from unilab.modules.transports.base import TransportBase


class TcpTransport(TransportBase):
    """
    Transporte TCP en modo servidor para UniLab.

    Escucha en un host y puerto, acepta una conexión de cliente y lee líneas.

    Configuración esperada:

    {
        "host": "0.0.0.0",   # Dirección de escucha
        "port": 5006,          # Puerto TCP
        "timeout": 1.0,        # Timeout de aceptación y lectura en segundos
        "buffer_size": 4096    # Tamaño del buffer de lectura
    }
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config=config)

        self._host: str = self.config.get("host", "0.0.0.0")
        self._port: int = int(self.config.get("port", 5006))
        self._timeout: float = float(self.config.get("timeout", 1.0))
        self._buffer_size: int = int(self.config.get("buffer_size", 4096))

        self._server_socket: socket.socket | None = None
        self._client_socket: socket.socket | None = None
        self._recv_buffer: bytes = b""

    def open(self) -> None:
        """
        Crea el servidor TCP y espera una conexión de cliente.

        Raises:
            RuntimeError: Si no se puede abrir el socket o el cliente no conecta.
        """
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind((self._host, self._port))
            self._server_socket.listen(1)
            self._server_socket.settimeout(self._timeout)

            self._client_socket, _ = self._server_socket.accept()
            self._client_socket.settimeout(self._timeout)
            self._is_open = True

        except socket.timeout as error:
            self._is_open = False
            raise RuntimeError(
                f"Ningún cliente TCP se conectó a {self._host}:{self._port} "
                f"dentro del timeout de {self._timeout}s."
            ) from error
        except OSError as error:
            self._is_open = False
            raise RuntimeError(
                f"No se pudo abrir el servidor TCP en {self._host}:{self._port}: {error}"
            ) from error

    def close(self) -> None:
        """
        Cierra el cliente y el servidor TCP.
        """
        if self._client_socket is not None:
            try:
                self._client_socket.close()
            except Exception:
                pass
            self._client_socket = None

        if self._server_socket is not None:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None

        self._recv_buffer = b""
        self._is_open = False

    def receive(self, buffer_size: int = 4096) -> bytes | None:
        """
        Lee una línea completa (terminada en \\n) del cliente TCP.

        Retorna:
            bytes: La línea recibida sin el newline.
            None: Si no llegaron datos (timeout).

        Raises:
            RuntimeError: Si el socket no está abierto o el cliente se desconectó.
        """
        if self._client_socket is None or not self._is_open:
            raise RuntimeError("El transporte TCP no está abierto.")

        try:
            while b"\n" not in self._recv_buffer:
                chunk = self._client_socket.recv(buffer_size or self._buffer_size)
                if not chunk:
                    raise RuntimeError("El cliente TCP se desconectó.")
                self._recv_buffer += chunk

            line, self._recv_buffer = self._recv_buffer.split(b"\n", 1)
            return line.strip()

        except socket.timeout:
            return None

    def send(self, data: bytes) -> None:
        """
        Envía datos al cliente TCP conectado.

        Raises:
            RuntimeError: Si el socket no está abierto.
        """
        if self._client_socket is None or not self._is_open:
            raise RuntimeError("El transporte TCP no está abierto.")

        self._client_socket.sendall(data)

    def get_status(self) -> dict[str, Any]:
        status = super().get_status()
        status.update({
            "host": self._host,
            "port": self._port,
            "timeout": self._timeout,
            "client_connected": self._client_socket is not None,
        })
        return status
