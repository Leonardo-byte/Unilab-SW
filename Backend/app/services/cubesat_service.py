import socket
import json
import math
import threading
from typing import Optional, Dict, Tuple
from app.config import settings
from app.models.telemetry import CubeSatTelemetry
from datetime import datetime

class CubeSatService:
    
    def __init__(self):
        self.udp_socket: Optional[socket.socket] = None
        self.is_listening = False
        self.simulation_mode = settings.SIMULATION_MODE
        self.last_telemetry: Optional[CubeSatTelemetry] = None
        self._stop_event = threading.Event()
        self._reader_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
    def start_udp_listener(self) -> bool:
        
        if self.simulation_mode:
            print(" [SIMULACIÓN] Iniciando listener UDP simulado...")
            self.is_listening = True
            return True
        
        try:
            self.udp_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            )
            self.udp_socket.bind(
                ('0.0.0.0', settings.CUBESAT_UDP_PORT)
            )
            self.udp_socket.settimeout(1.0)
            
            self._stop_event.clear()
            self._reader_thread = threading.Thread(
                target=self._udp_reader_loop,
                name="cubesat-udp-reader",
                daemon=True
            )
            self._reader_thread.start()
            
            self.is_listening = True
            print(f" UDP listener iniciado en puerto {settings.CUBESAT_UDP_PORT}")
            return True
            
        except Exception as e:
            print(f" Error iniciando UDP listener: {e}")
            self.is_listening = False
            return False
    
    def _udp_reader_loop(self):
        while not self._stop_event.is_set():
            try:
                data, addr = self.udp_socket.recvfrom(4096)
                tel = CubeSatService._parse_udp_packet(data)
                if tel is not None:
                    with self._lock:
                        self.last_telemetry = tel
            except socket.timeout:
                continue
            except Exception as e:
                if not self._stop_event.is_set():
                    print(f" Error leyendo UDP: {e}")
    
    @staticmethod
    def _parse_udp_packet(raw: bytes) -> Optional[CubeSatTelemetry]:
        try:
            json_data = json.loads(raw.decode('utf-8'))
            roll  = float(json_data.get("roll", 0.0))
            pitch = float(json_data.get("pitch", 0.0))
            yaw   = float(json_data.get("yaw", 0.0))
            mx    = float(json_data.get("mx", 0.0))
            my    = float(json_data.get("my", 0.0))
            mz    = float(json_data.get("mz", 0.0))

            q0, q1, q2, q3 = CubeSatService._euler_a_cuaternion(roll, pitch, yaw)

            return CubeSatTelemetry(
                timestamp=datetime.now(),
                roll=roll, pitch=pitch, yaw=yaw,
                q0=q0, q1=q1, q2=q2, q3=q3,
                acc_x=0.0, acc_y=0.0, acc_z=0.0,
                gyro_x=0.0, gyro_y=0.0, gyro_z=0.0,
                mag_x=mx, mag_y=my, mag_z=mz,
            )
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f" Error decodificando JSON UDP: {e}")
            return None
    
    def stop_udp_listener(self):
        
        self._stop_event.set()
        
        if self._reader_thread is not None:
            self._reader_thread.join(timeout=2.0)
            self._reader_thread = None
        
        if self.udp_socket:
            self.udp_socket.close()
            self.is_listening = False
            print(" UDP listener detenido")
    
    @staticmethod
    def _euler_a_cuaternion(roll_deg: float, pitch_deg: float, yaw_deg: float) -> Tuple[float, float, float, float]:
        cr = math.radians(roll_deg)
        cp = math.radians(pitch_deg)
        cy = math.radians(yaw_deg)

        sr = math.sin(cr / 2)
        cr_ = math.cos(cr / 2)
        sp = math.sin(cp / 2)
        cp_ = math.cos(cp / 2)
        sy = math.sin(cy / 2)
        cy_ = math.cos(cy / 2)

        q0 = cr_ * cp_ * cy_ + sr * sp * sy
        q1 = sr * cp_ * cy_ - cr_ * sp * sy
        q2 = cr_ * sp * sy + sr * cp_ * cy_
        q3 = cr_ * cp_ * sy - sr * sp * sy

        return q0, q1, q2, q3

    def receive_telemetry(self) -> Optional[CubeSatTelemetry]:
        
        if self.simulation_mode:
            from app.services.simulation_service import simulador
            self.last_telemetry = simulador.generar_telemetria_cubesat()
            return self.last_telemetry
        
        if not self.is_listening or not self.udp_socket:
            return None
        
        # El paquete es capturado de forma asíncrona por _udp_reader_loop y
        # guardado en self.last_telemetry. Aquí solo devolvemos la última
        # muestra válida (sin bloquear el event loop del WebSocket).
        with self._lock:
            return self.last_telemetry
    
    def send_http_command(self, endpoint: str, data: Dict = None) -> bool:
        
        if self.simulation_mode:
            print(f" [SIM] HTTP {endpoint} -> {data}")
            return True
        
        try:
            import requests
            
            url = f"http://{settings.CUBESAT_IP}:{settings.CUBESAT_HTTP_PORT}/{endpoint}"
            
            if data:
                response = requests.post(url, json=data, timeout=2)
            else:
                response = requests.get(url, timeout=2)
            
            return response.status_code == 200
            
        except Exception as e:
            print(f" Error HTTP: {e}")
            return False
    
    def get_telemetry_http(self) -> Optional[Dict]:
       
        if self.simulation_mode:
            from app.services.simulation_service import simulador
            tel = simulador.generar_telemetria_cubesat()
            return tel.model_dump()
        
        try:
            import requests
            
            url = f"http://{settings.CUBESAT_IP}:{settings.CUBESAT_HTTP_PORT}/telemetry.json"
            response = requests.get(url, timeout=2)
            
            if response.status_code == 200:
                return response.json()
            
        except Exception as e:
            print(f" Error GET telemetry: {e}")
        
        return None

cubesat_service = CubeSatService()