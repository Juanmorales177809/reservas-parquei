"""Lógica de estructura institucional, asignaciones y auditoría
(API-07 §2 y §3, API-08 §5; la auditoría es solo lectura).

Dueño de `RN-UNI-01..05` y `RN-PER-03/04/05/06/08/09` (administration).
Aplica `RN-AUTH-ROL-06/09` (auth) sin redefinirlos.

Cada escritura deja su fila en `administration.auditoria` dentro de la misma
transacción (precedente AUTH-C1): si el registro falla, la operación tampoco
se confirma en silencio.
"""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import audit
from app.core.deps import ContextoAutenticado
from app.core.errors import Conflicto, NoEncontrado, SolicitudInvalida, Validacion
from app.db.models.auth import Permisos
from app.modules.administration import repository as repo
from app.modules.administration import schemas

# Ámbito habitual por código, de `auth/data-model.md` §"Catálogo inicial".
# Solo display para GET /api/permisos: la autorización nunca lo lee
# (el alcance efectivo lo fija id_unidad por asignación, RN-PER-06).
AMBITO_HABITUAL = {
    "reservas.administrar": "unidad",
    "reservas.exportar": "unidad o global",
    "espacios.administrar": "unidad",
    "recursos.administrar": "unidad",
    "recursos.editar_equipos": "unidad",
    "recursos.administrar_equipos": "global",
    "recursos.reasignar_unidad": "global",
    "laboratorios.configurar": "unidad",
    "cuentas.administrar": "global",
    "usuarios.administrar": "global",
    "permisos.asignar": "global",
    "unidades.administrar": "global",
    "importacion.ejecutar": "global",
    "reportes.consultar": "unidad o global",
}

# Códigos que solo admiten asignación global (id_unidad IS NULL).
SOLO_GLOBALES = {"cuentas.administrar", "usuarios.administrar"}


def _unidad_dict(unidad) -> dict:
    return {
        "id_unidad": unidad.id_unidad,
        "nombre": unidad.nombre,
        "tipo": unidad.tipo,
        "id_unidad_padre": unidad.id_unidad_padre,
        "estado": unidad.estado,
    }


def _cargo_dict(cargo) -> dict:
    return {
        "id_cargo": cargo.id_cargo,
        "nombre_cargo": cargo.nombre_cargo,
        "id_unidad": cargo.id_unidad,
    }


# --- §2 Unidades ----------------------------------------------------------------------


def crear_unidad(db: Session, datos: schemas.UnidadCrear, actor: ContextoAutenticado) -> dict:
    if repo.existe_nombre_unidad(db, datos.nombre):
        raise Conflicto("Ya existe una unidad con ese nombre.")
    if datos.id_unidad_padre is not None and repo.obtener_unidad(db, datos.id_unidad_padre) is None:
        raise NoEncontrado("La unidad padre no existe.")
    try:
        with db.begin_nested():
            unidad = repo.crear_unidad(
                db, nombre=datos.nombre, tipo=datos.tipo, id_unidad_padre=datos.id_unidad_padre
            )
    except IntegrityError as exc:
        raise Conflicto("Ya existe una unidad con ese nombre.") from exc
    audit.registrar(
        db, actor_cuenta_id=actor.id_cuenta, entidad="unidadOrganizacional.unidad_organizacional",
        entidad_id=unidad.id_unidad, accion="CREAR_UNIDAD",
        datos_nuevos={"nombre": unidad.nombre, "tipo": unidad.tipo},
    )
    db.commit()
    db.refresh(unidad)
    return _unidad_dict(unidad)


def detalle_unidad(db: Session, id_unidad: int) -> dict:
    unidad = repo.obtener_unidad(db, id_unidad)
    if unidad is None:
        raise NoEncontrado()
    return _unidad_dict(unidad)


def listar_unidades(
    db: Session, *, estado: bool | None, tipo: str | None, id_unidad_padre: int | None,
    busqueda: str | None, paginacion,
) -> tuple[list, int]:
    filas, total = repo.listar_unidades(
        db, estado=estado, tipo=tipo, id_unidad_padre=id_unidad_padre, busqueda=busqueda,
        limite=paginacion.tamano, desplazamiento=paginacion.offset, orden=paginacion.orden,
    )
    return [_unidad_dict(f) for f in filas], total


def actualizar_unidad(
    db: Session, id_unidad: int, datos: schemas.UnidadActualizar, actor: ContextoAutenticado,
) -> dict:
    unidad = repo.obtener_unidad(db, id_unidad)
    if unidad is None:
        raise NoEncontrado()
    anteriores = {"nombre": unidad.nombre, "tipo": unidad.tipo, "id_unidad_padre": unidad.id_unidad_padre}
    if datos.nombre is not None and datos.nombre != unidad.nombre:
        # RN-UNI-03: el nombre cambia, la identidad interna no.
        if repo.existe_nombre_unidad(db, datos.nombre, excluir_id=id_unidad):
            raise Conflicto("Ya existe una unidad con ese nombre.")
        unidad.nombre = datos.nombre
    if datos.tipo is not None:
        unidad.tipo = datos.tipo
    if datos.id_unidad_padre is not None:
        if datos.id_unidad_padre == id_unidad or datos.id_unidad_padre in repo.descendientes_unidad(db, id_unidad):
            raise Conflicto("El cambio de padre crea un ciclo en la jerarquía.")
        padre = repo.obtener_unidad(db, datos.id_unidad_padre)
        if padre is None:
            raise NoEncontrado("La unidad padre no existe.")
        unidad.id_unidad_padre = datos.id_unidad_padre
    try:
        audit.registrar(
            db, actor_cuenta_id=actor.id_cuenta, entidad="unidadOrganizacional.unidad_organizacional",
            entidad_id=id_unidad, accion="EDITAR_UNIDAD",
            datos_anteriores=anteriores,
            datos_nuevos={"nombre": unidad.nombre, "tipo": unidad.tipo, "id_unidad_padre": unidad.id_unidad_padre},
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise Conflicto("Ya existe una unidad con ese nombre.") from exc
    db.refresh(unidad)
    return _unidad_dict(unidad)


def cambiar_estado_unidad(
    db: Session, id_unidad: int, estado: bool, actor: ContextoAutenticado,
) -> dict:
    unidad = repo.obtener_unidad(db, id_unidad)
    if unidad is None:
        raise NoEncontrado()
    # RN-UNI-04 (administration), RN-HAB-03/05: baja lógica pura, sin tocar nada más.
    anterior = unidad.estado
    unidad.estado = estado
    audit.registrar(
        db, actor_cuenta_id=actor.id_cuenta, entidad="unidadOrganizacional.unidad_organizacional",
        entidad_id=id_unidad, accion="CAMBIAR_ESTADO_UNIDAD",
        datos_anteriores={"estado": anterior}, datos_nuevos={"estado": estado},
    )
    db.commit()
    db.refresh(unidad)
    return _unidad_dict(unidad)


# --- §2 Cargos --------------------------------------------------------------------------


def crear_cargo(db: Session, datos: schemas.CargoCrear, actor: ContextoAutenticado) -> dict:
    unidad = repo.obtener_unidad(db, datos.id_unidad)
    if unidad is None:
        raise NoEncontrado("La unidad no existe.")
    if not unidad.estado:
        # RN-UNI-05: una unidad deshabilitada no recibe configuraciones nuevas.
        raise Validacion("La unidad está deshabilitada.")
    cargo = repo.crear_cargo(db, nombre_cargo=datos.nombre_cargo, id_unidad=datos.id_unidad)
    audit.registrar(
        db, actor_cuenta_id=actor.id_cuenta, entidad="cargos.cargo",
        entidad_id=cargo.id_cargo, accion="CREAR_CARGO",
        datos_nuevos={"nombre_cargo": cargo.nombre_cargo, "id_unidad": cargo.id_unidad},
    )
    db.commit()
    db.refresh(cargo)
    return _cargo_dict(cargo)


def listar_cargos(db: Session, *, id_unidad: int | None, paginacion) -> tuple[list, int]:
    filas, total = repo.listar_cargos(
        db, id_unidad=id_unidad,
        limite=paginacion.tamano, desplazamiento=paginacion.offset, orden=paginacion.orden,
    )
    return [_cargo_dict(f) for f in filas], total


def actualizar_cargo(
    db: Session, id_cargo: int, datos: schemas.CargoActualizar, actor: ContextoAutenticado,
) -> dict:
    cargo = repo.obtener_cargo(db, id_cargo)
    if cargo is None:
        raise NoEncontrado()
    anteriores = {"nombre_cargo": cargo.nombre_cargo, "id_unidad": cargo.id_unidad}
    if datos.nombre_cargo is not None:
        cargo.nombre_cargo = datos.nombre_cargo
    if datos.id_unidad is not None and datos.id_unidad != cargo.id_unidad:
        unidad = repo.obtener_unidad(db, datos.id_unidad)
        if unidad is None:
            raise NoEncontrado("La unidad no existe.")
        if not unidad.estado:
            raise Validacion("La unidad está deshabilitada.")
        # RN-PER-09: cambia el ámbito del personal que ocupa el cargo.
        cargo.id_unidad = datos.id_unidad
    audit.registrar(
        db, actor_cuenta_id=actor.id_cuenta, entidad="cargos.cargo",
        entidad_id=id_cargo, accion="EDITAR_CARGO",
        datos_anteriores=anteriores,
        datos_nuevos={"nombre_cargo": cargo.nombre_cargo, "id_unidad": cargo.id_unidad},
    )
    db.commit()
    db.refresh(cargo)
    return _cargo_dict(cargo)


# --- §3 Permisos ----------------------------------------------------------------------------


def catalogo_permisos(db: Session) -> list:
    return [
        {
            "codigo": p.codigo,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "habilitado": p.habilitado,
              "ambito": AMBITO_HABITUAL.get(p.codigo, "unidad o global"),
        }
        for p in repo.listar_permisos(db)
    ]


def asignaciones_de_cuenta(db: Session, id_cuenta: int) -> list:
    if repo.obtener_cuenta(db, id_cuenta) is None:
        raise NoEncontrado("La cuenta no existe.")
    filas = repo.asignaciones_de_cuenta(db, id_cuenta)
    return [_asignacion_dict(db, f) for f in filas]


def _asignacion_dict(db: Session, fila) -> dict:
    permiso = db.get(Permisos, fila.permiso_id)
    return {
        "id_cuenta_permiso": fila.id_cuenta_permiso,
        "id_cuenta": fila.id_cuenta,
        "codigo": permiso.codigo if permiso else None,
        "id_unidad": fila.id_unidad,
        "otorgado_por": fila.otorgado_por,
        "created_at": fila.created_at,
    }


def otorgar_permiso(
    db: Session, id_cuenta: int, datos: schemas.PermisoOtorgar, actor: ContextoAutenticado,
) -> dict:
    cuenta = repo.obtener_cuenta(db, id_cuenta)
    if cuenta is None:
        raise NoEncontrado("La cuenta no existe.")
    permiso = repo.obtener_permiso_por_codigo(db, datos.codigo)
    if permiso is None or not permiso.habilitado:
        raise Validacion("El código no existe en el catálogo o está deshabilitado.")
    # RN-PER-08: solo PERSONAL activa con ficha activa recibe permisos.
    if cuenta.tipo_cuenta == "USUARIO":
        raise Validacion("Una cuenta USUARIO nunca recibe permisos administrativos.")
    persona = repo.persona_de_cuenta(db, cuenta)
    if persona is None or not persona.estado:
        raise Validacion("La cuenta no está vinculada a una ficha activa de personal.")
    if not cuenta.estado:
        raise Validacion("La cuenta no está activa.")
    if datos.codigo in SOLO_GLOBALES and datos.id_unidad is not None:
        raise Validacion("Este permiso solo admite asignación global.")
    if datos.id_unidad is not None:
        unidad = repo.obtener_unidad(db, datos.id_unidad)
        if unidad is None or not unidad.estado:
            raise Validacion("La unidad no existe o está deshabilitada.")
        # RN-AUTH-ROL-06 (auth) / RN-PER-09: coincide con el cargo vigente.
        if repo.unidad_del_cargo(db, persona.id_cargo) != datos.id_unidad:
            raise Validacion("La unidad no coincide con la del cargo vigente de la persona.")
    try:
        with db.begin_nested():
            fila = repo.otorgar_permiso(
                db, id_cuenta=id_cuenta, permiso_id=permiso.id,
                id_unidad=datos.id_unidad, otorgado_por=actor.id_cuenta,
            )
    except IntegrityError as exc:
        raise Conflicto("La asignación ya existe.") from exc
    audit.registrar(
        db, actor_cuenta_id=actor.id_cuenta, entidad="auth.cuenta_permisos",
        entidad_id=fila.id_cuenta_permiso, accion="ASIGNAR_PERMISO",
        datos_nuevos={"codigo": datos.codigo, "id_unidad": datos.id_unidad},
    )
    db.commit()
    return _asignacion_dict(db, fila)


def retirar_permiso(db: Session, id_cuenta: int, codigo: str, actor: ContextoAutenticado) -> int:
    """Retira todas las asignaciones del código. Devuelve cuántas."""
    if repo.obtener_cuenta(db, id_cuenta) is None:
        raise NoEncontrado("La cuenta no existe.")
    permiso = repo.obtener_permiso_por_codigo(db, codigo)
    if permiso is None:
        raise NoEncontrado("La asignación no existe.")
    filas = repo.asignaciones_de_cuenta(db, id_cuenta)
    objetivos = [f for f in filas if f.permiso_id == permiso.id]
    if not objetivos:
        raise NoEncontrado("La asignación no existe.")
    globales = [f for f in objetivos if f.id_unidad is None]
    if globales and repo.es_administrador_activo(db, id_cuenta):
        if repo.otros_administradores_activos(db, id_cuenta) == 0:
            # RN-AUTH-ROL-09 (auth): sin permisos globales vigentes no hay sistema.
            raise Conflicto("La operación dejaría al sistema sin ninguna cuenta con permisos globales vigentes.")
    for fila in objetivos:
        audit.registrar(
            db, actor_cuenta_id=actor.id_cuenta, entidad="auth.cuenta_permisos",
            entidad_id=fila.id_cuenta_permiso, accion="RETIRAR_PERMISO",
            datos_anteriores={"codigo": codigo, "id_unidad": fila.id_unidad},
        )
        db.delete(fila)
    # RN-PER-04: rige desde ahora; lo ya autorizado conserva validez (RN-PER-05).
    db.commit()
    return len(objetivos)


# --- §5 Auditoría (API-08; solo lectura) -----------------------------------------------------


def listar_auditoria(
    db: Session, *, entidad: str | None, entidad_id: str | None, actor_cuenta_id: str | None,
    accion: str | None, desde: str | None, hasta: str | None, paginacion,
) -> tuple[list, int]:
    """Filtros del contrato §5.1. Formatos inválidos → 400."""
    actor = _entero_o_400(actor_cuenta_id, "actor_cuenta_id")
    inicio = _instante_o_400(desde, "desde")
    fin = _instante_o_400(hasta, "hasta")
    orden = (paginacion.orden or "-created_at").removeprefix("-")
    if orden != "created_at":
        raise SolicitudInvalida("'orden' no admite el campo '%s'." % orden)
    descendente = (paginacion.orden or "-created_at").startswith("-")
    filas, total = repo.listar_auditoria(
        db, entidad=entidad, entidad_id=entidad_id, actor_cuenta_id=actor,
        accion=accion, desde=inicio, hasta=fin,
        limite=paginacion.tamano, desplazamiento=paginacion.offset, descendente=descendente,
    )
    return [
        {
            "id": f.id,
            "actor_cuenta_id": f.actor_cuenta_id,
            "entidad": f.entidad,
            "entidad_id": f.entidad_id,
            "accion": f.accion,
            "datos_anteriores": f.datos_anteriores,
            "datos_nuevos": f.datos_nuevos,
            "motivo": f.motivo,
            "created_at": f.created_at,
        }
        for f in filas
    ], total


def _entero_o_400(raw: str | None, campo: str) -> int | None:
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        raise SolicitudInvalida("'%s' debe ser un entero." % campo)


def _instante_o_400(raw: str | None, campo: str):
    if raw is None:
        return None
    from datetime import datetime

    try:
        momento = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        momento = None
    if momento is None:
        raise SolicitudInvalida("'%s' debe ser una fecha ISO 8601." % campo)
    return momento
