# -*- coding: utf-8 -*-
"""Invitación de Outlook Calendar por correo (2026-09-03, rediseño).

La primera versión de esta feature llamaba a la API de eventos de
Microsoft Graph (`Calendars.ReadWrite`) desde un outbox propio
(`EventoCalendarioSaliente`, retirado). Ese scope quedó bloqueado: el
tenant del ITM exige aprobación de un admin de Entra para concederlo (a
diferencia de `Mail.Send`, ya consentido) -- ver `backend/CLAUDE.md`.

Este módulo la reemplaza con el mecanismo estándar de cualquier invitación
de calendario por correo (RFC 5545, `METHOD:REQUEST`/`CANCEL` --
`services/ics.py::construir_ics_invitacion`): el `.ics` viaja como adjunto
de un correo normal, por el mismo canal (`Mail.Send`/SMTP) que ya
funciona. Sin permiso de Graph nuevo, y sin outbox propio -- encolar un
correo (`encolar_correo`/`CorreoSaliente`) ya es asíncrono por sí solo, no
hace falta duplicar ese mecanismo.
"""

from __future__ import annotations

from datetime import date, datetime, time

from sqlalchemy.orm import Session

from app.config import settings
from app.models.reserva import Reserva
from app.services.email import Adjunto, encolar_correo
from app.services.ics import construir_ics_invitacion

ORGANIZADOR_NOMBRE = "Sistema de Reservas"


def _uid_invitacion(reserva_id: int) -> str:
    return f"reserva-{reserva_id}@reservas-parquei"


def _organizador_email() -> str:
    """Misma dirección desde la que efectivamente sale el correo (ver
    `services/email.py::procesar_pendientes`) -- el `ORGANIZER` del `.ics`
    tiene que coincidir con el remitente real del mensaje."""
    return settings.graph_mail_sender if settings.email_transport == "graph_delegado" else settings.smtp_from


def _cuerpo_invitacion(*, laboratorio_nombre: str, fecha: date, hora_inicio: time, hora_fin: time, cancelado: bool) -> str:
    if cancelado:
        return f"<p>Se canceló la reserva en {laboratorio_nombre} del {fecha} {hora_inicio}-{hora_fin}.</p>"
    return f"<p>Invitación de calendario para la reserva en {laboratorio_nombre}, {fecha} {hora_inicio}-{hora_fin}.</p>"


def _enviar_invitacion(
    db: Session,
    *,
    reserva: Reserva,
    laboratorio_nombre: str,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    asistentes: list[tuple[str, str]],
    cancelado: bool,
) -> None:
    """Arma el `.ics` (REQUEST o CANCEL) y encola un correo por cada
    asistente -- mismo criterio que el resto del proyecto ("una fila de
    `CorreoSaliente` por destinatario"), para que cada quien reciba su
    propia invitación con el resto de los asistentes visibles en el
    `ATTENDEE` list."""
    uid = reserva.graph_event_id or _uid_invitacion(reserva.id)
    reserva.calendario_secuencia = (reserva.calendario_secuencia or 0) + (0 if reserva.graph_event_id is None else 1)
    reserva.graph_event_id = uid
    contenido = construir_ics_invitacion(
        uid=uid,
        secuencia=reserva.calendario_secuencia,
        resumen=f"Reserva: {laboratorio_nombre}",
        descripcion=f"Reserva en {laboratorio_nombre}, {fecha} {hora_inicio}-{hora_fin}.",
        ubicacion=laboratorio_nombre,
        inicio=datetime.combine(fecha, hora_inicio),
        fin=datetime.combine(fecha, hora_fin),
        organizador_email=_organizador_email(),
        organizador_nombre=ORGANIZADOR_NOMBRE,
        asistentes=asistentes,
        categoria=laboratorio_nombre,
        cancelado=cancelado,
    )
    asunto = f"Reserva cancelada: {laboratorio_nombre}" if cancelado else f"Invitación: {laboratorio_nombre}"
    cuerpo = _cuerpo_invitacion(laboratorio_nombre=laboratorio_nombre, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin, cancelado=cancelado)
    for email, _nombre in asistentes:
        encolar_correo(
            db,
            destinatario=email,
            asunto=asunto,
            cuerpo=cuerpo,
            es_html=True,
            adjunto=Adjunto(nombre="invitacion.ics", contenido=contenido, content_type="text/calendar"),
        )


def encolar_invitacion_calendario(
    db: Session, *, reserva: Reserva, laboratorio_nombre: str, asistentes: list[tuple[str, str]]
) -> None:
    """Reserva recién aprobada -- invitación nueva, `SEQUENCE:0`."""
    _enviar_invitacion(
        db,
        reserva=reserva,
        laboratorio_nombre=laboratorio_nombre,
        fecha=reserva.fecha,
        hora_inicio=reserva.hora_inicio,
        hora_fin=reserva.hora_fin,
        asistentes=asistentes,
        cancelado=False,
    )


def encolar_actualizacion_calendario(
    db: Session,
    *,
    reserva: Reserva,
    laboratorio_nombre: str,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    asistentes: list[tuple[str, str]],
) -> None:
    """Reserva ya aprobada que cambió de horario -- mismo `UID`, `SEQUENCE`
    incrementado para que el cliente del destinatario la reconozca como
    una actualización, no como un evento nuevo."""
    _enviar_invitacion(
        db,
        reserva=reserva,
        laboratorio_nombre=laboratorio_nombre,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        asistentes=asistentes,
        cancelado=False,
    )


def encolar_cancelacion_calendario(
    db: Session, *, reserva: Reserva, laboratorio_nombre: str, asistentes: list[tuple[str, str]]
) -> None:
    """`METHOD:CANCEL` -- el cliente del destinatario retira el evento de
    su calendario solo, sin que tenga que borrarlo a mano."""
    _enviar_invitacion(
        db,
        reserva=reserva,
        laboratorio_nombre=laboratorio_nombre,
        fecha=reserva.fecha,
        hora_inicio=reserva.hora_inicio,
        hora_fin=reserva.hora_fin,
        asistentes=asistentes,
        cancelado=True,
    )
