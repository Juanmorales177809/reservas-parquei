# -*- coding: utf-8 -*-
"""Outbox de eventos de Outlook Calendar (`EventoCalendarioSaliente`) --
mismo patrón *transactional outbox* que `app/services/email.py`, pero para
la invitación de Graph Calendar (ver `app/services/email_graph.py`).

Deliberadamente diferido: crear un evento de Graph es la primera llamada
HTTP real en vivo de este tipo en el proyecto (a diferencia del `.ics`,
bytes en memoria que nunca fallan por red) -- no puede alargar ni poder
tumbar la request que aprueba la reserva.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import settings
from app.models.evento_calendario_saliente import EventoCalendarioSaliente
from app.models.reserva import Reserva
from app.services.email_graph import (
    actualizar_evento_calendario_graph,
    cancelar_evento_calendario_graph,
    crear_evento_calendario_graph,
)

logger = logging.getLogger("app.calendario")

# Mismo criterio que `services/email.py::MAX_INTENTOS`.
MAX_INTENTOS = 5


def encolar_evento_calendario(
    db: Session,
    *,
    reserva_id: int | None,
    accion: str,
    graph_event_id: str | None = None,
    asunto: str | None = None,
    cuerpo: str | None = None,
    ubicacion: str | None = None,
    inicio: datetime | None = None,
    fin: datetime | None = None,
    asistentes: list[tuple[str, str]] | None = None,
    comentario: str | None = None,
) -> EventoCalendarioSaliente:
    """Escribe una fila `pendiente` en el outbox. NO hace `commit` -- debe
    viajar en la MISMA transacción que el cambio de negocio que la origina
    (mismo contrato que `email.py::encolar_correo`)."""
    evento = EventoCalendarioSaliente(
        reserva_id=reserva_id,
        accion=accion,
        estado="pendiente",
        graph_event_id=graph_event_id,
        asunto=asunto,
        cuerpo=cuerpo,
        ubicacion=ubicacion,
        inicio=inicio,
        fin=fin,
        asistentes=[list(a) for a in asistentes] if asistentes is not None else None,
        comentario=comentario,
    )
    db.add(evento)
    return evento


def procesar_eventos_calendario_pendientes(db: Session) -> None:
    """Intenta procesar cada fila `pendiente` del outbox. Nunca propaga una
    excepción -- un timeout o error de Graph no debe tumbar la operación
    que la encoló, la fila simplemente queda `pendiente` (o pasa a
    `fallido` tras `MAX_INTENTOS`).

    Gateado por `settings.email_enabled`, el mismo interruptor que
    `email.py::procesar_pendientes` -- la invitación de calendario depende
    del mismo puente MSAL que el correo por Graph (`email_graph.py`), así
    que no tiene sentido intentarla si ese puente ni siquiera está
    habilitado.
    """
    if not settings.email_enabled:
        return
    pendientes = db.query(EventoCalendarioSaliente).filter(EventoCalendarioSaliente.estado == "pendiente").all()
    for evento in pendientes:
        try:
            if evento.accion == "crear":
                asistentes = [(email, nombre) for email, nombre in (evento.asistentes or [])]
                event_id = crear_evento_calendario_graph(
                    asunto=evento.asunto or "",
                    cuerpo=evento.cuerpo or "",
                    inicio=evento.inicio,
                    fin=evento.fin,
                    ubicacion=evento.ubicacion or "",
                    asistentes=asistentes,
                )
                evento.graph_event_id = event_id
                reserva = db.query(Reserva).filter(Reserva.id == evento.reserva_id).first()
                if reserva is not None:
                    reserva.graph_event_id = event_id
            elif evento.accion == "actualizar":
                actualizar_evento_calendario_graph(evento.graph_event_id, inicio=evento.inicio, fin=evento.fin)
            elif evento.accion == "cancelar":
                cancelar_evento_calendario_graph(evento.graph_event_id, comentario=evento.comentario or "")
        except Exception:
            logger.exception(
                "Fallo procesando evento de calendario id=%s reserva_id=%s accion=%s",
                evento.id,
                evento.reserva_id,
                evento.accion,
            )
            evento.intentos += 1
            if evento.intentos >= MAX_INTENTOS:
                evento.estado = "fallido"
        else:
            evento.estado = "enviado"
            evento.procesado_en = datetime.now(timezone.utc)
    db.commit()
