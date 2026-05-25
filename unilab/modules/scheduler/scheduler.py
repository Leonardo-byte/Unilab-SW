# unilab/modules/scheduler/scheduler.py
from typing import List, Dict, Any
from unilab.modules.simulation.base import BaseSimulator

class ExperimentScheduler:
    """El motor encargado de procesar secuencialmente los pasos del plan en el simulador."""
    def __init__(self,name: str, simulator: BaseSimulator):
        self.name = name
        self.simulator = simulator
        self._history = []
        self._active = False
    
    def setup(self) -> bool:
        self._active = True
        return True
    
    def shutdown(self) -> bool:
        self._active = False
        return True
    
    def get_status(self) -> dict:
        return {
            "name": self.name,
            "active": self._active,
            "history_count": len(self._history)
        }

    def execute_plan(self, experiment_plan, validator: None) -> bool:
        if not self._active:
            raise RuntimeError("El scheduler no está activo. Ejecuta setup() primero.")
        
        """
        Recorre los pasos del perfil del plan, los envía al simulador
        y registra el historial de respuestas recopiladas.
        """
        if validator is not None:
            validator.validate(experiment_plan)

        for step in experiment_plan.steps:
            # Consumir el simulador lógico creado 
            result = self.simulator.generate_response(step.target_value)
            # Registrar el estado de la ejecución simulada con los metadatos del paso
            self._history.append({
                "step": step.name,
                "target": step.target_value,
                "result": result
            })
        return True
    
    def get_execution_history(self) -> List[dict]:
        return self._history
    
    def clear_history(self) -> None:
        self._history.clear()
