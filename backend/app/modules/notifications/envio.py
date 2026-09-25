"""Remitente de correo (API-18): transmite un envío ya registrado.

Tres transportes, elegidos por settings (`EMAIL_TRANSPORT`):
`log` (desarrollo: registra y da por transmitido), `smtp` (stdlib) y
`graph_delegado` (patrón del repositorio anterior: Microsoft Graph con
token delegado cacheado en disco tras un login interactivo único, fuera
del backend). Ninguno persiste secretos: los errores se sanitizan antes
de guardar `ultimo_error`.

Adjunto: dict con `nombre`, `content_type` y `contenido` (bytes).
"""

from __future__ import annotations

import base64
import logging
import smtplib
from email.message import EmailMessage

logger = logging.getLogger("reservas.envio")


class ErrorTransmision(Exception):
    """Falla ya sanitizada, apta para `ultimo_error`."""


def transmitir(destinatario: str, titulo: str, cuerpo: str, adjuntos: list[dict] | None = None) -> None:
    from app.core.config import get_settings

    settings = get_settings()
    adjuntos = adjuntos or []
    if settings.email_transport == "log":
        logger.info("Correo(dev) para %s: %s", destinatario, titulo)
        return
    try:
        if settings.email_transport == "smtp":
            _enviar_smtp(settings, destinatario, titulo, cuerpo, adjuntos)
        else:
            _enviar_graph(settings, destinatario, titulo, cuerpo, adjuntos)
    except ErrorTransmision:
        raise
    except Exception as exc:
        raise ErrorTransmision(f"Transmisión fallida ({type(exc).__name__}).") from exc


def _mensaje(settings, destinatario: str, titulo: str, cuerpo: str, adjuntos: list[dict]) -> EmailMessage:
    mensaje = EmailMessage()
    mensaje["From"] = settings.smtp_from or settings.graph_mail_sender or "reservas@itm.edu.co"
    mensaje["To"] = destinatario
    mensaje["Subject"] = titulo
    mensaje.set_content(cuerpo)
    for adjunto in adjuntos:
        mensaje.add_attachment(
            adjunto["contenido"], maintype=adjunto["content_type"].split("/")[0],
            subtype=adjunto["content_type"].split("/", 1)[1],
            filename=adjunto["nombre"],
        )
    return mensaje


def _enviar_smtp(settings, destinatario: str, titulo: str, cuerpo: str, adjuntos: list[dict]) -> None:
    mensaje = _mensaje(settings, destinatario, titulo, cuerpo, adjuntos)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as cliente:
            cliente.starttls()
            if settings.smtp_user:
                cliente.login(settings.smtp_user, settings.smtp_password)
            cliente.send_message(mensaje)
    except (smtplib.SMTPException, OSError) as exc:
        raise ErrorTransmision(f"SMTP falló ({type(exc).__name__}).") from exc


def _token_graph(settings) -> str:
    """Token delegado silencioso del cache en disco. El login interactivo
    inicial se hace fuera del backend; aquí solo se renueva en silencio."""
    from msal import PublicClientApplication, SerializableTokenCache

    from app.core.config import get_settings as _ajustes

    settings = settings or _ajustes()
    cache = SerializableTokenCache()
    try:
        with open(settings.graph_token_cache_path, encoding="utf-8") as f:
            cache.deserialize(f.read())
    except OSError:
        pass
    # ID público de "Microsoft Graph Command Line Tools": mismo cliente que
    # usa Connect-MgGraph; evita registrar una app solo para enviar correo.
    app = PublicClientApplication(
        "14d82eec-204b-4c2f-b7e8-296a70dab67e",
        authority="https://login.microsoftonline.com/common",
        token_cache=cache,
    )
    cuentas = app.get_accounts()
    if not cuentas:
        raise ErrorTransmision("Sin sesión de Graph cacheada; falta el login interactivo inicial.")
    resultado = app.acquire_token_silent(["Mail.Send"], account=cuentas[0])
    if not resultado or "access_token" not in resultado:
        raise ErrorTransmision("La sesión de Graph venció; repetir el login interactivo.")
    return resultado["access_token"]


def _enviar_graph(settings, destinatario: str, titulo: str, cuerpo: str, adjuntos: list[dict]) -> None:
    import httpx

    if not settings.graph_mail_sender:
        raise ErrorTransmision("GRAPH_MAIL_SENDER sin configurar.")
    anexos = [
        {
            "@odata.type": "#microsoft.graph.fileAttachment",
            "name": a["nombre"],
            "contentType": a["content_type"],
            "contentBytes": base64.b64encode(a["contenido"]).decode(),
        }
        for a in adjuntos
    ]
    url = f"https://graph.microsoft.com/v1.0/users/{settings.graph_mail_sender}/sendMail"
    respuesta = httpx.post(
        url,
        headers={"Authorization": f"Bearer {_token_graph(settings)}"},
        json={
            "message": {
                "subject": titulo,
                "body": {"contentType": "Text", "content": cuerpo},
                "toRecipients": [{"emailAddress": {"address": destinatario}}],
                "attachments": anexos,
            }
        },
        timeout=20,
    )
    if respuesta.status_code >= 300:
        raise ErrorTransmision(f"Graph sendMail falló ({respuesta.status_code}).")
