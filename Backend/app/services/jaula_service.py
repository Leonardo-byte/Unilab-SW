import serial
import time
import json
from typing import Dict, Optional
from app.config import settings
from app.models.telemetry import JaulaTelemetry
from datetime import datetime

class JaulaService:
    
    def __init__(self):
        self.serial_port: Optional[serial.Serial] = None
        self.is_connected = False
        self.simulation_mode = settings.SIMULATION_MODE
        
    def connect(self, port: str = None, baudrate: int = None) -> bool:
        
        if self.simulation_mode:
            print(" [SIMULACIÓN] Conectando con Jaula simulada...")
            self.is_connected = True
            return True
        
        try:
            port = port or settings.JAULA_SERIAL_PORT
            baudrate = baudrate or settings.JAULA_BAUDRATE
            
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=1
            )
            time.sleep(2)  
            
            if self.serial_port.is_open:
                self.is_connected = True
                print(f" Conectado a {port} @ {baudrate} bps")
                return True
            else:
                return False
                
        except serial.SerialException as e:
            print(f" Error de conexión serial: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):

        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print(" Desconectado de la jaula")
        self.is_connected = False
    
    def send_command(self, command: str) -> bool:
        
        if self.simulation_mode:
            print(f" [SIM] Comando enviado: {command.strip()}")
            return True
        
        if not self.is_connected or not self.serial_port:
            return False
        
        try:
            self.serial_port.write(command.encode())
            self.serial_port.flush()
            return True
        except Exception as e:
            print(f" Error enviando comando: {e}")
            return False
    
    def set_corriente(self, eje: str, valor: float) -> bool:
        
        if eje not in ["X", "Y", "Z"]:
            raise ValueError(f"Eje inválido: {eje}. Debe ser X, Y o Z")
        
        if not (settings.MIN_CURRENT <= valor <= settings.MAX_CURRENT):
            raise ValueError(f"Corriente fuera de rango: {valor}A")
        
        command = f"{eje}:{valor}\n"
        return self.send_command(command)
    
    def read_telemetry(self) -> Optional[JaulaTelemetry]:
        
        if self.simulation_mode:
            from app.services.simulation_service import simulador
            return simulador.generar_telemetria_jaula()
        
        if not self.is_connected or not self.serial_port:
            return None
        
        try:
            if self.serial_port.in_waiting > 0:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    data = json.loads(line)
                    return JaulaTelemetry(**data)
        except Exception as e:
            print(f" Error leyendo telemetría: {e}")
        
        return None
    
jaula_service = JaulaService()