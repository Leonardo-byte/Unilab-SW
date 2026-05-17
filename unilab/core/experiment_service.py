from unilab.contracts.models import ExperimentConfig


class ExperimentService:
    def __init__(self) -> None:
        self.current_experiment: ExperimentConfig | None = None
        self.status = "idle"

    def create_experiment(self, config: ExperimentConfig) -> None:
        self.current_experiment = config
        self.status = "created"

    def start(self) -> None:
        if self.current_experiment is None:
            raise RuntimeError("No experiment has been configured")

        self.status = "running"

    def stop(self) -> None:
        self.status = "stopped"

    def get_status(self) -> str:
        return self.status
