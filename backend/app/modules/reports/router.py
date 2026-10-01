"""Router de reports (API-19): `/api/reportes`. Todo es solo lectura."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.deps import ContextoAutenticado, obtener_contexto
from app.core.errors import SolicitudInvalida
from app.core.pagination import envolver_listado, paginacion_para
from app.db.session import get_db
from app.modules.reports import schemas, service

router = APIRouter(prefix="/api/reportes", tags=["reportes"])

_FILTROS = frozenset({"id_unidad", "espacio_id", "recurso_id", "proyecto_id", "semillero_id"})
_ORDENES = frozenset({"nombre"})
_TIPOS_EXPORTACION = frozenset({"ocupacion", "solicitudes", "lista-espera"})


def _entero(request: Request, nombre: str) -> int | None:
    v = request.query_params.get(nombre)
    if v is None:
        return None
    try:
        return int(v)
    except ValueError:
        raise SolicitudInvalida(f"'{nombre}' debe ser un entero.")


def _filtros(request: Request) -> dict:
    return {
        "id_unidad": _entero(request, "id_unidad"),
        "espacio_id": _entero(request, "espacio_id"),
        "recurso_id": _entero(request, "recurso_id"),
        "proyecto_id": _entero(request, "proyecto_id"),
        "semillero_id": _entero(request, "semillero_id"),
    }


def _periodo(request: Request) -> tuple[str | None, str | None]:
    return request.query_params.get("desde"), request.query_params.get("hasta")


@router.get("/ocupacion", response_model=schemas.ReporteRespuesta)
def ocupacion(
    request: Request,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    pag=Depends(paginacion_para(filtros_admitidos=_FILTROS | {"dimension", "desde", "hasta"}, ordenes_admitidos=_ORDENES)),
) -> schemas.ReporteRespuesta:
    """§3.1."""
    dimension = request.query_params.get("dimension", "laboratorio")
    desde, hasta = _periodo(request)
    resumen, datos, total = service.ocupacion(db, dimension, desde, hasta, _filtros(request), contexto, pagina=pag.pagina, tamano=pag.tamano)
    pagina = envolver_listado(datos, pagina=pag.pagina, tamano=pag.tamano, total=total)
    return schemas.ReporteRespuesta(resumen=resumen, **pagina)


@router.get("/solicitudes", response_model=schemas.ReporteRespuesta)
def solicitudes(
    request: Request,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    pag=Depends(paginacion_para(filtros_admitidos=_FILTROS | {"dimension", "desde", "hasta"}, ordenes_admitidos=_ORDENES)),
) -> schemas.ReporteRespuesta:
    """§3.2."""
    dimension = request.query_params.get("dimension", "laboratorio")
    desde, hasta = _periodo(request)
    resumen, datos, total = service.solicitudes(db, dimension, desde, hasta, _filtros(request), contexto, pagina=pag.pagina, tamano=pag.tamano)
    pagina = envolver_listado(datos, pagina=pag.pagina, tamano=pag.tamano, total=total)
    return schemas.ReporteRespuesta(resumen=resumen, **pagina)


@router.get("/lista-espera", response_model=schemas.ReporteRespuesta)
def lista_espera(
    request: Request,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    pag=Depends(paginacion_para(filtros_admitidos=_FILTROS | {"desde", "hasta"}, ordenes_admitidos=_ORDENES)),
) -> schemas.ReporteRespuesta:
    """§3.3. Sin dimension: siempre por unidad."""
    desde, hasta = _periodo(request)
    resumen, datos, total = service.lista_espera(db, desde, hasta, _filtros(request), contexto, pagina=pag.pagina, tamano=pag.tamano)
    pagina = envolver_listado(datos, pagina=pag.pagina, tamano=pag.tamano, total=total)
    return schemas.ReporteRespuesta(resumen=resumen, **pagina)


@router.get("/resumen", response_model=schemas.ResumenRespuesta)
def resumen(
    request: Request,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> schemas.ResumenRespuesta:
    """§3.4. Panel de inicio en una sola consulta; solo periodo e id_unidad."""
    desde, hasta = _periodo(request)
    return schemas.ResumenRespuesta(**service.resumen(db, desde, hasta, _filtros(request), contexto))


@router.get("/{tipo}/exportacion")
def exportar(
    tipo: str,
    request: Request,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> Response:
    """§4.1. Mismos parámetros que la consulta más `formato`; resultado completo."""
    if tipo not in _TIPOS_EXPORTACION:
        raise SolicitudInvalida("tipo debe ser 'ocupacion', 'solicitudes' o 'lista-espera'.")
    desde, hasta = _periodo(request)
    contenido, media_type, nombre = service.exportar(
        db, tipo, request.query_params.get("dimension"), desde, hasta,
        _filtros(request), request.query_params.get("formato", ""), contexto,
    )
    return Response(
        content=contenido, media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )
