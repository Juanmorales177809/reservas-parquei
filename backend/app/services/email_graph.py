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
"""

from __future__ import annotations

import base64
import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING

import httpx
from msal import PublicClientApplication, SerializableTokenCache

from app.config import settings

if TYPE_CHECKING:
    from app.services.email import Adjunto

logger = logging.getLogger("app.email_graph")

CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"
AUTHORITY = "https://login.microsoftonline.com/common"
# `Calendars.ReadWrite` (2026-09-03, invitación de Outlook Calendar):
# ampliado sobre el scope original de solo correo. El token cacheado antes
# de este cambio SOLO consintió `Mail.Send` -- hace falta correr
# `python -m scripts.graph_login` de nuevo (a mano, con la contraseña de
# `settings.graph_mail_sender`) para que el nuevo scope quede consentido;
# `_token_silencioso()` no lo hace sola. Ver `services/calendario.py`.
SCOPES = ["Mail.Send", "Calendars.ReadWrite"]

_GRAPH_SEND_MAIL_URL_TEMPLATE = "https://graph.microsoft.com/v1.0/users/{sender}/sendMail"
_GRAPH_EVENTS_URL_TEMPLATE = "https://graph.microsoft.com/v1.0/users/{sender}/events"
_GRAPH_EVENT_URL_TEMPLATE = "https://graph.microsoft.com/v1.0/users/{sender}/events/{event_id}"
_GRAPH_EVENT_CANCEL_URL_TEMPLATE = "https://graph.microsoft.com/v1.0/users/{sender}/events/{event_id}/cancel"


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


def enviar_graph(destinatario: str, asunto: str, cuerpo: str, es_html: bool = False, adjunto: "Adjunto | None" = None) -> None:
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
    if adjunto is not None:
        payload["message"]["attachments"] = [
            {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": adjunto.nombre,
                "contentType": adjunto.content_type,
                "contentBytes": base64.b64encode(adjunto.contenido).decode("ascii"),
            }
        ]
    respuesta = httpx.post(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=10,
    )
    if respuesta.status_code >= 400:
        raise RuntimeError(f"Graph sendMail falló ({respuesta.status_code}): {respuesta.text}")


def crear_evento_calendario_graph(
    *,
    asunto: str,
    cuerpo: str,
    inicio: datetime,
    fin: datetime,
    ubicacion: str,
    asistentes: list[tuple[str, str]],
) -> str:
    """Crea una reunión organizada por `settings.graph_mail_sender`,
    invitando a `asistentes` (email, nombre) -- Outlook la agrega sola al
    calendario de cada uno al recibir la invitación, sin necesitar acceso
    directo al calendario de nadie más. Devuelve el `id` del evento creado
    (se guarda en `Reserva.graph_event_id` para poder actualizarlo o
    cancelarlo después)."""
    token = _token_silencioso()
    url = _GRAPH_EVENTS_URL_TEMPLATE.format(sender=settings.graph_mail_sender)
    payload = {
        "subject": asunto,
        "body": {"contentType": "HTML", "content": cuerpo},
        "start": {"dateTime": inicio.isoformat(), "timeZone": "America/Bogota"},
        "end": {"dateTime": fin.isoformat(), "timeZone": "America/Bogota"},
        "location": {"displayName": ubicacion},
        "attendees": [
            {"emailAddress": {"address": email, "name": nombre}, "type": "required"}
            for email, nombre in asistentes
        ],
    }
    respuesta = httpx.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload, timeout=10)
    if respuesta.status_code >= 400:
        raise RuntimeError(f"Graph crear evento falló ({respuesta.status_code}): {respuesta.text}")
    return respuesta.json()["id"]


def actualizar_evento_calendario_graph(event_id: str, *, inicio: datetime, fin: datetime) -> None:
    """Reprograma un evento ya creado (reserva aprobada que cambió de
    horario vía `actualizar_reserva`)."""
    token = _token_silencioso()
    url = _GRAPH_EVENT_URL_TEMPLATE.format(sender=settings.graph_mail_sender, event_id=event_id)
    payload = {
        "start": {"dateTime": inicio.isoformat(), "timeZone": "America/Bogota"},
        "end": {"dateTime": fin.isoformat(), "timeZone": "America/Bogota"},
    }
    respuesta = httpx.patch(url, headers={"Authorization": f"Bearer {token}"}, json=payload, timeout=10)
    if respuesta.status_code >= 400:
        raise RuntimeError(f"Graph actualizar evento falló ({respuesta.status_code}): {respuesta.text}")


def cancelar_evento_calendario_graph(event_id: str, *, comentario: str = "") -> None:
    """`POST .../cancel`, no `DELETE` -- Outlook manda automáticamente el
    aviso de cancelación a los asistentes (decisión confirmada: ya habían
    recibido la invitación, deben enterarse de que se retiró)."""
    token = _token_silencioso()
    url = _GRAPH_EVENT_CANCEL_URL_TEMPLATE.format(sender=settings.graph_mail_sender, event_id=event_id)
    respuesta = httpx.post(url, headers={"Authorization": f"Bearer {token}"}, json={"comment": comentario}, timeout=10)
    if respuesta.status_code >= 400:
        raise RuntimeError(f"Graph cancelar evento falló ({respuesta.status_code}): {respuesta.text}")
