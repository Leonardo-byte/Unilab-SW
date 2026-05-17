from typing import Any, Protocol, runtime_checkable

from unilab.contracts.models import Command, Measurement, TelemetryPacket


@runtime_checkable
class ModuleProtocol(Protocol):
    """
    Protocolo base para cualquier módulo del sistema UniLab.

    Un módulo puede ser un instrumento, un receptor de adquisición,
    un simulador, un scheduler, un módulo de almacenamiento, safety,
    web, SiLA u otro componente interno.
    """

    name: str

    def setup(self) -> None:
        """
        Inicializa el módulo.

        Este método se debe llamar antes de usar el módulo.
        Puede cargar configuración, preparar recursos internos
        o validar dependencias.
        """
        ...

    def shutdown(self) -> None:
        """
        Libera los recursos usados por el módulo.

        Este método se debe llamar al cerrar la aplicación o cuando
        el módulo ya no será utilizado.
        """
        ...

    def get_status(self) -> dict[str, Any]:
        """
        Devuelve el estado actual del módulo.

        El formato exacto puede variar según el módulo, pero debería
        incluir información útil para diagnóstico.
        """
        ...


@runtime_checkable
class InstrumentProtocol(ModuleProtocol, Protocol):
    """
    Protocolo base para instrumentos reales o simulados.

    Todo instrumento debe poder conectarse, desconectarse,
    reportar estado, recibir comandos y entregar mediciones.
    """

    instrument_id: str

    def connect(self) -> None:
        """
        Establece conexión con el instrumento.

        En un instrumento real, esto puede abrir un puerto serial,
        socket, bus de comunicación u otro recurso físico.
        """
        ...

    def disconnect(self) -> None:
        """
        Cierra la conexión con el instrumento.
        """
        ...

    def is_connected(self) -> bool:
        """
        Indica si el instrumento está conectado.
        """
        ...

    def read_status(self) -> dict[str, Any]:
        """
        Lee el estado actual del instrumento.

        Puede incluir conexión, modo de operación, errores,
        versión de firmware, límites, etc.
        """
        ...

    def send_command(self, command: Command) -> None:
        """
        Envía un comando al instrumento.

        El comando debe seguir el modelo común definido en contracts.models.
        """
        ...

    def get_measurement(self) -> Measurement:
        """
        Obtiene una medición individual desde el instrumento.
        """
        ...


@runtime_checkable
class AcquisitionProtocol(ModuleProtocol, Protocol):
    """
    Protocolo base para módulos de adquisición de datos.

    Un módulo de adquisición puede recibir datos desde UDP, TCP,
    archivo, serial, instrumentos u otra fuente externa.
    """

    source: str

    def start(self) -> None:
        """
        Inicia la adquisición de datos.
        """
        ...

    def stop(self) -> None:
        """
        Detiene la adquisición de datos.
        """
        ...

    def read_packet(self) -> TelemetryPacket:
        """
        Lee un paquete de telemetría.

        El paquete debe usar el modelo común TelemetryPacket.
        """
        ...


@runtime_checkable
class SimulationProtocol(ModuleProtocol, Protocol):
    """
    Protocolo base para modelos de simulación.

    Permite ejecutar simulaciones de instrumentos, procesos físicos
    o experimentos sin necesidad de hardware real.
    """

    model_name: str

    def reset(self) -> None:
        """
        Reinicia el modelo de simulación a su estado inicial.
        """
        ...

    def step(self, dt: float) -> TelemetryPacket:
        """
        Avanza la simulación un intervalo de tiempo.

        Parámetros:
            dt: intervalo de tiempo en segundos.

        Retorna:
            Un paquete de telemetría generado por la simulación.
        """
        ...


@runtime_checkable
class StorageProtocol(ModuleProtocol, Protocol):
    """
    Protocolo base para almacenamiento de datos.

    Esta interfaz permite que el resto del sistema guarde mediciones,
    eventos y resultados sin depender directamente de SQL u otra tecnología.
    """

    def save_measurement(self, measurement: Measurement) -> None:
        """
        Guarda una medición individual.
        """
        ...

    def save_telemetry_packet(self, packet: TelemetryPacket) -> None:
        """
        Guarda un paquete de telemetría.
        """
        ...

    def save_event(self, event: Any) -> None:
        """
        Guarda un evento del sistema.

        Se usa Any para evitar acoplar demasiado este protocolo,
        aunque normalmente debería recibir un Event o FaultEvent.
        """
        ...


@runtime_checkable
class SafetyProtocol(ModuleProtocol, Protocol):
    """
    Protocolo base para módulos de seguridad.

    Safety debe evaluar condiciones de operación, detectar fallas
    y reportar si el sistema puede continuar ejecutándose.
    """

    def check(self, packet: TelemetryPacket) -> bool:
        """
        Evalúa si un paquete de telemetría cumple las condiciones de seguridad.

        Retorna:
            True si el sistema puede continuar.
            False si existe una condición insegura.
        """
        ...

    def get_faults(self) -> list[Any]:
        """
        Devuelve la lista de fallas o advertencias activas.
        """
        ...