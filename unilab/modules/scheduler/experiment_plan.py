# unilab/modules/scheduler/experiment_plan.py
from typing import List
from unilab.modules.profiles.waveforms import ProfileGenerator

class ExperimentPlan:
    """Mapea un perfil validado a un plan ejecutable por el scheduler."""
    def __init__(self, plan_id: str, profile_generator: ProfileGenerator):
        self.plan_id = plan_id
        self.profile = profile_generator
        self.status = "PENDING"

    def start(self) -> None:
        self.status = "RUNNING"

    def complete(self) -> None:
        self.status = "COMPLETED"