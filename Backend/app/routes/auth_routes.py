from fastapi import APIRouter, HTTPException
from app.models.user import LoginRequest

router = APIRouter()

USUARIOS = {
    "admin": "unilab",
}

@router.post("/login")
async def login(request: LoginRequest):
    usuario = USUARIOS.get(request.username)
    if usuario is None or usuario != request.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {
        "message": "Login exitoso",
        "username": request.username,
        "token": "unilab-token"
    }

@router.post("/logout")
async def logout():
    return {
        "message": "Logout exitoso"
    }

@router.get("/verify")
async def verify_token():
    return {"authenticated": True}
