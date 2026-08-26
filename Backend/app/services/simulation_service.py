import math
import random
from datetime import datetime
from typing import Dict, List
from app.models.telemetry import JaulaTelemetry, CubeSatTelemetry
from app.config import settings

class SimulationService:
    
    def __init__(self):
        self.jaula_estado = "reposo"
        self.tiempo_simulacion = 0
        self.perfil_activo = None
        self.corrientes_objetivo = {"X": 0.0, "Y": 0.0, "Z": 0.0}
        
    def generar_telemetria_jaula(self) -> JaulaTelemetry:
       
        self.tiempo_simulacion += 1
        
        if self.jaula_estado == "reposo":
            return JaulaTelemetry(
                timestamp=datetime.now(),
                eje_x_corriente=0.0,
                eje_y_corriente=0.0,
                eje_z_corriente=0.0,
                eje_x_campo=0.0,
                eje_y_campo=0.0,
                eje_z_campo=0.0,
                estado="reposo",
                magnitud_total=0.0
            )
        
        tiempo = self.tiempo_simulacion * 0.1
        
        corriente_x = self._calcular_corriente_actual("X", tiempo)
        corriente_y = self._calcular_corriente_actual("Y", tiempo)
        corriente_z = self._calcular_corriente_actual("Z", tiempo)
        
        campo_x = corriente_x * settings.KX + random.uniform(-1.5, 1.5)
        campo_y = corriente_y * settings.KY + random.uniform(-1.5, 1.5)
        campo_z = corriente_z * settings.KZ + random.uniform(-1.5, 1.5)
        
        
        magnitud = math.sqrt(campo_x**2 + campo_y**2 + campo_z**2)
        
        return JaulaTelemetry(
            timestamp=datetime.now(),
            eje_x_corriente=round(corriente_x, 2),
            eje_y_corriente=round(corriente_y, 2),
            eje_z_corriente=round(corriente_z, 2),
            eje_x_campo=round(campo_x, 1),
            eje_y_campo=round(campo_y, 1),
            eje_z_campo=round(campo_z, 1),
            estado=self.jaula_estado,
            magnitud_total=round(magnitud, 1)
        )
    
    def _calcular_corriente_actual(self, eje: str, tiempo: float) -> float:

        objetivo = self.corrientes_objetivo[eje]
        factor = 1 - math.exp(-tiempo / 2)
        return objetivo * factor
    
    def generar_telemetria_cubesat(self) -> CubeSatTelemetry:
        
        tiempo = self.tiempo_simulacion * 0.1
        
        roll = 14.2 + math.sin(tiempo * 0.05) * 2 + random.uniform(-0.5, 0.5)
        pitch = -2.5 + math.cos(tiempo * 0.03) * 1.5 + random.uniform(-0.5, 0.5)
        yaw = 89.1 + math.sin(tiempo * 0.02) * 3 + random.uniform(-0.5, 0.5)
        
        q0 = 0.707
        q1 = 0.000
        q2 = 0.707
        q3 = 0.000
        
        acc_x = 0.98 + random.uniform(-0.02, 0.02)
        acc_y = 0.12 + random.uniform(-0.02, 0.02)
        acc_z = -0.05 + random.uniform(-0.02, 0.02)
        
        gyro_x = random.uniform(-0.05, 0.05)
        gyro_y = random.uniform(-0.05, 0.05)
        gyro_z = random.uniform(-0.05, 0.05)
        
        campo_jaula_x = self.corrientes_objetivo["X"] * settings.KX
        campo_jaula_y = self.corrientes_objetivo["Y"] * settings.KY
        campo_jaula_z = self.corrientes_objetivo["Z"] * settings.KZ
        
        mag_x = 24.1 + campo_jaula_x + random.uniform(-1, 1)
        mag_y = -12.5 + campo_jaula_y + random.uniform(-1, 1)
        mag_z = 45.2 + campo_jaula_z + random.uniform(-1, 1)
        
        sun_1 = int(2847 + random.randint(-50, 50))   # +X (iluminado)
        sun_2 = int(123 + random.randint(-20, 20))    # -X (sombra)
        sun_3 = int(3102 + random.randint(-50, 50))   # +Y (iluminado)
        sun_4 = int(89 + random.randint(-20, 20))     # -Y (sombra)
        sun_5 = int(1456 + random.randint(-30, 30))   # +Z (parcial)
        sun_6 = int(201 + random.randint(-20, 20))    # -Z (sombra)
        
        return CubeSatTelemetry(
            timestamp=datetime.now(),
            roll=round(roll, 1),
            pitch=round(pitch, 1),
            yaw=round(yaw, 1),
            q0=q0, q1=q1, q2=q2, q3=q3,
            acc_x=round(acc_x, 2),
            acc_y=round(acc_y, 2),
            acc_z=round(acc_z, 2),
            gyro_x=round(gyro_x, 2),
            gyro_y=round(gyro_y, 2),
            gyro_z=round(gyro_z, 2),
            mag_x=round(mag_x, 1),
            mag_y=round(mag_y, 1),
            mag_z=round(mag_z, 1),
            sun_1=sun_1, sun_2=sun_2, sun_3=sun_3,
            sun_4=sun_4, sun_5=sun_5, sun_6=sun_6,
            adcs_mode="SUN_ACQUISITION",
            mtq_x_pwm=45 if random.random() > 0.5 else 0,
            mtq_y_pwm=12 if random.random() > 0.7 else 0,
            battery_voltage=3.7 + random.uniform(-0.1, 0.1),
            battery_percentage=85.0
        )
    
    def iniciar_ensayo(self, perfil: Dict[str, float]):
        self.jaula_estado = "ejecutando"
        self.tiempo_simulacion = 0
        self.corrientes_objetivo = {
            "X": perfil.get("bx", 0) / settings.KX,
            "Y": perfil.get("by", 0) / settings.KY,
            "Z": perfil.get("bz", 0) / settings.KZ
        }
    
    def detener_ensayo(self):
        self.jaula_estado = "reposo"
        self.corrientes_objetivo = {"X": 0.0, "Y": 0.0, "Z": 0.0}
        self.tiempo_simulacion = 0

simulador = SimulationService()