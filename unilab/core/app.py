from unilab.config.settings import Settings
from unilab.core.registry import ModuleRegistry
from unilab.core.module_loader import ModuleLoader
from unilab.core.experiment_service import ExperimentService


class UniLabApp:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.registry = ModuleRegistry()
        self.loader = ModuleLoader()
        self.experiments = ExperimentService()

    def register_module(self, name: str, module: object) -> None:
        self.registry.register(name, module)

    def get_module(self, name: str) -> object:
        return self.registry.get(name)

    def list_modules(self) -> list[str]:
        return self.registry.list_modules()
