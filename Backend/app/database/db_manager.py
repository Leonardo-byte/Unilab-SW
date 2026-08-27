import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

class DBManager:
    
    def __init__(self, db_path: str = "unilab.db"):
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None
        self._initialize_db()
    
    def _initialize_db(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sesiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                operador TEXT NOT NULL,
                tipo_prueba TEXT NOT NULL,
                fecha_inicio TIMESTAMP NOT NULL,
                fecha_fin TIMESTAMP,
                estado TEXT DEFAULT 'activa',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jaula_telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sesion_id INTEGER,
                timestamp TIMESTAMP NOT NULL,
                eje_x_corriente REAL,
                eje_y_corriente REAL,
                eje_z_corriente REAL,
                eje_x_campo REAL,
                eje_y_campo REAL,
                eje_z_campo REAL,
                estado TEXT,
                FOREIGN KEY (sesion_id) REFERENCES sesiones(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cubesat_telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sesion_id INTEGER,
                timestamp TIMESTAMP NOT NULL,
                roll REAL,
                pitch REAL,
                yaw REAL,
                q0 REAL,
                q1 REAL,
                q2 REAL,
                q3 REAL,
                acc_x REAL,
                acc_y REAL,
                acc_z REAL,
                gyro_x REAL,
                gyro_y REAL,
                gyro_z REAL,
                mag_x REAL,
                mag_y REAL,
                mag_z REAL,
                sun_1 INTEGER,
                sun_2 INTEGER,
                sun_3 INTEGER,
                sun_4 INTEGER,
                sun_5 INTEGER,
                sun_6 INTEGER,
                adcs_mode TEXT,
                FOREIGN KEY (sesion_id) REFERENCES sesiones(id)
            )
        ''')
        
        self.conn.commit()
        print(f" Base de datos inicializada: {self.db_path}")
    
    def create_session(self, nombre: str, operador: str, tipo_prueba: str, 
                      descripcion: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO sesiones (nombre, descripcion, operador, tipo_prueba, fecha_inicio)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, descripcion, operador, tipo_prueba, datetime.now()))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def close_session(self, sesion_id: int):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE sesiones 
            SET fecha_fin = ?, estado = 'completada'
            WHERE id = ?
        ''', (datetime.now(), sesion_id))
        self.conn.commit()
    
    def log_jaula_telemetry(self, sesion_id: int, telemetry_data: dict):
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO jaula_telemetry 
            (sesion_id, timestamp, eje_x_corriente, eje_y_corriente, eje_z_corriente,
             eje_x_campo, eje_y_campo, eje_z_campo, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,)
        ''', (
            sesion_id,
            telemetry_data.get('timestamp', datetime.now()),
            telemetry_data.get('eje_x_corriente'),
            telemetry_data.get('eje_y_corriente'),
            telemetry_data.get('eje_z_corriente'),
            telemetry_data.get('eje_x_campo'),
            telemetry_data.get('eje_y_campo'),
            telemetry_data.get('eje_z_campo'),
            telemetry_data.get('estado')
        ))
        self.conn.commit()
    
    def log_cubesat_telemetry(self, sesion_id: int, telemetry_data: dict):
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO cubesat_telemetry 
            (sesion_id, timestamp, roll, pitch, yaw,
             q0, q1, q2, q3,
             acc_x, acc_y, acc_z,
             gyro_x, gyro_y, gyro_z,
             mag_x, mag_y, mag_z,
             sun_1, sun_2, sun_3, sun_4, sun_5, sun_6,
             adcs_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sesion_id,
            telemetry_data.get('timestamp', datetime.now()),
            telemetry_data.get('roll'),
            telemetry_data.get('pitch'),
            telemetry_data.get('yaw'),
            telemetry_data.get('q0'),
            telemetry_data.get('q1'),
            telemetry_data.get('q2'),
            telemetry_data.get('q3'),
            telemetry_data.get('acc_x'),
            telemetry_data.get('acc_y'),
            telemetry_data.get('acc_z'),
            telemetry_data.get('gyro_x'),
            telemetry_data.get('gyro_y'),
            telemetry_data.get('gyro_z'),
            telemetry_data.get('mag_x'),
            telemetry_data.get('mag_y'),
            telemetry_data.get('mag_z'),
            telemetry_data.get('sun_1'),
            telemetry_data.get('sun_2'),
            telemetry_data.get('sun_3'),
            telemetry_data.get('sun_4'),
            telemetry_data.get('sun_5'),
            telemetry_data.get('sun_6'),
            telemetry_data.get('adcs_mode')
        ))
        self.conn.commit()
    
    def get_sessions(self, limit: int = 50) -> List[Dict]:
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM sesiones 
            ORDER BY fecha_inicio DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_session_telemetry(self, sesion_id: int) -> Dict:
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM jaula_telemetry WHERE sesion_id = ?
        ''', (sesion_id,))
        jaula_data = cursor.fetchall()
        
        cursor.execute('''
            SELECT * FROM cubesat_telemetry WHERE sesion_id = ?
        ''', (sesion_id,))
        cubesat_data = cursor.fetchall()
        
        return {
            "jaula": jaula_data,
            "cubesat": cubesat_data
        }
    
    def __del__(self):
        if self.conn:
            self.conn.close()

db_manager = DBManager()