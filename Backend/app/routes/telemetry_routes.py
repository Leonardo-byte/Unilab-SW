from fastapi import APIRouter
from app.services.simulation_service import simulador
from app.models.telemetry import JaulaTelemetry, CubeSatTelemetry

router = APIRouter()

@router.get("/jaula", response_model=JaulaTelemetry)
async def get_jaula_telemetry():
   
    return simulador.generar_telemetria_jaula()

@router.get("/cubesat", response_model=CubeSatTelemetry)
async def get_cubesat_telemetry():
   
    return simulador.generar_telemetria_cubesat()

@router.post("/jaula/iniciar")
async def iniciar_ensayo_jaula(bx: float, by: float, bz: float):

    simulador.iniciar_ensayo({"bx": bx, "by": by, "bz": bz})
    return {
        "message": "Ensayo de jaula iniciado",
        "estado": "ejecutando",
        "perfil": {"bx": bx, "by": by, "bz": bz}
    }

@router.post("/jaula/detener")
async def detener_ensayo_jaula():
    
    simulador.detener_ensayo()
    return {"message": "Ensayo de jaula detenido", "estado": "reposo"}