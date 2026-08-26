from fastapi import APIRouter, HTTPException
from app.models.telemetry import ControlCommand, PerfilMagnetico
from app.config import settings
from app.services.simulation_service import simulador

router = APIRouter()

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