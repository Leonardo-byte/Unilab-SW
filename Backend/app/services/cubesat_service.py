import socket
import json
from typing import Optional, Dict
from app.config import settings
from app.models.telemetry import CubeSatTelemetry
from datetime import datetime

class CubeSatService:
    
    def __init__(self):
        self.udp_socket: Optional[socket.socket] = None
        self.is_listening = False
        self.simulation_mode = settings.SIMULATION_MODE
        self.last_telemetry: Optional[CubeSatTelemetry] = None
        
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
            
            self.is_listening = True
            print(f" UDP listener iniciado en puerto {settings.CUBESAT_UDP_PORT}")
            return True
            
        except Exception as e:
            print(f" Error iniciando UDP listener: {e}")
            self.is_listening = False
            return False
    
    def stop_udp_listener(self):
       
        if self.udp_socket:
            self.udp_socket.close()
            self.is_listening = False
            print(" UDP listener detenido")
    
    def receive_telemetry(self) -> Optional[CubeSatTelemetry]:
       
        if self.simulation_mode:
            from app.services.simulation_service import simulador
            self.last_telemetry = simulador.generar_telemetria_cubesat()
            return self.last_telemetry
        
        if not self.is_listening or not self.udp_socket:
            return None
        
        try:
            data, addr = self.udp_socket.recvfrom(4096)
            json_data = json.loads(data.decode('utf-8'))
            
            self.last_telemetry = CubeSatTelemetry(**json_data)
            return self.last_telemetry
            
        except socket.timeout:
            return None
        except json.JSONDecodeError as e:
            print(f" Error decodificando JSON: {e}")
            return None
        except Exception as e:
            print(f"Error recibiendo telemetría: {e}")
            return None
    
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