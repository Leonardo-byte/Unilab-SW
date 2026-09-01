from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import telemetry_routes, control_routes, websocket_routes, auth_routes
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="API para Plataforma de Pruebas ADCS - Jaula de Helmholtz + CubeSat",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(telemetry_routes.router, prefix="/api/telemetry", tags=["Telemetría"])
app.include_router(control_routes.router, prefix="/api/control", tags=["Control"])
app.include_router(websocket_routes.router, prefix="/ws", tags=["WebSocket"])

@app.get("/")
async def read_root():
    return {
        "message": "UNILAB Backend API - Sistema de Pruebas ADCS",
        "status": "online",
        "simulation_mode": settings.SIMULATION_MODE,
        "docs": "/docs"
    }

@app.get("/api/status")
async def get_status():
    return {
        "jaula": "simulada" if settings.SIMULATION_MODE else "conectada",
        "cubesat": "simulado" if settings.SIMULATION_MODE else "conectado",
        "simulador_solar": "simulado",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )