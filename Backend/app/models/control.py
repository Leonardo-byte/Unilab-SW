from pydantic import BaseModel
from datetime import datetime

class ControlCubesat(BaseModel):
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
    mtq_x_pwm: float
    mtq_y_pwm: float