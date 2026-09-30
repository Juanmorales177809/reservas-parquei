"""PrestamoFisicoPolicy: comportamiento compartido exclusivamente por
`RECURSO_CAMPUS` y `RECURSO_EXTERNO` (`architecture.md`; RN-RES-14,
RN-DIS-06, RN-TIP-RC-07, RN-TIP-RE-07). No es una sexta Strategy: no se
selecciona como tipo ni actúa como Context.

`establecer_compromisos` es la única vía por la que este módulo llama a
`reservas.establecer_compromiso_fisico()` (DB-12): ejecuta el retiro
atómico de complementarios de `ESPACIO` de RN-TIP-PE-28 y traduce su
`RAISE` (recurso en uso por un espacio `EN_EJECUCION`) a `409 CONFLICTO`
del contrato, sin exponer el error de PostgreSQL.

`generar_fgl` es el componente compartido de generación/persistencia de la
FGL 030 (RN-TIP-RC-07/12/13, RN-SAL) que exige el cierre de API-13 para la
creación autoaprobada, y que API-14 reutiliza al aprobar manualmente.
"""

from __future__ import annotations

from zoneinfo import ZoneInfo

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.core.errors import Conflicto, NoEncontrado, Validacion
from app.modules.reservations import repository as repo
from app.modules.resources import repository as rec_repo
from app.modules.usuarios import repository as usr_repo

_ZONA_OPERATIVA = ZoneInfo("America/Bogota")


def validar_recurso_disponible_fisicamente(db: Session, recurso_id: int, *, excluir_reserva_id: int | None = None) -> None:
    """RN-RES-14/RN-DIS-06: rechaza si el recurso ya tiene un compromiso
    físico vigente ajeno; se excluye el propio al revalidar (edición,
    aprobación, entrega)."""
    if repo.tiene_compromiso_fisico_vigente(db, recurso_id, excluir_reserva_id=excluir_reserva_id):
        raise Conflicto("El recurso tiene un compromiso vigente y no puede incluirse en otra solicitud.")


def establecer_compromisos(db: Session, *, reserva_id: int, recurso_ids: list[int]) -> None:
    """Un recurso a la vez: si alguno falla por estar en uso de un espacio
    `EN_EJECUCION`, la excepción propaga y el `rollback` de la transacción
    del servicio deshace cualquier retiro ya aplicado a recursos previos del
    lote, conforme a la atomicidad exigida por RN-TIP-PE-28."""
    for recurso_id in recurso_ids:
        try:
            repo.establecer_compromiso_fisico(db, recurso_id, reserva_id)
        except DBAPIError as exc:
            sqlstate = getattr(getattr(exc.orig, "diag", None), "sqlstate", None) or getattr(exc.orig, "sqlstate", None)
            if sqlstate == "P0001":
                raise Conflicto("El recurso está en uso por un espacio en ejecución.") from exc
            raise


def validar_creacion(db: Session, *, detalle: dict, recursos: list[dict], ahora, excluir_reserva_id: int | None = None) -> None:
    """RN-TIP-RC-02/03/04, RN-TIP-RE-02/03/04: fechas, un único PRINCIPAL,
    y cada recurso habilitado, operativo y libre de compromiso ajeno."""
    for campo in ("fecha_salida", "fecha_devolucion_estimada", "razon_solicitud", "lugar_nombre", "lugar_direccion"):
        valor = detalle.get(campo)
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise Validacion(f"detalle.{campo} es obligatorio.")
    if detalle["fecha_salida"] < ahora.astimezone(_ZONA_OPERATIVA).date():
        raise Validacion("No se aceptan fechas pasadas.")
    if detalle["fecha_devolucion_estimada"] < detalle["fecha_salida"]:
        raise Validacion("fecha_devolucion_estimada debe ser posterior o igual a fecha_salida.")

    principales = [r for r in recursos if r["rol"] == "PRINCIPAL"]
    if len(principales) != 1:
        raise Validacion("Se exige exactamente un recurso PRINCIPAL.")

    for r in recursos:
        recurso = rec_repo.obtener_recurso(db, r["recurso_id"])
        if recurso is None or not recurso.habilitado:
            raise NoEncontrado(f"El recurso {r['recurso_id']} no existe o no está habilitado.")
        if recurso.tipo == "EQUIPO":
            equipo = rec_repo.obtener_especializacion(db, "EQUIPO", r["recurso_id"])
            if equipo is not None and equipo.estado is False:
                raise Conflicto(f"El recurso {r['recurso_id']} no está operativo.")
        validar_recurso_disponible_fisicamente(db, r["recurso_id"], excluir_reserva_id=excluir_reserva_id)


# --- Casillas de la FGL 030 (RN-SAL) ------------------------------------------------

_MAPEO_ACTIVIDADES = (
    ("proyecto_id", "PROYECTO_INVESTIGACION"),
    ("semillero_id", "SEMILLERO_INVESTIGACION"),
    ("pasantia_id", "OTRO"),
    ("trabajo_grado_id", "OTRO"),
    ("actividad_institucional_id", "OTRO"),
)


def generar_fgl(db: Session, *, reserva, contexto_actor) -> object:
    """Genera y persiste la FGL 030 con los datos vigentes al aprobar,
    incluida la autoaprobación (RN-TIP-RC-07/12/13, RN-TIP-RE-07/12/13,
    RN-SAL). No regenera ni versiona: se llama una sola vez por reserva,
    dentro de la misma transacción que la aprobación."""
    datos_salida = repo.obtener_datos_salida(db, reserva.id)
    contexto = repo.obtener_contexto(db, reserva.id)

    if contexto_actor.tipo_cuenta == "USUARIO":
        usuario = usr_repo.obtener_usuario(db, contexto_actor.id_usuario)
        dependencia = usuario.dependencia
        responsable_nombre, responsable_cedula = usuario.nombre, usuario.documento
        responsable_correo, responsable_telefono = usuario.correo, usuario.telefono
    elif contexto_actor.tipo_cuenta == "ADMINISTRADOR":
        # Cuenta propia de Reservas: sin ficha; el responsable se identifica por su cuenta.
        dependencia = "Administración de Reservas"
        responsable_nombre, responsable_cedula = "Administrador", ""
        responsable_correo, responsable_telefono = contexto_actor.correo, ""
    else:
        persona = usr_repo.obtener_personal(db, contexto_actor.id_persona)
        id_unidad_cargo = repo.unidad_del_cargo_de_persona(db, contexto_actor.id_persona)
        unidad = rec_repo.obtener_unidad(db, id_unidad_cargo) if id_unidad_cargo else None
        dependencia = unidad.nombre if unidad else ""
        responsable_nombre, responsable_cedula = persona.nombre, persona.documento
        responsable_correo, responsable_telefono = persona.correo, persona.telefono

    orden = repo.crear_orden_salida(
        db, reserva.id,
        razon_solicitud=datos_salida.razon_solicitud, nombre_actividad_evento=datos_salida.nombre_actividad_evento,
        lugar_nombre=datos_salida.lugar_nombre, lugar_direccion=datos_salida.lugar_direccion,
        dependencia_solicitante_snapshot=dependencia,
        fecha_retiro_snapshot=_fecha_salida(db, reserva),
        fecha_regreso_snapshot=_fecha_devolucion(db, reserva),
        proyecto_codigo_snapshot=contexto.proyecto_codigo,
        responsable_nombre_snapshot=responsable_nombre, responsable_cedula_snapshot=responsable_cedula,
        responsable_correo_snapshot=responsable_correo, responsable_telefono_snapshot=responsable_telefono,
        observaciones=None,
    )

    for campo, actividad in _MAPEO_ACTIVIDADES:
        if getattr(contexto, campo) is not None:
            repo.agregar_actividad_orden(db, orden.id, actividad)

    for asignacion in repo.asignaciones_de_reserva(db, reserva.id, solo_vigentes=True):
        snapshot = _snapshot_recurso(db, asignacion.recurso_id)
        repo.agregar_item_orden(db, orden.id, asignacion.id, **snapshot)

    return orden


def _fecha_salida(db: Session, reserva):
    detalle = repo.obtener_detalle_campus(db, reserva.id) or repo.obtener_detalle_externo(db, reserva.id)
    return detalle.fecha_salida


def _fecha_devolucion(db: Session, reserva):
    detalle = repo.obtener_detalle_campus(db, reserva.id) or repo.obtener_detalle_externo(db, reserva.id)
    return detalle.fecha_devolucion_estimada


def _snapshot_recurso(db: Session, recurso_id: int) -> dict:
    recurso = rec_repo.obtener_recurso(db, recurso_id)
    especializacion = rec_repo.obtener_especializacion(db, recurso.tipo, recurso_id)
    if recurso.tipo == "EQUIPO":
        return {
            "placa_snapshot": especializacion.placa, "descripcion_snapshot": especializacion.nombre_equipo,
            "bodega_snapshot": especializacion.bodega, "cc_snapshot": especializacion.centro_costo,
            "fecha_compra_snapshot": especializacion.fecha_compra,
        }
    return {
        "placa_snapshot": None, "descripcion_snapshot": especializacion.nombre,
        "bodega_snapshot": None, "cc_snapshot": None, "fecha_compra_snapshot": None,
    }
