"""Acceso a datos de investigación: catálogos, actividades, perfiles y
vinculaciones (API-11).

Las funciones de vinculación (`_ENTIDAD`/`_VINCULACION` y las que operan
sobre ellas) son de propósito general a propósito: las usa tanto el router
administrativo de este módulo (`/api/investigacion`, sobre un `id_usuario`
ajeno) como el módulo `usuarios` (`/api/perfil`, sobre la propia sesión).
Ninguna de las dos valida permisos aquí — eso es responsabilidad de cada
servicio llamador, que además difiere en qué código de error usa para el
mismo conflicto (`CONFLICTO` genérico en researchs, `VINCULACION_DUPLICADA`
propio de usuarios), por lo que esa validación no se centraliza tampoco.
"""

from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models.investigacion import (
    ActividadesInstitucionales,
    Pasantias,
    Perfiles,
    Proyectos,
    Semilleros,
    TrabajosGrado,
    UsuarioPasantias,
    UsuarioPerfiles,
    UsuarioProyectos,
    UsuarioSemilleros,
    UsuarioTrabajosGrado,
)

_ENTIDAD = {
    "proyectos": (Proyectos, "id_proyecto"),
    "semilleros": (Semilleros, "id_semillero"),
    "pasantias": (Pasantias, "id_pasantia"),
    "trabajos_grado": (TrabajosGrado, "id_trabajo_grado"),
}
_VINCULACION = {
    "proyectos": (UsuarioProyectos, "id_proyecto"),
    "semilleros": (UsuarioSemilleros, "id_semillero"),
    "pasantias": (UsuarioPasantias, "id_pasantia"),
    "trabajos_grado": (UsuarioTrabajosGrado, "id_trabajo_grado"),
}


# --- Proyectos y semilleros (§2) --------------------------------------------------


def obtener_proyecto(db: Session, id_proyecto: int) -> Proyectos | None:
    return db.get(Proyectos, id_proyecto)


def obtener_semillero(db: Session, id_semillero: int) -> Semilleros | None:
    return db.get(Semilleros, id_semillero)


def obtener_proyecto_por_codigo(db: Session, codigo: str) -> Proyectos | None:
    """Idempotencia de la importación masiva por código normalizado (API-12, RN-IMP-04 de administration)."""
    return db.scalar(select(Proyectos).where(Proyectos.codigo == codigo))


def obtener_semillero_por_codigo(db: Session, codigo: str) -> Semilleros | None:
    return db.scalar(select(Semilleros).where(Semilleros.codigo == codigo))


def crear_proyecto(db: Session, codigo: str, nombre: str, estado: bool) -> Proyectos:
    proyecto = Proyectos(codigo=codigo, nombre=nombre, estado=estado)
    db.add(proyecto)
    db.flush()
    return proyecto


def crear_semillero(db: Session, codigo: str, nombre: str, estado: bool) -> Semilleros:
    semillero = Semilleros(codigo=codigo, nombre=nombre, estado=estado)
    db.add(semillero)
    db.flush()
    return semillero


def _listar_catalogo(db: Session, modelo, campo_codigo, campo_nombre, *, estado, busqueda, orden, offset, tamano):
    stmt = select(modelo)
    if estado is not None:
        stmt = stmt.where(modelo.estado.is_(estado))
    if busqueda:
        patron = f"%{busqueda}%"
        stmt = stmt.where(or_(campo_codigo.ilike(patron), campo_nombre.ilike(patron)))
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    if orden == "codigo":
        stmt = stmt.order_by(campo_codigo)
    elif orden == "-codigo":
        stmt = stmt.order_by(campo_codigo.desc())
    elif orden == "nombre":
        stmt = stmt.order_by(campo_nombre)
    elif orden == "-nombre":
        stmt = stmt.order_by(campo_nombre.desc())
    items = db.scalars(stmt.offset(offset).limit(tamano)).all()
    return items, total


def listar_proyectos(db: Session, *, estado, busqueda, orden, offset, tamano):
    return _listar_catalogo(db, Proyectos, Proyectos.codigo, Proyectos.nombre, estado=estado, busqueda=busqueda, orden=orden, offset=offset, tamano=tamano)


def listar_semilleros(db: Session, *, estado, busqueda, orden, offset, tamano):
    return _listar_catalogo(db, Semilleros, Semilleros.codigo, Semilleros.nombre, estado=estado, busqueda=busqueda, orden=orden, offset=offset, tamano=tamano)


def cambiar_estado_entidad(db: Session, entidad, estado: bool) -> None:
    entidad.estado = estado


# --- Actividades institucionales (§3) ---------------------------------------------


def crear_actividad(db: Session, nombre: str, dependencia: str) -> ActividadesInstitucionales:
    actividad = ActividadesInstitucionales(nombre=nombre, dependencia=dependencia, estado=True)
    db.add(actividad)
    db.flush()
    return actividad


def obtener_actividad(db: Session, id_actividad: int) -> ActividadesInstitucionales | None:
    return db.get(ActividadesInstitucionales, id_actividad)


def listar_actividades(db: Session, *, estado, dependencia, busqueda, offset, tamano):
    stmt = select(ActividadesInstitucionales)
    if estado is not None:
        stmt = stmt.where(ActividadesInstitucionales.estado.is_(estado))
    if dependencia:
        stmt = stmt.where(ActividadesInstitucionales.dependencia == dependencia)
    if busqueda:
        stmt = stmt.where(ActividadesInstitucionales.nombre.ilike(f"%{busqueda}%"))
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.scalars(stmt.order_by(ActividadesInstitucionales.id_actividad).offset(offset).limit(tamano)).all()
    return items, total


# --- Catálogo de perfiles (§4) ------------------------------------------------------


def crear_perfil(db: Session, nombre: str, descripcion: str | None) -> Perfiles:
    perfil = Perfiles(nombre=nombre, descripcion=descripcion, estado=True)
    db.add(perfil)
    db.flush()
    return perfil


def obtener_perfil_catalogo(db: Session, id_perfil: int) -> Perfiles | None:
    return db.get(Perfiles, id_perfil)


def listar_perfiles(db: Session, *, habilitado, offset, tamano):
    stmt = select(Perfiles)
    if habilitado is not None:
        stmt = stmt.where(Perfiles.estado.is_(habilitado))
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.scalars(stmt.order_by(Perfiles.id_perfil).offset(offset).limit(tamano)).all()
    return items, total


def perfiles_habilitados(db: Session) -> list[Perfiles]:
    return list(db.scalars(select(Perfiles).where(Perfiles.estado.is_(True)).order_by(Perfiles.nombre)).all())


# --- Perfiles asignados a un usuario (usuario_perfiles) -----------------------------


def perfiles_activos_de_usuario(db: Session, id_usuario: int) -> list[tuple[UsuarioPerfiles, Perfiles]]:
    stmt = (
        select(UsuarioPerfiles, Perfiles)
        .join(Perfiles, Perfiles.id_perfil == UsuarioPerfiles.id_perfil)
        .where(UsuarioPerfiles.id_usuario == id_usuario, UsuarioPerfiles.estado.is_(True))
    )
    return list(db.execute(stmt).all())


def obtener_asignacion_perfil(db: Session, id_usuario: int, id_perfil: int) -> UsuarioPerfiles | None:
    return db.get(UsuarioPerfiles, {"id_usuario": id_usuario, "id_perfil": id_perfil})


def asignar_perfil(db: Session, id_usuario: int, id_perfil: int) -> UsuarioPerfiles:
    fila = UsuarioPerfiles(id_usuario=id_usuario, id_perfil=id_perfil, estado=True)
    db.add(fila)
    db.flush()
    return fila


# --- Vinculaciones (genérico por tipo; §5, y usuarios §3/§4) -----------------------


def campo_fk_vinculacion(tipo: str) -> str:
    return _VINCULACION[tipo][1]


def obtener_entidad(db: Session, tipo: str, entidad_id: int):
    modelo, _ = _ENTIDAD[tipo]
    return db.get(modelo, entidad_id)


def obtener_vinculacion(db: Session, tipo: str, id_usuario: int, entidad_id: int):
    modelo, campo_fk = _VINCULACION[tipo]
    return db.scalar(select(modelo).where(modelo.id_usuario == id_usuario, getattr(modelo, campo_fk) == entidad_id))


def crear_vinculacion(db: Session, tipo: str, id_usuario: int, entidad_id: int):
    modelo, campo_fk = _VINCULACION[tipo]
    fila = modelo(id_usuario=id_usuario, estado=True, **{campo_fk: entidad_id})
    db.add(fila)
    db.flush()
    return fila


def reactivar_vinculacion(db: Session, vinculacion) -> None:
    vinculacion.estado = True


def desactivar_vinculacion_fila(db: Session, vinculacion) -> None:
    vinculacion.estado = False


def vinculaciones_usuario(db: Session, tipo: str, id_usuario: int) -> list:
    modelo, _ = _VINCULACION[tipo]
    return list(db.scalars(select(modelo).where(modelo.id_usuario == id_usuario)).all())


def tiene_vinculacion_activa(db: Session, id_usuario: int) -> bool:
    """RN-USR-07/RN-USR-11 de usuarios: ¿tiene al menos una vinculación
    activa de cualquiera de los cuatro tipos?"""
    for modelo, _ in _VINCULACION.values():
        existe = db.scalar(
            select(modelo.id_usuario).where(modelo.id_usuario == id_usuario, modelo.estado.is_(True)).limit(1)
        )
        if existe is not None:
            return True
    return False


# --- Pasantías y trabajos de grado: se crean junto con su vinculación (usuarios §4.4/4.5) --


def crear_pasantia(db: Session, universidad: str, docente_nombre: str, docente_correo: str) -> Pasantias:
    pasantia = Pasantias(universidad=universidad, docente_itm_nombre=docente_nombre, docente_itm_correo=docente_correo, estado=True)
    db.add(pasantia)
    db.flush()
    return pasantia


def crear_trabajo_grado(db: Session, director_nombre: str, director_correo: str) -> TrabajosGrado:
    trabajo = TrabajosGrado(director_nombre=director_nombre, director_correo=director_correo, estado=True)
    db.add(trabajo)
    db.flush()
    return trabajo
