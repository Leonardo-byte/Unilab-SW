"""
Módulos funcionales de UniLab.

Esta carpeta contiene las implementaciones concretas construidas encima de la
base definida por Persona 1.

Aquí se ubican los módulos de:

- adquisición de datos
- seguridad
- almacenamiento
- visualización web
- simulación
- instrumentación
- transportes
- reportes
- integración SiLA

Para la demo mínima ESP32 → UniLab → Dashboard, inicialmente se usan:

- acquisition
- safety
- storage
- web

"""

from unilab.modules.acquisition import AcquisitionBase, UdpJsonReceiver
from unilab.modules.safety import SafetyManager
from unilab.modules.storage import MemoryStorage

# =====================================================================
# ADICIONES PERSONA 3: Perfiles, Simulación y Planificación (Scheduler)
# =====================================================================
from unilab.modules.profiles.base import ExperimentStep, ExperimentPlan, ProfileGenerator
from unilab.modules.profiles.validators import ProfileValidator
from unilab.modules.scheduler.scheduler import ExperimentScheduler
from unilab.modules.simulation.base import BaseSimulator
from unilab.modules.simulation.simple_model import LabSimulator



__all__ = [
    "AcquisitionBase",
    "UdpJsonReceiver",
    "SafetyManager",
    "MemoryStorage",
    # -----------------------------------------------------------------
    # Exports Persona 3
    # -----------------------------------------------------------------
    "ExperimentStep",
    "ExperimentPlan",
    "ProfileGenerator",
    "ProfileValidator",
    "ExperimentScheduler",
    "BaseSimulator",
    "LabSimulator",
]
