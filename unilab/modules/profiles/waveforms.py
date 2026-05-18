# unilab/modules/profiles/waveforms.py
from typing import List, Dict, Any

class ExperimentStep:
    """Representa un punto o paso individual dentro de un perfil de ensayo."""
    def __init__(self, name: str, value: float, duration_seconds: float):
        self.name = name
        self.value = value
        self.duration_seconds = duration_seconds

class ProfileGenerator:
    """Generador y administrador de perfiles y formas de onda para los ensayos."""
    def __init__(self, profile_id: str, description: str):
        self.profile_id = profile_id
        self.description = description
        self.steps: List[ExperimentStep] = []

    def add_step(self, name: str, value: float, duration_seconds: float) -> None:
        """Añade un paso secuencial al perfil del experimento."""
        step = ExperimentStep(name, value, duration_seconds)
        self.steps.append(step)

    def total_duration(self) -> float:
        """Calcula la duración total del perfil sumando todos sus pasos."""
        return sum(step.duration_seconds for step in self.steps)

    def to_dict(self) -> Dict[str, Any]:
        """Exporta el perfil a un diccionario."""
        return {
            "profile_id": self.profile_id,
            "description": self.description,
            "total_duration": self.total_duration(),
            "steps": [
                {"name": s.name, "value": s.value, "duration": s.duration_seconds}
                for s in self.steps
            ]
        }
        

