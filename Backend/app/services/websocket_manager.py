from fastapi import WebSocket
from typing import List, Dict
import json

class ConnectionManager:
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.telemetry_subscribers: List[WebSocket] = []
        self.control_clients: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket, client_type: str = "telemetry"):
        
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if client_type == "telemetry":
            self.telemetry_subscribers.append(websocket)
        elif client_type == "control":
            self.control_clients.append(websocket)
        
        print(f" Cliente {client_type} conectado. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, client_type: str = "telemetry"):
        
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if client_type == "telemetry" and websocket in self.telemetry_subscribers:
            self.telemetry_subscribers.remove(websocket)
        elif client_type == "control" and websocket in self.control_clients:
            self.control_clients.remove(websocket)
        
        print(f" Cliente {client_type} desconectado. Total: {len(self.active_connections)}")
    
    async def broadcast_telemetry(self, data: dict):
       
        disconnected = []
        
        for connection in self.telemetry_subscribers:
            try:
                await connection.send_json({
                    "type": "telemetry",
                    "data": data
                })
            except Exception as e:
                print(f" Error enviando telemetría: {e}")
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn, "telemetry")
    
    async def send_to_control_client(self, websocket: WebSocket, data: dict):
        try:
            await websocket.send_json(data)
        except Exception as e:
            print(f" Error enviando a cliente control: {e}")
            self.disconnect(websocket, "control")
    
    async def broadcast_control(self, data: dict):
        disconnected = []
        
        for connection in self.control_clients:
            try:
                await connection.send_json(data)
            except Exception as e:
                print(f" Error broadcast control: {e}")
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn, "control")

manager = ConnectionManager()