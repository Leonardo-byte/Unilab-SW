from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class JaulaTelemetry(BaseModel):
    timestamp: datetime
    eje_x_corriente: float = Field(..., description="Corriente eje X (A)")
    eje_y_corriente: float
    eje_z_corriente: float
    eje_x_campo: float = Field(..., description="Campo magnético eje X (μT)")
    eje_y_campo: float
    eje_z_campo: float
    estado: str = Field(..., description="reposo|ejecutando|error")
    magnitud_total: Optional[float] = None

class CubeSatTelemetry(BaseModel):
    timestamp: datetime
    roll: float
    pitch: float
    yaw: float
    q0: float
    q1: float
    q2: float
    q3: float
    acc_x: float
    acc_y: float
    acc_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    mag_x: float
    mag_y: float
    mag_z: float

class ControlCommand(BaseModel):
    eje: str = Field(..., description="X|Y|Z")
    corriente: float = Field(..., description="Corriente objetivo (A)")
    duracion: Optional[int] = Field(None, description="Duración en segundos")

class PerfilMagnetico(BaseModel):
    bx: float
    by: float
    bz: float
    duracion: Optional[int] = 60  
    tipo: str = Field(default="manual", description="manual|igrf|funcion")