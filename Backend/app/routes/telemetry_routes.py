from fastapi import APIRouter
from app.services.simulation_service import simulador
from app.models.telemetry import JaulaTelemetry, CubeSatTelemetry, PerfilMagnetico

router = APIRouter()

@router.get("/jaula", response_model=JaulaTelemetry)
async def get_jaula_telemetry():
   
    return simulador.generar_telemetria_jaula()

@router.get("/cubesat", response_model=CubeSatTelemetry)
async def get_cubesat_telemetry():
    
    return simulador.generar_telemetria_cubesat()

@router.post("/jaula/iniciar")
async def iniciar_ensayo_jaula(perfil: PerfilMagnetico):

    simulador.iniciar_ensayo({"bx": perfil.bx, "by": perfil.by, "bz": perfil.bz})
    return {
        "message": "Ensayo de jaula iniciado",
        "estado": "ejecutando",
        "perfil": {"bx": perfil.bx, "by": perfil.by, "bz": perfil.bz}
    }

@router.post("/jaula/detener")
async def detener_ensayo_jaula():
    
    simulador.detener_ensayo()
    return {"message": "Ensayo de jaula detenido", "estado": "reposo"}