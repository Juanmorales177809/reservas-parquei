from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.config import settings


from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"])


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None else timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


# Fase 9F-A (fase dual): además del body de TokenResponse, el token se
# expone como cookie HttpOnly con este nombre. app/api/auth.py la fija y
# la borra; app/deps.py la lee como fallback cuando no hay header
# Authorization.
NOMBRE_COOKIE_ACCESO = "access_token"


def atributos_cookie_acceso() -> dict:
    """Atributos comunes de la cookie de sesión, compartidos entre
    ``set_cookie`` (login) y ``delete_cookie`` (logout).

    SameSite=Lax y sin Domain explícito: el navegador del frontend solo ve
    un origen real (Next.js reescribe /api hacia el backend, ver
    frontend/next.config.js), así que no hace falta SameSite=None ni fijar
    Domain manualmente. Secure solo se activa con ENVIRONMENT=production
    confirmado explícitamente — mismo gate que Strict-Transport-Security/
    Cross-Origin-Opener-Policy en app/main.py — para no romper el login en
    desarrollo local sobre HTTP simple (docker-compose.yml actual, sin TLS
    documentado).
    """
    return {
        "httponly": True,
        "samesite": "lax",
        "path": "/",
        "secure": settings.environment == "production",
    }


def max_age_cookie_acceso() -> int:
    return settings.access_token_expire_minutes * 60
