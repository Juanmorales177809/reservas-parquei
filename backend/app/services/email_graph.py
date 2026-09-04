# -*- coding: utf-8 -*-
"""Correo saliente vía Microsoft Graph con token DELEGADO cacheado en disco.

PUENTE TEMPORAL mientras Sistemas del ITM entrega el App Registration con
`Mail.Send` de aplicación (`client_credentials`, sin sesión de usuario) --
ver `backend/CLAUDE.md`, sección "Correo por Microsoft Graph (puente
temporal)", y el ticket en `ticket-sistemas-graph-mail.html` (raíz del
repo). Reemplazar `_enviar_graph` por un flujo `client_credentials` real
apenas lleguen esas credenciales; no queda pensado como solución permanente.

Cómo funciona:
- Alguien con la contraseña de `settings.graph_mail_sender` corre
  `python -m scripts.graph_login` UNA VEZ, de forma interactiva (device
  code flow -- ningún navegador tiene que abrirse en el servidor, solo
  visitar una URL e ingresar un código desde cualquier dispositivo). Ese
  script deja el token (y su refresh token) cacheado en
  `settings.graph_token_cache_path`.
- El backend, en su ciclo normal (`procesar_pendientes`), SOLO intenta
  renovar el token en silencio (`acquire_token_silent`) -- nunca dispara
  un login interactivo por su cuenta, porque no hay ningún humano mirando
  la salida de un proceso desatendido. Si el token cacheado venció o el
  refresh token quedó inválido (cambio de contraseña, revocación de
  sesión, política de Conditional Access), el envío falla con un
  `RuntimeError` explícito -- mismo contrato que `_enviar_smtp`, capturado
  por `procesar_pendientes`, la fila queda `pendiente`/`fallido` según
  corresponda. Hace falta volver a correr `graph_login` a mano.

`CLIENT_ID` es el ID público bien conocido de "Microsoft Graph Command
Line Tools" (el mismo cliente que usa `Connect-MgGraph` de PowerShell por
defecto) -- una app de primera parte de Microsoft, pre-consentida en la
mayoría de los tenants, que no requiere que Sistemas cree ni apruebe nada
para este puente temporal. Es exactamente lo que permite arrancar "mientras
llega el permiso" sin otro ticket de por medio.

Nota (2026-09-03): se evaluó ampliar `SCOPES` con `Calendars.ReadWrite`
para invitar por la API de eventos de Graph -- descartado, el tenant del
ITM exige aprobación de un admin de Entra para ese scope puntual (a
diferencia de `Mail.Send`). La invitación de Outlook Calendar se resuelve
en cambio con un `.ics` de invitación real (`METHOD:REQUEST`) mandado por
este mismo canal de correo -- ver `services/calendario.py`, sin scope
nuevo. No reintroducir `Calendars.ReadWrite` acá sin que Sistemas lo
apruebe primero sobre el App Registration permanente (no sobre este
cliente genérico).
"""

from __future__ import annotations

import base64
import logging
import os
from typing import TYPE_CHECKING

import httpx
from msal import PublicClientApplication, SerializableTokenCache

from app.config import settings

if TYPE_CHECKING:
    from app.services.email import Adjunto
    from app.services.email_templates import ImagenInline

logger = logging.getLogger("app.email_graph")

CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"
AUTHORITY = "https://login.microsoftonline.com/common"
SCOPES = ["Mail.Send"]

_GRAPH_SEND_MAIL_URL_TEMPLATE = "https://graph.microsoft.com/v1.0/users/{sender}/sendMail"


def _cargar_cache() -> SerializableTokenCache:
    cache = SerializableTokenCache()
    ruta = settings.graph_token_cache_path
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            cache.deserialize(f.read())
    return cache


def _persistir_cache(cache: SerializableTokenCache) -> None:
    if not cache.has_state_changed:
        return
    ruta = settings.graph_token_cache_path
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(cache.serialize())


def _construir_app(cache: SerializableTokenCache) -> PublicClientApplication:
    return PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)


def _token_silencioso() -> str:
    """Renueva el token SOLO desde la caché -- nunca dispara un login
    interactivo (no hay humano mirando un proceso desatendido)."""
    cache = _cargar_cache()
    app = _construir_app(cache)
    cuentas = app.get_accounts()
    if not cuentas:
        raise RuntimeError(
            "No hay ninguna sesión de Graph cacheada -- correr "
            "'python -m scripts.graph_login' de forma interactiva para crearla."
        )
    resultado = app.acquire_token_silent(SCOPES, account=cuentas[0])
    _persistir_cache(cache)
    if not resultado or "access_token" not in resultado:
        detalle = (resultado or {}).get("error_description", "sin detalle")
        raise RuntimeError(
            "La sesión de Graph cacheada venció o quedó inválida "
            f"({detalle}) -- correr 'python -m scripts.graph_login' de nuevo."
        )
    return resultado["access_token"]


def login_interactivo() -> None:
    """Login único por device code flow -- pensado para correrse a mano
    (`scripts/graph_login.py`), nunca desde el backend en producción."""
    cache = _cargar_cache()
    app = _construir_app(cache)
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise RuntimeError(f"No se pudo iniciar el device flow: {flow}")
    print(flow["message"])  # noqa: T201 -- script interactivo, no logging
    resultado = app.acquire_token_by_device_flow(flow)
    _persistir_cache(cache)
    if "access_token" not in resultado:
        raise RuntimeError(f"No se pudo obtener el token: {resultado}")
    print(f"OK -- sesión cacheada en {settings.graph_token_cache_path}")  # noqa: T201


def enviar_graph(
    destinatario: str,
    asunto: str,
    cuerpo: str,
    es_html: bool = False,
    adjunto: "Adjunto | None" = None,
    imagenes_inline: "list[ImagenInline] | None" = None,
) -> None:
    token = _token_silencioso()
    url = _GRAPH_SEND_MAIL_URL_TEMPLATE.format(sender=settings.graph_mail_sender)
    payload = {
        "message": {
            "subject": asunto,
            "body": {"contentType": "HTML" if es_html else "Text", "content": cuerpo},
            "toRecipients": [{"emailAddress": {"address": destinatario}}],
        },
        "saveToSentItems": True,
    }
    attachments = []
    if adjunto is not None:
        attachments.append(
            {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": adjunto.nombre,
                "contentType": adjunto.content_type,
                "contentBytes": base64.b64encode(adjunto.contenido).decode("ascii"),
            }
        )
    for imagen in imagenes_inline or []:
        # `isInline`/`contentId`: el HTML la referencia por `cid:<id>`
        # (ver `email_templates.py::imagenes_inline_para`), mismo motivo
        # que en `_enviar_smtp` -- Outlook de escritorio no soporta
        # imágenes `data:` embebidas.
        attachments.append(
            {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": f"{imagen.cid}.png",
                "contentType": imagen.content_type,
                "contentBytes": base64.b64encode(imagen.contenido).decode("ascii"),
                "isInline": True,
                "contentId": imagen.cid,
            }
        )
    if attachments:
        payload["message"]["attachments"] = attachments
    respuesta = httpx.post(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=10,
    )
    if respuesta.status_code >= 400:
        raise RuntimeError(f"Graph sendMail falló ({respuesta.status_code}): {respuesta.text}")
