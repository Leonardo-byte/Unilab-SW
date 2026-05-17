import pytest

from unilab.core.registry import ModuleRegistry
from unilab.core.app import UniLabApp
from unilab.contracts.models import ExperimentConfig


class DummyModule:
    name = "dummy"

    def setup(self):
        pass

    def shutdown(self):
        pass


def test_registry_register_and_get_module():
    registry = ModuleRegistry()
    module = DummyModule()

    registry.register("dummy", module)

    assert registry.get("dummy") is module
    assert "dummy" in registry.list_modules()


def test_registry_rejects_duplicate_module():
    registry = ModuleRegistry()
    module = DummyModule()

    registry.register("dummy", module)

    with pytest.raises(ValueError):
        registry.register("dummy", module)


def test_app_registers_module():
    app = UniLabApp()
    module = DummyModule()

    app.register_module("dummy", module)

    assert app.get_module("dummy") is module


def test_experiment_service_flow():
    app = UniLabApp()

    config = ExperimentConfig(
        experiment_id="exp001",
        name="Test experiment",
        description="Basic test"
    )

    app.experiments.create_experiment(config)
    app.experiments.start()

    assert app.experiments.get_status() == "running"

    app.experiments.stop()

    assert app.experiments.get_status() == "stopped"
