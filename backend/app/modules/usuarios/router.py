"""Router de perfil propio (API-06 §2, y API-11 §3/§4 orquestados aquí).

Sin permiso administrativo: opera sobre la identidad de la sesión
(contrato de usuarios §1). Las vinculaciones y perfiles académicos
delegan la validación y persistencia en `researchs` a través de
`usuarios.service`, que llama directamente a `researchs.repository`; este
router no importa `researchs` (contrato: "este módulo orquesta").
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import ContextoAutenticado, obtener_contexto
from app.core.errors import SolicitudInvalida
from app.core.pagination import envolver_catalogo, envolver_listado, paginacion_para
from app.core.security import exigir_csrf
from app.db.session import get_db
from app.modules.usuarios import schemas, service

router = APIRouter(prefix="/api/perfil", tags=["perfil"])

_PAG_CATALOGO_VINCULACION = paginacion_para(filtros_admitidos=frozenset({"tipo", "busqueda"}))


@router.get("", response_model=schemas.PerfilRespuesta)
def leer_perfil(
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> schemas.PerfilRespuesta:
    """§2.1. El correo se devuelve como solo lectura. PERSONAL → 404."""
    return schemas.PerfilRespuesta(**service.obtener_perfil(db, contexto))


@router.patch("", response_model=schemas.PerfilRespuesta)
def editar_perfil(
    cuerpo: schemas.PerfilActualizar,
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.PerfilRespuesta:
    """§2.2. Cinco campos editables; el correo se rechaza con 409."""
    return schemas.PerfilRespuesta(**service.actualizar_perfil(db, contexto, cuerpo))


@router.post("/actualizacion-inicial", response_model=schemas.ActualizacionInicialRespuesta)
def confirmar_actualizacion_inicial(
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.ActualizacionInicialRespuesta:
    """§2.3 (RN-USR-07). Sin cuerpo: verifica datos completos y al menos una vinculación activa."""
    return schemas.ActualizacionInicialRespuesta(**service.confirmar_actualizacion_inicial(db, contexto))


# --- §3 Perfiles académicos e investigativos ----------------------------------------


@router.get("/perfiles/catalogo", response_model=dict)
def catalogo_perfiles(
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> dict:
    """§3.0. Catálogo cerrado: solo habilitados, sin paginación."""
    return envolver_catalogo(service.catalogo_perfiles(db))


@router.put("/perfiles", response_model=dict)
def actualizar_perfiles(
    cuerpo: schemas.PerfilesActualizar,
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> dict:
    """§3.1. Reemplaza el conjunto completo (UF-USR-05)."""
    return {"perfiles": service.reemplazar_perfiles(db, contexto, cuerpo.perfiles)}


# --- §4 Vinculaciones académicas e investigativas -----------------------------------


@router.get("/vinculaciones/catalogo", response_model=dict)
def catalogo_vinculacion(
    request: Request,
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(obtener_contexto),
    pag=Depends(_PAG_CATALOGO_VINCULACION),
) -> dict:
    """§4.1. `tipo` admite `proyectos` y `semilleros`."""
    tipo = request.query_params.get("tipo")
    if tipo not in ("proyectos", "semilleros"):
        raise SolicitudInvalida("'tipo' debe ser 'proyectos' o 'semilleros'.")
    datos, total = service.catalogo_vinculacion(db, tipo, request.query_params.get("busqueda"), pag.pagina, pag.tamano)
    return envolver_listado(datos, pagina=pag.pagina, tamano=pag.tamano, total=total)


@router.post("/vinculaciones/proyectos", status_code=201, response_model=dict)
def vincular_proyecto(
    cuerpo: schemas.ProyectoVincularBody,
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> dict:
    """§4.2 (UF-USR-06). Reactiva si existía inactiva."""
    return service.vincular_proyecto(db, contexto, cuerpo.id_proyecto)


@router.post("/vinculaciones/semilleros", status_code=201, response_model=dict)
def vincular_semillero(
    cuerpo: schemas.SemilleroVincularBody,
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> dict:
    """§4.3 (UF-USR-07). Reactiva si existía inactiva."""
    return service.vincular_semillero(db, contexto, cuerpo.id_semillero)


@router.post("/vinculaciones/pasantias", status_code=201, response_model=dict)
def registrar_pasantia(
    cuerpo: schemas.PasantiaCrear,
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> dict:
    """§4.4 (UF-USR-08). La pasantía se crea aquí, no es un catálogo administrado."""
    return service.registrar_pasantia(db, contexto, cuerpo)


@router.post("/vinculaciones/trabajos-grado", status_code=201, response_model=dict)
def registrar_trabajo_grado(
    cuerpo: schemas.TrabajoGradoCrear,
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> dict:
    """§4.5 (UF-USR-09)."""
    return service.registrar_trabajo_grado(db, contexto, cuerpo)


@router.delete("/vinculaciones/{tipo}/{id_entidad}", response_model=schemas.DesactivarVinculacionRespuesta)
def desactivar_vinculacion(
    tipo: str,
    id_entidad: int,
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.DesactivarVinculacionRespuesta:
    """§4.6 (UF-USR-10). `200`, no `204`: siempre trae `sin_vinculaciones_activas`."""
    return schemas.DesactivarVinculacionRespuesta(
        **service.desactivar_vinculacion_propia(db, contexto, tipo.replace("-", "_"), id_entidad)
    )
