# unilab/modules/simulation/simple_model.py
import random
from typing import Dict, Any
from unilab.modules.simulation.base import BaseSimulator

class LabSimulator(BaseSimulator):
    """Simulador para emular las respuestas físicas de los ensayos del laboratorio."""
    
    def __init__(self, attenuation_factor: float = -1.2, noise_level: float = 0.05):
        self.attenuation_factor = attenuation_factor
        self.noise_level = noise_level

    def run_simulation_step(self, input_value: float) -> Dict[str, Any]:
        """
        Calcula una respuesta simulada (ej. atenuación en dB).
        Fórmula: respuesta = (entrada * factor) + ruido_aleatorio
        """
        # Generar un componente de ruido aleatorio entre -noise_level y +noise_level
        simulated_noise = random.uniform(-self.noise_level, self.noise_level)
        
        # Calcular respuesta matemática base
        calculated_response = (input_value * self.attenuation_factor) + simulated_noise
        
        return {
            "input_value": input_value,
            "simulated_response_db": round(calculated_response, 4),
            "status": "SUCCESS" if calculated_response > -20.0 else "CRITICAL_ATTENUATED"
        }