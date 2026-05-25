# tests/test_scheduler.py
import pytest
from unilab.modules.profiles.validators import ProfileValidator
from unilab.modules.profiles.base import ExperimentPlan, ExperimentStep
from unilab.modules.simulation.simple_model import LabSimulator
from unilab.modules.scheduler.scheduler import ExperimentScheduler

def test_experiment_scheduler_execution_and_history():
    """Probar que ExpermientScheduler ejecute un plan completo y guarda historial."""
    simulator = LabSimulator(name="Simulador Auxiliar")
    simulator.setup() # Inicializamos el simulador del que depende

    scheduler = ExperimentScheduler(name="Scheduler Central", simulator=simulator)
    validator = ProfileValidator()

    # Crear un plan de prueba válido
    plan = ExperimentPlan("Plan de Control")
    plan.add_step(ExperimentStep("Fase Alfa", 15.0, 5.0))
    plan.add_step(ExperimentStep("Fase Beta", 30.0, 5.0))

    # No debería ejecutar si el scheduler no ha hecho setup()
    with pytest.raises(RuntimeError, match="El scheduler no está activo"):
        scheduler.execute_plan(plan, validator=validator)

    # Inicializar planificador y ejecutar
    assert scheduler.setup() is True
    assert scheduler.execute_plan(plan, validator=validator) is True

    # Verificar almacenamiento de historial
    history = scheduler.get_execution_history()
    assert len(history) == 2
    assert history[0]["step"] == "Fase Alfa"
    assert history[0]["target"] == 15.0
    
    # Verificar limpieza de historial
    scheduler.clear_history()
    assert len(scheduler.get_execution_history()) == 0

    scheduler.shutdown()