"""Router administrativo de investigación (API-11): `/api/investigacion`.

Permiso siempre global (`usuarios.administrar`, contrato §1); se exige con
`exigir_permiso_dep` para todo el router, incluidas las lecturas, igual que
`auditoria` en `API-08`. Las vinculaciones propias de un Usuario bajo
`/api/perfil` viven en el módulo `usuarios`, no aquí (contrato §6).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.deps import ContextoAutenticado, exigir_permiso_dep
from app.core.errors import SolicitudInvalida
from app.core.pagination import envolver_listado, paginacion_para
from app.core.security import exigir_csrf
from app.db.session import get_db
from app.modules.researchs import schemas, service

router = APIRouter(prefix="/api/investigacion", tags=["investigacion"])

_PERMISO = exigir_permiso_dep("usuarios.administrar")
_PAG_CATALOGO = paginacion_para(filtros_admitidos=frozenset({"estado", "busqueda"}), ordenes_admitidos=frozenset({"codigo", "nombre"}))
_PAG_ACTIVIDADES = paginacion_para(filtros_admitidos=frozenset({"estado", "dependencia", "busqueda"}))
_PAG_PERFILES = paginacion_para(filtros_admitidos=frozenset({"habilitado"}))


def _booleano(request: Request, nombre: str) -> bool | None:
    v = request.query_params.get(nombre)
    if v is None:
        return None
    if v.lower() in ("true", "1"):
        return True
    if v.lower() in ("false", "0"):
        return False
    raise SolicitudInvalida(f"'{nombre}' debe ser booleano.")


# --- §2 Proyectos y semilleros ----------------------------------------------------


@router.get("/proyectos", response_model=dict)
def listar_proyectos(
    request: Request,
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(_PERMISO),
    pag=Depends(_PAG_CATALOGO),
) -> dict:
    """§2.1."""
    filtros = {"estado": _booleano(request, "estado"), "busqueda": request.query_params.get("busqueda")}
    datos, total = service.listar_proyectos(db, filtros, pag.pagina, pag.tamano, pag.orden)
    return envolver_listado(datos, pagina=pag.pagina, tamano=pag.tamano, total=total)


@router.get("/semilleros", response_model=dict)
def listar_semilleros(
    request: Request,
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(_PERMISO),
    pag=Depends(_PAG_CATALOGO),
) -> dict:
    """§2.1."""
    filtros = {"estado": _booleano(request, "estado"), "busqueda": request.query_params.get("busqueda")}
    datos, total = service.listar_semilleros(db, filtros, pag.pagina, pag.tamano, pag.orden)
    return envolver_listado(datos, pagina=pag.pagina, tamano=pag.tamano, total=total)


@router.patch("/proyectos/{id_proyecto}/estado", response_model=schemas.ProyectoResumen)
def cambiar_estado_proyecto(
    id_proyecto: int,
    cuerpo: schemas.EstadoActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.ProyectoResumen:
    """§2.2."""
    return schemas.ProyectoResumen(**service.cambiar_estado_proyecto(db, id_proyecto, cuerpo.estado, contexto))


@router.patch("/semilleros/{id_semillero}/estado", response_model=schemas.SemilleroResumen)
def cambiar_estado_semillero(
    id_semillero: int,
    cuerpo: schemas.EstadoActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.SemilleroResumen:
    """§2.2."""
    return schemas.SemilleroResumen(**service.cambiar_estado_semillero(db, id_semillero, cuerpo.estado, contexto))


# --- §3 Actividades institucionales -----------------------------------------------


@router.post("/actividades", status_code=201, response_model=schemas.ActividadResumen)
def crear_actividad(
    cuerpo: schemas.ActividadCrear,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.ActividadResumen:
    """§3.1. `nombre` y `dependencia` son obligatorios (RN-ACT-01)."""
    return schemas.ActividadResumen(**service.crear_actividad(db, cuerpo, contexto))


@router.get("/actividades", response_model=dict)
def listar_actividades(
    request: Request,
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(_PERMISO),
    pag=Depends(_PAG_ACTIVIDADES),
) -> dict:
    """§3.2."""
    filtros = {
        "estado": _booleano(request, "estado"),
        "dependencia": request.query_params.get("dependencia"),
        "busqueda": request.query_params.get("busqueda"),
    }
    datos, total = service.listar_actividades(db, filtros, pag.pagina, pag.tamano)
    return envolver_listado(datos, pagina=pag.pagina, tamano=pag.tamano, total=total)


@router.patch("/actividades/{id_actividad}", response_model=schemas.ActividadResumen)
def actualizar_actividad(
    id_actividad: int,
    cuerpo: schemas.ActividadActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.ActividadResumen:
    """§3.3. No altera las reservas que ya la usaron como contexto."""
    return schemas.ActividadResumen(**service.actualizar_actividad(db, id_actividad, cuerpo, contexto))


@router.patch("/actividades/{id_actividad}/estado", response_model=schemas.ActividadResumen)
def cambiar_estado_actividad(
    id_actividad: int,
    cuerpo: schemas.EstadoActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.ActividadResumen:
    """§3.4. Solo una actividad activa puede usarse en una reserva nueva (RN-ACT-02)."""
    return schemas.ActividadResumen(**service.cambiar_estado_actividad(db, id_actividad, cuerpo.estado, contexto))


# --- §4 Catálogo de perfiles ---------------------------------------------------------


@router.post("/perfiles", status_code=201, response_model=schemas.PerfilResumen)
def crear_perfil(
    cuerpo: schemas.PerfilCrear,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.PerfilResumen:
    """§4.1."""
    return schemas.PerfilResumen(**service.crear_perfil(db, cuerpo, contexto))


@router.get("/perfiles", response_model=dict)
def listar_perfiles(
    request: Request,
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(_PERMISO),
    pag=Depends(_PAG_PERFILES),
) -> dict:
    """§4.2. Incluye los deshabilitados."""
    filtros = {"habilitado": _booleano(request, "habilitado")}
    datos, total = service.listar_perfiles(db, filtros, pag.pagina, pag.tamano)
    return envolver_listado(datos, pagina=pag.pagina, tamano=pag.tamano, total=total)


@router.patch("/perfiles/{id_perfil}", response_model=schemas.PerfilResumen)
def actualizar_perfil(
    id_perfil: int,
    cuerpo: schemas.PerfilActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.PerfilResumen:
    """§4.3."""
    return schemas.PerfilResumen(**service.actualizar_perfil_catalogo(db, id_perfil, cuerpo, contexto))


@router.patch("/perfiles/{id_perfil}/estado", response_model=schemas.PerfilResumen)
def cambiar_estado_perfil(
    id_perfil: int,
    cuerpo: schemas.EstadoActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.PerfilResumen:
    """§4.3. Un perfil deshabilitado no se asigna en nuevas operaciones (RN-INV-14)."""
    return schemas.PerfilResumen(**service.cambiar_estado_perfil(db, id_perfil, cuerpo.estado, contexto))


# --- §5 Vinculaciones de terceros -------------------------------------------------


@router.get("/usuarios/{id_usuario}/vinculaciones", response_model=schemas.VinculacionesUsuario)
def vinculaciones_de_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(_PERMISO),
) -> schemas.VinculacionesUsuario:
    """§5.1. Activas e inactivas, agrupadas por tipo."""
    return schemas.VinculacionesUsuario(**service.vinculaciones_de_usuario(db, id_usuario))


@router.post("/usuarios/{id_usuario}/vinculaciones/{tipo}", status_code=201, response_model=dict)
def crear_vinculacion_ajena(
    id_usuario: int,
    tipo: str,
    cuerpo: schemas.VinculacionAjenaCrear,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> dict:
    """§5.2. `tipo` admite `proyectos` y `semilleros`; reactiva si ya existía inactiva."""
    return service.crear_vinculacion_ajena(db, id_usuario, tipo, cuerpo, contexto)


@router.delete("/usuarios/{id_usuario}/vinculaciones/{tipo}/{id_entidad}", status_code=204)
def desactivar_vinculacion_ajena(
    id_usuario: int,
    tipo: str,
    id_entidad: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> Response:
    """§5.3. `204` sin cuerpo. No borra el registro; conserva el historial (RN-INV-05)."""
    service.desactivar_vinculacion_ajena(db, id_usuario, tipo.replace("-", "_"), id_entidad, contexto)
    return Response(status_code=204)
