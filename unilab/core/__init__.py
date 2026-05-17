"""
Paquete core de UniLab.

Este paquete contiene los componentes centrales de la aplicación:

- UniLabApp: aplicación principal y punto de integración.
- ModuleRegistry: registro central de módulos.
- ModuleLoader: cargador dinámico de módulos y clases.
- ExperimentService: servicio para gestionar el ciclo de vida de experimentos.

Estos componentes forman la base sobre la cual se integran los demás módulos
del sistema, como instrumentos, adquisición, simulación, scheduler, safety,
storage, web y SiLA.
"""

from .app import UniLabApp
from .experiment_service import ExperimentService
from .module_loader import ModuleLoader
from .registry import ModuleRegistry

__all__ = [
    "UniLabApp",
    "ExperimentService",
    "ModuleLoader",
    "ModuleRegistry",
]