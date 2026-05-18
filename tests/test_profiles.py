# tests/test_profiles.py
import pytest
from unilab.modules.profiles.waveforms import ProfileGenerator
from unilab.modules.profiles.validators import ProfileValidator

def test_profile_generation_and_duration():
    """Prueba que el perfil sume correctamente los tiempos y valores."""
    generator = ProfileGenerator(profile_id="PROF-001", description="Ensayo de Antena 2.4GHz")
    generator.add_step("Fase Inicial", value=1.5, duration_seconds=10.0)
    generator.add_step("Fase Pico", value=3.5, duration_seconds=20.0)
    
    assert len(generator.steps) == 2
    assert generator.total_duration() == 30.0
    
    data = generator.to_dict()
    assert data["profile_id"] == "PROF-001"

def test_profile_validator_safety_limits():
    """Prueba que el validador bloquee perfiles peligrosos o erróneos."""
    generator = ProfileGenerator(profile_id="PROF-TEST", description="Test de límites")
    
    # Caso 1: Perfil vacío debe ser inválido
    assert ProfileValidator.is_safe_profile(generator, max_value=5.0, max_duration=60.0) is False
    
    # Caso 2: Perfil con valores seguros
    generator.add_step("Paso 1", value=2.0, duration_seconds=15.0)
    assert ProfileValidator.is_safe_profile(generator, max_value=5.0, max_duration=60.0) is True
    
    # Caso 3: Paso excede el voltaje/valor máximo configurado (ej: pide 6.0V cuando el tope es 5.0V)
    generator.add_step("Paso Peligroso", value=6.0, duration_seconds=10.0)
    assert ProfileValidator.is_safe_profile(generator, max_value=5.0, max_duration=60.0) is False

