"""Router de estructura institucional (API-07 §2).

Todo exige `unidades.administrar` global: un Técnico no la ejerce.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import ContextoAutenticado, exigir_permiso_dep
from app.core.errors import SolicitudInvalida
from app.core.pagination import envolver_listado, paginacion_para
from app.core.security import exigir_csrf
from app.db.session import get_db
from app.modules.administration import schemas, service

_PERMISO = exigir_permiso_dep("unidades.administrar")
_PAG_UNIDADES = paginacion_para(
    filtros_admitidos=frozenset({"estado", "tipo", "id_unidad_padre", "busqueda"}),
    ordenes_admitidos=frozenset({"nombre", "tipo"}),
)
_PAG_CARGOS = paginacion_para(
    filtros_admitidos=frozenset({"id_unidad"}),
    ordenes_admitidos=frozenset({"nombre_cargo"}),
)

router_unidades = APIRouter(prefix="/api/unidades", tags=["unidades"])
router_cargos = APIRouter(prefix="/api/cargos", tags=["cargos"])


def _estado(raw: str | None) -> bool | None:
    if raw is None:
        return None
    if raw == "true":
        return True
    if raw == "false":
        return False
    raise SolicitudInvalida("'estado' debe ser 'true' o 'false'.")


@router_unidades.post("", status_code=201, response_model=schemas.UnidadRespuesta)
def crear_unidad(
    cuerpo: schemas.UnidadCrear,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.UnidadRespuesta:
    """§2.1. Nombre duplicado → 409; padre inexistente → 404."""
    return schemas.UnidadRespuesta(**service.crear_unidad(db, cuerpo, contexto))


@router_unidades.get("", response_model=dict)
def listar_unidades(
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
    paginacion=Depends(_PAG_UNIDADES),
    estado: str | None = None,
    tipo: str | None = None,
    id_unidad_padre: int | None = None,
    busqueda: str | None = None,
) -> dict:
    """§2.2."""
    datos, total = service.listar_unidades(
        db, estado=_estado(estado), tipo=tipo, id_unidad_padre=id_unidad_padre,
        busqueda=busqueda, paginacion=paginacion,
    )
    return envolver_listado(
        [schemas.UnidadRespuesta(**d).model_dump(mode="json") for d in datos],
        pagina=paginacion.pagina, tamano=paginacion.tamano, total=total,
    )


@router_unidades.get("/{id_unidad}", response_model=schemas.UnidadRespuesta)
def detalle_unidad(
    id_unidad: int,
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
) -> schemas.UnidadRespuesta:
    """§2.2."""
    return schemas.UnidadRespuesta(**service.detalle_unidad(db, id_unidad))


@router_unidades.patch("/{id_unidad}", response_model=schemas.UnidadRespuesta)
def editar_unidad(
    id_unidad: int,
    cuerpo: schemas.UnidadActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.UnidadRespuesta:
    """§2.3. El nombre cambia, la identidad interna no (RN-UNI-03). Ciclo → 409."""
    return schemas.UnidadRespuesta(**service.actualizar_unidad(db, id_unidad, cuerpo, contexto))


@router_unidades.patch("/{id_unidad}/estado", response_model=schemas.UnidadRespuesta)
def estado_unidad(
    id_unidad: int,
    cuerpo: schemas.EstadoSolicitud,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.UnidadRespuesta:
    """§2.4. Baja lógica pura: no elimina ni propaga (RN-UNI-04, RN-HAB-05)."""
    return schemas.UnidadRespuesta(**service.cambiar_estado_unidad(db, id_unidad, cuerpo.estado, contexto))


@router_cargos.post("", status_code=201, response_model=schemas.CargoRespuesta)
def crear_cargo(
    cuerpo: schemas.CargoCrear,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.CargoRespuesta:
    """§2.5. Unidad inexistente → 404; deshabilitada → 422."""
    return schemas.CargoRespuesta(**service.crear_cargo(db, cuerpo, contexto))


@router_cargos.get("", response_model=dict)
def listar_cargos(
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
    paginacion=Depends(_PAG_CARGOS),
    id_unidad: int | None = None,
) -> dict:
    """§2.6."""
    datos, total = service.listar_cargos(db, id_unidad=id_unidad, paginacion=paginacion)
    return envolver_listado(
        [schemas.CargoRespuesta(**d).model_dump(mode="json") for d in datos],
        pagina=paginacion.pagina, tamano=paginacion.tamano, total=total,
    )


@router_cargos.patch("/{id_cargo}", response_model=schemas.CargoRespuesta)
def editar_cargo(
    id_cargo: int,
    cuerpo: schemas.CargoActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.CargoRespuesta:
    """§2.6. Cambiar la unidad mueve el ámbito del personal (RN-PER-09)."""
    return schemas.CargoRespuesta(**service.actualizar_cargo(db, id_cargo, cuerpo, contexto))
