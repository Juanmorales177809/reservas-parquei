import html
import uuid
from datetime import date, datetime, time, timedelta, timezone
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.reservas import (
    get_espacio_ids_reserva,
    get_espacios_bloqueantes,
    get_recurso_ids_reserva,
    get_reserva,
    get_reservas_bloqueantes,
    get_reservas_de_grupo,
)
from app.deps import get_managed_laboratory_id
from app.domain.enums import (
    EstadoEntidad,
    EstadoReserva,
    Rol,
    TipoNotificacion,
    TipoSolicitud,
)
from app.domain.protocols import Reloj
from app.models import (
    Espacio,
    EspacioRecurso,
    Laboratorio,
    MotivoSolicitud,
    Notificacion,
    Personal,
    Recurso,
    Reserva,
    ReservaEspacio,
    ReservaRecurso,
    TipoReserva,
    Usuario,
    UsuarioLaboratorio,
)
from app.models.reserva import ESTADOS_BLOQUEANTES
from app.schemas.reserva import (
    OcurrenciaInput,
    OcurrenciaOmitida,
    ReservaCreate,
    ReservaGrupoCreate,
    ReservaUpdate,
)
from app.services.actores import columnas_actor, es_actor
from app.services.auditoria import registrar_cambio
from app.services.calendario import (
    encolar_actualizacion_calendario,
    encolar_cancelacion_calendario,
    encolar_invitacion_calendario,
)
from app.services.email import Adjunto, encolar_correo, procesar_pendientes
from app.services.ics import construir_ics
from app.services.email_templates import (
    plantilla_contrapropuesta_tecnico,
    plantilla_propuesta_horarios,
    plantilla_reserva_actualizada,
    plantilla_reserva_cancelada_por_usuario,
    plantilla_reserva_eliminada,
    plantilla_reserva_estado,
    plantilla_reserva_pendiente,
    plantilla_reserva_recibida,
)
from app.services.horarios import horario_cubre_reserva
from app.services.lista_espera import notificar_primero_en_espera
from app.services.preferencias_correo import correo_habilitado
from app.services.reloj import RelojLocal


def _notificar_lista_espera_liberados(db: Session, reserva: Reserva) -> None:
    """Se llama justo después de que `reserva` deja de bloquear horario
    (rechazo, cancelación o borrado) -- avisa a la lista de espera de cada
    recurso efectivamente liberado (Fase 12C-6: `reserva_recursos` es la
    fuente de verdad, no la columna histórica `recurso_id`)."""
    for recurso_id in get_recurso_ids_reserva(db, reserva.id):
        notificar_primero_en_espera(
            db,
            recurso_id=recurso_id,
            fecha=reserva.fecha,
            hora_inicio=reserva.hora_inicio,
            hora_fin=reserva.hora_fin,
        )


def _adjunto_ics_reserva(*, reserva_id: int, espacio: str, fecha, hora_inicio, hora_fin) -> Adjunto:
    """`.ics` de confirmación (Fase 2026-08-29, ronda 2) -- solo se adjunta
    cuando una reserva queda `aprobada` de una (auto-aprobación en
    `crear_reserva`, o el branch `aprobada` de `cambiar_estado`): un `.ics`
    para una reserva `esperando` sería prematuro, la fecha/horario todavía
    puede cambiar o rechazarse."""
    contenido = construir_ics(
        uid=f"reserva-{reserva_id}@reservas-parquei",
        resumen=espacio,
        descripcion=f"Reserva #{reserva_id} confirmada en {espacio}.",
        ubicacion=espacio,
        inicio=datetime.combine(fecha, hora_inicio),
        fin=datetime.combine(fecha, hora_fin),
    )
    return Adjunto(nombre=f"reserva-{reserva_id}.ics", contenido=contenido, content_type="text/calendar")


def _asistentes_evento_calendario(db: Session, laboratorio_id: int, dueno: Personal | Usuario) -> list[tuple[str, str]]:
    """Invitación de Outlook Calendar (2026-09-03): técnico(s) + dueño de
    la reserva, mismo público que ya recibe el correo de "reserva
    pendiente" (join `Personal`+`UsuarioLaboratorio` filtrando
    `rol=gestor`). Deduplicado por email -- un gestor que reserva su propio
    laboratorio es a la vez "técnico" y "dueño"; sin esto quedaría dos
    veces en la lista (dos `ATTENDEE` y dos correos a la misma persona)."""
    gestores = (
        db.query(Personal.username, Personal.email)
        .join(UsuarioLaboratorio, UsuarioLaboratorio.usuario_id == Personal.id)
        .filter(Personal.rol == Rol.GESTOR.value, UsuarioLaboratorio.laboratorio_id == laboratorio_id)
        .all()
    )
    asistentes = [(email, username) for username, email in gestores]
    if not any(email == dueno.email for email, _ in asistentes):
        asistentes.append((dueno.email, dueno.username))
    return asistentes


def _encolar_evento_calendario_crear(db: Session, *, reserva: Reserva, laboratorio: Laboratorio, dueno: Personal | Usuario) -> None:
    """Mismo criterio que `_adjunto_ics_reserva`: solo se encola cuando la
    reserva queda `aprobada` de una. Independiente del toggle de correo
    opcional (`services/preferencias_correo.py`) -- decisión confirmada,
    son dos preferencias separadas."""
    encolar_invitacion_calendario(
        db,
        reserva=reserva,
        laboratorio_nombre=laboratorio.nombre,
        asistentes=_asistentes_evento_calendario(db, laboratorio.id, dueno),
    )


SOLAPAMIENTO_CONSTRAINT = "reservas_sin_solapamiento"
RESERVA_RECURSOS_CONSTRAINT = "reserva_recursos_sin_solapamiento"
RESERVA_ESPACIOS_CONSTRAINT = "reserva_espacios_sin_solapamiento"

# Fase 12C-4d/12C-6: la doble escritura mantiene `reservas` y las tablas de
# asociación sincronizadas, así que un solapamiento puede disparar cualquiera
# de las tres constraints EXCLUDE (depende de qué tabla detecta primero el
# conflicto en el flush de la transacción). Todas se traducen al mismo 409.
_CONSTRAINTS_SOLAPAMIENTO = (
    SOLAPAMIENTO_CONSTRAINT,
    RESERVA_RECURSOS_CONSTRAINT,
    RESERVA_ESPACIOS_CONSTRAINT,
)


def _es_conflicto_solapamiento(exc: IntegrityError) -> bool:
    origen = exc.orig
    diagnostico = getattr(origen, "diag", None)
    constraint_name = getattr(diagnostico, "constraint_name", None)
    return constraint_name in _CONSTRAINTS_SOLAPAMIENTO or any(
        constraint in str(origen) for constraint in _CONSTRAINTS_SOLAPAMIENTO
    )


def _traducir_error_integridad(db: Session, exc: IntegrityError) -> None:
    db.rollback()
    if _es_conflicto_solapamiento(exc):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El recurso acaba de ser reservado en ese horario",
        ) from exc
    raise exc


@dataclass
class _ObjetivoReserva:
    """Conjunto objetivo de una reserva (Fase 12C-6): recursos directos,
    espacios, recursos efectivos (deduplicados, orden estable por id) y el
    laboratorio único al que todos pertenecen."""

    laboratorio: Laboratorio
    recurso_ids: list[int]
    espacio_ids: list[int]
    recursos_efectivos: list[Recurso]
    espacios: list[Espacio]


def _cargar_recursos(db: Session, recurso_ids: list[int]) -> list[Recurso]:
    if not recurso_ids:
        return []
    recursos = db.query(Recurso).filter(Recurso.id.in_(recurso_ids)).all()
    por_id = {r.id: r for r in recursos}
    faltantes = sorted(set(recurso_ids) - set(por_id))
    if faltantes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Los recursos {faltantes} no existen",
        )
    return [por_id[i] for i in sorted(por_id)]


def _cargar_espacios(db: Session, espacio_ids: list[int]) -> list[Espacio]:
    if not espacio_ids:
        return []
    espacios = db.query(Espacio).filter(Espacio.id.in_(espacio_ids)).all()
    por_id = {e.id: e for e in espacios}
    faltantes = sorted(set(espacio_ids) - set(por_id))
    if faltantes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Los espacios {faltantes} no existen",
        )
    return [por_id[i] for i in sorted(por_id)]


def _miembros_espacio(db: Session, espacio: Espacio) -> list[Recurso]:
    return (
        db.query(Recurso)
        .join(EspacioRecurso, EspacioRecurso.recurso_id == Recurso.id)
        .filter(EspacioRecurso.espacio_id == espacio.id)
        .order_by(Recurso.id.asc())
        .all()
    )


def _resolver_objetivo(
    db: Session,
    *,
    recurso_ids: list[int],
    espacio_ids: list[int],
    usuario: Personal | Usuario,
    laboratorio_id_fijo: int | None = None,
) -> _ObjetivoReserva:
    """Resuelve y valida el conjunto objetivo de una reserva (Fase 12C-6).

    Reglas aprobadas aplicadas aquí:
    - Recursos y espacios deben pertenecer a un mismo laboratorio (el de la
      reserva; para edición, `laboratorio_id_fijo` lo fija y valida
      pertenencia).
    - Espacios y recursos efectivos deben estar activos.
    - Recursos efectivos = directos ∪ miembros de los espacios, sin
      duplicados, en orden estable por id.
    """
    directos = _cargar_recursos(db, recurso_ids)
    espacios = _cargar_espacios(db, espacio_ids)

    laboratorios = {r.laboratorio_id for r in directos} | {e.laboratorio_id for e in espacios}
    if not laboratorios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes indicar al menos un recurso o un espacio",
        )
    if len(laboratorios) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los recursos y espacios deben pertenecer al mismo laboratorio",
        )
    laboratorio_id = laboratorios.pop()
    if laboratorio_id_fijo is not None and laboratorio_id != laboratorio_id_fijo:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
                if usuario.rol in {Rol.GESTOR.value, Rol.ADMIN.value}
                else status.HTTP_400_BAD_REQUEST
            ),
            detail="Los recursos y espacios deben pertenecer al laboratorio de la reserva",
        )
    laboratorio = db.query(Laboratorio).filter(Laboratorio.id == laboratorio_id).first()
    if laboratorio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El laboratorio no existe")

    for espacio in espacios:
        if espacio.estado != EstadoEntidad.ACTIVO.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El espacio {espacio.nombre} no está activo para reservas",
            )

    por_id: dict[int, Recurso] = {}
    for recurso in directos:
        if recurso.estado != EstadoEntidad.ACTIVO.value or laboratorio.estado != EstadoEntidad.ACTIVO.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El recurso no está activo para reservas",
            )
        por_id[recurso.id] = recurso
    for espacio in espacios:
        for miembro in _miembros_espacio(db, espacio):
            if miembro.estado != EstadoEntidad.ACTIVO.value or laboratorio.estado != EstadoEntidad.ACTIVO.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El recurso no está activo para reservas",
                )
            por_id[miembro.id] = miembro
    efectivos = [por_id[i] for i in sorted(por_id)]

    return _ObjetivoReserva(
        laboratorio=laboratorio,
        recurso_ids=sorted({r.id for r in directos}),
        espacio_ids=sorted({e.id for e in espacios}),
        recursos_efectivos=efectivos,
        espacios=espacios,
    )


def _resolver_efectivos(
    db: Session,
    recurso_ids: list[int],
    espacio_ids: list[int],
) -> tuple[list[Recurso], list[Espacio], list[Recurso]]:
    """Resuelve recursos directos, espacios y recursos efectivos SIN volver a
    validar actividad — usado en la aprobación, donde los objetivos ya
    fueron validados al crear/editar y solo resta chequear el solapamiento
    transitivo."""
    directos = _cargar_recursos(db, recurso_ids)
    espacios = _cargar_espacios(db, espacio_ids)
    por_id: dict[int, Recurso] = {}
    for recurso in directos:
        por_id[recurso.id] = recurso
    for espacio in espacios:
        for miembro in _miembros_espacio(db, espacio):
            por_id[miembro.id] = miembro
    return directos, espacios, [por_id[i] for i in sorted(por_id)]


def _capacidad_efectiva(laboratorio: Laboratorio, objetivo: _ObjetivoReserva) -> int:
    """Capacidad efectiva = min(laboratorio, espacios definidos, recursos
    efectivos) (decisión aprobada 12C-6)."""
    capacidades = [laboratorio.capacidad]
    capacidades_espacios = [e.capacidad for e in objetivo.espacios if e.capacidad is not None]
    if capacidades_espacios:
        capacidades.append(min(capacidades_espacios))
    if objetivo.recursos_efectivos:
        capacidades.append(min(r.capacidad for r in objetivo.recursos_efectivos))
    return min(capacidades)


def _recurso_ancla(db: Session, laboratorio: Laboratorio, recursos_efectivos: list[Recurso]) -> int:
    """Recurso efectivo canónico (orden estable) para la columna histórica
    `Reserva.recurso_id` (Fase 12C-6). La columna es NOT NULL y las
    migraciones están congeladas, así que un espacio sin recursos efectivos
    se ancla al recurso de menor id de su laboratorio; riesgo residual
    documentado (la EXCLUDE histórica podría, en un caso extremo, chocar con
    una reserva directa de ese recurso ancla). Sin recurso en el
    laboratorio, la reserva es irrepresentable y se rechaza con 400."""
    if recursos_efectivos:
        return min(r.id for r in recursos_efectivos)
    recurso = (
        db.query(Recurso)
        .filter(Recurso.laboratorio_id == laboratorio.id)
        .order_by(Recurso.id.asc())
        .first()
    )
    if recurso is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El espacio sin recursos asociados no puede reservarse mientras la columna recurso_id sea obligatoria",
        )
    return recurso.id


def _validar_solapamiento_efectivos(
    db: Session,
    recursos_efectivos: list[Recurso],
    espacios: list[Espacio],
    *,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    exclude_id: int | None = None,
) -> None:
    """Solapamiento transitivo (Fase 12C-6): cada recurso efectivo contra
    `reserva_recursos` y cada espacio contra `reserva_espacios`. Como todo
    espacio reservado materializa sus recursos efectivos, el cruce
    espacio<->recurso queda cubierto por la misma tabla."""
    for recurso in recursos_efectivos:
        if get_reservas_bloqueantes(db, recurso.id, fecha, hora_inicio, hora_fin, exclude_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El recurso ya tiene una reserva en ese horario",
            )
    for espacio in espacios:
        if get_espacios_bloqueantes(db, espacio.id, fecha, hora_inicio, hora_fin, exclude_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El espacio ya tiene una reserva en ese horario",
            )


def _reescribir_acompanantes(db: Session, reserva: Reserva, acompanantes) -> None:
    """Borra y recrea las filas de `reserva_acompanantes` (Fase 12E, mismo
    idioma borrar+recrear dentro de la misma transacción, sin commit propio).
    `acompanantes` es `list[AcompananteInput]` (Pydantic) o lista de dicts
    con `nombre`/`correo`."""

    from app.models.reserva_acompanante import ReservaAcompanante

    db.query(ReservaAcompanante).filter(ReservaAcompanante.reserva_id == reserva.id).delete(
        synchronize_session=False
    )
    for ac in acompanantes or []:
        nombre = ac.nombre if hasattr(ac, "nombre") else ac["nombre"]
        correo = ac.correo if hasattr(ac, "correo") else ac["correo"]
        db.add(ReservaAcompanante(reserva_id=reserva.id, nombre=nombre, correo=correo))


def _reescribir_asociaciones(db: Session, reserva: Reserva, objetivo: _ObjetivoReserva) -> None:
    """Borra y recrea las filas de `reserva_espacios` y `reserva_recursos` de
    la reserva dentro de la misma transacción (regla aprobada 12C-6). NUNCA
    hace `commit`/`rollback` — el flujo llamante es dueño de la transacción,
    igual que la doble escritura de 12C-4d. Sin filas parciales: cualquier
    fallo en el commit revierte reserva y asociaciones como una sola unidad."""
    db.query(ReservaEspacio).filter(ReservaEspacio.reserva_id == reserva.id).delete(synchronize_session=False)
    db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == reserva.id).delete(synchronize_session=False)
    for espacio in objetivo.espacios:
        db.add(
            ReservaEspacio(
                reserva_id=reserva.id,
                espacio_id=espacio.id,
                fecha=reserva.fecha,
                hora_inicio=reserva.hora_inicio,
                hora_fin=reserva.hora_fin,
                estado=reserva.estado,
            )
        )
    for recurso in objetivo.recursos_efectivos:
        db.add(
            ReservaRecurso(
                reserva_id=reserva.id,
                recurso_id=recurso.id,
                fecha=reserva.fecha,
                hora_inicio=reserva.hora_inicio,
                hora_fin=reserva.hora_fin,
                estado=reserva.estado,
            )
        )


def _sincronizar_campos_asociaciones(db: Session, reserva: Reserva) -> None:
    """Sincroniza las columnas desnormalizadas (fecha/horas/estado) en las
    filas existentes de ambas tablas de asociación cuando NO cambia el
    conjunto objetivo (cambiar/cancelar estado). """
    db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == reserva.id).update(
        {
            ReservaRecurso.fecha: reserva.fecha,
            ReservaRecurso.hora_inicio: reserva.hora_inicio,
            ReservaRecurso.hora_fin: reserva.hora_fin,
            ReservaRecurso.estado: reserva.estado,
        },
        synchronize_session=False,
    )
    db.query(ReservaEspacio).filter(ReservaEspacio.reserva_id == reserva.id).update(
        {
            ReservaEspacio.fecha: reserva.fecha,
            ReservaEspacio.hora_inicio: reserva.hora_inicio,
            ReservaEspacio.hora_fin: reserva.hora_fin,
            ReservaEspacio.estado: reserva.estado,
        },
        synchronize_session=False,
    )


def _etiqueta_objetivo(objetivo: _ObjetivoReserva) -> str:
    partes = []
    if objetivo.espacios:
        partes.append("el espacio " + ", ".join(e.nombre for e in objetivo.espacios))
    if objetivo.recursos_efectivos:
        partes.append(
            "los recursos " + ", ".join(sorted({r.nombre for r in objetivo.recursos_efectivos}))
        )
    return "de " + " y ".join(partes) if partes else ""


def preparar_reserva(db: Session) -> None:
    try:
        db.flush()
    except IntegrityError as exc:
        _traducir_error_integridad(db, exc)


def confirmar_cambios_reserva(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        _traducir_error_integridad(db, exc)


def validar_horario(laboratorio: Laboratorio, fecha: date, hora_inicio: time, hora_fin: time) -> None:
    if hora_inicio >= hora_fin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La hora de inicio debe ser menor que la hora de fin")

    if not horario_cubre_reserva(laboratorio, fecha.weekday(), hora_inicio, hora_fin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El horario seleccionado no está habilitado en la configuración del laboratorio",
        )


def validar_anticipacion(
    laboratorio: Laboratorio,
    fecha: date,
    hora_inicio: time,
    reloj: Reloj | None = None,
) -> None:
    inicio = datetime.combine(fecha, hora_inicio)
    fecha_minima = (reloj or RelojLocal()).ahora() + timedelta(hours=laboratorio.horas_antelacion)
    if inicio < fecha_minima:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La reserva debe hacerse con mínimo {laboratorio.horas_antelacion} horas de anticipación",
        )


def validar_solapamiento(
    db: Session,
    recurso_id: int,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    exclude_id: int | None = None,
) -> None:
    bloqueantes = get_reservas_bloqueantes(db, recurso_id, fecha, hora_inicio, hora_fin, exclude_id)
    if bloqueantes:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El recurso ya tiene una reserva en ese horario")


def validar_transicion_estado(
    estado_actual: str | EstadoReserva,
    nuevo_estado: str | EstadoReserva,
) -> None:
    actual = EstadoReserva(estado_actual)
    nuevo = EstadoReserva(nuevo_estado)
    if not actual.puede_transicionar_a(nuevo):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede cambiar una reserva de {actual.value} a {nuevo.value}",
        )


def validar_recurso_activo(recurso: Recurso | None) -> None:
    if recurso is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El recurso solicitado no existe")
    if recurso.estado != EstadoEntidad.ACTIVO.value or recurso.laboratorio.estado != EstadoEntidad.ACTIVO.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El recurso no está activo para reservas")


def validar_capacidad(asistentes: int, recurso_capacidad: int) -> None:
    if asistentes > recurso_capacidad:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cantidad de asistentes supera la capacidad del recurso")


def _validar_objetivo(
    db: Session,
    objetivo: _ObjetivoReserva,
    *,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    asistentes: int,
    exclude_id: int | None = None,
) -> None:
    validar_horario(objetivo.laboratorio, fecha, hora_inicio, hora_fin)
    validar_anticipacion(objetivo.laboratorio, fecha, hora_inicio)
    if asistentes > _capacidad_efectiva(objetivo.laboratorio, objetivo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cantidad de asistentes supera la capacidad efectiva de la reserva",
        )
    _validar_solapamiento_efectivos(
        db,
        objetivo.recursos_efectivos,
        objetivo.espacios,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        exclude_id=exclude_id,
    )


def _validar_tipo_reserva(db: Session, tipo_reserva_id: int | None, laboratorio_id: int) -> None:
    """Fase 7: si se manda `tipo_reserva_id`, tiene que existir y ser del
    mismo laboratorio que la reserva -- mismo criterio que la validación de
    recursos/espacios "fuera de laboratorio" en app/api/espacios.py."""
    if tipo_reserva_id is None:
        return
    tipo_reserva = db.query(TipoReserva).filter(TipoReserva.id == tipo_reserva_id).first()
    if tipo_reserva is None:
        raise HTTPException(status_code=404, detail="Tipo de reserva no encontrado")
    if tipo_reserva.laboratorio_id != laboratorio_id:
        raise HTTPException(
            status_code=400,
            detail="El tipo de reserva no pertenece al laboratorio de la reserva",
        )


def _validar_motivo_solicitud(db: Session, motivo_solicitud_id: int | None, laboratorio_id: int) -> None:
    if motivo_solicitud_id is None:
        return
    motivo = db.query(MotivoSolicitud).filter(MotivoSolicitud.id == motivo_solicitud_id).first()
    if motivo is None:
        raise HTTPException(status_code=404, detail="Motivo de solicitud no encontrado")
    if motivo.laboratorio_id != laboratorio_id:
        raise HTTPException(status_code=400, detail="El motivo no pertenece al laboratorio de la reserva")


def _apoyo_auxiliar_forzado(objetivo: _ObjetivoReserva) -> bool:
    """Si algún recurso efectivo (directo o cubierto por un espacio
    seleccionado) exige acompañamiento del auxiliar/técnico, la reserva
    hereda esa obligación sin importar lo que haya mandado el cliente --
    nunca se rechaza con un error, simplemente se activa por la persona
    (mismo criterio silencioso que "recursos cubiertos por un espacio se
    agregan solos")."""
    return any(r.requiere_apoyo_auxiliar for r in objetivo.recursos_efectivos)


def crear_reserva(
    db: Session, data: ReservaCreate, usuario: Personal | Usuario, *, grupo_id: uuid.UUID | None = None
) -> Reserva:
    objetivo = _resolver_objetivo(
        db,
        recurso_ids=data.recurso_ids,
        espacio_ids=data.espacio_ids,
        usuario=usuario,
    )
    _validar_objetivo(
        db,
        objetivo,
        fecha=data.fecha,
        hora_inicio=data.hora_inicio,
        hora_fin=data.hora_fin,
        asistentes=data.asistentes,
    )
    laboratorio_gestionado = get_managed_laboratory_id(db, usuario) if usuario.rol == Rol.GESTOR.value else None
    aprobacion_automatica = objetivo.laboratorio.aprobacion_automatica or laboratorio_gestionado == objetivo.laboratorio.id
    _validar_tipo_reserva(db, data.tipo_reserva_id, objetivo.laboratorio.id)
    _validar_motivo_solicitud(db, data.motivo_solicitud_id, objetivo.laboratorio.id)

    # Validar motivo_solicitud_id y su relación con ubicacion_uso
    if data.motivo_solicitud_id is not None:
        motivo_obj = db.query(MotivoSolicitud).filter(MotivoSolicitud.id == data.motivo_solicitud_id).first()
        if motivo_obj and motivo_obj.codigo == "reserva_fuera_laboratorio" and not data.ubicacion_uso:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ubicacion_uso es requerido para reserva fuera del laboratorio")
    reserva = Reserva(
        **columnas_actor(usuario),
        laboratorio_id=objetivo.laboratorio.id,
        recurso_id=_recurso_ancla(db, objetivo.laboratorio, objetivo.recursos_efectivos),
        fecha=data.fecha,
        hora_inicio=data.hora_inicio,
        hora_fin=data.hora_fin,
        asistentes=data.asistentes,
        tipo=data.tipo,
        tipo_reserva_id=data.tipo_reserva_id,
        descripcion=data.descripcion,
        tipo_solicitud=data.tipo_solicitud,
        motivo_solicitud_id=data.motivo_solicitud_id,
        ubicacion_uso=data.ubicacion_uso,
        requiere_apoyo_auxiliar=data.requiere_apoyo_auxiliar or _apoyo_auxiliar_forzado(objetivo),
        estado=(
            EstadoReserva.APROBADA.value if aprobacion_automatica else EstadoReserva.ESPERANDO.value
        ),
        grupo_id=grupo_id,
    )
    db.add(reserva)
    preparar_reserva(db)
    _reescribir_asociaciones(db, reserva, objetivo)
    _reescribir_acompanantes(db, reserva, data.acompanantes)
    if not aprobacion_automatica:
        gestores = (
            db.query(Personal.id, Personal.username, Personal.email, Personal.recibir_correos)
            .join(UsuarioLaboratorio, UsuarioLaboratorio.usuario_id == Personal.id)
            .filter(
                Personal.rol == Rol.GESTOR.value,
                UsuarioLaboratorio.laboratorio_id == objetivo.laboratorio.id,
            )
            .all()
        )
        for gestor_id, gestor_username, gestor_email, gestor_recibir_correos in gestores:
            db.add(
                Notificacion(
                    personal_id=gestor_id,
                    reserva_id=reserva.id,
                    tipo=TipoNotificacion.PENDIENTE.value,
                )
            )
            if objetivo.laboratorio.notificar_por_correo and gestor_recibir_correos:
                encolar_correo(
                    db,
                    destinatario=gestor_email,
                    asunto="Nueva reserva pendiente de aprobación",
                    cuerpo=plantilla_reserva_pendiente(
                        nombre_saludo=gestor_username,
                        espacio=objetivo.laboratorio.nombre,
                        fecha=str(data.fecha),
                        hora_inicio=str(data.hora_inicio),
                        hora_fin=str(data.hora_fin),
                        reserva_id=reserva.id,
                    ),
                    es_html=True,
                )
        if correo_habilitado(objetivo.laboratorio, usuario):
            encolar_correo(
                db,
                destinatario=usuario.email,
                asunto="Recibimos tu solicitud de reserva",
                cuerpo=plantilla_reserva_recibida(
                    nombre_saludo=usuario.username,
                    espacio=objetivo.laboratorio.nombre,
                    fecha=str(data.fecha),
                    hora_inicio=str(data.hora_inicio),
                    hora_fin=str(data.hora_fin),
                    reserva_id=reserva.id,
                ),
                es_html=True,
            )
    else:
        if correo_habilitado(objetivo.laboratorio, usuario):
            encolar_correo(
                db,
                destinatario=usuario.email,
                asunto="Tu reserva fue aprobada",
                cuerpo=plantilla_reserva_estado(
                    nombre_saludo=usuario.username,
                    reserva_id=reserva.id,
                    espacio=objetivo.laboratorio.nombre,
                    fecha=str(data.fecha),
                    hora_inicio=str(data.hora_inicio),
                    hora_fin=str(data.hora_fin),
                    estado="aprobada",
                ),
                es_html=True,
                adjunto=_adjunto_ics_reserva(
                    reserva_id=reserva.id,
                    espacio=objetivo.laboratorio.nombre,
                    fecha=data.fecha,
                    hora_inicio=data.hora_inicio,
                    hora_fin=data.hora_fin,
                ),
            )
        _encolar_evento_calendario_crear(db, reserva=reserva, laboratorio=objetivo.laboratorio, dueno=usuario)
    registrar_cambio(
        db,
        usuario,
        "crear",
        "reserva",
        reserva.id,
        f"Creó una reserva {_etiqueta_objetivo(objetivo)} con estado {reserva.estado}",
    )
    confirmar_cambios_reserva(db)
    procesar_pendientes(db)
    db.refresh(reserva)
    return get_reserva(db, reserva.id) or reserva


def crear_reservas_grupo(
    db: Session, data: ReservaGrupoCreate, usuario: Personal | Usuario
) -> tuple[uuid.UUID, list[Reserva], list[OcurrenciaOmitida]]:
    """Reservas multi-día agrupadas (2026-09-03): "mejor esfuerzo", mismo
    mecanismo que tenía `crear_reserva_serie` (revertida) -- cada ocurrencia
    se crea con su propia llamada a `crear_reserva` (que hace su propio
    commit), así que un 409/400 en una ocurrencia solo revierte esa
    ocurrencia, nunca las ya confirmadas."""
    grupo_id = uuid.uuid4()
    creadas: list[Reserva] = []
    omitidas: list[OcurrenciaOmitida] = []
    for ocurrencia in data.ocurrencias:
        individual = ReservaCreate(
            recurso_ids=data.recurso_ids,
            espacio_ids=data.espacio_ids,
            tipo=data.tipo,
            tipo_reserva_id=data.tipo_reserva_id,
            acompanantes=data.acompanantes,
            descripcion=data.descripcion,
            tipo_solicitud=data.tipo_solicitud,
            ubicacion_uso=data.ubicacion_uso,
            requiere_apoyo_auxiliar=data.requiere_apoyo_auxiliar,
            motivo_solicitud_id=data.motivo_solicitud_id,
            fecha=ocurrencia.fecha,
            hora_inicio=ocurrencia.hora_inicio,
            hora_fin=ocurrencia.hora_fin,
            asistentes=data.asistentes,
        )
        try:
            creadas.append(crear_reserva(db, individual, usuario, grupo_id=grupo_id))
        except HTTPException as exc:
            omitidas.append(
                OcurrenciaOmitida(
                    fecha=ocurrencia.fecha,
                    hora_inicio=ocurrencia.hora_inicio,
                    hora_fin=ocurrencia.hora_fin,
                    motivo=str(exc.detail),
                )
            )
    return grupo_id, creadas, omitidas


def cambiar_estado(
    db: Session, reserva_id: int, nuevo_estado: str, admin_user: Personal, motivo: str | None = None
) -> Reserva:
    if admin_user.rol not in {Rol.ADMIN.value, Rol.GESTOR.value}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para cambiar el estado de una reserva")
    nuevo = EstadoReserva(nuevo_estado)
    if nuevo not in {EstadoReserva.APROBADA, EstadoReserva.RECHAZADA, EstadoReserva.CANCELADA}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El estado solo puede cambiarse a aprobada, rechazada o cancelada",
        )
    if nuevo == EstadoReserva.RECHAZADA:
        if motivo is None or len(motivo.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debes indicar el motivo del rechazo",
            )
        motivo = motivo.strip()
        if len(motivo) > 500:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El motivo no puede superar los 500 caracteres",
            )

    reserva = get_reserva(db, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La reserva no existe")
    laboratorio_gestionado = get_managed_laboratory_id(db, admin_user)
    if laboratorio_gestionado is not None and reserva.laboratorio_id != laboratorio_gestionado:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes gestionar reservas de tu laboratorio")
    validar_transicion_estado(reserva.estado, nuevo)
    if nuevo == EstadoReserva.APROBADA and reserva.estado != nuevo.value:
        _, espacios, efectivos = _resolver_efectivos(
            db,
            get_recurso_ids_reserva(db, reserva.id),
            get_espacio_ids_reserva(db, reserva.id),
        )
        _validar_solapamiento_efectivos(
            db,
            efectivos,
            espacios,
            fecha=reserva.fecha,
            hora_inicio=reserva.hora_inicio,
            hora_fin=reserva.hora_fin,
            exclude_id=reserva.id,
        )
    estado_anterior = reserva.estado
    reserva.estado = nuevo.value
    if nuevo == EstadoReserva.RECHAZADA:
        reserva.motivo_rechazo = motivo
    else:
        reserva.motivo_rechazo = None
    if estado_anterior != nuevo.value:
        tipo_notificacion = {
            EstadoReserva.APROBADA: TipoNotificacion.APROBADA,
            EstadoReserva.RECHAZADA: TipoNotificacion.RECHAZADA,
            EstadoReserva.CANCELADA: TipoNotificacion.CANCELADA,
        }[nuevo].value
        db.add(
            Notificacion(
                **columnas_actor(reserva.actor),
                reserva_id=reserva.id,
                tipo=tipo_notificacion,
            )
        )
        estado_legible = {
            EstadoReserva.APROBADA: "aprobada",
            EstadoReserva.RECHAZADA: "rechazada",
            EstadoReserva.CANCELADA: "cancelada",
        }[nuevo]
        if correo_habilitado(reserva.laboratorio, reserva.actor):
            encolar_correo(
                db,
                destinatario=reserva.actor.email,
                asunto=f"Tu reserva fue {estado_legible}",
                cuerpo=plantilla_reserva_estado(
                    nombre_saludo=reserva.actor.username,
                    reserva_id=reserva.id,
                    espacio=reserva.laboratorio.nombre,
                    fecha=str(reserva.fecha),
                    hora_inicio=str(reserva.hora_inicio),
                    hora_fin=str(reserva.hora_fin),
                    estado=estado_legible,
                    motivo=motivo,
                ),
                es_html=True,
                adjunto=(
                    _adjunto_ics_reserva(
                        reserva_id=reserva.id,
                        espacio=reserva.laboratorio.nombre,
                        fecha=reserva.fecha,
                        hora_inicio=reserva.hora_inicio,
                        hora_fin=reserva.hora_fin,
                    )
                    if nuevo == EstadoReserva.APROBADA
                    else None
                ),
            )
        if nuevo == EstadoReserva.APROBADA:
            _encolar_evento_calendario_crear(db, reserva=reserva, laboratorio=reserva.laboratorio, dueno=reserva.actor)
        elif nuevo == EstadoReserva.CANCELADA and reserva.graph_event_id is not None:
            encolar_cancelacion_calendario(
                db,
                reserva=reserva,
                laboratorio_nombre=reserva.laboratorio.nombre,
                asistentes=_asistentes_evento_calendario(db, reserva.laboratorio_id, reserva.actor),
            )
        if nuevo in {EstadoReserva.RECHAZADA, EstadoReserva.CANCELADA} and estado_anterior in ESTADOS_BLOQUEANTES:
            _notificar_lista_espera_liberados(db, reserva)
        mensaje_auditoria = f"Cambió la reserva #{reserva.id} de {estado_anterior} a {nuevo.value}"
        if nuevo == EstadoReserva.RECHAZADA and motivo:
            mensaje_auditoria += f" - Motivo: {motivo}"
        registrar_cambio(
            db,
            admin_user,
            "cambiar estado",
            "reserva",
            reserva.id,
            mensaje_auditoria,
        )
    _sincronizar_campos_asociaciones(db, reserva)
    confirmar_cambios_reserva(db)
    procesar_pendientes(db)
    db.refresh(reserva)
    return get_reserva(db, reserva.id) or reserva


def _validar_propuesta_texto(motivo: str, horarios: str) -> tuple[str, str]:
    motivo = motivo.strip()
    horarios = horarios.strip()
    if not motivo or not horarios:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Motivo y horarios son obligatorios")
    if len(motivo) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El motivo no puede superar los 500 caracteres")
    if len(horarios) > 1000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Los horarios no pueden superar los 1000 caracteres")
    return motivo, horarios


def proponer_horarios(
    db: Session, reserva_id: int, motivo: str, horarios: str, tecnico: Personal
) -> Reserva:
    """Fase C: el técnico propone horarios alternativos sin cambiar estado."""
    if tecnico.rol not in {Rol.ADMIN.value, Rol.GESTOR.value}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el técnico puede proponer horarios")
    motivo, horarios = _validar_propuesta_texto(motivo, horarios)
    reserva = get_reserva(db, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La reserva no existe")
    if reserva.estado != EstadoReserva.ESPERANDO.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo se puede proponer horarios para reservas pendientes")
    laboratorio_gestionado = get_managed_laboratory_id(db, tecnico)
    if laboratorio_gestionado is not None and reserva.laboratorio_id != laboratorio_gestionado:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes gestionar reservas de tu laboratorio")
    reserva.propuesta_motivo = motivo
    reserva.propuesta_horarios = horarios
    reserva.propuesta_por = "tecnico"
    reserva.propuesta_en = datetime.now(timezone.utc)
    # Notificación + correo al dueño
    db.add(
        Notificacion(
            **columnas_actor(reserva.actor),
            reserva_id=reserva.id,
            tipo=TipoNotificacion.ACTUALIZADA.value,
        )
    )
    if correo_habilitado(reserva.laboratorio, reserva.actor):
        encolar_correo(
            db,
            destinatario=reserva.actor.email,
            asunto=f"Tu reserva #{reserva.id} tiene una propuesta de nuevo horario",
            cuerpo=plantilla_propuesta_horarios(
                nombre_saludo=reserva.actor.username,
                reserva_id=reserva.id,
                espacio=reserva.laboratorio.nombre,
                fecha=str(reserva.fecha),
                hora_inicio=str(reserva.hora_inicio),
                hora_fin=str(reserva.hora_fin),
                motivo=motivo,
                horarios=horarios,
                es_contrapropuesta=False,
            ),
            es_html=True,
        )
    registrar_cambio(
        db,
        tecnico,
        "proponer horarios",
        "reserva",
        reserva.id,
        f"Propuso horarios para #{reserva.id}: {horarios} - Motivo: {motivo}",
    )
    confirmar_cambios_reserva(db)
    procesar_pendientes(db)
    db.refresh(reserva)
    return get_reserva(db, reserva.id) or reserva


def contraproponer(
    db: Session, reserva_id: int, motivo: str, horarios: str, usuario: Personal | Usuario
) -> Reserva:
    """Fase C: el usuario contrapropone horarios al técnico."""
    motivo, horarios = _validar_propuesta_texto(motivo, horarios)
    reserva = get_reserva(db, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La reserva no existe")
    if not es_actor(reserva, usuario):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el dueño de la reserva puede contraproponer")
    if reserva.estado != EstadoReserva.ESPERANDO.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo se puede contraproponer para reservas pendientes")
    if reserva.propuesta_por != "tecnico":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo puedes contraproponer cuando el técnico te propuso horarios")
    reserva.propuesta_motivo = motivo
    reserva.propuesta_horarios = horarios
    reserva.propuesta_por = "usuario"
    reserva.propuesta_en = datetime.now(timezone.utc)
    # Notificar a gestores del laboratorio
    gestores = (
        db.query(Personal.id, Personal.username, Personal.email, Personal.recibir_correos)
        .join(UsuarioLaboratorio, UsuarioLaboratorio.usuario_id == Personal.id)
        .filter(Personal.rol == Rol.GESTOR.value, UsuarioLaboratorio.laboratorio_id == reserva.laboratorio_id)
        .all()
    )
    # También admin ve todo, pero el correo al menos a gestores; admin puede ver en UI
    for _, _, gestor_email, gestor_recibir_correos in gestores:
        if reserva.laboratorio.notificar_por_correo and gestor_recibir_correos:
            encolar_correo(
                db,
                destinatario=gestor_email,
                asunto=f"Contrapropuesta para reserva #{reserva.id}",
                cuerpo=plantilla_contrapropuesta_tecnico(
                    nombre_saludo=reserva.actor.username,
                    reserva_id=reserva.id,
                    espacio=reserva.laboratorio.nombre,
                    fecha=str(reserva.fecha),
                    hora_inicio=str(reserva.hora_inicio),
                    hora_fin=str(reserva.hora_fin),
                    motivo=motivo,
                    horarios=horarios,
                ),
                es_html=True,
            )
    # Notificación al técnico no es directa (no hay actor único), se usa auditoría; el gestor verá en su bandeja si filtramos por laboratorio
    db.add(
        Notificacion(
            **columnas_actor(reserva.actor),
            reserva_id=reserva.id,
            tipo=TipoNotificacion.ACTUALIZADA.value,
        )
    )
    registrar_cambio(
        db,
        usuario,
        "contraproponer",
        "reserva",
        reserva.id,
        f"Contrapropuso para #{reserva.id}: {horarios} - Motivo: {motivo}",
    )
    confirmar_cambios_reserva(db)
    procesar_pendientes(db)
    db.refresh(reserva)
    return get_reserva(db, reserva.id) or reserva


def aceptar_propuesta(
    db: Session, reserva_id: int, fecha: date, hora_inicio: time, hora_fin: time, actor: Personal | Usuario
) -> Reserva:
    """Fase C: acepta la propuesta vigente re-agendando la reserva."""
    reserva = get_reserva(db, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La reserva no existe")
    if reserva.estado != EstadoReserva.ESPERANDO.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo se puede aceptar propuesta para reservas pendientes")
    if not reserva.propuesta_horarios or not reserva.propuesta_por:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No hay propuesta vigente para aceptar")
    # Quién puede aceptar: si la propuesta es del técnico, solo el dueño; si es del usuario, solo gestor/admin del lab
    if reserva.propuesta_por == "tecnico":
        if not es_actor(reserva, actor):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el dueño puede aceptar la propuesta del técnico")
    else:  # propuesta_por == usuario
        if actor.rol not in {Rol.ADMIN.value, Rol.GESTOR.value}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el técnico puede aceptar la contrapropuesta")
        lab_gestionado = get_managed_laboratory_id(db, actor)
        if lab_gestionado is not None and reserva.laboratorio_id != lab_gestionado:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes gestionar reservas de tu laboratorio")
    if hora_inicio >= hora_fin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La hora de inicio debe ser menor que la hora de fin")
    # Validar contra el laboratorio y solapamiento (mismo que crear/editar)
    objetivo = _resolver_objetivo(
        db,
        recurso_ids=get_recurso_ids_reserva(db, reserva.id),
        espacio_ids=get_espacio_ids_reserva(db, reserva.id),
        usuario=actor if isinstance(actor, Personal) else reserva.actor,  # para validar laboratorio fijo
        laboratorio_id_fijo=reserva.laboratorio_id,
    )
    _validar_objetivo(
        db,
        objetivo,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        asistentes=reserva.asistentes,
        exclude_id=reserva.id,
    )
    # Todo ok: re-agendar y limpiar propuesta
    reserva.fecha = fecha
    reserva.hora_inicio = hora_inicio
    reserva.hora_fin = hora_fin
    # recurso ancla puede necesitar recalcular si el objetivo cambió de laboratorio? No, laboratorio fijo, así que igual
    reserva.propuesta_motivo = None
    reserva.propuesta_horarios = None
    reserva.propuesta_por = None
    reserva.propuesta_en = None
    _reescribir_asociaciones(db, reserva, objetivo)  # recrea con nueva fecha/hora pero mismo objetivo
    # Notificar al otro lado
    otro_email = None
    otro_nombre = None
    if actor_es_dueno := es_actor(reserva, actor):
        # dueño aceptó propuesta del técnico → avisar a gestores
        gestores = (
            db.query(Personal.email, Personal.username, Personal.recibir_correos)
            .join(UsuarioLaboratorio, UsuarioLaboratorio.usuario_id == Personal.id)
            .filter(Personal.rol == Rol.GESTOR.value, UsuarioLaboratorio.laboratorio_id == reserva.laboratorio_id)
            .all()
        )
        for email, username, gestor_recibir_correos in gestores:
            if reserva.laboratorio.notificar_por_correo and gestor_recibir_correos:
                encolar_correo(
                    db,
                    destinatario=email,
                    asunto=f"Propuesta aceptada para reserva #{reserva.id}",
                    cuerpo=plantilla_reserva_actualizada(
                        nombre_saludo=username,
                        reserva_id=reserva.id,
                        espacio=reserva.laboratorio.nombre,
                        fecha=str(fecha),
                        hora_inicio=str(hora_inicio),
                        hora_fin=str(hora_fin),
                        detalle=f"nuevo horario {fecha} {hora_inicio}-{hora_fin}",
                    ),
                    es_html=True,
                )
        # Notificación al dueño ya no hace falta (él aceptó)
        registrar_cambio(db, actor, "aceptar propuesta", "reserva", reserva.id, f"Aceptó propuesta y re-agendó #{reserva.id} a {fecha} {hora_inicio}-{hora_fin}")
    else:
        # técnico aceptó contrapropuesta del usuario → avisar al dueño
        otro_email = reserva.actor.email
        otro_nombre = reserva.actor.username
        if correo_habilitado(reserva.laboratorio, reserva.actor):
            encolar_correo(
                db,
                destinatario=otro_email,
                asunto=f"Tu contrapropuesta para #{reserva.id} fue aceptada",
                cuerpo=plantilla_propuesta_horarios(
                    nombre_saludo=otro_nombre,
                    reserva_id=reserva.id,
                    espacio=reserva.laboratorio.nombre,
                    fecha=str(fecha),
                    hora_inicio=str(hora_inicio),
                    hora_fin=str(hora_fin),
                    motivo="Tu propuesta fue aceptada",
                    horarios=f"{fecha} {hora_inicio}-{hora_fin}",
                    es_contrapropuesta=True,
                ),
                es_html=True,
            )
        db.add(Notificacion(**columnas_actor(reserva.actor), reserva_id=reserva.id, tipo=TipoNotificacion.ACTUALIZADA.value))
        registrar_cambio(db, actor, "aceptar contrapropuesta", "reserva", reserva.id, f"Aceptó contrapropuesta y re-agendó #{reserva.id} a {fecha} {hora_inicio}-{hora_fin}")
    _sincronizar_campos_asociaciones(db, reserva)
    confirmar_cambios_reserva(db)
    procesar_pendientes(db)
    db.refresh(reserva)
    return get_reserva(db, reserva.id) or reserva


def rechazar_propuesta(
    db: Session, reserva_id: int, actor: Personal | Usuario
) -> Reserva:
    """Fase C: rechaza la propuesta vigente y la limpia, queda `esperando`."""
    reserva = get_reserva(db, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La reserva no existe")
    if reserva.estado != EstadoReserva.ESPERANDO.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo se puede rechazar propuesta para reservas pendientes")
    if not reserva.propuesta_horarios:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No hay propuesta vigente para rechazar")
    # Quién puede rechazar: dueño si propuesta es de técnico, técnico si es de usuario
    if reserva.propuesta_por == "tecnico" and not es_actor(reserva, actor):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el dueño puede rechazar la propuesta del técnico")
    if reserva.propuesta_por == "usuario" and actor.rol not in {Rol.ADMIN.value, Rol.GESTOR.value}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el técnico puede rechazar la contrapropuesta")
    if reserva.propuesta_por == "usuario":
        lab_gestionado = get_managed_laboratory_id(db, actor)
        if lab_gestionado is not None and reserva.laboratorio_id != lab_gestionado:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes gestionar reservas de tu laboratorio")
    propuesta_previa = reserva.propuesta_horarios
    reserva.propuesta_motivo = None
    reserva.propuesta_horarios = None
    reserva.propuesta_por = None
    reserva.propuesta_en = None
    # Notificar al otro lado
    if es_actor(reserva, actor):
        # dueño rechazó propuesta del técnico → avisar a gestores
        gestores = (
            db.query(Personal.email, Personal.username, Personal.recibir_correos)
            .join(UsuarioLaboratorio, UsuarioLaboratorio.usuario_id == Personal.id)
            .filter(Personal.rol == Rol.GESTOR.value, UsuarioLaboratorio.laboratorio_id == reserva.laboratorio_id)
            .all()
        )
        for email, username, gestor_recibir_correos in gestores:
            if reserva.laboratorio.notificar_por_correo and gestor_recibir_correos:
                encolar_correo(
                    db,
                    destinatario=email,
                    asunto=f"Propuesta rechazada para reserva #{reserva.id}",
                    cuerpo=f"<p>{html.escape(actor.username)} rechazó tu propuesta de horarios para la reserva #{reserva.id}. La reserva sigue pendiente con su horario original.</p>",
                    es_html=True,
                )
    else:
        if correo_habilitado(reserva.laboratorio, reserva.actor):
            encolar_correo(
                db,
                destinatario=reserva.actor.email,
                asunto=f"Tu contrapropuesta para #{reserva.id} fue rechazada",
                cuerpo=f"<p>Tu contrapropuesta para la reserva #{reserva.id} fue rechazada. La reserva sigue pendiente; el técnico podrá proponerte nuevos horarios.</p>",
                es_html=True,
            )
        db.add(Notificacion(**columnas_actor(reserva.actor), reserva_id=reserva.id, tipo=TipoNotificacion.ACTUALIZADA.value))
    registrar_cambio(db, actor, "rechazar propuesta", "reserva", reserva.id, f"Rechazó propuesta {propuesta_previa} para #{reserva.id}")
    confirmar_cambios_reserva(db)
    procesar_pendientes(db)
    db.refresh(reserva)
    return get_reserva(db, reserva.id) or reserva


def marcar_asistencia(db: Session, reserva_id: int, asistio: bool, admin_user: Personal) -> Reserva:
    """Fase 12D-bis: marca la asistencia real de una reserva.

    Copia el molde de `cambiar_estado` pero sin máquina de estados: solo
    verifica rol gestor/admin, existencia de la reserva y pertenencia del
    gestor a su laboratorio asignado. No hay transición que validar ni
    solapamiento que re-evaluar; solo se persiste `asistio` y se audita.
    """

    if admin_user.rol not in {Rol.ADMIN.value, Rol.GESTOR.value}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para marcar la asistencia de una reserva",
        )
    reserva = get_reserva(db, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La reserva no existe")
    laboratorio_gestionado = get_managed_laboratory_id(db, admin_user)
    if laboratorio_gestionado is not None and reserva.laboratorio_id != laboratorio_gestionado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes gestionar reservas de tu laboratorio"
        )
    reserva.asistio = asistio
    registrar_cambio(
        db,
        admin_user,
        "marcar_asistencia",
        "reserva",
        reserva.id,
        f"Marcó asistencia={asistio} en la reserva #{reserva.id}",
    )
    confirmar_cambios_reserva(db)
    db.refresh(reserva)
    return get_reserva(db, reserva.id) or reserva


def cancelar_reserva_usuario(db: Session, reserva_id: int, usuario: Personal | Usuario) -> Reserva:
    reserva = get_reserva(db, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La reserva no existe")
    if not es_actor(reserva, usuario):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes cancelar tus propias reservas")
    if reserva.estado != EstadoReserva.APROBADA.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo puedes cancelar reservas aprobadas",
        )

    reserva.estado = EstadoReserva.CANCELADA.value
    gestores = (
        db.query(Personal.id, Personal.username, Personal.email, Personal.recibir_correos)
        .join(UsuarioLaboratorio, UsuarioLaboratorio.usuario_id == Personal.id)
        .filter(
            Personal.rol == Rol.GESTOR.value,
            UsuarioLaboratorio.laboratorio_id == reserva.laboratorio_id,
        )
        .all()
    )
    for gestor_id, gestor_username, gestor_email, gestor_recibir_correos in gestores:
        db.add(
            Notificacion(
                personal_id=gestor_id,
                reserva_id=reserva.id,
                tipo=TipoNotificacion.CANCELADA.value,
            )
        )
        if reserva.laboratorio.notificar_por_correo and gestor_recibir_correos:
            encolar_correo(
                db,
                destinatario=gestor_email,
                asunto="Se canceló una reserva aprobada",
                cuerpo=plantilla_reserva_cancelada_por_usuario(
                    nombre_saludo=gestor_username,
                    reserva_id=reserva.id,
                    espacio=reserva.laboratorio.nombre,
                    fecha=str(reserva.fecha),
                    hora_inicio=str(reserva.hora_inicio),
                    hora_fin=str(reserva.hora_fin),
                ),
                es_html=True,
            )
    registrar_cambio(
        db,
        usuario,
        "cancelar",
        "reserva",
        reserva.id,
        f"Canceló su reserva #{reserva.id}",
    )
    if reserva.graph_event_id is not None:
        encolar_cancelacion_calendario(
            db,
            reserva=reserva,
            laboratorio_nombre=reserva.laboratorio.nombre,
            asistentes=_asistentes_evento_calendario(db, reserva.laboratorio_id, reserva.actor),
        )
    _notificar_lista_espera_liberados(db, reserva)
    _sincronizar_campos_asociaciones(db, reserva)
    confirmar_cambios_reserva(db)
    procesar_pendientes(db)
    db.refresh(reserva)
    return get_reserva(db, reserva.id) or reserva


def cancelar_grupo(
    db: Session, grupo_id: uuid.UUID, actor: Personal | Usuario
) -> tuple[list[int], list[OcurrenciaOmitida]]:
    """Reservas multi-día agrupadas (2026-09-03): "mejor esfuerzo", mismo
    molde que `cancelar_serie` (revertida) -- cancelar un solo día del
    grupo, sin tocar los demás, sigue siendo posible vía
    `PUT /reservas/{id}/cancelar` (cada ocurrencia es una `Reserva`
    completa e independiente); esto es solo el atajo de "cancelar todas de
    una"."""
    ocurrencias = get_reservas_de_grupo(db, grupo_id, actor)
    canceladas: list[int] = []
    omitidas: list[OcurrenciaOmitida] = []
    for reserva in ocurrencias:
        try:
            cancelar_reserva_usuario(db, reserva.id, actor)
            canceladas.append(reserva.id)
        except HTTPException as exc:
            omitidas.append(
                OcurrenciaOmitida(
                    fecha=reserva.fecha,
                    hora_inicio=reserva.hora_inicio,
                    hora_fin=reserva.hora_fin,
                    motivo=str(exc.detail),
                )
            )
    return canceladas, omitidas


def actualizar_reserva(db: Session, reserva_id: int, data: ReservaUpdate, usuario: Personal | Usuario) -> Reserva:
    reserva = get_reserva(db, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La reserva no existe")
    es_propietario = es_actor(reserva, usuario)
    es_gestor = usuario.rol in {Rol.ADMIN.value, Rol.GESTOR.value}
    if not es_propietario and not es_gestor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes editar tus propias reservas")
    if es_propietario and usuario.rol == Rol.USUARIO.value and reserva.estado != EstadoReserva.ESPERANDO.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo puedes editar reservas pendientes",
        )
    laboratorio_gestionado = get_managed_laboratory_id(db, usuario) if usuario.rol == Rol.GESTOR.value else None
    if not es_propietario and laboratorio_gestionado is not None and reserva.laboratorio_id != laboratorio_gestionado:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes gestionar reservas de tu laboratorio")

    cambios = data.model_dump(exclude_unset=True)
    if not cambios:
        return reserva

    # Capturar conjuntos previos para detectar agregados (Feature B).
    viejos_recurso_ids = set(get_recurso_ids_reserva(db, reserva.id))
    viejos_espacio_ids = set(get_espacio_ids_reserva(db, reserva.id))

    # Ejes de reemplazo completo (Fase 12C-6): un eje ausente se conserva;
    # un eje presente reemplaza el conjunto completo de ese eje.
    recurso_ids = cambios.get("recurso_ids", get_recurso_ids_reserva(db, reserva.id))
    espacio_ids = cambios.get("espacio_ids", get_espacio_ids_reserva(db, reserva.id))
    if not recurso_ids and not espacio_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La reserva debe tener al menos un recurso o un espacio",
        )
    fecha = cambios.get("fecha", reserva.fecha)
    hora_inicio = cambios.get("hora_inicio", reserva.hora_inicio)
    hora_fin = cambios.get("hora_fin", reserva.hora_fin)
    asistentes = cambios.get("asistentes", reserva.asistentes)

    objetivo = _resolver_objetivo(
        db,
        recurso_ids=recurso_ids,
        espacio_ids=espacio_ids,
        usuario=usuario,
        laboratorio_id_fijo=reserva.laboratorio_id,
    )
    _validar_objetivo(
        db,
        objetivo,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        asistentes=asistentes,
        exclude_id=reserva.id,
    )
    # Invitación de Outlook Calendar (2026-09-03): capturado ANTES de
    # reasignar `reserva.fecha`/etc, para comparar contra el horario
    # previo. Solo una reserva ya `aprobada` con evento ya creado
    # (`graph_event_id`) necesita reprogramarlo -- una `esperando` todavía
    # no tiene evento (se crea recién al aprobarse).
    reprogramar_evento_calendario = (
        reserva.estado == EstadoReserva.APROBADA.value
        and reserva.graph_event_id is not None
        and (fecha != reserva.fecha or hora_inicio != reserva.hora_inicio or hora_fin != reserva.hora_fin)
    )
    reserva.fecha = fecha
    reserva.hora_inicio = hora_inicio
    reserva.hora_fin = hora_fin
    reserva.asistentes = asistentes
    reserva.tipo = cambios.get("tipo", reserva.tipo)
    nuevo_tipo_reserva_id = cambios.get("tipo_reserva_id", reserva.tipo_reserva_id)
    _validar_tipo_reserva(db, nuevo_tipo_reserva_id, reserva.laboratorio_id)
    reserva.tipo_reserva_id = nuevo_tipo_reserva_id
    nuevo_motivo_solicitud_id = cambios.get("motivo_solicitud_id", reserva.motivo_solicitud_id)
    _validar_motivo_solicitud(db, nuevo_motivo_solicitud_id, reserva.laboratorio_id)
    reserva.motivo_solicitud_id = nuevo_motivo_solicitud_id
    reserva.descripcion = cambios.get("descripcion", reserva.descripcion)
    nuevo_tipo_solicitud = cambios.get("tipo_solicitud", reserva.tipo_solicitud)
    nueva_ubicacion_uso = cambios.get("ubicacion_uso", reserva.ubicacion_uso)
    if nueva_ubicacion_uso is not None and nuevo_tipo_solicitud != TipoSolicitud.RESERVA_FUERA_LABORATORIO.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ubicacion_uso solo aplica cuando tipo_solicitud es reserva_fuera_laboratorio",
        )
    reserva.tipo_solicitud = nuevo_tipo_solicitud
    reserva.ubicacion_uso = nueva_ubicacion_uso
    reserva.requiere_apoyo_auxiliar = (
        cambios.get("requiere_apoyo_auxiliar", reserva.requiere_apoyo_auxiliar) or _apoyo_auxiliar_forzado(objetivo)
    )
    reserva.recurso_id = _recurso_ancla(db, objetivo.laboratorio, objetivo.recursos_efectivos)
    _reescribir_asociaciones(db, reserva, objetivo)
    if "acompanantes" in cambios:
        _reescribir_acompanantes(db, reserva, cambios["acompanantes"] or [])
    # Feature B: notificar al dueño si el gestor/admin agrega recursos o espacios.
    nuevos_recurso_ids = set(recurso_ids)
    nuevos_espacio_ids = set(espacio_ids)
    agregados_recurso_ids = nuevos_recurso_ids - viejos_recurso_ids
    agregados_espacio_ids = nuevos_espacio_ids - viejos_espacio_ids
    if (agregados_recurso_ids or agregados_espacio_ids) and not es_actor(reserva, usuario) and usuario.rol in {Rol.ADMIN.value, Rol.GESTOR.value}:
        db.add(
            Notificacion(
                **columnas_actor(reserva.actor),
                reserva_id=reserva.id,
                tipo=TipoNotificacion.ACTUALIZADA.value,
            )
        )
        propietario = reserva.actor
        if propietario is not None:
            nombres_recursos: list[str] = []
            if agregados_recurso_ids:
                agregados_recursos = db.query(Recurso).filter(Recurso.id.in_(list(agregados_recurso_ids))).all()
                nombres_recursos = [r.nombre for r in agregados_recursos]
            nombres_espacios: list[str] = []
            if agregados_espacio_ids:
                agregados_espacios = db.query(Espacio).filter(Espacio.id.in_(list(agregados_espacio_ids))).all()
                nombres_espacios = [e.nombre for e in agregados_espacios]
            partes: list[str] = []
            if nombres_recursos:
                partes.append(f"recursos: {', '.join(nombres_recursos)}")
            if nombres_espacios:
                partes.append(f"espacios: {', '.join(nombres_espacios)}")
            detalle = " y ".join(partes) if partes else "nuevos recursos"
            if correo_habilitado(objetivo.laboratorio, propietario):
                encolar_correo(
                    db,
                    destinatario=propietario.email,
                    asunto="Tu reserva fue actualizada con nuevos recursos",
                    cuerpo=plantilla_reserva_actualizada(
                        nombre_saludo=propietario.username,
                        reserva_id=reserva.id,
                        espacio=objetivo.laboratorio.nombre,
                        fecha=str(reserva.fecha),
                        hora_inicio=str(reserva.hora_inicio),
                        hora_fin=str(reserva.hora_fin),
                        detalle=detalle,
                    ),
                    es_html=True,
                )
    if reprogramar_evento_calendario:
        encolar_actualizacion_calendario(
            db,
            reserva=reserva,
            laboratorio_nombre=objetivo.laboratorio.nombre,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            asistentes=_asistentes_evento_calendario(db, objetivo.laboratorio.id, reserva.actor),
        )
    registrar_cambio(db, usuario, "actualizar", "reserva", reserva.id, f"Actualizó la reserva #{reserva.id}")

    confirmar_cambios_reserva(db)
    db.refresh(reserva)
    return get_reserva(db, reserva.id) or reserva


def eliminar_reserva(db: Session, reserva_id: int, usuario: Personal | Usuario) -> None:
    reserva = get_reserva(db, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La reserva no existe")
    es_propietario = es_actor(reserva, usuario)
    es_gestor = usuario.rol in {Rol.ADMIN.value, Rol.GESTOR.value}
    if not es_propietario and not es_gestor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes eliminar tus propias reservas")
    if usuario.rol == Rol.USUARIO.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los usuarios no pueden eliminar reservas",
        )
    if usuario.rol == Rol.GESTOR.value and not es_propietario:
        laboratorio_gestionado = get_managed_laboratory_id(db, usuario)
        if reserva.laboratorio_id != laboratorio_gestionado:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes gestionar reservas de tu laboratorio")

    descripcion = f"Eliminó la reserva #{reserva.id}"
    # Capturar antes del delete: si el actor no es el propio dueño (un
    # gestor/admin borrando la reserva de otra persona), esa persona no se
    # entera de otra forma -- eliminar es distinto de cancelar, no deja
    # rastro visible para ella en la app.
    propietario = None if es_propietario else reserva.actor
    # También antes del delete: `reserva_recursos` cascadea junto con la
    # reserva (ver `Reserva.recursos_asociados`), así que el conjunto
    # efectivo de recursos ya no se puede leer después.
    fecha, hora_inicio, hora_fin = reserva.fecha, reserva.hora_inicio, reserva.hora_fin
    recurso_ids_liberados = get_recurso_ids_reserva(db, reserva.id) if reserva.estado in ESTADOS_BLOQUEANTES else []
    laboratorio_obj = reserva.laboratorio
    graph_event_id = reserva.graph_event_id
    asistentes_calendario = _asistentes_evento_calendario(db, reserva.laboratorio_id, reserva.actor) if graph_event_id is not None else []
    if propietario is not None:
        datos_correo = {
            "email": propietario.email,
            "nombre_saludo": propietario.username,
            "reserva_id": reserva.id,
            "espacio": reserva.laboratorio.nombre,
            "fecha": str(reserva.fecha),
            "hora_inicio": str(reserva.hora_inicio),
            "hora_fin": str(reserva.hora_fin),
        }
    db.delete(reserva)
    registrar_cambio(db, usuario, "eliminar", "reserva", reserva_id, descripcion)
    if propietario is not None and correo_habilitado(laboratorio_obj, propietario):
        encolar_correo(
            db,
            destinatario=datos_correo["email"],
            asunto="Tu reserva fue eliminada",
            cuerpo=plantilla_reserva_eliminada(
                nombre_saludo=datos_correo["nombre_saludo"],
                reserva_id=datos_correo["reserva_id"],
                espacio=datos_correo["espacio"],
                fecha=datos_correo["fecha"],
                hora_inicio=datos_correo["hora_inicio"],
                hora_fin=datos_correo["hora_fin"],
            ),
            es_html=True,
        )
    if graph_event_id is not None:
        encolar_cancelacion_calendario(
            db,
            reserva=reserva,
            laboratorio_nombre=laboratorio_obj.nombre,
            asistentes=asistentes_calendario,
        )
    db.commit()
    if propietario is not None or graph_event_id is not None:
        procesar_pendientes(db)
    for recurso_id in recurso_ids_liberados:
        notificar_primero_en_espera(db, recurso_id=recurso_id, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin)
