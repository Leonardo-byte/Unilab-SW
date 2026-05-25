# unilab/modules/simulation/simple_model.py
import random
from typing import Dict, Any
from unilab.modules.simulation.base import BaseSimulator

class LabSimulator(BaseSimulator):
    """Simulador para emular las respuestas físicas de los ensayos del laboratorio."""
    
    def __init__(self, name: str, attenuation_factor: float = -1.2, noise_level: float = 0.05):
        super().__init__(name)
        self.attenuation_factor = attenuation_factor
        self.noise_level = noise_level
        self._is_ready = False

    def setup(self) -> bool:
        self._is_ready = True
        return True
    
    def shutdown(self) -> bool:
        self._is_ready = False
        return True
    
    def get_status(self) -> dict:
        return {
            "name": self.name,
            "ready": self._is_ready,
            "attenuation_factor": self.attenuation_factor,
            "noise_level": self.noise_level
        }
        
    def generate_response(self, input_value: float) -> float:
        if not self._is_ready:
            raise RuntimeError("El simulador no está inicializado. Ejecuta setup() primero.")   
        # Lógica de simulación
        """
        Calcula una respuesta simulada (ej. atenuación en dB).
        Fórmula: respuesta = (entrada * factor) + ruido_aleatorio
        """
        base_calc = input_value * self.attenuation_factor
        # Generar un componente de ruido aleatorio
        noise = random.uniform(-self.noise_level, self.noise_level)

        return base_calc + noise