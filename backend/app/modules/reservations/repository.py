"""Acceso a datos de reservations (API-13).

Reutiliza los repositorios de los módulos propietarios en vez de
duplicarlos: `resources.repository` para recursos/laboratorios_config,
`espacios.repository` para espacios/campos, `researchs.repository` para
proyectos/semilleros/vinculaciones. Este archivo solo resuelve lo propio
de `reservas.*`.

Ninguna función escribe `periodo`, `bloqueante` ni `compromiso_fisico`:
son proyecciones técnicas mantenidas por los disparadores de `DB-12`
(`009_concurrencia.sql`).
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone

from sqlalchemy import exists, func, or_, select, text
from sqlalchemy.orm import Session

from app.db.models.auth import Cuentas
from app.db.models.identidad import Cargo, Personal
from app.db.models.reservas import (
    EstadosReserva,
    OrdenesSalida,
    OrdenSalidaActividades,
    OrdenSalidaItems,
    ReservaAcompanantes,
    ReservaAdjuntos,
    ReservaCamposValores,
    ReservaContexto,
    ReservaDatosSalida,
    ReservaEjecucionRecursos,
    ReservaEspacio,
    ReservaHistorialEstado,
    ReservaListaEspera,
    ReservaListaEsperaFormulario,
    ReservaPropuestas,
    ReservaRecursoCampus,
    ReservaRecursoExterno,
    ReservaRecursoInterno,
    ReservaRecursos,
    Reservas,
    TiposReserva,
)


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


# --- Catálogos -----------------------------------------------------------------------


def obtener_tipo_por_codigo(db: Session, codigo: str) -> TiposReserva | None:
    return db.scalar(select(TiposReserva).where(TiposReserva.codigo == codigo, TiposReserva.habilitado.is_(True)))


def obtener_tipo(db: Session, id_tipo: int) -> TiposReserva | None:
    return db.get(TiposReserva, id_tipo)


def obtener_estado_por_codigo(db: Session, codigo: str) -> EstadosReserva | None:
    return db.scalar(select(EstadosReserva).where(EstadosReserva.codigo == codigo))


def obtener_estado(db: Session, id_estado: int) -> EstadosReserva | None:
    return db.get(EstadosReserva, id_estado)


def id_usuario_de_cuenta(db: Session, id_cuenta: int) -> int | None:
    return db.scalar(select(Cuentas.id_usuario).where(Cuentas.id_cuenta == id_cuenta))


def nombre_de_cuenta(db: Session, id_cuenta: int | None) -> str | None:
    """Nombre de la persona titular de la cuenta (usuario o personal); las pantallas no muestran ids."""
    if id_cuenta is None:
        return None
    from app.db.models.identidad import Usuarios

    fila = db.execute(select(Cuentas.id_usuario, Cuentas.id_persona, Cuentas.tipo_cuenta).where(Cuentas.id_cuenta == id_cuenta)).first()
    if fila is None:
        return None
    if fila[0] is not None:
        return db.scalar(select(Usuarios.nombre).where(Usuarios.id_usuario == fila[0]))
    if fila[1] is not None:
        return db.scalar(select(Personal.nombre).where(Personal.id_persona == fila[1]))
    if fila[2] == "ADMINISTRADOR":
        return "Administrador"  # cuenta propia de Reservas: no tiene ficha con nombre
    return None


def nombre_de_espacio(db: Session, espacio_id: int) -> str | None:
    from app.db.models.reservas import Espacios

    return db.scalar(select(Espacios.nombre).where(Espacios.id == espacio_id))


def cuentas_activas_de_usuarios(db: Session, ids_usuario: list[int]) -> list[tuple[int, str]]:
    """(id_cuenta, nombre) de las cuentas activas de esos usuarios, ordenadas por nombre."""
    if not ids_usuario:
        return []
    from app.db.models.identidad import Usuarios

    filas = db.execute(
        select(Cuentas.id_cuenta, Usuarios.nombre)
        .join(Usuarios, Usuarios.id_usuario == Cuentas.id_usuario)
        .where(Cuentas.id_usuario.in_(ids_usuario), Cuentas.estado.is_(True))
        .order_by(Usuarios.nombre)
    ).all()
    return [(f[0], f[1]) for f in filas]


def unidad_del_cargo_de_persona(db: Session, id_persona: int) -> int | None:
    """RN-RES-15: unidad del laboratorio asociada al cargo vigente de la persona."""
    persona = db.get(Personal, id_persona)
    if persona is None:
        return None
    cargo = db.get(Cargo, persona.id_cargo)
    return cargo.id_unidad if cargo else None


# --- Cabecera --------------------------------------------------------------------------


def crear_reserva(
    db: Session, *, id_unidad: int, tipo_reserva_id: int, id_cuenta: int, estado_id: int,
    observacion: str | None, requiere_apoyo: bool, created_by: int,
) -> Reservas:
    ahora = _ahora()
    reserva = Reservas(
        id_unidad=id_unidad, tipo_reserva_id=tipo_reserva_id, id_cuenta=id_cuenta, estado_id=estado_id,
        observacion=observacion, requiere_apoyo=requiere_apoyo, created_by=created_by,
        created_at=ahora, updated_at=ahora,
    )
    db.add(reserva)
    db.flush()
    return reserva


def obtener_reserva(db: Session, id_reserva: int) -> Reservas | None:
    return db.get(Reservas, id_reserva)


def registrar_historial(
    db: Session, *, reserva_id: int, estado_anterior_id: int | None, estado_nuevo_id: int,
    actor_cuenta_id: int | None, motivo: str | None,
) -> None:
    db.add(ReservaHistorialEstado(
        reserva_id=reserva_id, estado_anterior_id=estado_anterior_id, estado_nuevo_id=estado_nuevo_id,
        actor_cuenta_id=actor_cuenta_id, motivo=motivo, created_at=_ahora(),
    ))


def historial_de_reserva(db: Session, reserva_id: int) -> list[ReservaHistorialEstado]:
    stmt = select(ReservaHistorialEstado).where(ReservaHistorialEstado.reserva_id == reserva_id).order_by(ReservaHistorialEstado.created_at)
    return list(db.scalars(stmt).all())


def listar_reservas(
    db: Session, *, id_cuenta: int | None, id_unidad: int | None, estado_codigo: str | None,
    tipo_codigo: str | None, desde: date | None, hasta: date | None, espacio_id: int | None,
    recurso_id: int | None, orden: str | None, offset: int, tamano: int,
) -> tuple[list[Reservas], int]:
    stmt = select(Reservas)
    if id_cuenta is not None:
        stmt = stmt.where(Reservas.id_cuenta == id_cuenta)
    if id_unidad is not None:
        stmt = stmt.where(Reservas.id_unidad == id_unidad)
    if estado_codigo is not None:
        stmt = stmt.join(EstadosReserva, EstadosReserva.id == Reservas.estado_id).where(EstadosReserva.codigo == estado_codigo)
    if tipo_codigo is not None:
        stmt = stmt.join(TiposReserva, TiposReserva.id == Reservas.tipo_reserva_id).where(TiposReserva.codigo == tipo_codigo)
    if desde is not None or hasta is not None:
        # Fecha de uso, no de creación: una reserva entra si su periodo comparte al menos un día con
        # [desde, hasta] (RN-DIS-02). La lista de espera no tiene fecha y queda fuera cuando se filtra por ella.
        periodos = (
            (ReservaEspacio, ReservaEspacio.fecha, ReservaEspacio.fecha),
            (ReservaRecursoInterno, ReservaRecursoInterno.fecha, ReservaRecursoInterno.fecha),
            (ReservaRecursoCampus, ReservaRecursoCampus.fecha_salida, ReservaRecursoCampus.fecha_devolucion_estimada),
            (ReservaRecursoExterno, ReservaRecursoExterno.fecha_salida, ReservaRecursoExterno.fecha_devolucion_estimada),
        )
        condiciones = []
        for modelo, inicio, fin in periodos:
            partes = [modelo.reserva_id == Reservas.id]
            if hasta is not None:
                partes.append(inicio <= hasta)
            if desde is not None:
                partes.append(fin >= desde)
            condiciones.append(exists().where(*partes))
        stmt = stmt.where(or_(*condiciones))
    if espacio_id is not None:
        stmt = stmt.join(ReservaEspacio, ReservaEspacio.reserva_id == Reservas.id).where(ReservaEspacio.espacio_id == espacio_id)
    if recurso_id is not None:
        stmt = stmt.join(ReservaRecursos, ReservaRecursos.reserva_id == Reservas.id).where(ReservaRecursos.recurso_id == recurso_id)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    if orden == "fecha" or orden == "-fecha":
        pass  # `fecha` vive en el detalle por tipo; se ordena por created_at como aproximación estable
    descendente = (orden or "").startswith("-")
    campo = (orden or "").removeprefix("-")
    columna = {"created_at": Reservas.created_at, "estado": Reservas.estado_id}.get(campo, Reservas.created_at)
    stmt = stmt.order_by(columna.desc() if descendente else columna)

    items = db.scalars(stmt.distinct().offset(offset).limit(tamano)).all()
    return list(items), total


# --- Contexto --------------------------------------------------------------------------


def crear_contexto(db: Session, reserva_id: int, **campos) -> ReservaContexto:
    contexto = ReservaContexto(reserva_id=reserva_id, **campos)
    db.add(contexto)
    db.flush()
    return contexto


def obtener_contexto(db: Session, reserva_id: int) -> ReservaContexto | None:
    return db.get(ReservaContexto, reserva_id)


# --- Detalle: ESPACIO --------------------------------------------------------------------


def crear_detalle_espacio(db: Session, reserva_id: int, *, espacio_id: int, fecha: date, hora_inicio: time, hora_fin: time, asistentes: int) -> ReservaEspacio:
    detalle = ReservaEspacio(reserva_id=reserva_id, espacio_id=espacio_id, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin, asistentes=asistentes)
    db.add(detalle)
    db.flush()
    return detalle


def obtener_detalle_espacio(db: Session, reserva_id: int) -> ReservaEspacio | None:
    return db.get(ReservaEspacio, reserva_id)


# --- Detalle: RECURSO_INTERNO -------------------------------------------------------------


def crear_detalle_interno(db: Session, reserva_id: int, *, fecha: date, hora_inicio: time, hora_fin: time) -> ReservaRecursoInterno:
    detalle = ReservaRecursoInterno(reserva_id=reserva_id, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin)
    db.add(detalle)
    db.flush()
    return detalle


def obtener_detalle_interno(db: Session, reserva_id: int) -> ReservaRecursoInterno | None:
    return db.get(ReservaRecursoInterno, reserva_id)


# --- Detalle: RECURSO_CAMPUS / RECURSO_EXTERNO ----------------------------------------------


def crear_detalle_campus(db: Session, reserva_id: int, *, fecha_salida: date, fecha_devolucion_estimada: date) -> ReservaRecursoCampus:
    detalle = ReservaRecursoCampus(reserva_id=reserva_id, fecha_salida=fecha_salida, fecha_devolucion_estimada=fecha_devolucion_estimada)
    db.add(detalle)
    db.flush()
    return detalle


def obtener_detalle_campus(db: Session, reserva_id: int) -> ReservaRecursoCampus | None:
    return db.get(ReservaRecursoCampus, reserva_id)


def crear_detalle_externo(db: Session, reserva_id: int, *, fecha_salida: date, fecha_devolucion_estimada: date) -> ReservaRecursoExterno:
    detalle = ReservaRecursoExterno(reserva_id=reserva_id, fecha_salida=fecha_salida, fecha_devolucion_estimada=fecha_devolucion_estimada)
    db.add(detalle)
    db.flush()
    return detalle


def obtener_detalle_externo(db: Session, reserva_id: int) -> ReservaRecursoExterno | None:
    return db.get(ReservaRecursoExterno, reserva_id)


def crear_datos_salida(db: Session, reserva_id: int, *, razon_solicitud: str, lugar_nombre: str, lugar_direccion: str, nombre_actividad_evento: str | None) -> ReservaDatosSalida:
    datos = ReservaDatosSalida(reserva_id=reserva_id, razon_solicitud=razon_solicitud, lugar_nombre=lugar_nombre, lugar_direccion=lugar_direccion, nombre_actividad_evento=nombre_actividad_evento)
    db.add(datos)
    db.flush()
    return datos


def obtener_datos_salida(db: Session, reserva_id: int) -> ReservaDatosSalida | None:
    return db.get(ReservaDatosSalida, reserva_id)


# --- Detalle: LISTA_ESPERA -------------------------------------------------------------------


def crear_detalle_lista_espera(db: Session, reserva_id: int, *, descripcion_necesidad: str) -> ReservaListaEspera:
    detalle = ReservaListaEspera(reserva_id=reserva_id, descripcion_necesidad=descripcion_necesidad, viable=None, fecha_evaluacion_viabilidad=None, fecha_recepcion_material=None, prioridad=None, horas_ejecucion=None)
    db.add(detalle)
    db.flush()
    return detalle


def obtener_detalle_lista_espera(db: Session, reserva_id: int) -> ReservaListaEspera | None:
    return db.get(ReservaListaEspera, reserva_id)


def obtener_formulario_lista_espera(db: Session, reserva_id: int) -> ReservaListaEsperaFormulario | None:
    return db.get(ReservaListaEsperaFormulario, reserva_id)


def crear_formulario_reservista(db: Session, reserva_id: int, datos_usuario: dict) -> ReservaListaEsperaFormulario:
    fila = ReservaListaEsperaFormulario(reserva_id=reserva_id, datos_usuario=datos_usuario, diligenciado_at=_ahora())
    db.add(fila)
    db.flush()
    return fila


# --- Recursos asignados ---------------------------------------------------------------------


def crear_asignacion_recurso(db: Session, *, reserva_id: int, recurso_id: int, rol: str, estado_asignacion: str = "ASIGNADO", incorporado_at: datetime | None = None) -> ReservaRecursos:
    fila = ReservaRecursos(
        reserva_id=reserva_id, recurso_id=recurso_id, rol=rol, estado_asignacion=estado_asignacion,
        incorporado_at=incorporado_at, bloqueante=False, compromiso_fisico=False,
    )
    db.add(fila)
    db.flush()
    return fila


def obtener_asignacion(db: Session, reserva_recurso_id: int) -> ReservaRecursos | None:
    return db.get(ReservaRecursos, reserva_recurso_id)


def asignaciones_de_reserva(db: Session, reserva_id: int, *, solo_vigentes: bool = False) -> list[ReservaRecursos]:
    stmt = select(ReservaRecursos).where(ReservaRecursos.reserva_id == reserva_id)
    if solo_vigentes:
        stmt = stmt.where(ReservaRecursos.estado_asignacion == "ASIGNADO")
    return list(db.scalars(stmt.order_by(ReservaRecursos.id)).all())


# --- Acompañantes ----------------------------------------------------------------------------


def acompanantes_de_reserva(db: Session, reserva_id: int) -> list[int]:
    stmt = select(ReservaAcompanantes.id_cuenta).where(ReservaAcompanantes.reserva_id == reserva_id)
    return list(db.scalars(stmt).all())


def reemplazar_acompanantes(db: Session, reserva_id: int, ids_cuentas: list[int]) -> None:
    db.query(ReservaAcompanantes).filter(ReservaAcompanantes.reserva_id == reserva_id).delete()
    for id_cuenta in ids_cuentas:
        db.add(ReservaAcompanantes(reserva_id=reserva_id, id_cuenta=id_cuenta))


# --- Campos adicionales (espacio) -----------------------------------------------------------


def campos_valores_de_reserva(db: Session, reserva_id: int) -> list[ReservaCamposValores]:
    stmt = select(ReservaCamposValores).where(ReservaCamposValores.reserva_id == reserva_id)
    return list(db.scalars(stmt).all())


def reemplazar_campos_valores(db: Session, reserva_id: int, valores: list[dict]) -> None:
    db.query(ReservaCamposValores).filter(ReservaCamposValores.reserva_id == reserva_id).delete()
    for v in valores:
        db.add(ReservaCamposValores(reserva_id=reserva_id, **v))


# --- Disponibilidad: solapamiento y compromiso físico ----------------------------------------

_ESTADOS_BLOQUEANTES = ("SOLICITADA", "APROBADA", "EN_EJECUCION")


def existe_solapamiento_espacio(db: Session, espacio_id: int, inicio: datetime, fin: datetime, *, excluir_reserva_id: int | None = None) -> bool:
    # Comparación directa en Python: el volumen por espacio es pequeño y evita
    # depender de la sintaxis de rangos en la consulta para esta revalidación
    # de aplicación (la garantía real la impone la restricción de exclusión).
    candidatos = db.execute(
        select(ReservaEspacio.fecha, ReservaEspacio.hora_inicio, ReservaEspacio.hora_fin)
        .select_from(ReservaEspacio)
        .join(Reservas, Reservas.id == ReservaEspacio.reserva_id)
        .join(EstadosReserva, EstadosReserva.id == Reservas.estado_id)
        .where(
            ReservaEspacio.espacio_id == espacio_id,
            EstadosReserva.codigo.in_(_ESTADOS_BLOQUEANTES),
            ReservaEspacio.reserva_id != (excluir_reserva_id or -1),
        )
    ).all()
    for fecha, hora_i, hora_f in candidatos:
        otro_inicio = datetime.combine(fecha, hora_i, tzinfo=inicio.tzinfo)
        otro_fin = datetime.combine(fecha, hora_f, tzinfo=inicio.tzinfo)
        if inicio < otro_fin and otro_inicio < fin:
            return True
    return False


def existe_solapamiento_recurso_interno(db: Session, recurso_id: int, inicio: datetime, fin: datetime, *, excluir_reserva_id: int | None = None) -> bool:
    candidatos = db.execute(
        select(ReservaRecursoInterno.fecha, ReservaRecursoInterno.hora_inicio, ReservaRecursoInterno.hora_fin)
        .select_from(ReservaRecursoInterno)
        .join(ReservaRecursos, ReservaRecursos.reserva_id == ReservaRecursoInterno.reserva_id)
        .join(Reservas, Reservas.id == ReservaRecursoInterno.reserva_id)
        .join(EstadosReserva, EstadosReserva.id == Reservas.estado_id)
        .where(
            ReservaRecursos.recurso_id == recurso_id,
            ReservaRecursos.estado_asignacion == "ASIGNADO",
            EstadosReserva.codigo.in_(_ESTADOS_BLOQUEANTES),
            ReservaRecursoInterno.reserva_id != (excluir_reserva_id or -1),
        )
    ).all()
    for fecha, hora_i, hora_f in candidatos:
        otro_inicio = datetime.combine(fecha, hora_i, tzinfo=inicio.tzinfo)
        otro_fin = datetime.combine(fecha, hora_f, tzinfo=inicio.tzinfo)
        if inicio < otro_fin and otro_inicio < fin:
            return True
    return False


def tiene_compromiso_fisico_vigente(db: Session, recurso_id: int, *, excluir_reserva_id: int | None = None) -> bool:
    stmt = select(ReservaRecursos.id).where(
        ReservaRecursos.recurso_id == recurso_id,
        ReservaRecursos.compromiso_fisico.is_(True),
    )
    if excluir_reserva_id is not None:
        stmt = stmt.where(ReservaRecursos.reserva_id != excluir_reserva_id)
    return db.scalar(stmt) is not None


def franjas_ocupadas_espacio(db: Session, espacio_id: int, desde: date, hasta: date) -> list[tuple[date, time, time]]:
    filas = db.execute(
        select(ReservaEspacio.fecha, ReservaEspacio.hora_inicio, ReservaEspacio.hora_fin)
        .select_from(ReservaEspacio)
        .join(Reservas, Reservas.id == ReservaEspacio.reserva_id)
        .join(EstadosReserva, EstadosReserva.id == Reservas.estado_id)
        .where(ReservaEspacio.espacio_id == espacio_id, EstadosReserva.codigo.in_(_ESTADOS_BLOQUEANTES), ReservaEspacio.fecha.between(desde, hasta))
        .order_by(ReservaEspacio.fecha, ReservaEspacio.hora_inicio)
    ).all()
    return [(f, hi, hf) for f, hi, hf in filas]


def franjas_ocupadas_recurso_interno(db: Session, recurso_id: int, desde: date, hasta: date) -> list[tuple[date, time, time]]:
    filas = db.execute(
        select(ReservaRecursoInterno.fecha, ReservaRecursoInterno.hora_inicio, ReservaRecursoInterno.hora_fin)
        .select_from(ReservaRecursoInterno)
        .join(ReservaRecursos, ReservaRecursos.reserva_id == ReservaRecursoInterno.reserva_id)
        .join(Reservas, Reservas.id == ReservaRecursoInterno.reserva_id)
        .join(EstadosReserva, EstadosReserva.id == Reservas.estado_id)
        .where(
            ReservaRecursos.recurso_id == recurso_id, ReservaRecursos.estado_asignacion == "ASIGNADO",
            EstadosReserva.codigo.in_(_ESTADOS_BLOQUEANTES), ReservaRecursoInterno.fecha.between(desde, hasta),
        )
        .order_by(ReservaRecursoInterno.fecha, ReservaRecursoInterno.hora_inicio)
    ).all()
    return [(f, hi, hf) for f, hi, hf in filas]


def obtener_estado_id_codigo(db: Session, codigo: str) -> int:
    return db.scalar(select(EstadosReserva.id).where(EstadosReserva.codigo == codigo))


def establecer_compromiso_fisico(db: Session, recurso_id: int, reserva_causante_id: int) -> None:
    """Ejecuta `reservas.establecer_compromiso_fisico()` (DB-12): retira
    atómicamente los complementarios de `ESPACIO` vigentes de ese recurso en
    `SOLICITADA`/`APROBADA`, o lanza si alguno está `EN_EJECUCION`. No
    inserta la nueva asignación física; eso lo hace el llamador después, en
    la misma transacción (RN-TIP-PE-28)."""
    db.execute(
        text("SELECT reservas.establecer_compromiso_fisico(:recurso_id, :reserva_causante_id)"),
        {"recurso_id": recurso_id, "reserva_causante_id": reserva_causante_id},
    )


# --- FGL 030 -----------------------------------------------------------------------------------


def crear_orden_salida(db: Session, reserva_id: int, **campos) -> OrdenesSalida:
    orden = OrdenesSalida(reserva_id=reserva_id, fecha_generacion=_ahora(), **campos)
    db.add(orden)
    db.flush()
    return orden


def agregar_actividad_orden(db: Session, orden_salida_id: int, actividad: str) -> None:
    db.add(OrdenSalidaActividades(orden_salida_id=orden_salida_id, actividad=actividad))


def agregar_item_orden(db: Session, orden_salida_id: int, reserva_recurso_id: int, **snapshot) -> None:
    db.add(OrdenSalidaItems(orden_salida_id=orden_salida_id, reserva_recurso_id=reserva_recurso_id, **snapshot))


def obtener_orden_por_reserva(db: Session, reserva_id: int) -> OrdenesSalida | None:
    return db.scalar(select(OrdenesSalida).where(OrdenesSalida.reserva_id == reserva_id))


def actividades_de_orden(db: Session, orden_salida_id: int) -> list[str]:
    return list(db.scalars(
        select(OrdenSalidaActividades.actividad)
        .where(OrdenSalidaActividades.orden_salida_id == orden_salida_id)
        .order_by(OrdenSalidaActividades.actividad)
    ).all())


def items_de_orden(db: Session, orden_salida_id: int) -> list[OrdenSalidaItems]:
    return list(db.scalars(
        select(OrdenSalidaItems)
        .where(OrdenSalidaItems.orden_salida_id == orden_salida_id)
        .order_by(OrdenSalidaItems.id)
    ).all())


# --- Adjuntos (§2.5-2.7) -----------------------------------------------------------------------


def crear_adjunto(db: Session, **campos) -> ReservaAdjuntos:
    adjunto = ReservaAdjuntos(created_at=_ahora(), **campos)
    db.add(adjunto)
    db.flush()
    return adjunto


def adjuntos_de_reserva(db: Session, reserva_id: int, *, offset: int, tamano: int) -> tuple[list[ReservaAdjuntos], int]:
    stmt = select(ReservaAdjuntos).where(ReservaAdjuntos.reserva_id == reserva_id)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(stmt.order_by(ReservaAdjuntos.created_at).offset(offset).limit(tamano)).all()
    return list(items), total


def obtener_adjunto(db: Session, adjunto_id: int) -> ReservaAdjuntos | None:
    return db.get(ReservaAdjuntos, adjunto_id)


# --- Ejecución de recursos: entrega y devolución física (API-14 §6) ----------------------------


def crear_ejecucion_recurso(db: Session, *, reserva_recurso_id: int, entregado_por: int, entregado_at: datetime, observacion_entrega: str | None) -> ReservaEjecucionRecursos:
    fila = ReservaEjecucionRecursos(
        reserva_recurso_id=reserva_recurso_id, entregado_por=entregado_por, entregado_at=entregado_at,
        observacion_entrega=observacion_entrega,
    )
    db.add(fila)
    db.flush()
    return fila


def entrega_abierta_de_asignacion(db: Session, reserva_recurso_id: int) -> ReservaEjecucionRecursos | None:
    stmt = select(ReservaEjecucionRecursos).where(
        ReservaEjecucionRecursos.reserva_recurso_id == reserva_recurso_id,
        ReservaEjecucionRecursos.devuelto_at.is_(None),
    )
    return db.scalar(stmt)


def entregas_abiertas_de_reserva(db: Session, reserva_id: int) -> list[ReservaEjecucionRecursos]:
    stmt = (
        select(ReservaEjecucionRecursos)
        .join(ReservaRecursos, ReservaRecursos.id == ReservaEjecucionRecursos.reserva_recurso_id)
        .where(ReservaRecursos.reserva_id == reserva_id, ReservaEjecucionRecursos.devuelto_at.is_(None))
    )
    return list(db.scalars(stmt).all())


# --- Propuestas de periodo (API-14 §5) ----------------------------------------------------------


def crear_propuesta(
    db: Session, *, reserva_id: int, origen: str, fecha_inicio_propuesta: date, fecha_fin_propuesta: date,
    hora_inicio: time | None, hora_fin: time | None, motivo: str, creada_por: int,
) -> ReservaPropuestas:
    propuesta = ReservaPropuestas(
        reserva_id=reserva_id, origen=origen, fecha_inicio_propuesta=fecha_inicio_propuesta,
        fecha_fin_propuesta=fecha_fin_propuesta, hora_inicio=hora_inicio, hora_fin=hora_fin, motivo=motivo,
        estado="VIGENTE", creada_por=creada_por, resuelta_por=None, created_at=_ahora(), resuelta_at=None,
    )
    db.add(propuesta)
    db.flush()
    return propuesta


def obtener_propuesta_vigente(db: Session, reserva_id: int) -> ReservaPropuestas | None:
    stmt = select(ReservaPropuestas).where(ReservaPropuestas.reserva_id == reserva_id, ReservaPropuestas.estado == "VIGENTE")
    return db.scalar(stmt)


def resolver_propuesta(db: Session, propuesta: ReservaPropuestas, *, estado: str, resuelta_por: int, resuelta_at: datetime) -> None:
    propuesta.estado = estado
    propuesta.resuelta_por = resuelta_por
    propuesta.resuelta_at = resuelta_at
