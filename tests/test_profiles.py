# tests/test_profiles.py
import pytest
from unilab.modules.profiles.base import ExperimentPlan, ExperimentStep, ProfileGenerator
from unilab.modules.profiles.validators import ProfileValidator

def test_profile_generator_creates_correctly():
    """Prueba que el perfil sume correctamente los tiempos y valores."""
    base_value = 10.0
    steps_count = 3
    plan = ProfileGenerator.generate_step_profile("Test Plan", base_value, steps_count)
    
    assert plan.name == "Test Plan"
    assert len(plan.steps) == steps_count
    assert plan.steps[0].target_value == 10.0
    assert plan.steps[2].target_value == 30.0

def test_profile_validator_rejects_invalid_profiles():
    """Probar que ProfileValidator rechaza perfiles inválidos"""
    validator = ProfileValidator(min_allowed=0.0, max_allowed=50.0)
    
    # Caso 1: Perfil vacío
    empty_plan = ExperimentPlan("Plan Vacío")
    with pytest.raises(ValueError, match="no contiene pasos"):
        validator.validate(empty_plan)
        
    # Caso 2: Duración inválida (0 o negativa)
    bad_duration_plan = ExperimentPlan("Plan Duración Mala")
    bad_duration_plan.add_step(ExperimentStep("Paso 1", 20.0, 0)) # Duración 0
    with pytest.raises(ValueError, match="Duración inválida"):
        validator.validate(bad_duration_plan)
        
    # Caso 3: Valor fuera de rango (mayor al máximo permitido)
    out_of_range_plan = ExperimentPlan("Plan Fuera de Rango")
    out_of_range_plan.add_step(ExperimentStep("Paso 1", 60.0, 10.0)) # 60.0 > 50.0
    with pytest.raises(ValueError, match="Valor fuera de rango"):
        validator.validate(out_of_range_plan)

