from fastapi import APIRouter, HTTPException
from app.models.telemetry import ControlCommand, PerfilMagnetico
from app.models.control import ControlCubesat
from app.config import settings
from app.services.simulation_service import simulador
from app.services.jaula_service import jaula_service
from app.services.cubesat_service import cubesat_service
from app.database.db_manager import db_manager

router = APIRouter()

@router.post("/jaula/conectar")
async def conectar_jaula(port: str = None, baudrate: int = None):
    success = jaula_service.connect(port or settings.JAULA_SERIAL_PORT, baudrate or settings.JAULA_BAUDRATE)
    if success:
        return {"message": "Jaula conectada", "estado": "conectada"}
    raise HTTPException(status_code=400, detail="No se pudo conectar la jaula")

@router.post("/jaula/desconectar")
async def desconectar_jaula():
    jaula_service.disconnect()
    return {"message": "Jaula desconectada", "estado": "desconectada"}

@router.post("/cubesat/conectar")
async def conectar_cubesat():
    success = cubesat_service.start_udp_listener()
    if success:
        return {"message": "CubeSat conectado", "estado": "conectado"}
    raise HTTPException(status_code=400, detail="No se pudo conectar el CubeSat")

@router.post("/cubesat/desconectar")
async def desconectar_cubesat():
    cubesat_service.stop_udp_listener()
    return {"message": "CubeSat desconectado", "estado": "desconectado"}

@router.get("/jaula/estado")
async def estado_jaula():
    return {"conectada": jaula_service.is_connected}

@router.get("/cubesat/estado")
async def estado_cubesat():
    return {"conectado": cubesat_service.is_listening}

@router.post("/jaula/corriente")
async def set_corriente_jaula(comando: ControlCommand):
    
    if not (settings.MIN_CURRENT <= comando.corriente <= settings.MAX_CURRENT):
        raise HTTPException(
            status_code=400,
            detail=f"Corriente fuera de rango. Debe estar entre {settings.MIN_CURRENT}A y {settings.MAX_CURRENT}A"
        )
    
    if comando.eje not in ["X", "Y", "Z"]:
        raise HTTPException(
            status_code=400,
            detail=f"Eje inválido. Debe ser X, Y o Z"
        )
    
    simulador.corrientes_objetivo[comando.eje] = comando.corriente
    
    print(f" COMANDO: Eje {comando.eje} -> {comando.corriente}A")
    
    return {
        "message": f"Comando enviado al eje {comando.eje}",
        "corriente": comando.corriente,
        "eje": comando.eje,
        "estado": "simulado" if settings.SIMULATION_MODE else "ejecutado"
    }

@router.post("/jaula/perfil")
async def set_perfil_magnetico(perfil: PerfilMagnetico):
    
    magnitud = (perfil.bx**2 + perfil.by**2 + perfil.bz**2)**0.5
    
    if not (settings.MIN_FIELD <= magnitud <= settings.MAX_FIELD):
        raise HTTPException(
            status_code=400,
            detail=f"Magnitud fuera de rango. Debe estar entre {settings.MIN_FIELD} μT y {settings.MAX_FIELD} μT"
        )
    
    print(f" PERFIL: Bx={perfil.bx} μT, By={perfil.by} μT, Bz={perfil.bz} μT")
    print(f" Magnitud total: {magnitud:.1f} μT")
    
    simulador.iniciar_ensayo({
        "bx": perfil.bx,
        "by": perfil.by,
        "bz": perfil.bz
    })
    
    return {
        "message": "Perfil de campo magnético configurado",
        "bx": perfil.bx,
        "by": perfil.by,
        "bz": perfil.bz,
        "magnitud_total": round(magnitud, 1),
        "estado": "simulado" if settings.SIMULATION_MODE else "ejecutando"
    }

@router.post("/cubesat/comando")
async def enviar_comando_control(comando: ControlCubesat):

    
    return {
            "mtq_x_pwm": "float",
            "mtq_y_pwm": "float"
    }

@router.get("/sessions")
async def get_sesiones(limit: int = 10):
    sessions = db_manager.get_sessions(limit)
    return sessions

@router.post("/sessions")
async def create_sesion(nombre: str, operador: str, tipo_prueba: str, descripcion: str = None):
    session_id = db_manager.create_session(nombre, operador, tipo_prueba, descripcion)
    return {"id": session_id, "message": "Sesión creada"}

@router.post("/sessions/{sesion_id}/cerrar")
async def cerrar_sesion(sesion_id: int):
    db_manager.close_session(sesion_id)
    return {"message": "Sesión cerrada"}

@router.post("/jaula/comando")
async def enviar_comando_serial(comando: str):
    success = jaula_service.send_command(comando + '\n')
    if success:
        return {"message": "Comando enviado", "comando": comando}
    raise HTTPException(status_code=400, detail="No se pudo enviar el comando")

@router.get("/config")
async def get_config():
    return {
        "simulation_mode": settings.SIMULATION_MODE,
        "jaula_serial_port": settings.JAULA_SERIAL_PORT,
        "jaula_baudrate": settings.JAULA_BAUDRATE,
        "cubesat_ip": settings.CUBESAT_IP,
        "cubesat_udp_port": settings.CUBESAT_UDP_PORT,
        "ws_update_interval": settings.WS_UPDATE_INTERVAL,
        "kx": settings.KX,
        "ky": settings.KY,
        "kz": settings.KZ,
        "min_current": settings.MIN_CURRENT,
        "max_current": settings.MAX_CURRENT,
        "min_field": settings.MIN_FIELD,
        "max_field": settings.MAX_FIELD
    }