"""Resolución de rol y autorización por rol y ámbito (BK-07, API-04).

Decisión 2026-09-30 (specs/docs/decisions/origen-externo-estructura-institucional.md):
los permisos **los define el rol**, no se otorgan a mano.

| Rol | Quién | Qué puede hacer |
|---|---|---|
| `USUARIO` | cuenta `USUARIO`, o cualquier cuenta que no cumpla lo de abajo | solo reservar |
| `TECNICO` | cuenta `PERSONAL` activa con ficha activa y un cargo con laboratorio | gestionar únicamente el laboratorio de su cargo |
| `ADMINISTRADOR` | cuenta `ADMINISTRADOR` activa (propia de Reservas, sin ficha en LIA) | todo |

Los permisos se siguen nombrando con códigos (`reservas.administrar`, ...) porque los endpoints los exigen
por nombre, pero el conjunto de cada rol está fijo en este módulo: `PERMISOS_DEL_TECNICO` para el técnico y
todos los habilitados del catálogo para el administrador. Se evalúan con información vigente en cada
operación, nunca desde el token (`SEC-JWT-04`, `RN-AUTH-ROL-05`).

Lo que este módulo NO hace: no resuelve la cuenta desde la sesión ni el JWT. Recibe `id_cuenta` ya
determinado; conectarlo con `obtener_contexto()` es `AUTH-A6` (`BK-09`).

La comprobación de que un recurso concreto pertenece al actor no es de este módulo (`SEC-AUTZ-06`):
`auth` no conoce la propiedad de entidades ajenas.
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

# Lo que el técnico puede hacer dentro del laboratorio de su cargo. Es el conjunto de ámbito «unidad» del
# catálogo: lo demás (unidades, cuentas, usuarios, importaciones, equipos y reasignaciones entre
# laboratorios) es solo del administrador.
PERMISOS_DEL_TECNICO = frozenset(
    {
        "reservas.administrar",
        "reservas.exportar",
        "espacios.administrar",
        "recursos.administrar",
        "recursos.editar_equipos",
        "laboratorios.configurar",
        "reportes.consultar",
    }
)

_CUENTA = """
    SELECT tipo_cuenta, estado, id_persona
    FROM auth.cuentas
    WHERE id_cuenta = :id_cuenta
"""

_LABORATORIO_DEL_CARGO_DE_LA_PERSONA = """
    SELECT car.id_unidad
    FROM personal.personal per
    JOIN cargos.cargo car ON car.id_cargo = per.id_cargo
    WHERE per.id_persona = :id_persona
      AND per.estado IS TRUE
"""

_PERMISO_HABILITADO = """
    SELECT EXISTS (
        SELECT 1 FROM auth.permisos p WHERE p.codigo = :codigo AND p.habilitado IS TRUE
    )
"""


@dataclass
class ContextoAutorizacion:
    rol: Rol
    unidades_autorizadas: list[int] | Literal["GLOBAL"]


def resolver_rol(sesion: Session, id_cuenta: int) -> ContextoAutorizacion:
    """Deriva el rol y las unidades autorizadas con datos vigentes.

    Una cuenta `USUARIO`, una inactiva, una `PERSONAL` sin ficha activa o sin laboratorio en su cargo, o
    cualquier condición que no pueda comprobarse resuelve `USUARIO` sin unidades: es el rol sin
    privilegios, nunca una excepción no controlada.
    """
    try:
        cuenta = sesion.execute(text(_CUENTA), {"id_cuenta": id_cuenta}).first()
        if cuenta is None or not cuenta.estado:
            return ContextoAutorizacion(rol="USUARIO", unidades_autorizadas=[])

        if cuenta.tipo_cuenta == "ADMINISTRADOR":
            return ContextoAutorizacion(rol="ADMINISTRADOR", unidades_autorizadas="GLOBAL")

        if cuenta.tipo_cuenta == "PERSONAL" and cuenta.id_persona is not None:
            laboratorio = sesion.execute(
                text(_LABORATORIO_DEL_CARGO_DE_LA_PERSONA), {"id_persona": cuenta.id_persona}
            ).scalar()
            if laboratorio is not None:
                return ContextoAutorizacion(rol="TECNICO", unidades_autorizadas=[laboratorio])

        return ContextoAutorizacion(rol="USUARIO", unidades_autorizadas=[])
    except Exception:
        # SEC-AUTZ-02: ante imposibilidad de comprobar, se deniega. No se
        # propaga como 500: un fallo de la consulta no es un error de negocio.
        logger.exception("No se pudo resolver el rol de la cuenta %s", id_cuenta)
        return ContextoAutorizacion(rol="USUARIO", unidades_autorizadas=[])


def exigir_permiso(sesion: Session, id_cuenta: int, codigo: str, id_unidad: int | None = None) -> None:
    """Evalúa `codigo` sobre `id_unidad` según el rol, con información vigente (RN-AUTH-ROL-05).

    Deniega con `403 NO_AUTORIZADO` si el rol no admite el permiso, si el ámbito no coincide o si no puede
    comprobarse. Un técnico nunca sale del laboratorio de su cargo vigente.
    """
    try:
        contexto = resolver_rol(sesion, id_cuenta)

        if contexto.rol == "USUARIO":
            raise NoAutorizado(f"La cuenta no tiene el permiso '{codigo}'.")

        habilitado = sesion.execute(text(_PERMISO_HABILITADO), {"codigo": codigo}).scalar()
        if not habilitado:
            raise NoAutorizado(f"La cuenta no tiene el permiso '{codigo}'.")

        if contexto.rol == "ADMINISTRADOR":
            return

        # TECNICO
        laboratorio_vigente = contexto.unidades_autorizadas[0]
        if id_unidad is not None and id_unidad != laboratorio_vigente:
            raise NoAutorizado("La operación está fuera de la unidad autorizada.")
        if codigo not in PERMISOS_DEL_TECNICO:
            raise NoAutorizado(f"La cuenta no tiene el permiso '{codigo}' en su unidad.")
    except NoAutorizado:
        raise
    except Exception:
        logger.exception("No se pudo comprobar el permiso '%s' de la cuenta %s", codigo, id_cuenta)
        raise NoAutorizado("No fue posible comprobar el permiso.")
