"""Router de espacios (API-10): `/api/espacios`.

El permiso administrativo es siempre `espacios.administrar` sobre la unidad
del espacio (contrato §1); se resuelve en el servicio con
`core.authz.exigir_permiso`, no con `exigir_permiso_dep`, porque casi toda
operación depende de la unidad del propio espacio. El listado (§2.3) además
varía por rol (RN visibilidad del contrato), así que el servicio recibe el
contexto completo, no solo exige sesión.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.deps import ContextoAutenticado, obtener_contexto
from app.core.errors import SolicitudInvalida
from app.core.pagination import envolver_listado, paginacion_para
from app.core.security import exigir_csrf
from app.db.session import get_db
from app.modules.espacios import schemas, service

router = APIRouter(prefix="/api/espacios", tags=["espacios"])

_FILTROS = frozenset({"id_unidad", "habilitado", "capacidad_minima"})
_ORDENES = frozenset({"nombre", "capacidad"})


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


# --- §2 Espacios ------------------------------------------------------------------


@router.post("", status_code=201, response_model=schemas.EspacioDetalle)
def crear_espacio(
    cuerpo: schemas.EspacioCrear,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.EspacioDetalle:
    """§2.1. Recursos y campos son opcionales; se crean atómicamente con el espacio."""
    return schemas.EspacioDetalle(**service.crear_espacio(db, cuerpo, contexto))


@router.patch("/{id_espacio}", response_model=schemas.EspacioDetalle)
def actualizar_espacio(
    id_espacio: int,
    cuerpo: schemas.EspacioActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.EspacioDetalle:
    """§2.2. No altera reservas históricas."""
    return schemas.EspacioDetalle(**service.actualizar_espacio(db, id_espacio, cuerpo, contexto))


@router.get("", response_model=dict)
def listar_espacios(
    request: Request,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    pag=Depends(paginacion_para(filtros_admitidos=_FILTROS, ordenes_admitidos=_ORDENES)),
) -> dict:
    """§2.3. Un Usuario solo ve espacios habilitados; un Técnico ve también los deshabilitados de su unidad."""
    filtros = {
        "id_unidad": _entero(request, "id_unidad"),
        "habilitado": _booleano(request, "habilitado"),
        "capacidad_minima": _entero(request, "capacidad_minima"),
    }
    datos, total = service.listar_espacios(db, filtros, pag.pagina, pag.tamano, pag.orden, contexto)
    return envolver_listado(datos, pagina=pag.pagina, tamano=pag.tamano, total=total)


@router.get("/{id_espacio}", response_model=schemas.EspacioDetalle)
def detalle_espacio(
    id_espacio: int,
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> schemas.EspacioDetalle:
    """§2.4. `horario_unidad` es una lectura de la configuración de la unidad, no un atributo propio."""
    return schemas.EspacioDetalle(**service.obtener_espacio(db, id_espacio))


@router.get("/{id_espacio}/impacto-deshabilitacion", response_model=schemas.ImpactoRespuesta)
def impacto_deshabilitacion(
    id_espacio: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> schemas.ImpactoRespuesta:
    """§2.6. Conteo previo, sin ejecutar nada."""
    return schemas.ImpactoRespuesta(**service.impacto_deshabilitacion(db, id_espacio, contexto))


@router.patch("/{id_espacio}/estado", response_model=schemas.EstadoRespuesta)
def cambiar_estado(
    id_espacio: int,
    cuerpo: schemas.EstadoActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.EstadoRespuesta:
    """§2.5. Deshabilitar con reservas futuras exige `confirmado` (RN-ESP-HAB-05)."""
    return schemas.EstadoRespuesta(**service.cambiar_estado(db, id_espacio, cuerpo, contexto))


# --- §3 Recursos asociados ----------------------------------------------------------


@router.post("/{id_espacio}/recursos", status_code=201, response_model=dict)
def asociar_recursos(
    id_espacio: int,
    cuerpo: schemas.RecursosAsociar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> dict:
    """§3.1. Cada recurso debe ser de la misma unidad y no tener otra asociación activa."""
    return service.asociar_recursos(db, id_espacio, cuerpo, contexto)


@router.delete("/{id_espacio}/recursos/{recurso_id}", status_code=204)
def retirar_recurso(
    id_espacio: int,
    recurso_id: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> Response:
    """§3.2. Deshabilita la fila; no la borra (conserva el historial)."""
    service.retirar_recurso(db, id_espacio, recurso_id, contexto)
    return Response(status_code=204)


# --- §4 Campos adicionales -----------------------------------------------------------


@router.post("/{id_espacio}/campos", status_code=201, response_model=schemas.EspacioCampoDetalle)
def crear_campo(
    id_espacio: int,
    cuerpo: schemas.EspacioCampoCrear,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.EspacioCampoDetalle:
    """§4.1. `SELECCION` sin ninguna opción responde `409 CAMPO_SIN_OPCIONES`."""
    return schemas.EspacioCampoDetalle(**service.crear_campo(db, id_espacio, cuerpo, contexto))


@router.patch("/{id_espacio}/campos/{campo_id}", response_model=schemas.EspacioCampoDetalle)
def actualizar_campo(
    id_espacio: int,
    campo_id: int,
    cuerpo: schemas.CampoActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.EspacioCampoDetalle:
    """§4.2. El tipo no se edita: cambiarlo rompería la interpretación histórica (RN-ESP-CAM-05)."""
    return schemas.EspacioCampoDetalle(**service.actualizar_campo(db, id_espacio, campo_id, cuerpo, contexto))


@router.patch("/{id_espacio}/campos/{campo_id}/estado", response_model=schemas.EspacioCampoDetalle)
def cambiar_estado_campo(
    id_espacio: int,
    campo_id: int,
    cuerpo: schemas.CampoEstadoActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.EspacioCampoDetalle:
    """§4.3. Un campo usado en reservas nunca se elimina, solo se deshabilita."""
    return schemas.EspacioCampoDetalle(**service.cambiar_estado_campo(db, id_espacio, campo_id, cuerpo, contexto))


@router.put("/{id_espacio}/campos/orden", response_model=dict)
def reordenar_campos(
    id_espacio: int,
    cuerpo: schemas.OrdenActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> dict:
    """§4.4. No modifica los valores históricos de reservas anteriores."""
    return {"datos": [schemas.EspacioCampoDetalle(**c) for c in service.reordenar_campos(db, id_espacio, cuerpo, contexto)]}


@router.post("/{id_espacio}/campos/{campo_id}/opciones", status_code=201, response_model=schemas.EspacioCampoDetalle)
def crear_opciones(
    id_espacio: int,
    campo_id: int,
    cuerpo: schemas.OpcionesCrear,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.EspacioCampoDetalle:
    """§4.5. Solo un campo `SELECCION` admite opciones."""
    return schemas.EspacioCampoDetalle(**service.crear_opciones(db, id_espacio, campo_id, cuerpo, contexto))


@router.patch("/{id_espacio}/campos/{campo_id}/opciones/{opcion_id}", response_model=schemas.EspacioCampoOpcion)
def actualizar_opcion(
    id_espacio: int,
    campo_id: int,
    opcion_id: int,
    cuerpo: schemas.OpcionActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.EspacioCampoOpcion:
    """§4.6. Una opción usada en una reserva se deshabilita, nunca se borra."""
    return schemas.EspacioCampoOpcion(**service.actualizar_opcion(db, id_espacio, campo_id, opcion_id, cuerpo, contexto))
