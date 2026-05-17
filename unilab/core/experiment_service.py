from datetime import datetime, timezone

from unilab.contracts.models import (
    ExperimentConfig,
    ExperimentState,
    ExperimentStatus,
)


class ExperimentService:
    """
    Servicio principal para gestionar el ciclo de vida de un experimento.

    Este servicio se encarga de crear, iniciar, pausar, detener, finalizar
    o marcar como fallido un experimento. No ejecuta todavía la lógica del
    scheduler ni controla hardware directamente; solo mantiene el estado
    general del experimento actual.
    """

    def __init__(self) -> None:
        """
        Inicializa el servicio sin experimento activo.
        """
        self.current_experiment: ExperimentConfig | None = None
        self.current_state: ExperimentState | None = None

    def create_experiment(self, config: ExperimentConfig) -> ExperimentState:
        """
        Crea un nuevo experimento y lo deja en estado CREATED.

        Args:
            config: Configuración general del experimento.

        Returns:
            Estado inicial del experimento.

        Raises:
            RuntimeError: Si ya existe un experimento corriendo.
        """

        if self.current_state is not None:
            if self.current_state.status == ExperimentStatus.RUNNING:
                raise RuntimeError(
                    "No se puede crear un nuevo experimento mientras otro está corriendo."
                )

        self.current_experiment = config
        self.current_state = ExperimentState(
            experiment_id=config.experiment_id,
            status=ExperimentStatus.CREATED,
        )

        return self.current_state

    def start(self) -> ExperimentState:
        """
        Inicia el experimento actual.

        Returns:
            Estado actualizado del experimento.

        Raises:
            RuntimeError: Si no existe un experimento configurado.
            RuntimeError: Si el experimento ya está corriendo.
            RuntimeError: Si el experimento ya finalizó o falló.
        """

        self._ensure_experiment_exists()

        assert self.current_state is not None

        if self.current_state.status == ExperimentStatus.RUNNING:
            raise RuntimeError("El experimento ya está corriendo.")

        if self.current_state.status in {
            ExperimentStatus.FINISHED,
            ExperimentStatus.FAILED,
        }:
            raise RuntimeError(
                "No se puede iniciar un experimento que ya finalizó o falló."
            )

        self.current_state.status = ExperimentStatus.RUNNING
        self.current_state.started_at = datetime.now(timezone.utc)

        return self.current_state

    def pause(self) -> ExperimentState:
        """
        Pausa el experimento actual.

        Returns:
            Estado actualizado del experimento.

        Raises:
            RuntimeError: Si no existe un experimento configurado.
            RuntimeError: Si el experimento no está corriendo.
        """

        self._ensure_experiment_exists()

        assert self.current_state is not None

        if self.current_state.status != ExperimentStatus.RUNNING:
            raise RuntimeError("Solo se puede pausar un experimento que está corriendo.")

        self.current_state.status = ExperimentStatus.PAUSED

        return self.current_state

    def resume(self) -> ExperimentState:
        """
        Reanuda un experimento pausado.

        Returns:
            Estado actualizado del experimento.

        Raises:
            RuntimeError: Si no existe un experimento configurado.
            RuntimeError: Si el experimento no está pausado.
        """

        self._ensure_experiment_exists()

        assert self.current_state is not None

        if self.current_state.status != ExperimentStatus.PAUSED:
            raise RuntimeError("Solo se puede reanudar un experimento pausado.")

        self.current_state.status = ExperimentStatus.RUNNING

        return self.current_state

    def stop(self) -> ExperimentState:
        """
        Detiene manualmente el experimento actual.

        Returns:
            Estado actualizado del experimento.

        Raises:
            RuntimeError: Si no existe un experimento configurado.
            RuntimeError: Si el experimento ya finalizó o falló.
        """

        self._ensure_experiment_exists()

        assert self.current_state is not None

        if self.current_state.status in {
            ExperimentStatus.FINISHED,
            ExperimentStatus.FAILED,
        }:
            raise RuntimeError("El experimento ya terminó y no puede detenerse.")

        self.current_state.status = ExperimentStatus.STOPPED
        self.current_state.finished_at = datetime.now(timezone.utc)

        return self.current_state

    def finish(self) -> ExperimentState:
        """
        Marca el experimento actual como finalizado correctamente.

        Returns:
            Estado actualizado del experimento.

        Raises:
            RuntimeError: Si no existe un experimento configurado.
        """

        self._ensure_experiment_exists()

        assert self.current_state is not None

        self.current_state.status = ExperimentStatus.FINISHED
        self.current_state.finished_at = datetime.now(timezone.utc)

        return self.current_state

    def fail(self, error_message: str) -> ExperimentState:
        """
        Marca el experimento actual como fallido.

        Args:
            error_message: Mensaje que describe la causa de la falla.

        Returns:
            Estado actualizado del experimento.

        Raises:
            RuntimeError: Si no existe un experimento configurado.
            ValueError: Si el mensaje de error está vacío.
        """

        self._ensure_experiment_exists()

        if not isinstance(error_message, str) or not error_message.strip():
            raise ValueError("El mensaje de error no puede estar vacío.")

        assert self.current_state is not None

        self.current_state.status = ExperimentStatus.FAILED
        self.current_state.finished_at = datetime.now(timezone.utc)
        self.current_state.error_message = error_message

        return self.current_state

    def get_status(self) -> ExperimentStatus:
        """
        Devuelve el estado actual del experimento.

        Returns:
            Estado del experimento. Si no hay experimento activo, retorna STOPPED.
        """

        if self.current_state is None:
            return ExperimentStatus.STOPPED

        return self.current_state.status

    def get_state(self) -> ExperimentState | None:
        """
        Devuelve el estado completo del experimento actual.

        Returns:
            Estado completo del experimento o None si no hay experimento activo.
        """

        return self.current_state

    def get_current_experiment(self) -> ExperimentConfig | None:
        """
        Devuelve la configuración del experimento actual.

        Returns:
            Configuración del experimento o None si no existe.
        """

        return self.current_experiment

    def reset(self) -> None:
        """
        Limpia el experimento actual y vuelve el servicio a estado inicial.
        """

        self.current_experiment = None
        self.current_state = None

    def _ensure_experiment_exists(self) -> None:
        """
        Verifica que exista un experimento configurado.

        Raises:
            RuntimeError: Si no existe un experimento actual.
        """

        if self.current_experiment is None or self.current_state is None:
            raise RuntimeError("No hay un experimento configurado.")