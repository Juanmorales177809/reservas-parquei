"""Resolución de rol y autorización por permiso y ámbito (BK-07, API-04).

Implementa la derivación de `auth/data-model.md` §"Derivación del rol
funcional" y `exigir_permiso` del contrato interno de auth (§7): evalúa
permiso y unidad con información vigente en cada operación, nunca desde el
token (`SEC-JWT-04`, `RN-AUTH-ROL-05`).

Lo que este módulo NO hace: no resuelve la cuenta desde la sesión ni el JWT.
Recibe `id_cuenta` ya determinado; conectarlo con `obtener_contexto()` sobre
la cookie de sesión es `AUTH-A6` (`BK-09`), que construye sobre esto.

La comprobación de que un recurso concreto pertenece al actor no es de este
módulo (`SEC-AUTZ-06`): `auth` no conoce la propiedad de entidades ajenas.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.errors import NoAutorizado

logger = logging.getLogger("reservas.authz")

Rol = Literal["USUARIO", "TECNICO", "ADMINISTRADOR"]

_CUENTA_PERSONAL_ACTIVA = """
    SELECT per.id_cargo
    FROM auth.cuentas c
    JOIN personal.personal per ON per.id_persona = c.id_persona
    WHERE c.id_cuenta = :id_cuenta
      AND c.estado IS TRUE
      AND c.tipo_cuenta = 'PERSONAL'
      AND per.estado IS TRUE
"""

_ES_ADMINISTRADOR_GLOBAL = """
    SELECT EXISTS (
        SELECT 1
        FROM auth.cuenta_permisos cp
        JOIN auth.permisos p ON p.id = cp.permiso_id
        WHERE cp.id_cuenta = :id_cuenta
          AND cp.id_unidad IS NULL
          AND p.habilitado IS TRUE
    )
"""

_UNIDAD_VIGENTE_DEL_CARGO = """
    SELECT id_unidad FROM cargos.cargo WHERE id_cargo = :id_cargo
"""

_TIENE_PERMISO_GLOBAL = """
    SELECT EXISTS (
        SELECT 1
        FROM auth.cuenta_permisos cp
        JOIN auth.permisos p ON p.id = cp.permiso_id
        WHERE cp.id_cuenta = :id_cuenta
          AND cp.id_unidad IS NULL
          AND p.codigo = :codigo
          AND p.habilitado IS TRUE
    )
"""

_TIENE_PERMISO_EN_UNIDAD = """
    SELECT EXISTS (
        SELECT 1
        FROM auth.cuenta_permisos cp
        JOIN auth.permisos p ON p.id = cp.permiso_id
        WHERE cp.id_cuenta = :id_cuenta
          AND cp.id_unidad = :id_unidad
          AND p.codigo = :codigo
          AND p.habilitado IS TRUE
    )
"""

_TIENE_ALGUN_PERMISO_EN_UNIDAD = """
    SELECT EXISTS (
        SELECT 1 FROM auth.cuenta_permisos cp
        JOIN auth.permisos p ON p.id = cp.permiso_id
        WHERE cp.id_cuenta = :id_cuenta
          AND cp.id_unidad = :id_unidad
          AND p.habilitado IS TRUE
    )
"""


@dataclass
class ContextoAutorizacion:
    rol: Rol
    unidades_autorizadas: list[int] | Literal["GLOBAL"]


def resolver_rol(sesion: Session, id_cuenta: int) -> ContextoAutorizacion:
    """Deriva el rol y las unidades autorizadas con datos vigentes.

    Una cuenta `USUARIO`, una `PERSONAL` inactiva o sin ficha activa, o
    cualquier condición que no pueda comprobarse resuelve `USUARIO` sin
    unidades: es el rol sin privilegios, nunca una excepción no controlada.
    """
    try:
        fila = sesion.execute(text(_CUENTA_PERSONAL_ACTIVA), {"id_cuenta": id_cuenta}).first()
        if fila is None:
            # Cuenta USUARIO, inactiva, o PERSONAL sin ficha activa vinculada.
            return ContextoAutorizacion(rol="USUARIO", unidades_autorizadas=[])

        es_admin = sesion.execute(text(_ES_ADMINISTRADOR_GLOBAL), {"id_cuenta": id_cuenta}).scalar()
        if es_admin:
            return ContextoAutorizacion(rol="ADMINISTRADOR", unidades_autorizadas="GLOBAL")

        id_cargo = fila.id_cargo
        unidad_vigente = sesion.execute(
            text(_UNIDAD_VIGENTE_DEL_CARGO), {"id_cargo": id_cargo}
        ).scalar()
        if unidad_vigente is None:
            return ContextoAutorizacion(rol="USUARIO", unidades_autorizadas=[])

        tiene_algun_permiso = sesion.execute(
            text(_TIENE_ALGUN_PERMISO_EN_UNIDAD),
            {"id_cuenta": id_cuenta, "id_unidad": unidad_vigente},
        ).scalar()
        if tiene_algun_permiso:
            return ContextoAutorizacion(rol="TECNICO", unidades_autorizadas=[unidad_vigente])

        return ContextoAutorizacion(rol="USUARIO", unidades_autorizadas=[])
    except Exception:
        # SEC-AUTZ-02: ante imposibilidad de comprobar, se deniega. No se
        # propaga como 500: un fallo de la consulta no es un error de negocio.
        logger.exception("No se pudo resolver el rol de la cuenta %s", id_cuenta)
        return ContextoAutorizacion(rol="USUARIO", unidades_autorizadas=[])


def exigir_permiso(sesion: Session, id_cuenta: int, codigo: str, id_unidad: int | None = None) -> None:
    """Evalúa `codigo` sobre `id_unidad` con información vigente (RN-AUTH-ROL-05).

    Deniega con `403 NO_AUTORIZADO` si el permiso no aplica, si el ámbito no
    coincide o si no puede comprobarse. Nunca amplía el ámbito de un Técnico
    a partir de asignaciones que no correspondan a su unidad vigente.
    """
    try:
        contexto = resolver_rol(sesion, id_cuenta)

        if contexto.rol == "ADMINISTRADOR":
            tiene = sesion.execute(
                text(_TIENE_PERMISO_GLOBAL), {"id_cuenta": id_cuenta, "codigo": codigo}
            ).scalar()
            if tiene:
                return
            raise NoAutorizado(f"La cuenta no tiene el permiso '{codigo}'.")

        if contexto.rol == "TECNICO":
            unidad_vigente = contexto.unidades_autorizadas[0]
            if id_unidad is not None and id_unidad != unidad_vigente:
                # Fuera de ámbito: ni se comprueba el permiso en la unidad ajena.
                raise NoAutorizado("La operación está fuera de la unidad autorizada.")
            tiene = sesion.execute(
                text(_TIENE_PERMISO_EN_UNIDAD),
                {"id_cuenta": id_cuenta, "id_unidad": unidad_vigente, "codigo": codigo},
            ).scalar()
            if tiene:
                return
            raise NoAutorizado(f"La cuenta no tiene el permiso '{codigo}' en su unidad.")

        raise NoAutorizado(f"La cuenta no tiene el permiso '{codigo}'.")
    except NoAutorizado:
        raise
    except Exception:
        logger.exception("No se pudo comprobar el permiso '%s' de la cuenta %s", codigo, id_cuenta)
        raise NoAutorizado("No fue posible comprobar el permiso.")
