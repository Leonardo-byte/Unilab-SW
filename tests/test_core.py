import pytest

from unilab.core.registry import ModuleRegistry
from unilab.core.module_loader import ModuleLoader

from unilab.contracts.models import (
    ExperimentConfig,
    ExperimentStatus,
)

from unilab.core.experiment_service import ExperimentService


from unilab.config.settings import Settings
from unilab.core.app import UniLabApp


class DummyModule:
    name = "dummy"

    def setup(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_status(self) -> dict:
        return {"status": "ok"}


class FailingStatusModule:
    name = "failing"

    def setup(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_status(self) -> dict:
        raise RuntimeError("No se pudo leer el estado")


class BadModule:
    pass


def test_registry_starts_empty():
    registry = ModuleRegistry()

    assert registry.count() == 0
    assert registry.list_modules() == []


def test_registry_register_and_get_module():
    registry = ModuleRegistry()
    module = DummyModule()

    registry.register("dummy", module)

    assert registry.get("dummy") is module
    assert registry.exists("dummy")
    assert registry.count() == 1
    assert "dummy" in registry.list_modules()


def test_registry_rejects_duplicate_module():
    registry = ModuleRegistry()
    module = DummyModule()

    registry.register("dummy", module)

    with pytest.raises(ValueError):
        registry.register("dummy", module)


def test_registry_rejects_empty_name():
    registry = ModuleRegistry()
    module = DummyModule()

    with pytest.raises(ValueError):
        registry.register("", module)


def test_registry_rejects_invalid_module():
    registry = ModuleRegistry()
    module = BadModule()

    with pytest.raises(TypeError):
        registry.register("bad", module)


def test_registry_get_unknown_module_raises_key_error():
    registry = ModuleRegistry()

    with pytest.raises(KeyError):
        registry.get("unknown")


def test_registry_unregister_module():
    registry = ModuleRegistry()
    module = DummyModule()

    registry.register("dummy", module)
    removed = registry.unregister("dummy")

    assert removed is module
    assert not registry.exists("dummy")
    assert registry.count() == 0


def test_registry_clear_modules():
    registry = ModuleRegistry()

    registry.register("dummy_1", DummyModule())
    registry.register("dummy_2", DummyModule())

    registry.clear()

    assert registry.count() == 0
    assert registry.list_modules() == []


def test_registry_get_all_returns_copy():
    registry = ModuleRegistry()
    module = DummyModule()

    registry.register("dummy", module)

    modules = registry.get_all()
    modules.clear()

    assert registry.exists("dummy")
    assert registry.count() == 1


def test_registry_get_status_summary():
    registry = ModuleRegistry()

    registry.register("dummy", DummyModule())

    summary = registry.get_status_summary()

    assert summary["dummy"]["status"] == "ok"


def test_registry_get_status_summary_handles_errors():
    registry = ModuleRegistry()

    registry.register("failing", FailingStatusModule())

    summary = registry.get_status_summary()

    assert summary["failing"]["status"] == "error"
    assert "No se pudo leer el estado" in summary["failing"]["message"]


def test_module_loader_loads_existing_module():
    loader = ModuleLoader()

    module = loader.load_module("unilab.core.registry")

    assert module is not None
    assert hasattr(module, "ModuleRegistry")


def test_module_loader_loads_existing_class():
    loader = ModuleLoader()

    loaded_class = loader.load_class(
        "unilab.core.registry",
        "ModuleRegistry",
    )

    assert loaded_class is ModuleRegistry


def test_module_loader_creates_instance():
    loader = ModuleLoader()

    instance = loader.create_instance(
        "unilab.core.registry",
        "ModuleRegistry",
    )

    assert isinstance(instance, ModuleRegistry)


def test_module_loader_rejects_empty_module_path():
    loader = ModuleLoader()

    with pytest.raises(ValueError):
        loader.load_module("")


def test_module_loader_rejects_empty_class_name():
    loader = ModuleLoader()

    with pytest.raises(ValueError):
        loader.load_class("unilab.core.registry", "")


def test_module_loader_rejects_unknown_module():
    loader = ModuleLoader()

    with pytest.raises(ImportError):
        loader.load_module("unilab.core.module_that_does_not_exist")


def test_module_loader_rejects_unknown_class():
    loader = ModuleLoader()

    with pytest.raises(AttributeError):
        loader.load_class(
            "unilab.core.registry",
            "UnknownClass",
        )


def test_module_loader_rejects_attribute_that_is_not_class():
    loader = ModuleLoader()

    with pytest.raises(TypeError):
        loader.load_class(
            "unilab.core.registry",
            "__name__",
        )


def make_experiment_config() -> ExperimentConfig:
    return ExperimentConfig(
        experiment_id="exp001",
        name="Test experiment",
        description="Basic test",
    )


def test_experiment_service_starts_without_experiment():
    service = ExperimentService()

    assert service.get_current_experiment() is None
    assert service.get_state() is None
    assert service.get_status() == ExperimentStatus.STOPPED


def test_experiment_service_create_experiment():
    service = ExperimentService()
    config = make_experiment_config()

    state = service.create_experiment(config)

    assert service.get_current_experiment() == config
    assert state.experiment_id == "exp001"
    assert state.status == ExperimentStatus.CREATED


def test_experiment_service_start_experiment():
    service = ExperimentService()
    config = make_experiment_config()

    service.create_experiment(config)
    state = service.start()

    assert state.status == ExperimentStatus.RUNNING
    assert state.started_at is not None


def test_experiment_service_cannot_start_without_experiment():
    service = ExperimentService()

    with pytest.raises(RuntimeError):
        service.start()


def test_experiment_service_pause_experiment():
    service = ExperimentService()
    config = make_experiment_config()

    service.create_experiment(config)
    service.start()
    state = service.pause()

    assert state.status == ExperimentStatus.PAUSED


def test_experiment_service_resume_experiment():
    service = ExperimentService()
    config = make_experiment_config()

    service.create_experiment(config)
    service.start()
    service.pause()
    state = service.resume()

    assert state.status == ExperimentStatus.RUNNING


def test_experiment_service_stop_experiment():
    service = ExperimentService()
    config = make_experiment_config()

    service.create_experiment(config)
    service.start()
    state = service.stop()

    assert state.status == ExperimentStatus.STOPPED
    assert state.finished_at is not None


def test_experiment_service_finish_experiment():
    service = ExperimentService()
    config = make_experiment_config()

    service.create_experiment(config)
    service.start()
    state = service.finish()

    assert state.status == ExperimentStatus.FINISHED
    assert state.finished_at is not None


def test_experiment_service_fail_experiment():
    service = ExperimentService()
    config = make_experiment_config()

    service.create_experiment(config)
    service.start()
    state = service.fail("Error de prueba")

    assert state.status == ExperimentStatus.FAILED
    assert state.error_message == "Error de prueba"
    assert state.finished_at is not None


def test_experiment_service_rejects_empty_error_message():
    service = ExperimentService()
    config = make_experiment_config()

    service.create_experiment(config)

    with pytest.raises(ValueError):
        service.fail("")


def test_experiment_service_reset():
    service = ExperimentService()
    config = make_experiment_config()

    service.create_experiment(config)
    service.start()
    service.reset()

    assert service.get_current_experiment() is None
    assert service.get_state() is None
    assert service.get_status() == ExperimentStatus.STOPPED


class AppDummyModule:
    name = "app_dummy"

    def __init__(self) -> None:
        self.was_setup = False
        self.was_shutdown = False

    def setup(self) -> None:
        self.was_setup = True

    def shutdown(self) -> None:
        self.was_shutdown = True

    def get_status(self) -> dict:
        return {
            "status": "ok",
            "was_setup": self.was_setup,
            "was_shutdown": self.was_shutdown,
        }


def test_app_initializes_with_default_settings():
    app = UniLabApp()

    assert app.settings is not None
    assert app.registry is not None
    assert app.loader is not None
    assert app.experiments is not None


def test_app_initializes_with_custom_settings():
    settings = Settings(
        app_name="UniLab Test",
        debug=False,
    )

    app = UniLabApp(settings=settings)

    assert app.settings.app_name == "UniLab Test"
    assert app.settings.debug is False


def test_app_register_and_get_module():
    app = UniLabApp()
    module = AppDummyModule()

    app.register_module("dummy", module)

    assert app.get_module("dummy") is module
    assert app.has_module("dummy")
    assert "dummy" in app.list_modules()


def test_app_unregister_module():
    app = UniLabApp()
    module = AppDummyModule()

    app.register_module("dummy", module)
    removed = app.unregister_module("dummy")

    assert removed is module
    assert not app.has_module("dummy")


def test_app_setup_calls_module_setup():
    app = UniLabApp()
    module = AppDummyModule()

    app.register_module("dummy", module)
    app.setup()

    assert module.was_setup is True
    assert app.get_status()["is_setup"] is True


def test_app_shutdown_calls_module_shutdown():
    app = UniLabApp()
    module = AppDummyModule()

    app.register_module("dummy", module)
    app.setup()
    app.shutdown()

    assert module.was_shutdown is True
    assert app.get_status()["is_setup"] is False


def test_app_get_status():
    app = UniLabApp()
    module = AppDummyModule()

    app.register_module("dummy", module)

    status = app.get_status()

    assert status["app_name"] == app.settings.app_name
    assert status["debug"] == app.settings.debug
    assert status["modules_count"] == 1
    assert "dummy" in status["modules"]
    assert status["experiment_status"] == ExperimentStatus.STOPPED


def test_app_get_modules_status():
    app = UniLabApp()
    module = AppDummyModule()

    app.register_module("dummy", module)

    modules_status = app.get_modules_status()

    assert modules_status["dummy"]["status"] == "ok"


def test_app_experiment_service_integration():
    app = UniLabApp()

    config = ExperimentConfig(
        experiment_id="exp001",
        name="Test experiment",
        description="Basic test",
    )

    app.experiments.create_experiment(config)
    app.experiments.start()

    assert app.experiments.get_status() == ExperimentStatus.RUNNING


def test_core_package_exports():
    from unilab.core import (
        UniLabApp,
        ModuleRegistry,
        ModuleLoader,
        ExperimentService,
    )

    assert UniLabApp is not None
    assert ModuleRegistry is not None
    assert ModuleLoader is not None
    assert ExperimentService is not None