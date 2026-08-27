from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.simulation_service import simulador
from app.config import settings
import asyncio
import json

router = APIRouter()

active_connections: list[WebSocket] = []

@router.websocket("/telemetry")
async def websocket_telemetry(websocket: WebSocket):
   
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:

            jaula_data = simulador.generar_telemetria_jaula()
            cubesat_data = simulador.generar_telemetria_cubesat()
            
            await websocket.send_json({
                "type": "telemetry",
                "jaula": jaula_data.model_dump(mode='json'),
                "cubesat": cubesat_data.model_dump(mode='json')
            })
            
            await asyncio.sleep(settings.WS_UPDATE_INTERVAL)
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print("Cliente WebSocket desconectado")

@router.websocket("/control")
async def websocket_control(websocket: WebSocket):

    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            print(f" Comando recibido: {data}")
            
            await websocket.send_json({
                "status": "ok",
                "message": f"Comando {data.get('action')} recibido"
            })
            
    except WebSocketDisconnect:
        print(" Cliente de control desconectado")