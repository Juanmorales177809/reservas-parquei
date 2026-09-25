"""Lógica administrativa de investigación (API-11): catálogos de proyectos y
semilleros, actividades institucionales, catálogo de perfiles y
vinculaciones ajenas.

Dueño de `RN-INV` y `RN-ACT` (researchs). El permiso administrativo es
siempre `usuarios.administrar` global (contrato §1); lo exige el router con
`core.deps.exigir_permiso_dep`, así que este servicio no lo repite.

`vinculaciones_de_usuario` y las funciones de bajo nivel de
`repository.py` (`crear_vinculacion`, `desactivar_vinculacion_fila`, etc.)
son de propósito general: las reutiliza el módulo `usuarios` para las
vinculaciones propias bajo `/api/perfil`, con su propia validación y sus
propios códigos de error (`VINCULACION_DUPLICADA` en vez de `CONFLICTO`),
en vez de duplicar el acceso a datos.

Cada escritura audita en la misma transacción (patrón de `AUTH-C1`).
"""

from __future__ import annotations

from app.core import audit
from app.core.deps import ContextoAutenticado
from app.core.errors import Conflicto, NoEncontrado, Validacion
from app.modules.researchs import repository as repo
from app.modules.researchs import schemas

TIPOS_VINCULACION_AJENA_CREABLES = ("proyectos", "semilleros")
TIPOS_VINCULACION = ("proyectos", "semilleros", "pasantias", "trabajos_grado")


def _no_vacio(valor: str, campo: str) -> str:
    valor = valor.strip()
    if not valor:
        raise Validacion(f"{campo} no puede estar vacío.")
    return valor


# --- §2 Proyectos y semilleros ----------------------------------------------------


def _proyecto_dict(p) -> dict:
    return {"id_proyecto": p.id_proyecto, "codigo": p.codigo, "nombre": p.nombre, "estado": p.estado}


def _semillero_dict(s) -> dict:
    return {"id_semillero": s.id_semillero, "codigo": s.codigo, "nombre": s.nombre, "estado": s.estado}


def listar_proyectos(db, filtros: dict, pagina: int, tamano: int, orden: str | None) -> tuple[list[dict], int]:
    items, total = repo.listar_proyectos(
        db, estado=filtros.get("estado"), busqueda=filtros.get("busqueda"),
        orden=orden, offset=(pagina - 1) * tamano, tamano=tamano,
    )
    return [_proyecto_dict(p) for p in items], total


def listar_semilleros(db, filtros: dict, pagina: int, tamano: int, orden: str | None) -> tuple[list[dict], int]:
    items, total = repo.listar_semilleros(
        db, estado=filtros.get("estado"), busqueda=filtros.get("busqueda"),
        orden=orden, offset=(pagina - 1) * tamano, tamano=tamano,
    )
    return [_semillero_dict(s) for s in items], total


def cambiar_estado_proyecto(db, id_proyecto: int, estado: bool, contexto: ContextoAutenticado) -> dict:
    proyecto = repo.obtener_proyecto(db, id_proyecto)
    if proyecto is None:
        raise NoEncontrado()
    repo.cambiar_estado_entidad(db, proyecto, estado)
    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="investigacion.proyectos", entidad_id=id_proyecto,
        accion="CAMBIAR_ESTADO_PROYECTO", datos_nuevos={"estado": estado},
    )
    db.commit()
    db.refresh(proyecto)
    return _proyecto_dict(proyecto)


def cambiar_estado_semillero(db, id_semillero: int, estado: bool, contexto: ContextoAutenticado) -> dict:
    semillero = repo.obtener_semillero(db, id_semillero)
    if semillero is None:
        raise NoEncontrado()
    repo.cambiar_estado_entidad(db, semillero, estado)
    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="investigacion.semilleros", entidad_id=id_semillero,
        accion="CAMBIAR_ESTADO_SEMILLERO", datos_nuevos={"estado": estado},
    )
    db.commit()
    db.refresh(semillero)
    return _semillero_dict(semillero)


# --- §3 Actividades institucionales -----------------------------------------------


def _actividad_dict(a) -> dict:
    return {"id_actividad": a.id_actividad, "nombre": a.nombre, "dependencia": a.dependencia, "estado": a.estado}


def crear_actividad(db, datos: schemas.ActividadCrear, contexto: ContextoAutenticado) -> dict:
    nombre = _no_vacio(datos.nombre, "nombre")
    dependencia = _no_vacio(datos.dependencia, "dependencia")
    actividad = repo.crear_actividad(db, nombre, dependencia)
    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="investigacion.actividades_institucionales",
        entidad_id=actividad.id_actividad, accion="CREAR_ACTIVIDAD",
        datos_nuevos={"nombre": nombre, "dependencia": dependencia},
    )
    db.commit()
    db.refresh(actividad)
    return _actividad_dict(actividad)


def listar_actividades(db, filtros: dict, pagina: int, tamano: int) -> tuple[list[dict], int]:
    items, total = repo.listar_actividades(
        db, estado=filtros.get("estado"), dependencia=filtros.get("dependencia"), busqueda=filtros.get("busqueda"),
        offset=(pagina - 1) * tamano, tamano=tamano,
    )
    return [_actividad_dict(a) for a in items], total


def actualizar_actividad(db, id_actividad: int, datos: schemas.ActividadActualizar, contexto: ContextoAutenticado) -> dict:
    actividad = repo.obtener_actividad(db, id_actividad)
    if actividad is None:
        raise NoEncontrado()
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "nombre" in cambios:
        cambios["nombre"] = _no_vacio(cambios["nombre"], "nombre")
    if "dependencia" in cambios:
        cambios["dependencia"] = _no_vacio(cambios["dependencia"], "dependencia")
    for campo, valor in cambios.items():
        setattr(actividad, campo, valor)
    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="investigacion.actividades_institucionales",
        entidad_id=id_actividad, accion="EDITAR_ACTIVIDAD", datos_nuevos=cambios,
    )
    db.commit()
    db.refresh(actividad)
    return _actividad_dict(actividad)


def cambiar_estado_actividad(db, id_actividad: int, estado: bool, contexto: ContextoAutenticado) -> dict:
    actividad = repo.obtener_actividad(db, id_actividad)
    if actividad is None:
        raise NoEncontrado()
    repo.cambiar_estado_entidad(db, actividad, estado)
    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="investigacion.actividades_institucionales",
        entidad_id=id_actividad, accion="CAMBIAR_ESTADO_ACTIVIDAD", datos_nuevos={"estado": estado},
    )
    db.commit()
    db.refresh(actividad)
    return _actividad_dict(actividad)


# --- §4 Catálogo de perfiles ---------------------------------------------------------


def _perfil_dict(p) -> dict:
    return {"id_perfil": p.id_perfil, "nombre": p.nombre, "descripcion": p.descripcion, "estado": p.estado}


def crear_perfil(db, datos: schemas.PerfilCrear, contexto: ContextoAutenticado) -> dict:
    nombre = _no_vacio(datos.nombre, "nombre")
    perfil = repo.crear_perfil(db, nombre, datos.descripcion)
    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="investigacion.perfiles", entidad_id=perfil.id_perfil,
        accion="CREAR_PERFIL", datos_nuevos={"nombre": nombre},
    )
    db.commit()
    db.refresh(perfil)
    return _perfil_dict(perfil)


def listar_perfiles(db, filtros: dict, pagina: int, tamano: int) -> tuple[list[dict], int]:
    items, total = repo.listar_perfiles(db, habilitado=filtros.get("habilitado"), offset=(pagina - 1) * tamano, tamano=tamano)
    return [_perfil_dict(p) for p in items], total


def actualizar_perfil_catalogo(db, id_perfil: int, datos: schemas.PerfilActualizar, contexto: ContextoAutenticado) -> dict:
    perfil = repo.obtener_perfil_catalogo(db, id_perfil)
    if perfil is None:
        raise NoEncontrado()
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "nombre" in cambios:
        cambios["nombre"] = _no_vacio(cambios["nombre"], "nombre")
    for campo, valor in cambios.items():
        setattr(perfil, campo, valor)
    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="investigacion.perfiles", entidad_id=id_perfil,
        accion="EDITAR_PERFIL", datos_nuevos=cambios,
    )
    db.commit()
    db.refresh(perfil)
    return _perfil_dict(perfil)


def cambiar_estado_perfil(db, id_perfil: int, estado: bool, contexto: ContextoAutenticado) -> dict:
    perfil = repo.obtener_perfil_catalogo(db, id_perfil)
    if perfil is None:
        raise NoEncontrado()
    repo.cambiar_estado_entidad(db, perfil, estado)
    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="investigacion.perfiles", entidad_id=id_perfil,
        accion="CAMBIAR_ESTADO_PERFIL", datos_nuevos={"estado": estado},
    )
    db.commit()
    db.refresh(perfil)
    return _perfil_dict(perfil)


# --- §5 Vinculaciones de terceros (y compartido con usuarios) ----------------------


def vinculacion_dict(db, tipo: str, vinculacion) -> dict:
    campo_fk = repo.campo_fk_vinculacion(tipo)
    entidad_id = getattr(vinculacion, campo_fk)
    entidad = repo.obtener_entidad(db, tipo, entidad_id)
    base = {"activa": vinculacion.estado}
    if tipo == "proyectos":
        base |= {"id_proyecto": entidad.id_proyecto, "codigo": entidad.codigo, "nombre": entidad.nombre}
    elif tipo == "semilleros":
        base |= {"id_semillero": entidad.id_semillero, "codigo": entidad.codigo, "nombre": entidad.nombre}
    elif tipo == "pasantias":
        base |= {
            "id_pasantia": entidad.id_pasantia, "universidad": entidad.universidad,
            "docente_itm_nombre": entidad.docente_itm_nombre, "docente_itm_correo": entidad.docente_itm_correo,
        }
    else:
        base |= {"id_trabajo_grado": entidad.id_trabajo_grado, "director_nombre": entidad.director_nombre, "director_correo": entidad.director_correo}
    return base


def vinculaciones_de_usuario(db, id_usuario: int) -> dict:
    """Agrupadas por tipo, activas e inactivas (researchs §5.1, usuarios §2.1)."""
    return {
        tipo: [vinculacion_dict(db, tipo, v) for v in repo.vinculaciones_usuario(db, tipo, id_usuario)]
        for tipo in TIPOS_VINCULACION
    }


def crear_vinculacion_ajena(db, id_usuario: int, tipo: str, datos: schemas.VinculacionAjenaCrear, contexto: ContextoAutenticado) -> dict:
    if tipo not in TIPOS_VINCULACION_AJENA_CREABLES:
        raise NoEncontrado()
    entidad_id = datos.id_proyecto if tipo == "proyectos" else datos.id_semillero
    if entidad_id is None:
        raise Validacion(f"id_{tipo[:-1]} es obligatorio.")
    entidad = repo.obtener_entidad(db, tipo, entidad_id)
    if entidad is None or not entidad.estado:
        raise NoEncontrado(f"El {tipo[:-1]} no existe o está deshabilitado.")

    existente = repo.obtener_vinculacion(db, tipo, id_usuario, entidad_id)
    if existente is not None and existente.estado:
        raise Conflicto("Ya existe una vinculación activa con esa entidad.")
    if existente is not None:
        repo.reactivar_vinculacion(db, existente)
        vinculacion = existente
    else:
        vinculacion = repo.crear_vinculacion(db, tipo, id_usuario, entidad_id)

    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad=f"investigacion.usuario_{tipo}", entidad_id=id_usuario,
        accion="CREAR_VINCULACION_AJENA", datos_nuevos={"tipo": tipo, "entidad_id": entidad_id},
    )
    db.commit()
    return vinculacion_dict(db, tipo, vinculacion)


def desactivar_vinculacion_ajena(db, id_usuario: int, tipo: str, entidad_id: int, contexto: ContextoAutenticado) -> dict:
    if tipo not in TIPOS_VINCULACION:
        raise NoEncontrado()
    vinculacion = repo.obtener_vinculacion(db, tipo, id_usuario, entidad_id)
    if vinculacion is None or not vinculacion.estado:
        raise NoEncontrado("La vinculación no existe o ya está inactiva.")

    repo.desactivar_vinculacion_fila(db, vinculacion)
    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad=f"investigacion.usuario_{tipo}", entidad_id=id_usuario,
        accion="DESACTIVAR_VINCULACION_AJENA", datos_nuevos={"tipo": tipo, "entidad_id": entidad_id},
    )
    db.commit()
    return {"sin_vinculaciones_activas": not repo.tiene_vinculacion_activa(db, id_usuario)}
