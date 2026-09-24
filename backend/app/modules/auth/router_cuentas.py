"""Router de auth, carril B: alta, recuperación, reautenticación y
administración de cuentas (AUTH-B1, AUTH-B2, AUTH-B4, AUTH-B5).

Invitaciones vive aparte, en `router_invitaciones.py`.
"""

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import ContextoAutenticado, exigir_autenticacion_reciente, exigir_permiso_dep, obtener_contexto
from app.core.security import asegurar_cookie_csrf, emitir_cookie_acceso, emitir_cookie_refresh, exigir_csrf
from app.db.session import get_db
from app.modules.auth import schemas, service, service_cuentas

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/registro", status_code=202, response_model=schemas.MensajeGenerico)
def registro(
    cuerpo: schemas.RegistroSolicitud,
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.MensajeGenerico:
    """§3.1 — limitado. Respuesta idéntica exista o no el correo (SEC-ABU-02)."""
    service_cuentas.limitar_registro(cuerpo.correo)
    service_cuentas.registrar(db, cuerpo)
    return schemas.MensajeGenerico(
        mensaje="Si el correo puede registrarse, la cuenta quedará disponible para iniciar sesión."
    )


@router.post("/recuperacion", status_code=202, response_model=schemas.MensajeGenerico)
def solicitar_recuperacion(
    cuerpo: schemas.RecuperacionSolicitud,
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.MensajeGenerico:
    """§3.6 — limitado. Respuesta idéntica exista o no la cuenta (SEC-REC-01)."""
    service_cuentas.limitar_recuperacion(cuerpo.correo)
    service_cuentas.solicitar_recuperacion(db, cuerpo.correo)
    return schemas.MensajeGenerico(
        mensaje="Si existe una cuenta asociada, se enviarán las instrucciones de recuperación."
    )


@router.get("/recuperacion/{token}", response_model=schemas.TokenVigente)
def validar_recuperacion(token: str, db: Session = Depends(get_db)) -> schemas.TokenVigente:
    """§3.7. La respuesta no revela a qué cuenta pertenece el token."""
    service_cuentas.validar_token_recuperacion(db, token)
    return schemas.TokenVigente(vigente=True)


@router.post("/recuperacion/{token}", status_code=204)
def restablecer_contrasena(
    token: str,
    cuerpo: schemas.RestablecerContrasena,
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> None:
    """§3.8 — limitado. Revoca todas las sesiones activas de la cuenta."""
    service_cuentas.limitar_recuperacion(token)
    service_cuentas.restablecer_contrasena(db, token, cuerpo.contrasena)


@router.post("/reautenticacion", response_model=schemas.ReautenticacionRespuesta)
def reautenticacion(
    cuerpo: schemas.ReautenticacionSolicitud,
    response: Response,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.ReautenticacionRespuesta:
    """§3.9 — limitado. Regenera el identificador de sesión."""
    service_cuentas.limitar_reautenticacion(f"cuenta:{contexto.id_cuenta}")
    datos, nuevo_acceso, nuevo_refresh = service_cuentas.reautenticar(db, contexto, cuerpo.contrasena)
    emitir_cookie_acceso(response, nuevo_acceso, get_settings().jwt_vigencia_acceso_segundos)
    emitir_cookie_refresh(response, nuevo_refresh, service.VIGENCIA_REFRESH_SEGUNDOS)
    return schemas.ReautenticacionRespuesta(**datos)


@router.put("/cuentas/actual/contrasena", status_code=204)
def cambiar_contrasena_propia(
    cuerpo: schemas.CambioContrasena,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(exigir_autenticacion_reciente),
    _csrf: None = Depends(exigir_csrf),
) -> None:
    """§5.1. Operación sensible: exige autenticación reciente."""
    service_cuentas.cambiar_contrasena_propia(db, contexto, cuerpo.contrasena)


@router.patch("/cuentas/{id_cuenta}/estado", response_model=schemas.CambioEstadoRespuesta)
def cambiar_estado(
    id_cuenta: int,
    cuerpo: schemas.CambioEstadoSolicitud,
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(exigir_permiso_dep("cuentas.administrar")),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.CambioEstadoRespuesta:
    """§6.1. Requiere `cuentas.administrar`, siempre global."""
    datos = service_cuentas.cambiar_estado(db, id_cuenta, cuerpo.estado)
    return schemas.CambioEstadoRespuesta(**datos)


@router.put("/cuentas/{id_cuenta}/identidad", response_model=schemas.CambioIdentidadRespuesta)
def cambiar_identidad(
    id_cuenta: int,
    cuerpo: schemas.CambioIdentidadSolicitud,
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(exigir_permiso_dep("cuentas.administrar")),
    _reciente: ContextoAutenticado = Depends(exigir_autenticacion_reciente),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.CambioIdentidadRespuesta:
    """§6.2. Requiere permiso y autenticación reciente: operación sensible."""
    datos = service_cuentas.cambiar_identidad(
        db, id_cuenta, cuerpo.tipo_cuenta, cuerpo.id_persona, cuerpo.id_usuario
    )
    return schemas.CambioIdentidadRespuesta(**datos)
