"""
Módulo de autenticación para UniLab.
 
Responsabilidades:
- Registrar usuarios (contraseñas nunca se guardan en texto plano).
- Verificar credenciales (login).
- Emitir y validar tokens de sesión.
 
Sigue el mismo patrón que los demás módulos del sistema (SafetyManager,
MemoryStorage): expone setup() / shutdown() / get_status() para integrarse
con UniLabApp y ModuleRegistry.
 
Nota de implementación:
Por ahora los usuarios y las sesiones se guardan en memoria (igual que
MemoryStorage para la telemetría). Si más adelante se agrega persistencia
real (base de datos), este módulo es el punto a modificar sin afectar
a los demás módulos, gracias a los contratos compartidos en
unilab/contracts/models.py.
"""
 
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
 
from unilab.contracts.models import User
 
# Duración de una sesión antes de expirar.
SESSION_DURATION_MINUTES = 8 * 60  # 8 horas
 
# Iteraciones de PBKDF2. 390k es un valor recomendado (OWASP, 2023+)
# para SHA-256. No requiere dependencias externas (passlib/bcrypt).
PBKDF2_ITERATIONS = 390_000
 
 
class AuthManager:
    """
    Maneja usuarios y sesiones de autenticación en memoria.
    """
 
    def __init__(self, name: str) -> None:
        self.name = name
        self._users: dict[str, dict[str, Any]] = {}
        self._sessions: dict[str, dict[str, Any]] = {}
        self._is_setup = False
 
    # ------------------------------------------------------------------
    # Ciclo de vida del módulo (requerido por ModuleProtocol)
    # ------------------------------------------------------------------
 
    def setup(self) -> None:
        """
        Inicializa el módulo. Crea un usuario de prueba si todavía
        no existe ninguno, para poder probar el login de inmediato.
        """
        if not self._users:
            self.register_user(
                username="admin",
                password="admin1234",
                email="admin@unilab.local",
            )
 
        self._is_setup = True
 
    def shutdown(self) -> None:
        """
        Apaga el módulo. Invalida todas las sesiones activas.
        """
        self._sessions.clear()
        self._is_setup = False
 
    def get_status(self) -> dict[str, Any]:
        """
        Resumen del estado del módulo, usado por /api/status y /api/modules.
        """
        return {
            "name": self.name,
            "type": "AuthManager",
            "is_setup": self._is_setup,
            "users_count": len(self._users),
            "active_sessions": len(self._sessions),
        }
 
    # ------------------------------------------------------------------
    # Hashing de contraseñas (PBKDF2-HMAC-SHA256 + salt aleatorio)
    # ------------------------------------------------------------------
 
    @staticmethod
    def _hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
        salt = salt or secrets.token_bytes(16)
 
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            PBKDF2_ITERATIONS,
        )
 
        return derived.hex(), salt.hex()
 
    @staticmethod
    def _verify_password(password: str, hashed_hex: str, salt_hex: str) -> bool:
        salt = bytes.fromhex(salt_hex)
        derived_hex, _ = AuthManager._hash_password(password, salt)
 
        # compare_digest evita ataques de timing.
        return hmac.compare_digest(derived_hex, hashed_hex)
 
    # ------------------------------------------------------------------
    # Usuarios
    # ------------------------------------------------------------------
 
    def register_user(
        self,
        username: str,
        password: str,
        email: str | None = None,
    ) -> User:
        """
        Registra un nuevo usuario. Lanza ValueError si ya existe.
        """
        normalized = username.strip().lower()
 
        if normalized in self._users:
            raise ValueError("El usuario ya existe.")
 
        hashed_hex, salt_hex = self._hash_password(password)
        user = User(username=username, email=email)
 
        self._users[normalized] = {
            "user": user,
            "hashed_password": hashed_hex,
            "salt": salt_hex,
        }
 
        return user
 
    def authenticate(self, username: str, password: str) -> User | None:
        """
        Verifica usuario/contraseña. Devuelve el User si son correctos,
        o None si no (sin distinguir si el usuario existe o no, para
        no filtrar esa información).
        """
        normalized = username.strip().lower()
        record = self._users.get(normalized)
 
        if record is None:
            return None
 
        if not self._verify_password(password, record["hashed_password"], record["salt"]):
            return None
 
        return record["user"]
 
    # ------------------------------------------------------------------
    # Sesiones (tokens)
    # ------------------------------------------------------------------
 
    def create_session(self, user: User) -> tuple[str, datetime]:
        """
        Crea un token de sesión aleatorio y seguro para el usuario dado.
        """
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=SESSION_DURATION_MINUTES)
 
        self._sessions[token] = {
            "username": user.username.strip().lower(),
            "expires_at": expires_at,
        }
 
        return token, expires_at
 
    def get_user_from_token(self, token: str) -> User | None:
        """
        Devuelve el User asociado a un token válido y no expirado.
        """
        session = self._sessions.get(token)
 
        if session is None:
            return None
 
        if datetime.now(timezone.utc) > session["expires_at"]:
            del self._sessions[token]
            return None
 
        record = self._users.get(session["username"])
 
        return record["user"] if record else None
 
    def revoke_session(self, token: str) -> None:
        """
        Invalida un token (logout).
        """
        self._sessions.pop(token, None)
 