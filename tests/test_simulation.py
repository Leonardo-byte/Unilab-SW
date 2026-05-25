# tests/test_simulation.py
import pytest
from unilab.modules.simulation.simple_model import LabSimulator

def test_simulator_lifecycle_and_response():
    """Probar que LabSimulator devuelve una respuesta válida y maneja su estado."""
    # Configuración estricta sin ruido para validar la matemática exacta
    simulator = LabSimulator(name="Simulador UNI", attenuation_factor=-1.5, noise_level=0.0)
    
    # No debería responder si no se ha llamado a setup()
    with pytest.raises(RuntimeError, match="Ejecuta setup\\(\\) primero"):
        simulator.generate_response(10.0)
        
    # Inicialización
    assert simulator.setup() is True
    status = simulator.get_status()
    assert status["ready"] is True
    assert status["name"] == "Simulador UNI"
    
    # Respuesta válida (10.0 * 2.0 = 20.0, ±0.1 de ruido)
    response = simulator.generate_response(10.0)
    assert response == -15.0
    
    # Apagado
    assert simulator.shutdown() is True
    assert simulator.get_status()["ready"] is False