import serial
import time
import json
import threading
from typing import Dict, Optional
from app.config import settings
from app.models.telemetry import JaulaTelemetry
from datetime import datetime

class JaulaService:

    def __init__(self):
        self.serial_port: Optional[serial.Serial] = None
        self.is_connected = False
        self.simulation_mode = settings.SIMULATION_MODE
        self.telemetry_data: Dict = {}
        self._lock = threading.Lock()

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

    def set_referencia_campo(self, bx: float, by: float) -> bool:
        command = f"REF:{bx:.2f},{by:.2f}\n"
        return self.send_command(command)

    def enable_driver(self, eje: str) -> bool:
        command = f"{eje} ON\n"
        return self.send_command(command)

    def disable_driver(self, eje: str) -> bool:
        command = f"{eje} OFF\n"
        return self.send_command(command)

    def read_serial_line(self) -> Optional[str]:
        if not self.is_connected or not self.serial_port:
            return None

        if self.serial_port.in_waiting > 0:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                return line if line else None
            except Exception as e:
                print(f" Error leyendo serial: {e}")
                return None
        return None

    def parse_serial_json(self, json_line: str) -> Optional[Dict]:
        try:
            data = json.loads(json_line)
            if data.get('device_id') == 'controlador_jaula':
                measurements = {}
                for m in data.get('measurements', []):
                    var = m['variable']
                    val = m['value']
                    measurements[var] = val

                with self._lock:
                    self.telemetry_data = measurements
                return measurements
        except json.JSONDecodeError:
            pass
        return None

    def read_telemetry(self) -> Optional[JaulaTelemetry]:
        if self.simulation_mode:
            from app.services.simulation_service import simulador
            return simulador.generar_telemetria_jaula()

        if not self.is_connected or not self.serial_port:
            return None

        with self._lock:
            data = self.telemetry_data.copy()

        if not data:
            return None

        ref_x = data.get('ref_x', 0.0)
        ref_y = data.get('ref_y', 0.0)
        current_x = data.get('current_x', 0.0)
        current_y = data.get('current_y', 0.0)
        current_z = data.get('current_z', 0.0)
        duty_x = data.get('duty_x', 0.0)
        duty_y = data.get('duty_y', 0.0)

        try:
            return JaulaTelemetry(
                timestamp=datetime.now(),
                eje_x_corriente=round(current_x, 2),
                eje_y_corriente=round(current_y, 2),
                eje_z_corriente=round(current_z, 2),
                eje_x_campo=ref_x,
                eje_y_campo=ref_y,
                eje_z_campo=0.0,
                estado="ejecutando" if self.is_connected else "reposo"
            )
        except Exception as e:
            print(f" Error creando telemetry: {e}")
            return None

    def get_latest_telemetry(self) -> Optional[Dict]:
        with self._lock:
            return self.telemetry_data.copy()

jaula_service = JaulaService()


jaula_reader_thread = None
jaula_reader_stop = threading.Event()


def start_jaula_reader():
    global jaula_reader_thread
    if jaula_reader_thread and jaula_reader_thread.is_alive():
        return

    jaula_reader_stop.clear()
    jaula_reader_thread = threading.Thread(target=_jaula_reader_loop, daemon=True)
    jaula_reader_thread.start()


def _jaula_reader_loop():
    while not jaula_reader_stop.is_set():
        if jaula_service.is_connected and not jaula_service.simulation_mode:
            line = jaula_service.read_serial_line()
            if line:
                jaula_service.parse_serial_json(line)
        time.sleep(0.01)


def stop_jaula_reader():
    jaula_reader_stop.set()
    global jaula_reader_thread
    if jaula_reader_thread:
        jaula_reader_thread.join(timeout=2)
        jaula_reader_thread = None