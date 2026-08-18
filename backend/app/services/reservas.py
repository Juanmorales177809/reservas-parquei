from datetime import date, datetime, time, timedelta

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.reservas import get_reserva, get_reservas_bloqueantes
from app.deps import get_managed_space_id
from app.domain.enums import EstadoEntidad, EstadoReserva, Rol, TipoNotificacion
from app.domain.protocols import Reloj
from app.models import Espacio, Notificacion, Recurso, Reserva, Usuario, UsuarioEspacio
from app.schemas.reserva import ReservaCreate, ReservaUpdate
from app.services.auditoria import registrar_cambio
from app.services.horarios import horario_cubre_reserva
from app.services.reloj import RelojLocal


SOLAPAMIENTO_CONSTRAINT = "reservas_sin_solapamiento"


def _es_conflicto_solapamiento(exc: IntegrityError) -> bool:
    origen = exc.orig
    diagnostico = getattr(origen, "diag", None)
    constraint_name = getattr(diagnostico, "constraint_name", None)
    return constraint_name == SOLAPAMIENTO_CONSTRAINT or SOLAPAMIENTO_CONSTRAINT in str(origen)


def _traducir_error_integridad(db: Session, exc: IntegrityError) -> None:
    db.rollback()
    if _es_conflicto_solapamiento(exc):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El recurso acaba de ser reservado en ese horario",
        ) from exc
    raise exc


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


def validar_acceso_ps(recurso: Recurso, usuario: Usuario) -> None:
    """RN-009 (Fase 12B): un recurso de prestación de servicios (PS) no
    puede reservarse por el rol `usuario` (investigador). `gestor`
    (laboratorista) y `admin` (administrador técnico) sí pueden.

    Punto de extensión para la Fase 12D: cuando exista el tipo de reserva
    (RN-012/RN-015, "servicio de ensayo"), esa fase debe agregar su propio
    chequeo -- p. ej. exigir `data.tipo == TipoReserva.SERVICIO_DE_ENSAYO`
    cuando `recurso.es_prestacion_servicio` sea verdadero -- como una
    validación adicional, sin tocar ni duplicar este gate de rol.
    """
    if recurso.es_prestacion_servicio and usuario.rol == Rol.USUARIO.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los recursos de prestación de servicios no están disponibles para tu rol",
        )


def validar_creacion(db: Session, data: ReservaCreate, usuario: Usuario, recurso: Recurso | None) -> None:
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Debes iniciar sesión para crear reservas")
    validar_recurso_activo(recurso)
    validar_acceso_ps(recurso, usuario)
    validar_capacidad(data.asistentes, recurso.capacidad)
    validar_horario(recurso.espacio, data.fecha, data.hora_inicio, data.hora_fin)
    validar_anticipacion(recurso.espacio, data.fecha, data.hora_inicio)
    validar_solapamiento(db, data.recurso_id, data.fecha, data.hora_inicio, data.hora_fin)


def crear_reserva(db: Session, data: ReservaCreate, usuario: Usuario) -> Reserva:
    recurso = db.query(Recurso).filter(Recurso.id == data.recurso_id).first()
    validar_creacion(db, data, usuario, recurso)
    espacio_gestionado = get_managed_space_id(db, usuario) if usuario.rol == Rol.GESTOR.value else None
    aprobacion_automatica = recurso.espacio.aprobacion_automatica or espacio_gestionado == recurso.espacio_id

    reserva = Reserva(
        usuario_id=usuario.id,
        espacio_id=recurso.espacio_id,
        recurso_id=data.recurso_id,
        fecha=data.fecha,
        hora_inicio=data.hora_inicio,
        hora_fin=data.hora_fin,
        asistentes=data.asistentes,
        estado=(
            EstadoReserva.APROBADA.value if aprobacion_automatica else EstadoReserva.ESPERANDO.value
        ),
    )
    db.add(reserva)
    preparar_reserva(db)
    if not aprobacion_automatica:
        gestores = (
            db.query(Usuario.id)
            .join(UsuarioEspacio, UsuarioEspacio.usuario_id == Usuario.id)
            .filter(
                Usuario.rol == Rol.GESTOR.value,
                UsuarioEspacio.espacio_id == recurso.espacio_id,
            )
            .all()
        )
        for (gestor_id,) in gestores:
            db.add(
                Notificacion(
                    usuario_id=gestor_id,
                    reserva_id=reserva.id,
                    tipo=TipoNotificacion.PENDIENTE.value,
                )
            )
    registrar_cambio(
        db,
        usuario,
        "crear",
        "reserva",
        reserva.id,
        f"Creó una reserva de {recurso.nombre} con estado {reserva.estado}",
    )
    confirmar_cambios_reserva(db)
    db.refresh(reserva)
    return get_reserva(db, reserva.id) or reserva


def cambiar_estado(db: Session, reserva_id: int, nuevo_estado: str, admin_user: Usuario) -> Reserva:
    if admin_user.rol not in {Rol.ADMIN.value, Rol.GESTOR.value}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para cambiar el estado de una reserva")
    nuevo = EstadoReserva(nuevo_estado)
    if nuevo not in {EstadoReserva.APROBADA, EstadoReserva.RECHAZADA, EstadoReserva.CANCELADA}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El estado solo puede cambiarse a aprobada, rechazada o cancelada",
        )

    reserva = get_reserva(db, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La reserva no existe")
    espacio_gestionado = get_managed_space_id(db, admin_user)
    if espacio_gestionado is not None and reserva.espacio_id != espacio_gestionado:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes gestionar reservas de tu espacio")
    validar_transicion_estado(reserva.estado, nuevo)
    if nuevo == EstadoReserva.APROBADA and reserva.estado != nuevo.value:
        validar_solapamiento(
            db,
            reserva.recurso_id,
            reserva.fecha,
            reserva.hora_inicio,
            reserva.hora_fin,
            exclude_id=reserva.id,
        )
    estado_anterior = reserva.estado
    reserva.estado = nuevo.value
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
        registrar_cambio(
            db,
            admin_user,
            "cambiar estado",
            "reserva",
            reserva.id,
            f"Cambió la reserva #{reserva.id} de {estado_anterior} a {nuevo.value}",
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

    recurso_id = cambios.get("recurso_id", reserva.recurso_id)
    fecha = cambios.get("fecha", reserva.fecha)
    hora_inicio = cambios.get("hora_inicio", reserva.hora_inicio)
    hora_fin = cambios.get("hora_fin", reserva.hora_fin)
    asistentes = cambios.get("asistentes", reserva.asistentes)
    recurso = db.query(Recurso).filter(Recurso.id == recurso_id).first()

    validar_recurso_activo(recurso)
    if not es_propietario and espacio_gestionado is not None and recurso.espacio_id != espacio_gestionado:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes usar recursos de tu espacio")
    validar_acceso_ps(recurso, usuario)
    validar_capacidad(asistentes, recurso.capacidad)
    validar_horario(recurso.espacio, fecha, hora_inicio, hora_fin)
    validar_anticipacion(recurso.espacio, fecha, hora_inicio)
    validar_solapamiento(db, recurso_id, fecha, hora_inicio, hora_fin, reserva.id)

    for campo, valor in cambios.items():
        setattr(reserva, campo, valor)
    reserva.espacio_id = recurso.espacio_id
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
