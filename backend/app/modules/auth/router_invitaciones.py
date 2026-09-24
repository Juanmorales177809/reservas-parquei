"""Router de auth, carril B: invitaciones (AUTH-B3)."""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import ContextoAutenticado, exigir_permiso_dep
from app.core.security import emitir_cookie_acceso, emitir_cookie_refresh, exigir_csrf
from app.db.session import get_db
from app.modules.auth import schemas, service, service_cuentas

router = APIRouter(prefix="/api/auth/invitaciones", tags=["auth"])


@router.post("", status_code=201, response_model=schemas.InvitacionCreada)
def emitir_invitacion(
    cuerpo: schemas.InvitacionSolicitud,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(exigir_permiso_dep("cuentas.administrar")),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.InvitacionCreada:
    """§4.1. La respuesta nunca incluye el token (SEC-TOK-02)."""
    datos = service_cuentas.emitir_invitacion(
        db, contexto, cuerpo.correo, cuerpo.tipo_cuenta, cuerpo.id_unidad
    )
    return schemas.InvitacionCreada(**datos)


@router.post("/{id_invitacion}/reenvio", response_model=schemas.InvitacionReenviada)
def reenviar_invitacion(
    id_invitacion: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(exigir_permiso_dep("cuentas.administrar")),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.InvitacionReenviada:
    """§4.2. Token nuevo, invalida el anterior (SEC-INV-03)."""
    datos = service_cuentas.reenviar_invitacion(db, id_invitacion, contexto)
    return schemas.InvitacionReenviada(**datos)


@router.get("/{token}", response_model=schemas.InvitacionVigente)
def validar_invitacion(token: str, db: Session = Depends(get_db)) -> schemas.InvitacionVigente:
    """§4.3. Público: quien tiene el token ya lo recibió en su buzón."""
    datos = service_cuentas.validar_invitacion(db, token)
    return schemas.InvitacionVigente(**datos)


@router.post("/{token}/activacion", status_code=201, response_model=schemas.SesionIniciada)
def activar_invitacion(
    token: str,
    cuerpo: schemas.ActivacionSolicitud,
    response: Response,
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.SesionIniciada:
    """§4.4 — limitado. Deja la sesión iniciada, igual que un login."""
    datos, token_acceso, refresh = service_cuentas.activar_invitacion(db, token, cuerpo.contrasena)
    emitir_cookie_acceso(response, token_acceso, get_settings().jwt_vigencia_acceso_segundos)
    emitir_cookie_refresh(response, refresh, service.VIGENCIA_REFRESH_SEGUNDOS)
    return schemas.SesionIniciada(**datos)
