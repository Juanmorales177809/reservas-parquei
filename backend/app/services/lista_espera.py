from datetime import date, time, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.reservas import get_reservas_bloqueantes
from app.domain.protocols import Reloj
from app.models import ListaEspera, Personal, Recurso, Usuario
from app.schemas.lista_espera import ListaEsperaCreate
from app.services.actores import columnas_actor, es_actor
from app.services.email import encolar_correo, procesar_pendientes
from app.services.email_templates import plantilla_cupo_disponible
from app.services.reloj import RelojLocal

# Cada cuánto tiempo sin reservar se le pasa el turno a la siguiente
# persona en la cola -- constante simple, mismo criterio que
# `services/recordatorios.py::INTERVALO_MINUTOS` (no hay caso de uso hoy
# que necesite configurarlo por instalación).
HORAS_EXPIRACION_DEFAULT = 2


def crear_entrada(db: Session, data: ListaEsperaCreate, actor: Personal | Usuario) -> ListaEspera:
    recurso = db.query(Recurso).filter(Recurso.id == data.recurso_id).first()
    if recurso is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El recurso no existe")
    entrada = ListaEspera(
        **columnas_actor(actor),
        recurso_id=data.recurso_id,
        fecha=data.fecha,
        hora_inicio=data.hora_inicio,
        hora_fin=data.hora_fin,
        estado="activa",
    )
    db.add(entrada)
    db.commit()
    db.refresh(entrada)
    return entrada


def listar_mias(db: Session, actor: Personal | Usuario) -> list[ListaEspera]:
    # "notificada" se incluye a propósito: la persona todavía quiere ver
    # que se liberó el cupo (y el aviso de "revisá tu correo" en la UI)
    # hasta que cancele la entrada a mano. "cancelada"/"expirada" se
    # ocultan -- una expirada ya le pasó el turno a la siguiente persona
    # de la cola, no aporta nada dejarla visible.
    query = db.query(ListaEspera).filter(ListaEspera.estado.notin_(("cancelada", "expirada")))
    if isinstance(actor, Personal):
        query = query.filter(ListaEspera.personal_id == actor.id)
    else:
        query = query.filter(ListaEspera.usuario_id == actor.id)
    return query.order_by(ListaEspera.created_at.desc()).all()


def cancelar(db: Session, entrada_id: int, actor: Personal | Usuario) -> None:
    entrada = db.query(ListaEspera).filter(ListaEspera.id == entrada_id).first()
    if entrada is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La entrada no existe")
    if not es_actor(entrada, actor):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes cancelar tus propias entradas")
    entrada.estado = "cancelada"
    db.commit()


def notificar_primero_en_espera(
    db: Session,
    *,
    recurso_id: int,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    reloj: Reloj | None = None,
) -> None:
    """Se liberó `recurso_id` en `[hora_inicio, hora_fin)` de `fecha` (una
    reserva que lo ocupaba se rechazó, canceló, eliminó, o una entrada
    previa expiró sin que reservara -- ver `vencer_y_reencolar`) -- si hay
    alguien en la lista de espera para ese horario, se le avisa por correo
    a la primera persona `activa` en la cola (FIFO)."""
    entrada = (
        db.query(ListaEspera)
        .filter(
            ListaEspera.estado == "activa",
            ListaEspera.recurso_id == recurso_id,
            ListaEspera.fecha == fecha,
            ListaEspera.hora_inicio < hora_fin,
            ListaEspera.hora_fin > hora_inicio,
        )
        .order_by(ListaEspera.created_at.asc())
        .first()
    )
    if entrada is None:
        return
    entrada.estado = "notificada"
    entrada.notificada_en = (reloj or RelojLocal()).ahora()
    actor = entrada.actor
    encolar_correo(
        db,
        destinatario=actor.email,
        asunto="Se liberó un cupo que estabas esperando",
        cuerpo=plantilla_cupo_disponible(
            nombre_saludo=actor.username,
            recurso=entrada.recurso.nombre,
            fecha=str(entrada.fecha),
            hora_inicio=str(entrada.hora_inicio),
            hora_fin=str(entrada.hora_fin),
        ),
        es_html=True,
    )
    db.commit()
    procesar_pendientes(db)


def vencer_y_reencolar(db: Session, *, horas_expiracion: int = HORAS_EXPIRACION_DEFAULT, reloj: Reloj | None = None) -> int:
    """Reintento de la lista de espera (2026-08-29, ronda 2): si pasaron
    `horas_expiracion` desde que se notificó a alguien y no reservó, le
    pasa el turno a la siguiente persona `activa` en la cola para ese
    mismo recurso/horario.

    Función pura de servicio (mismo patrón que
    `services/recordatorios.py::enviar_recordatorios_pendientes`) -- no
    conoce al scheduler que la llama, testeable directo con un reloj fijo.
    """
    ahora = (reloj or RelojLocal()).ahora()
    limite = ahora - timedelta(hours=horas_expiracion)

    candidatas = (
        db.query(ListaEspera)
        .filter(ListaEspera.estado == "notificada", ListaEspera.notificada_en <= limite)
        .all()
    )

    vencidas = 0
    for entrada in candidatas:
        entrada.estado = "expirada"
        vencidas += 1
        sigue_libre = not get_reservas_bloqueantes(
            db, entrada.recurso_id, entrada.fecha, entrada.hora_inicio, entrada.hora_fin
        )
        if sigue_libre:
            db.commit()
            notificar_primero_en_espera(
                db,
                recurso_id=entrada.recurso_id,
                fecha=entrada.fecha,
                hora_inicio=entrada.hora_inicio,
                hora_fin=entrada.hora_fin,
                reloj=reloj,
            )

    if vencidas:
        db.commit()
    return vencidas
