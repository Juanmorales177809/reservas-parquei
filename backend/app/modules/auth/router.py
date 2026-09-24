"""Router de auth, carril A: sesión y credenciales propias.

`GET /api/auth/csrf` (BK-06) y §3.2 a §3.5 (AUTH-A2, AUTH-A3). El resto del
contrato —registro, recuperación, invitaciones, administración— vive en
`router_cuentas.py` y `router_invitaciones.py`, carril B.
"""

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.deps import ContextoAutenticado, obtener_contexto
from app.core.security import (
    COOKIE_ACCESO,
    COOKIE_REFRESH,
    asegurar_cookie_csrf,
    borrar_cookies_sesion,
    emitir_cookie_acceso,
    emitir_cookie_refresh,
    exigir_csrf,
    verificar_token_acceso,
)
from app.core.config import get_settings
from app.db.session import get_db
from app.modules.auth import schemas, service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/csrf", status_code=204)
def obtener_csrf(request: Request, response: Response) -> None:
    """Contrato §3.0: emite `rp_csrf` sin exigir sesión. Idéntica exista o no una."""
    asegurar_cookie_csrf(request, response)


@router.post("/sesiones", status_code=201, response_model=schemas.SesionIniciada)
def iniciar_sesion(
    cuerpo: schemas.LoginSolicitud,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.SesionIniciada:
    """§3.2 — limitado. La clave de límite es el correo: no bloquea por IP
    compartida, y superar el límite nunca concede acceso (SEC-ABU-03)."""
    service.limitar_login(cuerpo.correo)
    datos, token_acceso, refresh = service.iniciar_sesion(db, cuerpo.correo, cuerpo.contrasena)

    emitir_cookie_acceso(response, token_acceso, get_settings().jwt_vigencia_acceso_segundos)
    emitir_cookie_refresh(response, refresh, service.VIGENCIA_REFRESH_SEGUNDOS)
    asegurar_cookie_csrf(request, response)

    return schemas.SesionIniciada(**datos)


@router.post("/sesiones/renovacion", response_model=schemas.RenovacionRespuesta)
def renovar_sesion(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.RenovacionRespuesta:
    """§3.3. Exige la cookie `rp_refresh`; no exige `rp_access` vigente."""
    refresh_token = request.cookies.get(COOKIE_REFRESH)
    datos, nuevo_acceso, nuevo_refresh = service.renovar_sesion(db, refresh_token)

    emitir_cookie_acceso(response, nuevo_acceso, get_settings().jwt_vigencia_acceso_segundos)
    emitir_cookie_refresh(response, nuevo_refresh, service.VIGENCIA_REFRESH_SEGUNDOS)

    return schemas.RenovacionRespuesta(**datos)


@router.get("/sesiones/actual", response_model=schemas.SesionActual)
def sesion_actual(contexto: ContextoAutenticado = Depends(obtener_contexto)) -> schemas.SesionActual:
    """§3.4. Solo para adaptar la interfaz: nunca sustituye la revalidación
    de permiso y ámbito en cada operación (SEC-AUTZ-01)."""
    return schemas.SesionActual(
        id_cuenta=contexto.id_cuenta,
        tipo_cuenta=contexto.tipo_cuenta,
        rol=contexto.rol,
        correo=contexto.correo,
        actualizacion_inicial_pendiente=contexto.actualizacion_inicial_pendiente,
        id_sesion=contexto.id_sesion,
        unidades_autorizadas=contexto.unidades_autorizadas,
        autenticacion_reciente=contexto.autenticacion_reciente,
    )


@router.delete("/sesiones/actual", status_code=204)
def cerrar_sesion(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> None:
    """§3.5. `204` también si la sesión ya estaba vencida o revocada: el
    resultado para el cliente es el mismo, así que no se usa `obtener_contexto`
    —fallaría con 401 justo en el caso que este endpoint debe tolerar—.
    """
    token = request.cookies.get(COOKIE_ACCESO)
    if token:
        try:
            claims = verificar_token_acceso(token)
            service.cerrar_sesion(db, claims["sid"])
        except Exception:
            pass  # un token ya inválido no impide limpiar las cookies
    borrar_cookies_sesion(response)
    response.delete_cookie("rp_csrf", path="/")
