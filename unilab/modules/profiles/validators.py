# unilab/modules/profiles/validators.py
from unilab.modules.profiles.base import ExperimentPlan

class ProfileValidator:
    def __init__(self, min_allowed: float = 0.0, max_allowed: float = 100.0):
        self.min_allowed = min_allowed
        self.max_allowed = max_allowed

    def validate(self, plan: ExperimentPlan) -> bool:
        """
        Valida el perfil ANTES de la ejecución (Estático).
        Evita duplicar el rol de SafetyManager, el cual actúa DURANTE la ejecución.
        """
        # 1. Validar perfiles vacíos
        if not plan.steps:
            raise ValueError(f"El plan de experimento '{plan.name}' no contiene pasos.")

        for step in plan.steps:
            # 2. Validar duraciones inválidas
            if step.duration <= 0:
                raise ValueError(f"Duración inválida en el paso '{step.name}': {step.duration}s. Debe ser mayor a 0.")
            
            # 3. Validar valores fuera de rango teórico estándar
            if not (self.min_allowed <= step.target_value <= self.max_allowed):
                raise ValueError(
                    f"Valor fuera de rango en el paso '{step.name}': {step.target_value}. "
                    f"Debe estar entre {self.min_allowed} y {self.max_allowed}."
                )
        
        return True