from fastapi import APIRouter
from app.services.simulation_service import simulador
from app.models.telemetry import JaulaTelemetry, CubeSatTelemetry, PerfilMagnetico
from app.database.db_manager import db_manager

router = APIRouter()

@router.get("/jaula", response_model=JaulaTelemetry)
async def get_jaula_telemetry(sesion_id: int = None):

    telemetry = simulador.generar_telemetria_jaula()
    if sesion_id:
        db_manager.log_jaula_telemetry(sesion_id, telemetry.model_dump(mode='json'))
    return telemetry

@router.get("/cubesat", response_model=CubeSatTelemetry)
async def get_cubesat_telemetry(sesion_id: int = None):

    telemetry = simulador.generar_telemetria_cubesat()
    if sesion_id:
        db_manager.log_cubesat_telemetry(sesion_id, telemetry.model_dump(mode='json'))
    return telemetry

@router.post("/jaula/iniciar")
async def iniciar_ensayo_jaula(perfil: PerfilMagnetico):

    sesion_id = db_manager.create_session(
        nombre=f"Ensayo Bx:{perfil.bx},By:{perfil.by},Bz:{perfil.bz}",
        operador="MIGUEL",
        tipo_prueba="ensayo_magnetico",
        descripcion=f"Bx={perfil.bx}μT By={perfil.by}μT Bz={perfil.bz}μT"
    )

    simulador.iniciar_ensayo({"bx": perfil.bx, "by": perfil.by, "bz": perfil.bz})
    return {
        "message": "Ensayo de jaula iniciado",
        "estado": "ejecutando",
        "perfil": {"bx": perfil.bx, "by": perfil.by, "bz": perfil.bz},
        "sesion_id": sesion_id
    }

@router.post("/jaula/detener")
async def detener_ensayo_jaula(sesion_id: int = None):

    simulador.detener_ensayo()

    if sesion_id:
        db_manager.close_session(sesion_id)

    return {"message": "Ensayo de jaula detenido", "estado": "reposo"}