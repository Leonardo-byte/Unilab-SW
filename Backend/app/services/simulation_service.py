import math
import random
from datetime import datetime
from typing import Dict, List
from app.models.telemetry import JaulaTelemetry, CubeSatTelemetry
from app.config import settings
from app.services.jaula_service import jaula_service
from app.services.cubesat_service import cubesat_service, CubeSatService

class SimulationService:

    def __init__(self):
        self.jaula_estado = "reposo"
        self.tiempo_simulacion = 0
        self.perfil_activo = None
        self.corrientes_objetivo = {"X": 0.0, "Y": 0.0, "Z": 0.0}
        self._ema = {
            "roll": 0.0, "pitch": 0.0, "yaw": 0.0,
            "acc_x": 0.0, "acc_y": 0.0, "acc_z": 0.0,
            "gyro_x": 0.0, "gyro_y": 0.0, "gyro_z": 0.0,
            "mag_x": 0.0, "mag_y": 0.0, "mag_z": 0.0,
            "campo_x": 0.0, "campo_y": 0.0, "campo_z": 0.0,
        }
        self._prev_yaw_unwrapped: float | None = None
        self._ema_alpha = 0.3

    def _smooth(self, key: str, value: float) -> float:
        prev = self._ema[key]
        out = self._ema_alpha * value + (1 - self._ema_alpha) * prev
        self._ema[key] = out
        return out

    @staticmethod
    def _unwrap(prev: float | None, current: float) -> float:
        if prev is None:
            return current
        delta = current - prev
        while delta > 180:
            current -= 360
            delta = current - prev
        while delta < -180:
            current += 360
            delta = current - prev
        return current

    def generar_telemetria_jaula(self) -> JaulaTelemetry:

        if jaula_service.is_connected and not jaula_service.simulation_mode:
            real = jaula_service.read_telemetry()
            if real:
                return real

        if self.jaula_estado == "reposo":
            return JaulaTelemetry(
                timestamp=datetime.now(),
                eje_x_corriente=0.0,
                eje_y_corriente=0.0,
                eje_z_corriente=0.0,
                eje_x_campo=0.0,
                eje_y_campo=0.0,
                eje_z_campo=0.0,
                estado="reposo"
            )

        self.tiempo_simulacion += 1

        tiempo = self.tiempo_simulacion * settings.WS_UPDATE_INTERVAL

        corriente_x = self._calcular_corriente_actual("X", tiempo)
        corriente_y = self._calcular_corriente_actual("Y", tiempo)
        corriente_z = self._calcular_corriente_actual("Z", tiempo)

        campo_x = corriente_x * settings.KX + random.uniform(-1.5, 1.5)
        campo_y = corriente_y * settings.KY + random.uniform(-1.5, 1.5)
        campo_z = corriente_z * settings.KZ + random.uniform(-1.5, 1.5)

        magnitud = math.sqrt(campo_x**2 + campo_y**2 + campo_z**2)

        campo_x_f = self._smooth("campo_x", campo_x)
        campo_y_f = self._smooth("campo_y", campo_y)
        campo_z_f = self._smooth("campo_z", campo_z)

        return JaulaTelemetry(
            timestamp=datetime.now(),
            eje_x_corriente=round(corriente_x, 2),
            eje_y_corriente=round(corriente_y, 2),
            eje_z_corriente=round(corriente_z, 2),
            eje_x_campo=round(campo_x_f, 1),
            eje_y_campo=round(campo_y_f, 1),
            eje_z_campo=round(campo_z_f, 1),
            estado=self.jaula_estado
        )

    def _calcular_corriente_actual(self, eje: str, tiempo: float) -> float:
        objetivo = self.corrientes_objetivo[eje]
        factor = 1 - math.exp(-tiempo / 2)
        return objetivo * factor

    def generar_telemetria_cubesat(self) -> CubeSatTelemetry:

        if cubesat_service.is_listening and not cubesat_service.simulation_mode:
            real = cubesat_service.receive_telemetry()
            if real:
                return real

        tiempo = self.tiempo_simulacion * settings.WS_UPDATE_INTERVAL

        roll_raw = 14.2 + math.sin(tiempo * 0.05) * 2 + random.uniform(-0.5, 0.5)
        pitch_raw = -2.5 + math.cos(tiempo * 0.03) * 1.5 + random.uniform(-0.5, 0.5)
        yaw_raw = 89.1 + math.sin(tiempo * 0.02) * 3 + random.uniform(-0.5, 0.5)

        yaw_unwrapped = self._unwrap(self._prev_yaw_unwrapped, yaw_raw)
        self._prev_yaw_unwrapped = yaw_unwrapped

        roll = self._smooth("roll", roll_raw)
        pitch = self._smooth("pitch", pitch_raw)
        yaw = self._smooth("yaw", yaw_unwrapped)

        q0, q1, q2, q3 = CubeSatService._euler_a_cuaternion(roll, pitch, yaw)

        acc_x = self._smooth("acc_x", 0.98 + random.uniform(-0.02, 0.02))
        acc_y = self._smooth("acc_y", 0.12 + random.uniform(-0.02, 0.02))
        acc_z = self._smooth("acc_z", -0.05 + random.uniform(-0.02, 0.02))

        gyro_x = self._smooth("gyro_x", random.uniform(-0.05, 0.05))
        gyro_y = self._smooth("gyro_y", random.uniform(-0.05, 0.05))
        gyro_z = self._smooth("gyro_z", random.uniform(-0.05, 0.05))

        campo_jaula_x = self.corrientes_objetivo["X"] * settings.KX
        campo_jaula_y = self.corrientes_objetivo["Y"] * settings.KY
        campo_jaula_z = self.corrientes_objetivo["Z"] * settings.KZ

        mag_x = self._smooth("mag_x", 24.1 + campo_jaula_x + random.uniform(-1, 1))
        mag_y = self._smooth("mag_y", -12.5 + campo_jaula_y + random.uniform(-1, 1))
        mag_z = self._smooth("mag_z", 45.2 + campo_jaula_z + random.uniform(-1, 1))

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
            mag_z=round(mag_z, 1)
        )

    def iniciar_ensayo(self, perfil: Dict[str, float]):
        self.jaula_estado = "ejecutando"
        self.tiempo_simulacion = 0
        self.perfil_activo = perfil
        self._ema = {k: 0.0 for k in self._ema}
        self._prev_yaw_unwrapped = None

        bx = perfil.get("bx", 0)
        by = perfil.get("by", 0)
        bz = perfil.get("bz", 0)

        self.corrientes_objetivo = {
            "X": bx / settings.KX,
            "Y": by / settings.KY,
            "Z": bz / settings.KZ
        }

        if jaula_service.is_connected and not jaula_service.simulation_mode:
            jaula_service.set_referencia_campo(bx, by)
            jaula_service.enable_driver("X")
            jaula_service.enable_driver("Y")

    def detener_ensayo(self):
        self.jaula_estado = "reposo"
        self.corrientes_objetivo = {"X": 0.0, "Y": 0.0, "Z": 0.0}
        self.tiempo_simulacion = 0
        self._ema = {k: 0.0 for k in self._ema}
        self._prev_yaw_unwrapped = None

        if jaula_service.is_connected and not jaula_service.simulation_mode:
            jaula_service.set_referencia_campo(0.0, 0.0)
            jaula_service.disable_driver("X")
            jaula_service.disable_driver("Y")

simulador = SimulationService()
