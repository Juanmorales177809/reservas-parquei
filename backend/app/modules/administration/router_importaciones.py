"""Router de importaciones masivas (API-12, contrato §4).

Permiso siempre global (`importacion.ejecutar`), exigido para las cuatro
rutas, lecturas incluidas — la trazabilidad de una carga es tan
administrativa como la carga misma.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import ContextoAutenticado, exigir_permiso_dep
from app.core.errors import SolicitudInvalida
from app.core.pagination import envolver_listado, paginacion_para
from app.core.security import exigir_csrf
from app.db.session import get_db
from app.modules.administration import schemas
from app.modules.administration import service_importaciones as service

router = APIRouter(prefix="/api/importaciones", tags=["importaciones"])

_PERMISO = exigir_permiso_dep("importacion.ejecutar")
_PAG = paginacion_para(filtros_admitidos=frozenset({"catalogo", "desde", "hasta"}))


def _instante_o_400(raw: str | None, campo: str):
    if raw is None:
        return None
    from datetime import datetime

    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        raise SolicitudInvalida(f"'{campo}' debe ser una fecha ISO 8601.")


@router.post("", status_code=201, response_model=schemas.ImportacionValidacionRespuesta)
async def validar_importacion(
    archivo: UploadFile = File(...),
    catalogo: str = Form(...),
    id_unidad: int | None = Form(default=None),
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.ImportacionValidacionRespuesta:
    """§4.1. Carga y valida sin escribir catálogo alguno."""
    contenido = await archivo.read()
    resultado = service.validar_importacion(
        db, catalogo=catalogo, id_unidad=id_unidad,
        archivo_nombre=archivo.filename or "archivo.xlsx", archivo_bytes=contenido, contexto=contexto,
    )
    return schemas.ImportacionValidacionRespuesta(**resultado)


@router.post("/{id_importacion}/confirmacion", response_model=schemas.ImportacionResumen)
def confirmar_importacion(
    id_importacion: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.ImportacionResumen:
    """§4.2. Sin cuerpo. Escribe en el módulo propietario del catálogo."""
    return schemas.ImportacionResumen(**service.confirmar_importacion(db, id_importacion, contexto))


@router.get("", response_model=dict)
def listar_importaciones(
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(_PERMISO),
    pag=Depends(_PAG),
    catalogo: str | None = None,
    desde: str | None = None,
    hasta: str | None = None,
) -> dict:
    """§4.3."""
    datos, total = service.listar_importaciones(
        db, catalogo=catalogo, desde=_instante_o_400(desde, "desde"), hasta=_instante_o_400(hasta, "hasta"), paginacion=pag,
    )
    return envolver_listado(datos, pagina=pag.pagina, tamano=pag.tamano, total=total)


@router.get("/{id_importacion}", response_model=schemas.ImportacionDetalle)
def detalle_importacion(
    id_importacion: int,
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(_PERMISO),
) -> schemas.ImportacionDetalle:
    """§4.3. Con el resultado de cada fila."""
    return schemas.ImportacionDetalle(**service.detalle_importacion(db, id_importacion))
