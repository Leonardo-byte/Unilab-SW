# unilab/modules/profiles/validators.py
# Modificado para soportar la estructura de pasos solicitada
class ExperimentStep:
    def __init__(self, name: str, target_value: float, duration: float):
        self.name = name
        self.target_value = target_value
        self.duration = duration  # Duración en segundos o minutos


class ExperimentPlan:
    def __init__(self, name: str):
        self.name = name
        self.steps = []

    def add_step(self, step: ExperimentStep):
        self.steps.append(step)


class ProfileGenerator:
    """Clase auxiliar encargada de construir perfiles típicos."""
    @staticmethod
    def generate_step_profile(name: str, base_value: float, steps_count: int) -> ExperimentPlan:
        plan = ExperimentPlan(name)
        for i in range(steps_count):
            plan.add_step(ExperimentStep(f"Paso_{i+1}", base_value * (i + 1), 10.0))
        return plan