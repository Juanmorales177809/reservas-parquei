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


def transmitir(destinatario: str, titulo: str, cuerpo: str, adjuntos: list[dict] | None = None, html: str | None = None) -> None:
    """`cuerpo` es el texto plano; `html`, el snapshot HTML institucional.
    Sin `html` se manda solo texto (compatibilidad y avisos simples)."""
    from app.core.config import get_settings

    settings = get_settings()
    adjuntos = adjuntos or []
    if settings.email_transport == "log":
        logger.info("Correo(dev) para %s: %s", destinatario, titulo)
        return
    try:
        if settings.email_transport == "smtp":
            _enviar_smtp(settings, destinatario, titulo, cuerpo, adjuntos, html)
        else:
            _enviar_graph(settings, destinatario, titulo, cuerpo, adjuntos, html)
    except ErrorTransmision:
        raise
    except Exception as exc:
        raise ErrorTransmision(f"Transmisión fallida ({type(exc).__name__}).") from exc


def _texto_plano(html: str) -> str:
    from html.parser import HTMLParser

    class _Extractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.partes: list[str] = []

        def handle_data(self, data: str):
            texto = data.strip()
            if texto:
                self.partes.append(texto)

    extractor = _Extractor()
    extractor.feed(html)
    return "\n".join(extractor.partes)


def _mensaje(settings, destinatario: str, titulo: str, cuerpo: str, adjuntos: list[dict], html: str | None = None) -> EmailMessage:
    from app.modules.notifications import plantillas

    mensaje = EmailMessage()
    mensaje["From"] = settings.smtp_from or settings.graph_mail_sender or "reservas@itm.edu.co"
    mensaje["To"] = destinatario
    mensaje["Subject"] = titulo
    if html:
        mensaje.set_content(_texto_plano(html))
        mensaje.add_alternative(html, subtype="html")
        parte_html = mensaje.get_body(("html",))
        for cid, tipo, contenido in plantillas.imagenes_inline_para(html):
            principal, secundario = tipo.split("/", 1)
            parte_html.add_related(contenido, maintype=principal, subtype=secundario, cid=cid)
    else:
        mensaje.set_content(cuerpo)
    for adjunto in adjuntos:
        mensaje.add_attachment(
            adjunto["contenido"], maintype=adjunto["content_type"].split("/")[0],
            subtype=adjunto["content_type"].split("/", 1)[1],
            filename=adjunto["nombre"],
        )
    return mensaje


def _enviar_smtp(settings, destinatario: str, titulo: str, cuerpo: str, adjuntos: list[dict], html: str | None = None) -> None:
    mensaje = _mensaje(settings, destinatario, titulo, cuerpo, adjuntos, html)
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


def _enviar_graph(settings, destinatario: str, titulo: str, cuerpo: str, adjuntos: list[dict], html: str | None = None) -> None:
    import httpx

    if not settings.graph_mail_sender:
        raise ErrorTransmision("GRAPH_MAIL_SENDER sin configurar.")
    # sendMail no admite inline `cid:` como los multipart de SMTP: el HTML
    # viaja igual y los adjuntos descargables aparte; las imágenes `cid:`
    # pueden no renderizar en algunos clientes por esta vía.
    cuerpo_html = html or f"<pre>{cuerpo}</pre>"
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
                "body": {"contentType": "HTML", "content": cuerpo_html},
                "toRecipients": [{"emailAddress": {"address": destinatario}}],
                "attachments": anexos,
            }
        },
        timeout=20,
    )
    if respuesta.status_code >= 300:
        raise ErrorTransmision(f"Graph sendMail falló ({respuesta.status_code}).")
