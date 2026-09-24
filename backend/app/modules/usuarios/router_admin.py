"""Router administrativo de identidades (API-06 §5 y §6).

Todo exige `usuarios.administrar`, siempre global (contrato §1): los Técnicos
no administran identidades.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import ContextoAutenticado, exigir_permiso_dep
from app.core.errors import NoEncontrado, SolicitudInvalida
from app.core.pagination import envolver_listado, paginacion_para
from app.core.security import exigir_csrf
from app.db.session import get_db
from app.modules.usuarios import schemas, service

_PERMISO = exigir_permiso_dep("usuarios.administrar")
_PAG_USUARIOS = paginacion_para(
    filtros_admitidos=frozenset({"estado", "busqueda"}),
    ordenes_admitidos=frozenset({"nombre", "correo", "documento"}),
)
_PAG_PERSONAL = paginacion_para(
    filtros_admitidos=frozenset({"estado", "id_unidad", "busqueda"}),
    ordenes_admitidos=frozenset({"nombre", "correo", "documento"}),
)

router_usuarios = APIRouter(prefix="/api/usuarios", tags=["usuarios"])
router_personal = APIRouter(prefix="/api/personal", tags=["personal"])


def _estado(raw: str | None) -> bool | None:
    if raw is None:
        return None
    if raw == "true":
        return True
    if raw == "false":
        return False
    raise SolicitudInvalida("'estado' debe ser 'true' o 'false'.")


# --- §5 Identidades de Usuario --------------------------------------------------


@router_usuarios.post("", status_code=201, response_model=schemas.UsuarioRespuesta)
def crear_usuario(
    cuerpo: schemas.UsuarioCrear,
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.UsuarioRespuesta:
    """§5.1. Paso previo a invitar la cuenta (RN-USR-06 de administration)."""
    return schemas.UsuarioRespuesta(**service.crear_usuario_admin(db, cuerpo))


@router_usuarios.get("", response_model=dict)
def listar_usuarios(
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
    paginacion=Depends(_PAG_USUARIOS),
    estado: str | None = None,
    busqueda: str | None = None,
) -> dict:
    """§5.2. Filtros: estado, busqueda sobre nombre, documento y correo."""
    datos, total = service.listar_usuarios(
        db, estado=_estado(estado), busqueda=busqueda, paginacion=paginacion
    )
    return envolver_listado(
        [schemas.UsuarioRespuesta(**d).model_dump(mode="json") for d in datos],
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
        total=total,
    )


@router_usuarios.get("/{id_usuario}", response_model=schemas.UsuarioRespuesta)
def detalle_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
) -> schemas.UsuarioRespuesta:
    """§5.2."""
    return schemas.UsuarioRespuesta(**service.detalle_usuario(db, id_usuario))


@router_usuarios.patch("/{id_usuario}", response_model=schemas.UsuarioRespuesta)
def editar_usuario(
    id_usuario: int,
    cuerpo: schemas.UsuarioActualizar,
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.UsuarioRespuesta:
    """§5.3. Con cuenta asociada el correo es inmutable → 409."""
    return schemas.UsuarioRespuesta(**service.actualizar_usuario(db, id_usuario, cuerpo))


@router_usuarios.patch("/{id_usuario}/estado", response_model=schemas.UsuarioRespuesta)
def estado_usuario(
    id_usuario: int,
    cuerpo: schemas.EstadoSolicitud,
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.UsuarioRespuesta:
    """§5.4. Baja lógica; el historial se conserva (RN-USR-03 de administration)."""
    return schemas.UsuarioRespuesta(**service.cambiar_estado_usuario(db, id_usuario, cuerpo.estado))


# --- §6 Fichas de Personal --------------------------------------------------------


@router_personal.post("", status_code=201, response_model=schemas.PersonalRespuesta)
def crear_personal(
    cuerpo: schemas.PersonalCrear,
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.PersonalRespuesta:
    """§6.1. La ficha nace activa; la cuenta se invita después desde auth."""
    return schemas.PersonalRespuesta(**service.crear_ficha(db, cuerpo))


@router_personal.get("", response_model=dict)
def listar_personal(
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
    paginacion=Depends(_PAG_PERSONAL),
    estado: str | None = None,
    id_unidad: int | None = None,
    busqueda: str | None = None,
) -> dict:
    """§6.2. Filtros: estado, id_unidad, busqueda sobre nombre, documento y correo."""
    datos, total = service.listar_personal(
        db, estado=_estado(estado), id_unidad=id_unidad, busqueda=busqueda, paginacion=paginacion
    )
    return envolver_listado(
        [schemas.PersonalRespuesta(**d).model_dump(mode="json") for d in datos],
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
        total=total,
    )


@router_personal.get("/{id_persona}", response_model=schemas.PersonalRespuesta)
def detalle_personal(
    id_persona: int,
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
) -> schemas.PersonalRespuesta:
    """§6.2. Incluye el cargo y la unidad que de él se deriva."""
    return schemas.PersonalRespuesta(**service.detalle_ficha(db, id_persona))


@router_personal.patch("/{id_persona}", response_model=schemas.PersonalRespuesta)
def editar_personal(
    id_persona: int,
    cuerpo: schemas.PersonalActualizar,
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.PersonalRespuesta:
    """§6.3. Con cuenta asociada el correo es inmutable → 409."""
    return schemas.PersonalRespuesta(**service.actualizar_ficha(db, id_persona, cuerpo))


@router_personal.patch("/{id_persona}/estado", response_model=schemas.PersonalRespuesta)
def estado_personal(
    id_persona: int,
    cuerpo: schemas.EstadoSolicitud,
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.PersonalRespuesta:
    """§6.4. Desactivar al último administrador global → 409."""
    return schemas.PersonalRespuesta(**service.cambiar_estado_ficha(db, id_persona, cuerpo.estado))
