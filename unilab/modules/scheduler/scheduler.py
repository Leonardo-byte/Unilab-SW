# unilab/modules/scheduler/scheduler.py
from typing import List, Dict, Any
from unilab.modules.scheduler.experiment_plan import ExperimentPlan
from unilab.modules.simulation.simple_model import LabSimulator

class ExperimentScheduler:
    """El motor encargado de procesar secuencialmente los pasos del plan en el simulador."""
    def __init__(self, simulator: LabSimulator):
        self.simulator = simulator
        self.execution_history: List[Dict[str, Any]] = []

    def execute_plan(self, plan: ExperimentPlan) -> Dict[str, Any]:
        """
        Recorre los pasos del perfil del plan, los envía al simulador
        y registra el historial de respuestas recopiladas.
        """
        plan.start()
        self.execution_history.clear()

        for step in plan.profile.steps:
            # Consumir el simulador lógico creado en el paso anterior
            sim_result = self.simulator.run_simulation_step(input_value=step.value)
            
            # Registrar el estado de la ejecución simulada con los metadatos del paso
            log_entry = {
                "step_name": step.name,
                "duration_seconds": step.duration_seconds,
                "telemetry": sim_result
            }
            self.execution_history.append(log_entry)

        plan.complete()
        return {
            "plan_id": plan.plan_id,
            "final_status": plan.status,
            "total_steps_executed": len(self.execution_history),
            "history": self.execution_history
        }