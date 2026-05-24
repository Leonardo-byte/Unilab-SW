"""Módulo de seguridad de UniLab."""

from unilab.modules.safety.manager import SafetyManager

__all__ = ["SafetyManager"]

def __init__(
    self,
    limits: dict[str, dict[str, float]] | None = None,
    name: str = "safety_manager",
) -> None:
    self.name = name
    self.limits = limits or {}
    self._is_setup = False
