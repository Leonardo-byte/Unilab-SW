# tests/test_scheduler.py
import pytest
from unilab.modules.profiles.waveforms import ProfileGenerator
from unilab.modules.scheduler.experiment_plan import ExperimentPlan
from unilab.modules.simulation.simple_model import LabSimulator
from unilab.modules.scheduler.scheduler import ExperimentScheduler

def test_scheduler_integrational_execution():
    """Valida la integración de perfiles, simulación y planificación en cadena."""
    # 1. Configurar Perfil
    profile = ProfileGenerator(profile_id="P-01", description="Perfil de Integración")
    profile.add_step("Fase Inicial", value=2.0, duration_seconds=5.0)
    profile.add_step("Fase Final", value=4.0, duration_seconds=5.0)

    # 2. Configurar Plan y Simulador (Sin ruido para verificar valores exactos)
    plan = ExperimentPlan(plan_id="PLAN-100", profile_generator=profile)
    simulator = LabSimulator(attenuation_factor=-2.0, noise_level=0.0)
    scheduler = ExperimentScheduler(simulator=simulator)

    # 3. Ejecutar Planificación
    report = scheduler.execute_plan(plan)

    # 4. Verificaciones
    assert report["plan_id"] == "PLAN-100"
    assert report["final_status"] == "COMPLETED"
    assert report["total_steps_executed"] == 2
    
    # Validar que los resultados del paso 1 coincidan matemáticamente
    first_step_log = report["history"][0]
    assert first_step_log["step_name"] == "Fase Inicial"
    assert first_step_log["telemetry"]["simulated_response_db"] == -4.0  # 2.0 * -2.0