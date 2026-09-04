# -*- coding: utf-8 -*-
"""Correo saliente vía outbox (`CorreoSaliente`).

El resto de este backend es enteramente síncrono (SQLAlchemy `Session`
síncrona, rutas FastAPI `def` normales, sin `asyncio` en ningún otro
módulo) — se usa `smtplib`/`email.mime` de la stdlib en vez de una
librería async, para no introducir el único punto async de todo el
proyecto por esto. Cero dependencia nueva en `requirements.txt`.
"""

from __future__ import annotations

import base64
import logging
import smtplib
from dataclasses import dataclass
from datetime import datetime, timezone
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy.orm import Session

from app.config import settings
from app.models.correo_saliente import CorreoSaliente
from app.services.email_graph import enviar_graph
from app.services.email_templates import ImagenInline, imagenes_inline_para

logger = logging.getLogger("app.email")

# Tras este número de intentos fallidos, la fila pasa a `fallido` y deja de
# reintentarse sola -- evita que un destinatario/SMTP permanentemente roto
# se reintente para siempre en cada arranque y en cada correo nuevo que se
# encole (procesar_pendientes barre TODAS las pendientes, no solo la nueva).
MAX_INTENTOS = 5


@dataclass(frozen=True)
class Adjunto:
    """Un único adjunto (2026-08-29, ronda 2 -- primer adjunto del outbox:
    `.ics` de confirmación de reserva, ver `app/services/ics.py`). Sin
    soporte para más de uno por correo -- no hay caso de uso hoy."""

    nombre: str
    contenido: bytes
    content_type: str


def encolar_correo(
    db: Session, *, destinatario: str, asunto: str, cuerpo: str, es_html: bool = False, adjunto: Adjunto | None = None
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
    if adjunto is not None:
        correo.adjunto_nombre = adjunto.nombre
        correo.adjunto_content_type = adjunto.content_type
        correo.adjunto_contenido = base64.b64encode(adjunto.contenido).decode("ascii")
    db.add(correo)
    return correo


def _enviar_smtp(
    destinatario: str,
    asunto: str,
    cuerpo: str,
    es_html: bool = False,
    adjunto: Adjunto | None = None,
    imagenes_inline: list[ImagenInline] | None = None,
) -> None:
    cuerpo_mime: MIMEText | MIMEMultipart = MIMEText(cuerpo, "html" if es_html else "plain", "utf-8")
    if imagenes_inline:
        # `multipart/related`: el HTML referencia cada imagen por
        # `cid:<id>` (ver `email_templates.py::imagenes_inline_para`) --
        # necesario porque Outlook de escritorio no renderiza imágenes
        # `data:` embebidas en `<img src>`.
        relacionado = MIMEMultipart("related")
        relacionado.attach(cuerpo_mime)
        for imagen in imagenes_inline:
            parte_imagen = MIMEImage(imagen.contenido, _subtype=imagen.content_type.split("/")[-1])
            parte_imagen.add_header("Content-ID", f"<{imagen.cid}>")
            parte_imagen.add_header("Content-Disposition", "inline", filename=f"{imagen.cid}.png")
            relacionado.attach(parte_imagen)
        cuerpo_mime = relacionado

    if adjunto is None:
        mensaje = cuerpo_mime
    else:
        mensaje = MIMEMultipart("mixed")
        mensaje.attach(cuerpo_mime)
        parte_adjunto = MIMEApplication(adjunto.contenido, _subtype=adjunto.content_type.split("/")[-1])
        parte_adjunto.add_header("Content-Disposition", "attachment", filename=adjunto.nombre)
        mensaje.attach(parte_adjunto)
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
        adjunto = (
            Adjunto(
                nombre=correo.adjunto_nombre,
                contenido=base64.b64decode(correo.adjunto_contenido),
                content_type=correo.adjunto_content_type,
            )
            if correo.adjunto_contenido is not None
            else None
        )
        # Solo las plantillas HTML referencian imágenes por `cid:` -- un
        # correo de texto plano nunca contiene esa marca, así que esto
        # devuelve una lista vacía sin costo extra en ese caso.
        imagenes_inline = imagenes_inline_para(correo.cuerpo) if correo.es_html else None
        try:
            enviar(correo.destinatario, correo.asunto, correo.cuerpo, correo.es_html, adjunto, imagenes_inline)
        except Exception:
            logger.exception("Fallo enviando correo id=%s a %s", correo.id, correo.destinatario)
            correo.intentos += 1
            if correo.intentos >= MAX_INTENTOS:
                correo.estado = "fallido"
        else:
            correo.estado = "enviado"
            correo.enviado_en = datetime.now(timezone.utc)
    db.commit()
