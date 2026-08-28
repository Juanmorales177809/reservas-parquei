# -*- coding: utf-8 -*-
"""Correo saliente vía outbox (`CorreoSaliente`).

El resto de este backend es enteramente síncrono (SQLAlchemy `Session`
síncrona, rutas FastAPI `def` normales, sin `asyncio` en ningún otro
módulo) — se usa `smtplib`/`email.mime` de la stdlib en vez de una
librería async, para no introducir el único punto async de todo el
proyecto por esto. Cero dependencia nueva en `requirements.txt`.
"""

from __future__ import annotations

import logging
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText

from sqlalchemy.orm import Session

from app.config import settings
from app.models.correo_saliente import CorreoSaliente
from app.services.email_graph import enviar_graph

logger = logging.getLogger("app.email")

# Tras este número de intentos fallidos, la fila pasa a `fallido` y deja de
# reintentarse sola -- evita que un destinatario/SMTP permanentemente roto
# se reintente para siempre en cada arranque y en cada correo nuevo que se
# encole (procesar_pendientes barre TODAS las pendientes, no solo la nueva).
MAX_INTENTOS = 5


def encolar_correo(
    db: Session, *, destinatario: str, asunto: str, cuerpo: str, es_html: bool = False
) -> CorreoSaliente:
    """Escribe una fila `pendiente` en el outbox.

    NO hace `commit`: debe viajar en la MISMA transacción que el cambio de
    negocio que la origina (reserva, alta de usuario, recuperación de
    contraseña) -- quien llama sigue siendo responsable de su propio commit.

    `es_html=True` para plantillas institucionales (ver
    `app/services/email_templates.py`) -- el resto de las notificaciones
    sigue en texto plano por default, sin cambiar su comportamiento actual.
    """
    correo = CorreoSaliente(destinatario=destinatario, asunto=asunto, cuerpo=cuerpo, es_html=es_html, estado="pendiente")
    db.add(correo)
    return correo


def _enviar_smtp(destinatario: str, asunto: str, cuerpo: str, es_html: bool = False) -> None:
    mensaje = MIMEText(cuerpo, "html" if es_html else "plain", "utf-8")
    mensaje["Subject"] = asunto
    mensaje["From"] = settings.smtp_from
    mensaje["To"] = destinatario

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        if settings.smtp_starttls:
            smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(mensaje)


def procesar_pendientes(db: Session) -> None:
    """Intenta enviar cada correo `pendiente` del outbox.

    Nunca propaga una excepción: un SMTP lento o caído no debe tumbar ni la
    petición que encoló el correo ni el arranque del backend (se llama
    también desde el `lifespan`, ver `app/main.py`) -- la fila simplemente
    queda `pendiente` (o pasa a `fallido` tras `MAX_INTENTOS`) para el
    próximo intento.

    Sin efecto si `EMAIL_ENABLED=false` (default): las notificaciones
    in-app siguen funcionando igual, el outbox solo se acumula sin
    intentar ningún envío real -- así se puede desplegar este código antes
    de tener credenciales SMTP reales.

    `EMAIL_TRANSPORT` decide el transporte real: `smtp` (default, sin
    cambios) o `graph_delegado` (puente temporal vía Microsoft Graph con
    token delegado cacheado -- ver `app/services/email_graph.py`).
    """
    if not settings.email_enabled:
        return
    enviar = enviar_graph if settings.email_transport == "graph_delegado" else _enviar_smtp
    pendientes = db.query(CorreoSaliente).filter(CorreoSaliente.estado == "pendiente").all()
    for correo in pendientes:
        try:
            enviar(correo.destinatario, correo.asunto, correo.cuerpo, correo.es_html)
        except Exception:
            logger.exception("Fallo enviando correo id=%s a %s", correo.id, correo.destinatario)
            correo.intentos += 1
            if correo.intentos >= MAX_INTENTOS:
                correo.estado = "fallido"
        else:
            correo.estado = "enviado"
            correo.enviado_en = datetime.now(timezone.utc)
    db.commit()
