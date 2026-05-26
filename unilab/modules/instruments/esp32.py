"""
Adaptador de instrumento para ESP32 en UniLab.

Este módulo representa un ESP32 como instrumento del sistema.
El ESP32 puede comunicarse por distintos transportes (UDP, TCP, Serial).
Este adaptador usa un transporte inyectado para recibir datos.

El ESP32 típicamente envía JSON con mediciones múltiples:

    {
        "device_id": "esp32_lab01",
        "measurements": [
            {"variable": "temperature", "value": 24.8, "unit": "C"},
            {"variable": "humidity", "value": 68.0, "unit": "%"}
        ]
    }

Este instrumento convierte ese paquete y retorna la primera medición disponible.
Para múltiples mediciones, usar directamente UdpJsonReceiver o TcpJsonReceiver.
"""

from typing import Any

from unilab.contracts.models import Command, Measurement, TelemetryPacket
from unilab.modules.instruments.base import InstrumentBase


class Esp32Instrument(InstrumentBase):
    """
    Instrumento que representa un ESP32 conectado al sistema.

    Se conecta usando un receptor de adquisición (UdpJsonReceiver, etc.)
    que se inyecta como dependencia. El instrumento delega la recepción
    de datos al receptor y expone la interfaz común de InstrumentBase.

    Esto permite que el core, el scheduler y safety traten al ESP32
    igual que a cualquier otro instrumento.
    """

    def __init__(
        self,
        instrument_id: str,
        name: str,
        receiver: Any,  # AcquisitionBase — sin import circular
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(instrument_id=instrument_id, name=name, config=config)

        if receiver is None:
            raise ValueError(
                "El ESP32 requiere un receptor de adquisición (receiver) para funcionar."
            )

        self._receiver = receiver
        self._last_packet: TelemetryPacket | None = None

    def connect(self) -> None:
        """
        Inicializa y arranca el receptor de adquisición del ESP32.
        """
        self._receiver.setup()
        self._receiver.start()
        self._connected = True

    def disconnect(self) -> None:
        """
        Detiene y apaga el receptor de adquisición.
        """
        self._receiver.shutdown()
        self._connected = False

    def read_status(self) -> dict[str, Any]:
        """
        Retorna el estado del receptor de adquisición asociado.
        """
        return {
            "instrument_id": self.instrument_id,
            "connected": self._connected,
            "receiver": self._receiver.get_status(),
            "last_packet_source": (
                self._last_packet.source if self._last_packet else None
            ),
            "last_packet_measurements": (
                len(self._last_packet.measurements) if self._last_packet else 0
            ),
        }

    def send_command(self, command: Command) -> None:
        """
        El ESP32 en modo adquisición pasiva no acepta comandos actualmente.

        Este método registra el intento pero no envía nada.
        En una implementación futura podría usar un canal de retorno
        (TCP, MQTT, HTTP) para enviar comandos al dispositivo.
        """
        self._mark_command_failed(command)
        raise NotImplementedError(
            f"El instrumento ESP32 '{self.name}' no soporta comandos salientes aún. "
            "Implementar un canal de retorno (TCP/HTTP/MQTT) en versiones futuras."
        )

    def get_measurement(self) -> Measurement:
        """
        Lee un paquete del receptor y retorna la primera medición disponible.

        Raises:
            RuntimeError: Si el instrumento no está conectado.
            RuntimeError: Si no hay mediciones disponibles en el paquete.
        """
        if not self._connected:
            raise RuntimeError(
                f"El instrumento ESP32 '{self.name}' no está conectado."
            )

        packet = self._receiver.read_packet()

        if packet is None:
            raise RuntimeError(
                f"El instrumento ESP32 '{self.name}' no recibió datos aún."
            )

        if not packet.measurements:
            raise RuntimeError(
                f"El paquete del ESP32 '{self.name}' no contiene mediciones."
            )

        self._last_packet = packet
        return packet.measurements[0]

    def get_last_packet(self) -> TelemetryPacket | None:
        """
        Retorna el último paquete de telemetría recibido.
        """
        return self._last_packet

    def get_status(self) -> dict[str, Any]:
        status = super().get_status()
        status["receiver_type"] = self._receiver.__class__.__name__
        return status
