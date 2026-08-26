from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class StartCalibrationCommand(BaseModel):
    ejes: List[str] = Field(default=["X", "Y", "Z"])
    puntos_por_eje: int = Field(default=100, ge=10, le=1000)
    corriente_min: float = Field(default=1.3, ge=0)
    corriente_max: float = Field(default=3.5, ge=0)

class SetSimulatorSolarCommand(BaseModel):
    intensidad: float = Field(default=0.0, ge=0.0, le=100.0)
    modo: str = Field(default="manual", description="manual|automatico|eclipse")

class SaveSessionCommand(BaseModel):
    nombre_sesion: str
    descripcion: Optional[str] = None
    operador: str
    tipo_prueba: str  # "calibracion"|"ensayo"|"validacion"