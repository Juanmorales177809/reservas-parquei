import uuid

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyCookie
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.auth.auth import NOMBRE_COOKIE_ACCESO
from app.config import settings
from app.crud.usuarios import get_usuario_by_supabase_id
from app.db import get_db
from app.models import Usuario, UsuarioEspacio


# El mecanismo de sesión es únicamente la cookie HttpOnly `access_token`,
# que a partir de la migración a Supabase Auth contiene el JWT de Supabase
# tal cual (ver app/api/auth.py::supabase_sesion). `auto_error=False` deja
# que cada dependiente decida su propio 401 con mensaje estable. La
# presencia de este `APIKeyCookie` como dependencia es lo que hace que
# FastAPI documente el esquema `cookieAuth` (apiKey, cookie) y lo exija en
# los endpoints protegidos; los públicos (con `get_current_user_optional`)
# no lo usan a propósito, para no exponer el esquema en rutas públicas
# (RN-005).
cookie_auth = APIKeyCookie(
    name=NOMBRE_COOKIE_ACCESO,
    auto_error=False,
    scheme_name="cookieAuth",
)


def _decode_token(token: str) -> dict:
    """Decodifica el JWT de Supabase (único emisor de tokens desde la
    migración -- este backend ya no emite JWT propios, ver
    app/api/auth.py). `verify_aud` desactivado: Supabase pone
    `aud=authenticated` y no hace falta validarlo para este caso de uso.
    """
    try:
        return jwt.decode(
            token, settings.supabase_jwt_secret, algorithms=[settings.algorithm], options={"verify_aud": False}
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar la autenticación",
        ) from exc


def _usuario_por_sub(db: Session, sub: str) -> Usuario | None:
    """El `sub` de un JWT de Supabase siempre es el UUID de `auth.users`."""
    try:
        supabase_id = uuid.UUID(str(sub))
    except (TypeError, ValueError):
        return None
    return get_usuario_by_supabase_id(db, supabase_id)


def _credenciales_invalidas() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la autenticación",
    )


def get_current_user(
    token: str | None = Depends(cookie_auth),
    db: Session = Depends(get_db),
) -> Usuario:
    credentials_exception = _credenciales_invalidas()
    if not token:
        raise credentials_exception
    try:
        payload = _decode_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
    except HTTPException:
        raise
    except Exception as exc:
        raise credentials_exception from exc

    usuario = _usuario_por_sub(db, str(sub))
    if usuario is None:
        raise credentials_exception
    return usuario


def require_admin_dashboard(
    token: str | None = Depends(cookie_auth),
    db: Session = Depends(get_db),
) -> Usuario:
    credentials_exception = _credenciales_invalidas()
    if not token:
        raise credentials_exception
    payload = _decode_token(token)
    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception
    usuario = _usuario_por_sub(db, str(sub))
    if usuario is None:
        raise credentials_exception
    if usuario.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El dashboard requiere rol admin",
        )
    return usuario


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.rol != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo un administrador puede realizar esta acción")
    return current_user


def require_resource_manager(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.rol not in {"admin", "gestor"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para gestionar recursos y reservas",
        )
    return current_user


def get_managed_space_id(db: Session, usuario: Usuario) -> int | None:
    if usuario.rol == "admin":
        return None
    asignacion = (
        db.query(UsuarioEspacio)
        .filter(UsuarioEspacio.usuario_id == usuario.id)
        .first()
    )
    if asignacion is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El gestor no tiene un espacio asignado",
        )
    return asignacion.espacio_id


def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
) -> Usuario | None:
    """Usuario autenticado por cookie, o None si no hay cookie o es inválida.

    Sin `Depends(cookie_auth)` a propósito, para NO añadir el esquema de
    seguridad al OpenAPI de los endpoints públicos que lo usan (RN-005 en
    GET /espacios). Un token inválido se trata como acceso anónimo.
    """
    token = request.cookies.get(NOMBRE_COOKIE_ACCESO)
    if not token:
        return None
    try:
        payload = _decode_token(token)
        sub = payload.get("sub")
        if sub is None:
            return None
    except (HTTPException, TypeError, ValueError):
        return None
    return _usuario_por_sub(db, str(sub))
