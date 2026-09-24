"""`obtener_contexto()` y las dependencias que se construyen sobre ella
(contrato de auth §7; AUTH-A2, AUTH-A3, AUTH-B5).

La identidad proviene siempre de la sesión —la cookie `rp_access`—, nunca de
un identificador enviado por el cliente (`SEC-AUTZ-03`). Cualquier otro
módulo que necesite saber quién hace la petición depende de esto, no relee
la cookie por su cuenta.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.authz import exigir_permiso as _exigir_permiso
from app.core.authz import resolver_rol
from app.core.config import get_settings
from app.core.errors import NoAutenticado, PerfilInicialPendiente, ReautenticacionRequerida
from app.core.security import COOKIE_ACCESO, verificar_token_acceso
from app.db.models.auth import Cuentas, Sesiones
from app.db.models.identidad import Personal, Usuarios
from app.db.session import get_db


@dataclass
class ContextoAutenticado:
    id_cuenta: int
    id_sesion: str
    tipo_cuenta: Literal["USUARIO", "PERSONAL"]
    id_usuario: int | None
    id_persona: int | None
    rol: Literal["USUARIO", "TECNICO", "ADMINISTRADOR"]
    unidades_autorizadas: list[int] | Literal["GLOBAL"]
    autenticacion_reciente: bool
    actualizacion_inicial_pendiente: bool | None
    correo: str


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def obtener_contexto(request: Request, db: Session = Depends(get_db)) -> ContextoAutenticado:
    """Resuelve el contexto autenticado desde `rp_access`.

    Verifica que cuenta e identidad estén activas (`RN-AUTH-ID-01`,
    `RN-AUTH-ID-05`) y que la sesión no esté revocada, vencida, ni haya
    superado la inactividad máxima (`SEC-SES-07`, `SEC-SES-09`). Falla con
    `401 NO_AUTENTICADO`. Actualiza `ultima_actividad_at` en cada llamada.
    """
    token = request.cookies.get(COOKIE_ACCESO)
    if not token:
        raise NoAutenticado()
    claims = verificar_token_acceso(token)

    sesion = db.get(Sesiones, claims["sid"])
    if sesion is None or sesion.revoked_at is not None:
        raise NoAutenticado()

    ahora = datetime.now(timezone.utc)
    if _aware(sesion.expires_at) <= ahora:
        raise NoAutenticado()
    inactividad_maxima = get_settings().sesion_inactividad_maxima_segundos
    if (ahora - _aware(sesion.ultima_actividad_at)).total_seconds() > inactividad_maxima:
        raise NoAutenticado()

    cuenta = db.get(Cuentas, sesion.id_cuenta)
    if cuenta is None or not cuenta.estado:
        raise NoAutenticado()

    if cuenta.tipo_cuenta == "PERSONAL":
        persona = db.get(Personal, cuenta.id_persona)
        if persona is None or not persona.estado:
            raise NoAutenticado()
        actualizacion_inicial_pendiente = None
    else:
        usuario = db.get(Usuarios, cuenta.id_usuario)
        if usuario is None or not usuario.estado:
            raise NoAutenticado()
        actualizacion_inicial_pendiente = usuario.perfil_actualizado_at is None

    contexto_autz = resolver_rol(db, cuenta.id_cuenta)

    autenticacion_reciente = False
    if sesion.reautenticado_at is not None:
        ventana = get_settings().reautenticacion_ventana_segundos
        autenticacion_reciente = (ahora - _aware(sesion.reautenticado_at)).total_seconds() <= ventana

    # SEC-SES-09: se actualiza en cada operación autenticada, no solo al
    # renovar. Confirma también que la sesión sigue siendo válida más allá
    # de esta petición.
    sesion.ultima_actividad_at = ahora
    db.commit()

    return ContextoAutenticado(
        id_cuenta=cuenta.id_cuenta,
        id_sesion=str(sesion.id_sesion),
        tipo_cuenta=cuenta.tipo_cuenta,
        id_usuario=cuenta.id_usuario,
        id_persona=cuenta.id_persona,
        rol=contexto_autz.rol,
        unidades_autorizadas=contexto_autz.unidades_autorizadas,
        autenticacion_reciente=autenticacion_reciente,
        actualizacion_inicial_pendiente=actualizacion_inicial_pendiente,
        correo=cuenta.correo,
    )


def exigir_autenticacion_reciente(
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> ContextoAutenticado:
    """`401 REAUTENTICACION_REQUERIDA` si no hay autenticación reciente (SEC-REAUTH-01)."""
    if not contexto.autenticacion_reciente:
        raise ReautenticacionRequerida()
    return contexto


def exigir_perfil_inicial_completo(
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> ContextoAutenticado:
    """`403 PERFIL_INICIAL_PENDIENTE` mientras el Usuario no complete su perfil."""
    if contexto.actualizacion_inicial_pendiente:
        raise PerfilInicialPendiente()
    return contexto


def exigir_permiso_dep(codigo: str):
    """Fábrica: dependencia que exige `codigo` con ámbito global.

    Suficiente para auth, cuyo único permiso administrativo
    (`cuentas.administrar`) es siempre global (contrato §1). Un módulo que
    necesite ámbito por unidad construye sobre `core.authz.exigir_permiso`
    directamente, con el `id_unidad` que resuelva de su propio recurso.
    """

    def _dep(
        contexto: ContextoAutenticado = Depends(obtener_contexto),
        db: Session = Depends(get_db),
    ) -> ContextoAutenticado:
        _exigir_permiso(db, contexto.id_cuenta, codigo, id_unidad=None)
        return contexto

    return _dep
