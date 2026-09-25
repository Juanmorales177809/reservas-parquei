"""Router de resources (API-09): `/api/recursos` y `/api/laboratorios`.

El permiso varía por tipo de recurso y por operación (contrato §1), así que
se resuelve dentro del servicio con `core.authz.exigir_permiso` y un
`id_unidad` que casi siempre depende del propio recurso — no con
`exigir_permiso_dep`, pensado solo para permisos globales fijos (ver
`core/deps.py`). El router solo exige sesión.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import ContextoAutenticado, obtener_contexto
from app.core.errors import SolicitudInvalida
from app.core.pagination import envolver_listado, paginacion_para
from app.core.security import exigir_csrf
from app.db.session import get_db
from app.modules.resources import schemas, service

router_recursos = APIRouter(prefix="/api/recursos", tags=["recursos"])
router_laboratorios = APIRouter(prefix="/api/laboratorios", tags=["laboratorios"])

_FILTROS = frozenset({"id_unidad", "tipo", "habilitado", "busqueda", "reservable"})
_ORDENES = frozenset({"nombre", "tipo"})


@router_recursos.post("", status_code=201, response_model=schemas.RecursoResumen)
def crear_recurso(
    cuerpo: schemas.RecursoCrear,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.RecursoResumen:
    """§2.1. Recurso y especialización se crean atómicamente."""
    return schemas.RecursoResumen(**service.crear_recurso(db, cuerpo, contexto))


@router_recursos.get("", response_model=dict)
def listar_recursos(
    request: Request,
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(obtener_contexto),
    pag=Depends(paginacion_para(filtros_admitidos=_FILTROS, ordenes_admitidos=_ORDENES)),
) -> dict:
    """§2.2. `reservable=true` excluye equipos acreditados (RN-REC-11)."""
    filtros = {
        "id_unidad": _entero(request, "id_unidad"),
        "tipo": request.query_params.get("tipo"),
        "habilitado": _booleano(request, "habilitado"),
        "busqueda": request.query_params.get("busqueda"),
        "reservable": _booleano(request, "reservable") or False,
    }
    datos, total = service.listar_recursos(db, filtros, pag.pagina, pag.tamano, pag.orden)
    return envolver_listado(datos, pagina=pag.pagina, tamano=pag.tamano, total=total)


def _entero(request: Request, nombre: str) -> int | None:
    v = request.query_params.get(nombre)
    if v is None:
        return None
    try:
        return int(v)
    except ValueError:
        raise SolicitudInvalida(f"'{nombre}' debe ser un entero.")


def _booleano(request: Request, nombre: str) -> bool | None:
    v = request.query_params.get(nombre)
    if v is None:
        return None
    if v.lower() in ("true", "1"):
        return True
    if v.lower() in ("false", "0"):
        return False
    raise SolicitudInvalida(f"'{nombre}' debe ser booleano.")


@router_recursos.get("/{id_recurso}", response_model=schemas.RecursoDetalle)
def detalle_recurso(
    id_recurso: int,
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> schemas.RecursoDetalle:
    """§2.3."""
    return schemas.RecursoDetalle(**service.obtener_recurso(db, id_recurso))


@router_recursos.patch("/{id_recurso}", response_model=schemas.RecursoDetalle)
def actualizar_recurso(
    id_recurso: int,
    cuerpo: schemas.RecursoActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.RecursoDetalle:
    """§2.4. `habilitado` se modifica por `/estado`, no aquí."""
    return schemas.RecursoDetalle(**service.actualizar_recurso(db, id_recurso, cuerpo, contexto))


@router_recursos.get("/{id_recurso}/impacto-deshabilitacion", response_model=schemas.ImpactoRespuesta)
def impacto_deshabilitacion(
    id_recurso: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> schemas.ImpactoRespuesta:
    """§2.6. Conteo previo, sin ejecutar nada."""
    return schemas.ImpactoRespuesta(**service.impacto_deshabilitacion(db, id_recurso, contexto))


@router_recursos.patch("/{id_recurso}/estado", response_model=schemas.EstadoRespuesta)
def cambiar_estado(
    id_recurso: int,
    cuerpo: schemas.EstadoActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.EstadoRespuesta:
    """§2.5. Deshabilitar con reservas `PRINCIPAL` futuras exige `confirmado`."""
    return schemas.EstadoRespuesta(**service.cambiar_estado(db, id_recurso, cuerpo, contexto))


@router_recursos.patch("/{id_recurso}/unidad", response_model=schemas.RecursoResumen)
def cambiar_unidad(
    id_recurso: int,
    cuerpo: schemas.UnidadActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.RecursoResumen:
    """§2.7. Requiere `recursos.reasignar_unidad`, siempre global."""
    return schemas.RecursoResumen(**service.cambiar_unidad(db, id_recurso, cuerpo, contexto))


@router_laboratorios.get("/{id_unidad}/configuracion", response_model=schemas.ConfiguracionRespuesta)
def obtener_configuracion(
    id_unidad: int,
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> schemas.ConfiguracionRespuesta:
    """§3.1. Lectura pública para cualquier cuenta autenticada (RN-DIS-07)."""
    return schemas.ConfiguracionRespuesta(**service.obtener_configuracion(db, id_unidad))


@router_laboratorios.patch("/{id_unidad}/configuracion", response_model=schemas.ConfiguracionRespuesta)
def actualizar_configuracion(
    id_unidad: int,
    cuerpo: schemas.ConfiguracionActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.ConfiguracionRespuesta:
    """§3.2. Cambiar el horario abre una nueva versión en el histórico (RN-LAB-08)."""
    return schemas.ConfiguracionRespuesta(**service.actualizar_configuracion(db, id_unidad, cuerpo, contexto))


@router_laboratorios.put("/{id_unidad}/tipos-reserva", response_model=dict)
def actualizar_tipos_reserva(
    id_unidad: int,
    cuerpo: schemas.TiposReservaActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> dict:
    """§3.3. Una lista vacía deja la unidad sin reservas posibles (RN-TIP-06)."""
    return service.actualizar_tipos_reserva(db, id_unidad, cuerpo, contexto)


@router_laboratorios.patch("/{id_unidad}/visibilidad", response_model=schemas.ConfiguracionRespuesta)
def actualizar_visibilidad(
    id_unidad: int,
    cuerpo: schemas.VisibilidadActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.ConfiguracionRespuesta:
    """§3.4. Ninguna opción puede ocultar el horario ni las franjas ocupadas (RN-DIS-07)."""
    return schemas.ConfiguracionRespuesta(**service.actualizar_visibilidad(db, id_unidad, cuerpo, contexto))
