from datetime import date, datetime, time, timedelta
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.reservas import (
    get_ensayo_ids_reserva,
    get_recurso_ids_reserva,
    get_reserva,
    get_reservas_bloqueantes,
    get_zona_ids_reserva,
    get_zonas_bloqueantes,
)
from app.deps import get_managed_space_id
from app.domain.enums import (
    EstadoEntidad,
    EstadoReserva,
    ModalidadEspacio,
    Rol,
    TipoNotificacion,
    TipoReserva,
)
from app.domain.protocols import Reloj
from app.models import (
    Espacio,
    Notificacion,
    Recurso,
    Reserva,
    ReservaRecurso,
    ReservaZona,
    Usuario,
    UsuarioEspacio,
    Zona,
    ZonaRecurso,
)
from app.schemas.reserva import ReservaCreate, ReservaUpdate
from app.services.auditoria import registrar_cambio
from app.services.email import encolar_correo, procesar_pendientes
from app.services.horarios import horario_cubre_reserva
from app.services.reloj import RelojLocal


SOLAPAMIENTO_CONSTRAINT = "reservas_sin_solapamiento"
RESERVA_RECURSOS_CONSTRAINT = "reserva_recursos_sin_solapamiento"
RESERVA_ZONAS_CONSTRAINT = "reserva_zonas_sin_solapamiento"

# Fase 12C-4d/12C-6: la doble escritura mantiene `reservas` y las tablas de
# asociación sincronizadas, así que un solapamiento puede disparar cualquiera
# de las tres constraints EXCLUDE (depende de qué tabla detecta primero el
# conflicto en el flush de la transacción). Todas se traducen al mismo 409.
_CONSTRAINTS_SOLAPAMIENTO = (
    SOLAPAMIENTO_CONSTRAINT,
    RESERVA_RECURSOS_CONSTRAINT,
    RESERVA_ZONAS_CONSTRAINT,
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
    zonas, recursos efectivos (deduplicados, orden estable por id) y el
    espacio único al que todos pertenecen."""

    espacio: Espacio
    recurso_ids: list[int]
    zona_ids: list[int]
    recursos_efectivos: list[Recurso]
    zonas: list[Zona]


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


def _cargar_zonas(db: Session, zona_ids: list[int]) -> list[Zona]:
    if not zona_ids:
        return []
    zonas = db.query(Zona).filter(Zona.id.in_(zona_ids)).all()
    por_id = {z.id: z for z in zonas}
    faltantes = sorted(set(zona_ids) - set(por_id))
    if faltantes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Las zonas {faltantes} no existen",
        )
    return [por_id[i] for i in sorted(por_id)]


def _miembros_zona(db: Session, zona: Zona) -> list[Recurso]:
    return (
        db.query(Recurso)
        .join(ZonaRecurso, ZonaRecurso.recurso_id == Recurso.id)
        .filter(ZonaRecurso.zona_id == zona.id)
        .order_by(Recurso.id.asc())
        .all()
    )


def _resolver_objetivo(
    db: Session,
    *,
    recurso_ids: list[int],
    zona_ids: list[int],
    usuario: Usuario,
    espacio_id_fijo: int | None = None,
    tipo: TipoReserva | None = None,
) -> _ObjetivoReserva:
    """Resuelve y valida el conjunto objetivo de una reserva (Fase 12C-6).

    Reglas aprobadas aplicadas aquí:
    - Modalidad del espacio: `equipos` no admite zonas; `zonas` no admite
      recursos directos; `mixto` admite ambos.
    - Recursos y zonas deben pertenecer a un mismo espacio (el de la reserva;
      para edición, `espacio_id_fijo` lo fija y valida pertenencia).
    - Zonas y recursos efectivos deben estar activos.
    - `validar_acceso_ps` se aplica a cada recurso efectivo (gate de rol de
      la Fase 12B + gate de tipo de la Fase 12D).
    - Recursos efectivos = directos ∪ miembros de las zonas, sin duplicados,
      en orden estable por id.
    """
    directos = _cargar_recursos(db, recurso_ids)
    zonas = _cargar_zonas(db, zona_ids)

    espacios = {r.espacio_id for r in directos} | {z.espacio_id for z in zonas}
    if not espacios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes indicar al menos un recurso o una zona",
        )
    if len(espacios) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los recursos y zonas deben pertenecer al mismo espacio",
        )
    espacio_id = espacios.pop()
    if espacio_id_fijo is not None and espacio_id != espacio_id_fijo:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
                if usuario.rol in {Rol.GESTOR.value, Rol.ADMIN.value}
                else status.HTTP_400_BAD_REQUEST
            ),
            detail="Los recursos y zonas deben pertenecer al espacio de la reserva",
        )
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if espacio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El espacio no existe")

    modalidad = espacio.modalidad_reserva
    if modalidad == ModalidadEspacio.EQUIPOS.value and zona_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este espacio no admite reservas por zonas",
        )
    if modalidad == ModalidadEspacio.ZONAS.value and recurso_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este espacio solo admite reservas por zonas",
        )

    for zona in zonas:
        if zona.estado != EstadoEntidad.ACTIVO.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La zona {zona.nombre} no está activa para reservas",
            )

    por_id: dict[int, Recurso] = {}
    for recurso in directos:
        if recurso.estado != EstadoEntidad.ACTIVO.value or espacio.estado != EstadoEntidad.ACTIVO.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El recurso no está activo para reservas",
            )
        por_id[recurso.id] = recurso
    for zona in zonas:
        for miembro in _miembros_zona(db, zona):
            if miembro.estado != EstadoEntidad.ACTIVO.value or espacio.estado != EstadoEntidad.ACTIVO.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El recurso no está activo para reservas",
                )
            por_id[miembro.id] = miembro
    efectivos = [por_id[i] for i in sorted(por_id)]

    for recurso in efectivos:
        validar_acceso_ps(recurso, usuario, tipo)

    return _ObjetivoReserva(
        espacio=espacio,
        recurso_ids=sorted({r.id for r in directos}),
        zona_ids=sorted({z.id for z in zonas}),
        recursos_efectivos=efectivos,
        zonas=zonas,
    )


def _resolver_efectivos(
    db: Session,
    recurso_ids: list[int],
    zona_ids: list[int],
) -> tuple[list[Recurso], list[Zona], list[Recurso]]:
    """Resuelve recursos directos, zonas y recursos efectivos SIN volver a
    validar modalidad/actividad/PS — usado en la aprobación, donde los
    objetivos ya fueron validados al crear/editar y solo resta chequear el
    solapamiento transitivo."""
    directos = _cargar_recursos(db, recurso_ids)
    zonas = _cargar_zonas(db, zona_ids)
    por_id: dict[int, Recurso] = {}
    for recurso in directos:
        por_id[recurso.id] = recurso
    for zona in zonas:
        for miembro in _miembros_zona(db, zona):
            por_id[miembro.id] = miembro
    return directos, zonas, [por_id[i] for i in sorted(por_id)]


def _capacidad_efectiva(espacio: Espacio, objetivo: _ObjetivoReserva) -> int:
    """Capacidad efectiva = min(espacio, zonas definidas, recursos efectivos)
    (decisión aprobada 12C-6)."""
    capacidades = [espacio.capacidad]
    capacidades_zonas = [z.capacidad for z in objetivo.zonas if z.capacidad is not None]
    if capacidades_zonas:
        capacidades.append(min(capacidades_zonas))
    if objetivo.recursos_efectivos:
        capacidades.append(min(r.capacidad for r in objetivo.recursos_efectivos))
    return min(capacidades)


def _recurso_ancla(db: Session, espacio: Espacio, recursos_efectivos: list[Recurso]) -> int:
    """Recurso efectivo canónico (orden estable) para la columna histórica
    `Reserva.recurso_id` (Fase 12C-6). La columna es NOT NULL y las
    migraciones están congeladas, así que una zona sin recursos efectivos se
    ancla al recurso de menor id de su espacio; riesgo residual documentado
    (la EXCLUDE histórica podría, en un caso extremo, chocar con una reserva
    directa de ese recurso ancla). Sin recurso en el espacio, la reserva es
    irrepresentable y se rechaza con 400."""
    if recursos_efectivos:
        return min(r.id for r in recursos_efectivos)
    recurso = (
        db.query(Recurso)
        .filter(Recurso.espacio_id == espacio.id)
        .order_by(Recurso.id.asc())
        .first()
    )
    if recurso is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La zona sin recursos asociados no puede reservarse mientras la columna recurso_id sea obligatoria",
        )
    return recurso.id


def _validar_solapamiento_efectivos(
    db: Session,
    recursos_efectivos: list[Recurso],
    zonas: list[Zona],
    *,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    exclude_id: int | None = None,
) -> None:
    """Solapamiento transitivo (Fase 12C-6): cada recurso efectivo contra
    `reserva_recursos` y cada zona contra `reserva_zonas`. Como toda zona
    reservada materializa sus recursos efectivos, el cruce zona<->recurso
    queda cubierto por la misma tabla."""
    for recurso in recursos_efectivos:
        if get_reservas_bloqueantes(db, recurso.id, fecha, hora_inicio, hora_fin, exclude_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El recurso ya tiene una reserva en ese horario",
            )
    for zona in zonas:
        if get_zonas_bloqueantes(db, zona.id, fecha, hora_inicio, hora_fin, exclude_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La zona ya tiene una reserva en ese horario",
            )


def _cargar_ensayos(db: Session, ensayo_ids: list[int]) -> list["Ensayo"]:
    if not ensayo_ids:
        return []
    from app.models.ensayo import Ensayo

    ensayos = db.query(Ensayo).filter(Ensayo.id.in_(ensayo_ids)).all()
    encontrados = {e.id for e in ensayos}
    faltantes = set(ensayo_ids) - encontrados
    if faltantes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ensayo(s) no encontrado(s): {sorted(faltantes)}",
        )
    return ensayos


def _validar_ensayos_pertenecen_a_zonas(ensayos: list["Ensayo"], objetivo: _ObjetivoReserva) -> None:
    """Fase 12E: cada ensayo debe pertenecer a una de las zonas
    efectivamente reservadas. Si no, 400."""
    if not ensayos:
        return
    zonas_ids = {z.id for z in objetivo.zonas}
    for ensayo in ensayos:
        if ensayo.zona_id not in zonas_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El ensayo no pertenece a ninguna de las zonas reservadas",
            )


def _reescribir_ensayos(db: Session, reserva: Reserva, ensayo_ids: list[int]) -> None:
    """Borra y recrea las filas de `reserva_ensayos` (Fase 12E, mismo idioma
    que `_reescribir_asociaciones`: borrar+recrear dentro de la misma
    transacción, sin commit propio)."""

    from app.models.reserva_ensayo import ReservaEnsayo

    db.query(ReservaEnsayo).filter(ReservaEnsayo.reserva_id == reserva.id).delete(synchronize_session=False)
    for ensayo_id in ensayo_ids:
        db.add(ReservaEnsayo(reserva_id=reserva.id, ensayo_id=ensayo_id))


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
    """Borra y recrea las filas de `reserva_zonas` y `reserva_recursos` de la
    reserva dentro de la misma transacción (regla aprobada 12C-6). NUNCA
    hace `commit`/`rollback` — el flujo llamante es dueño de la transacción,
    igual que la doble escritura de 12C-4d. Sin filas parciales: cualquier
    fallo en el commit revierte reserva y asociaciones como una sola unidad."""
    db.query(ReservaZona).filter(ReservaZona.reserva_id == reserva.id).delete(synchronize_session=False)
    db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == reserva.id).delete(synchronize_session=False)
    for zona in objetivo.zonas:
        db.add(
            ReservaZona(
                reserva_id=reserva.id,
                zona_id=zona.id,
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
    db.query(ReservaZona).filter(ReservaZona.reserva_id == reserva.id).update(
        {
            ReservaZona.fecha: reserva.fecha,
            ReservaZona.hora_inicio: reserva.hora_inicio,
            ReservaZona.hora_fin: reserva.hora_fin,
            ReservaZona.estado: reserva.estado,
        },
        synchronize_session=False,
    )


def _etiqueta_objetivo(objetivo: _ObjetivoReserva) -> str:
    partes = []
    if objetivo.zonas:
        partes.append("la zona " + ", ".join(z.nombre for z in objetivo.zonas))
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


def validar_horario(espacio: Espacio, fecha: date, hora_inicio: time, hora_fin: time) -> None:
    if hora_inicio >= hora_fin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La hora de inicio debe ser menor que la hora de fin")

    if not horario_cubre_reserva(espacio, fecha.weekday(), hora_inicio, hora_fin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El horario seleccionado no está habilitado en la configuración del espacio",
        )


def validar_anticipacion(
    espacio: Espacio,
    fecha: date,
    hora_inicio: time,
    reloj: Reloj | None = None,
) -> None:
    inicio = datetime.combine(fecha, hora_inicio)
    fecha_minima = (reloj or RelojLocal()).ahora() + timedelta(hours=espacio.horas_antelacion)
    if inicio < fecha_minima:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La reserva debe hacerse con mínimo {espacio.horas_antelacion} horas de anticipación",
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
    if recurso.estado != EstadoEntidad.ACTIVO.value or recurso.espacio.estado != EstadoEntidad.ACTIVO.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El recurso no está activo para reservas")


def validar_capacidad(asistentes: int, recurso_capacidad: int) -> None:
    if asistentes > recurso_capacidad:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cantidad de asistentes supera la capacidad del recurso")


def validar_acceso_ps(recurso: Recurso, usuario: Usuario, tipo: TipoReserva | None = None) -> None:
    """RN-009 (Fase 12B) + Fase 12D: un recurso de prestación de servicios
    (PS) no puede reservarse por el rol `usuario` (investigador) — el gate
    de rol, que se evalúa primero y sin cambios. `gestor` (laboratorista) y
    `admin` (administrador técnico) sí pueden, pero desde la Fase 12D
    únicamente cuando la reserva declara `tipo == SERVICIO_DE_ENSAYO`
    (RN-015): un recurso PS es un servicio de ensayo, no una reserva de
    investigación ni de grado. Cualquier otro valor (u ausencia) de `tipo`
    responde 400 para esos roles.
    """
    if recurso.es_prestacion_servicio and usuario.rol == Rol.USUARIO.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los recursos de prestación de servicios no están disponibles para tu rol",
        )
    if recurso.es_prestacion_servicio and tipo != TipoReserva.SERVICIO_DE_ENSAYO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los recursos de prestación de servicios solo pueden reservarse con tipo de reserva de ensayo",
        )


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
    validar_horario(objetivo.espacio, fecha, hora_inicio, hora_fin)
    validar_anticipacion(objetivo.espacio, fecha, hora_inicio)
    if asistentes > _capacidad_efectiva(objetivo.espacio, objetivo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cantidad de asistentes supera la capacidad efectiva de la reserva",
        )
    _validar_solapamiento_efectivos(
        db,
        objetivo.recursos_efectivos,
        objetivo.zonas,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        exclude_id=exclude_id,
    )


def crear_reserva(db: Session, data: ReservaCreate, usuario: Usuario) -> Reserva:
    objetivo = _resolver_objetivo(
        db,
        recurso_ids=data.recurso_ids,
        zona_ids=data.zona_ids,
        usuario=usuario,
        tipo=data.tipo,
    )
    _validar_objetivo(
        db,
        objetivo,
        fecha=data.fecha,
        hora_inicio=data.hora_inicio,
        hora_fin=data.hora_fin,
        asistentes=data.asistentes,
    )
    ensayos = _cargar_ensayos(db, data.ensayo_ids)
    _validar_ensayos_pertenecen_a_zonas(ensayos, objetivo)
    espacio_gestionado = get_managed_space_id(db, usuario) if usuario.rol == Rol.GESTOR.value else None
    aprobacion_automatica = objetivo.espacio.aprobacion_automatica or espacio_gestionado == objetivo.espacio.id

    reserva = Reserva(
        usuario_id=usuario.id,
        espacio_id=objetivo.espacio.id,
        recurso_id=_recurso_ancla(db, objetivo.espacio, objetivo.recursos_efectivos),
        fecha=data.fecha,
        hora_inicio=data.hora_inicio,
        hora_fin=data.hora_fin,
        asistentes=data.asistentes,
        tipo=data.tipo,
        estado=(
            EstadoReserva.APROBADA.value if aprobacion_automatica else EstadoReserva.ESPERANDO.value
        ),
    )
    db.add(reserva)
    preparar_reserva(db)
    _reescribir_asociaciones(db, reserva, objetivo)
    _reescribir_ensayos(db, reserva, data.ensayo_ids)
    _reescribir_acompanantes(db, reserva, data.acompanantes)
    if not aprobacion_automatica:
        gestores = (
            db.query(Usuario.id, Usuario.username, Usuario.email)
            .join(UsuarioEspacio, UsuarioEspacio.usuario_id == Usuario.id)
            .filter(
                Usuario.rol == Rol.GESTOR.value,
                UsuarioEspacio.espacio_id == objetivo.espacio.id,
            )
            .all()
        )
        for gestor_id, gestor_username, gestor_email in gestores:
            db.add(
                Notificacion(
                    usuario_id=gestor_id,
                    reserva_id=reserva.id,
                    tipo=TipoNotificacion.PENDIENTE.value,
                )
            )
            encolar_correo(
                db,
                destinatario=gestor_email,
                asunto="Nueva reserva pendiente de aprobación",
                cuerpo=(
                    f"Hola {gestor_username},\n\n"
                    f"Hay una nueva reserva pendiente de tu aprobación en {objetivo.espacio.nombre}.\n"
                    f"Fecha: {data.fecha} de {data.hora_inicio} a {data.hora_fin}.\n\n"
                    "Ingresá al sistema de reservas para aprobarla o rechazarla."
                ),
            )
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


def cambiar_estado(
    db: Session, reserva_id: int, nuevo_estado: str, admin_user: Usuario, motivo: str | None = None
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
    espacio_gestionado = get_managed_space_id(db, admin_user)
    if espacio_gestionado is not None and reserva.espacio_id != espacio_gestionado:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes gestionar reservas de tu espacio")
    validar_transicion_estado(reserva.estado, nuevo)
    if nuevo == EstadoReserva.APROBADA and reserva.estado != nuevo.value:
        _, zonas, efectivos = _resolver_efectivos(
            db,
            get_recurso_ids_reserva(db, reserva.id),
            get_zona_ids_reserva(db, reserva.id),
        )
        _validar_solapamiento_efectivos(
            db,
            efectivos,
            zonas,
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
                usuario_id=reserva.usuario_id,
                reserva_id=reserva.id,
                tipo=tipo_notificacion,
            )
        )
        estado_legible = {
            EstadoReserva.APROBADA: "aprobada",
            EstadoReserva.RECHAZADA: "rechazada",
            EstadoReserva.CANCELADA: "cancelada",
        }[nuevo]
        cuerpo_correo = f"Hola {reserva.usuario.username},\n\nTu reserva #{reserva.id} fue {estado_legible}."
        if nuevo == EstadoReserva.RECHAZADA and motivo:
            cuerpo_correo += f"\nMotivo: {motivo}"
        cuerpo_correo += "\n\nIngresá al sistema de reservas para más detalles."
        encolar_correo(
            db,
            destinatario=reserva.usuario.email,
            asunto=f"Tu reserva fue {estado_legible}",
            cuerpo=cuerpo_correo,
        )
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


def marcar_asistencia(db: Session, reserva_id: int, asistio: bool, admin_user: Usuario) -> Reserva:
    """Fase 12D-bis: marca la asistencia real de una reserva.

    Copia el molde de `cambiar_estado` pero sin máquina de estados: solo
    verifica rol gestor/admin, existencia de la reserva y pertenencia del
    gestor a su espacio asignado. No hay transición que validar ni
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
    espacio_gestionado = get_managed_space_id(db, admin_user)
    if espacio_gestionado is not None and reserva.espacio_id != espacio_gestionado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes gestionar reservas de tu espacio"
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


def cancelar_reserva_usuario(db: Session, reserva_id: int, usuario: Usuario) -> Reserva:
    reserva = get_reserva(db, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La reserva no existe")
    if reserva.usuario_id != usuario.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes cancelar tus propias reservas")
    if reserva.estado != EstadoReserva.APROBADA.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo puedes cancelar reservas aprobadas",
        )

    reserva.estado = EstadoReserva.CANCELADA.value
    registrar_cambio(
        db,
        usuario,
        "cancelar",
        "reserva",
        reserva.id,
        f"Canceló su reserva #{reserva.id}",
    )
    _sincronizar_campos_asociaciones(db, reserva)
    confirmar_cambios_reserva(db)
    db.refresh(reserva)
    return get_reserva(db, reserva.id) or reserva


def actualizar_reserva(db: Session, reserva_id: int, data: ReservaUpdate, usuario: Usuario) -> Reserva:
    reserva = get_reserva(db, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La reserva no existe")
    es_propietario = reserva.usuario_id == usuario.id
    es_gestor = usuario.rol in {Rol.ADMIN.value, Rol.GESTOR.value}
    if not es_propietario and not es_gestor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes editar tus propias reservas")
    if es_propietario and usuario.rol == Rol.USUARIO.value and reserva.estado != EstadoReserva.ESPERANDO.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo puedes editar reservas pendientes",
        )
    espacio_gestionado = get_managed_space_id(db, usuario) if usuario.rol == Rol.GESTOR.value else None
    if not es_propietario and espacio_gestionado is not None and reserva.espacio_id != espacio_gestionado:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes gestionar reservas de tu espacio")

    cambios = data.model_dump(exclude_unset=True)
    if not cambios:
        return reserva

    # Ejes de reemplazo completo (Fase 12C-6): un eje ausente se conserva;
    # un eje presente reemplaza el conjunto completo de ese eje.
    recurso_ids = cambios.get("recurso_ids", get_recurso_ids_reserva(db, reserva.id))
    zona_ids = cambios.get("zona_ids", get_zona_ids_reserva(db, reserva.id))
    if not recurso_ids and not zona_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La reserva debe tener al menos un recurso o una zona",
        )
    fecha = cambios.get("fecha", reserva.fecha)
    hora_inicio = cambios.get("hora_inicio", reserva.hora_inicio)
    hora_fin = cambios.get("hora_fin", reserva.hora_fin)
    asistentes = cambios.get("asistentes", reserva.asistentes)

    objetivo = _resolver_objetivo(
        db,
        recurso_ids=recurso_ids,
        zona_ids=zona_ids,
        usuario=usuario,
        espacio_id_fijo=reserva.espacio_id,
        tipo=cambios.get("tipo", reserva.tipo),
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
    if "ensayo_ids" in cambios:
        ensayos_nuevos = _cargar_ensayos(db, cambios["ensayo_ids"] or [])
        _validar_ensayos_pertenecen_a_zonas(ensayos_nuevos, objetivo)

    reserva.fecha = fecha
    reserva.hora_inicio = hora_inicio
    reserva.hora_fin = hora_fin
    reserva.asistentes = asistentes
    reserva.tipo = cambios.get("tipo", reserva.tipo)
    reserva.recurso_id = _recurso_ancla(db, objetivo.espacio, objetivo.recursos_efectivos)
    _reescribir_asociaciones(db, reserva, objetivo)
    if "ensayo_ids" in cambios:
        _reescribir_ensayos(db, reserva, cambios["ensayo_ids"] or [])
    if "acompanantes" in cambios:
        _reescribir_acompanantes(db, reserva, cambios["acompanantes"] or [])
    registrar_cambio(db, usuario, "actualizar", "reserva", reserva.id, f"Actualizó la reserva #{reserva.id}")

    confirmar_cambios_reserva(db)
    db.refresh(reserva)
    return get_reserva(db, reserva.id) or reserva


def eliminar_reserva(db: Session, reserva_id: int, usuario: Usuario) -> None:
    reserva = get_reserva(db, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La reserva no existe")
    es_propietario = reserva.usuario_id == usuario.id
    es_gestor = usuario.rol in {Rol.ADMIN.value, Rol.GESTOR.value}
    if not es_propietario and not es_gestor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes eliminar tus propias reservas")
    if usuario.rol == Rol.USUARIO.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los usuarios no pueden eliminar reservas",
        )
    if usuario.rol == Rol.GESTOR.value and not es_propietario:
        espacio_gestionado = get_managed_space_id(db, usuario)
        if reserva.espacio_id != espacio_gestionado:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes gestionar reservas de tu espacio")

    descripcion = f"Eliminó la reserva #{reserva.id}"
    db.delete(reserva)
    registrar_cambio(db, usuario, "eliminar", "reserva", reserva_id, descripcion)
    db.commit()
