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



__all__ = [
    "AcquisitionBase",
    "UdpJsonReceiver",
    "SafetyManager",
    "MemoryStorage",
]
