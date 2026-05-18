# tests/test_simulation.py
import pytest
from unilab.modules.simulation.simple_model import LabSimulator

def test_simulator_math_response():
    """Valida que el simulador aplique el factor matemático correctamente."""
    # Configuración estricta sin ruido para validar la matemática exacta
    simulator = LabSimulator(attenuation_factor=-1.5, noise_level=0.0)
    
    result = simulator.run_simulation_step(input_value=2.0)
    
    assert result["input_value"] == 2.0
    assert result["simulated_response_db"] == -3.0  # 2.0 * -1.5
    assert result["status"] == "SUCCESS"

def test_simulator_noise_boundaries():
    """Valida que el simulador añada variabilidad dentro del rango de ruido permitido."""
    noise_limit = 0.1
    simulator = LabSimulator(attenuation_factor=-1.0, noise_level=noise_limit)
    
    # Ejecutar múltiples pasos para validar que el ruido no rompa los límites teóricos
    for _ in range(10):
        result = simulator.run_simulation_step(input_value=5.0)
        expected_base = -5.0
        
        # La respuesta debe estar en el rango de: [base - limite, base + limite]
        assert (expected_base - noise_limit) <= result["simulated_response_db"] <= (expected_base + noise_limit)