# unilab/modules/simulation/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseSimulator(ABC):
    """Clase abstracta que define el comportamiento mínimo de un simulador."""
    
    @abstractmethod
    def run_simulation_step(self, input_value: float) -> Dict[str, Any]:
        """Calcula el estado del sistema simulado basándose en un valor de entrada."""
        pass