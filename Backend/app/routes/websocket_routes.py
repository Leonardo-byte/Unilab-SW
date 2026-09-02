import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.simulation_service import simulador
from app.config import settings

router = APIRouter()

active_connections: set[WebSocket] = set()
broadcaster_task: asyncio.Task | None = None
lock = asyncio.Lock()


async def telemetry_broadcaster():
    while True:
        if active_connections:
            jaula_data = simulador.generar_telemetria_jaula()
            cubesat_data = simulador.generar_telemetria_cubesat()
            payload = {
                "type": "telemetry",
                "jaula": jaula_data.model_dump(mode="json"),
                "cubesat": cubesat_data.model_dump(mode="json"),
            }
            disconnected = []
            for ws in list(active_connections):
                try:
                    await ws.send_json(payload)
                except Exception:
                    disconnected.append(ws)
            for ws in disconnected:
                active_connections.discard(ws)
        await asyncio.sleep(settings.WS_UPDATE_INTERVAL)


async def ensure_broadcaster():
    global broadcaster_task
    async with lock:
        if broadcaster_task is None or broadcaster_task.done():
            broadcaster_task = asyncio.create_task(telemetry_broadcaster())


@router.websocket("/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    await ensure_broadcaster()
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.discard(websocket)
    except Exception:
        active_connections.discard(websocket)


@router.websocket("/control")
async def websocket_control(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({
                "status": "ok",
                "message": f"Comando {data.get('action')} recibido",
            })
    except WebSocketDisconnect:
        pass
