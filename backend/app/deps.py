from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import Usuario, UsuarioEspacio


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _decode_token(token: str) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la autenticación",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise credentials_exception from exc


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la autenticación",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = _decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except (TypeError, ValueError) as exc:
        raise credentials_exception from exc

    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if usuario is None:
        raise credentials_exception
    return usuario


def require_admin_dashboard(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    payload = _decode_token(token)
    role = payload.get("role") or payload.get("rol")
    raw_scopes = payload.get("scope", payload.get("scopes", []))
    if isinstance(raw_scopes, str):
        scopes = set(raw_scopes.split())
    elif isinstance(raw_scopes, (list, tuple, set)):
        scopes = set(raw_scopes)
    else:
        scopes = set()

    if role != "admin" and "admin:*" not in scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El dashboard requiere role=admin o scope admin:*",
        )

    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar la autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar la autenticación",
            headers={"WWW-Authenticate": "Bearer"},
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
    """Usuario autenticado, o None si no hay token o es inválido.

    Lee el header Authorization manualmente (sin OAuth2PasswordBearer) para
    NO añadir un esquema de seguridad al OpenAPI de los endpoints públicos
    que lo usan (RN-005 en GET /espacios). Un token inválido se trata como
    acceso anónimo.
    """
    cabecera = request.headers.get("Authorization", "")
    if not cabecera.startswith("Bearer "):
        return None
    token = cabecera[len("Bearer ") :]
    try:
        payload = _decode_token(token)
        user_id = int(payload.get("sub"))
    except (HTTPException, TypeError, ValueError):
        return None
    return db.query(Usuario).filter(Usuario.id == user_id).first()
