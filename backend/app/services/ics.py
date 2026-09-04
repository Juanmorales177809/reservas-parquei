"""Adjuntos `.ics` (RFC 5545) para reservas -- texto armado a mano con la
stdlib, sin depender del paquete `icalendar` (mismo criterio que el CSV del
export: alcanza con lo mínimo necesario).

`DTSTART`/`DTEND` se escriben como hora "flotante" (sin `Z`, sin `TZID`):
mismo criterio que el resto del dominio de reservas, que trata
`fecha`+`hora_inicio`/`hora_fin` como hora local naive de Bogotá en todos
lados (`services/reloj.py`), sin manejo explícito de zona horaria.
"""

from datetime import datetime, timezone

_CRLF = "\r\n"


def _escapar(texto: str) -> str:
    """Caracteres especiales de un campo de texto ICS (RFC 5545 §3.3.11)."""
    return texto.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def construir_ics(
    *, uid: str, resumen: str, descripcion: str, ubicacion: str, inicio: datetime, fin: datetime
) -> bytes:
    """`METHOD:PUBLISH` -- informativo, no es una invitación real (sin
    `ORGANIZER`/`ATTENDEE`). Se sigue usando como adjunto pasivo en el
    correo de confirmación al propio solicitante (`_adjunto_ics_reserva`
    en `services/reservas.py`) -- distinto de
    `construir_ics_invitacion`, que sí genera una invitación de reunión
    real (ver ese docstring)."""
    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lineas = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Sistema de Reservas de Laboratorios//ES",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART:{inicio.strftime('%Y%m%dT%H%M%S')}",
        f"DTEND:{fin.strftime('%Y%m%dT%H%M%S')}",
        f"SUMMARY:{_escapar(resumen)}",
        f"DESCRIPTION:{_escapar(descripcion)}",
        f"LOCATION:{_escapar(ubicacion)}",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return (_CRLF.join(lineas) + _CRLF).encode("utf-8")


def construir_ics_invitacion(
    *,
    uid: str,
    secuencia: int,
    resumen: str,
    descripcion: str,
    ubicacion: str,
    inicio: datetime,
    fin: datetime,
    organizador_email: str,
    organizador_nombre: str,
    asistentes: list[tuple[str, str]],
    categoria: str | None = None,
    cancelado: bool = False,
) -> bytes:
    """Invitación real de reunión (2026-09-03, `METHOD:REQUEST`/`CANCEL`)
    -- a diferencia de `construir_ics` (`PUBLISH`, pasivo), esta SÍ lleva
    `ORGANIZER`/`ATTENDEE`: es el estándar que usa cualquier invitación de
    calendario por correo (Outlook, Google Calendar, etc.) para que el
    cliente de correo del destinatario la reconozca sola y ofrezca
    Aceptar/Rechazar/Provisional, agregándola al calendario sin que la
    persona tenga que abrir el adjunto a mano.

    Reemplaza el intento original de esta feature (API de eventos de
    Microsoft Graph, `Calendars.ReadWrite`) -- ese scope quedó bloqueado
    por política de admin del tenant del ITM (ver `backend/CLAUDE.md`,
    sección de esta feature). Este mecanismo no depende de ningún permiso
    de Graph: viaja como adjunto de un correo normal, por el mismo canal
    (`Mail.Send`/SMTP) que ya funciona.

    `secuencia` (`SEQUENCE`, RFC 5545 §3.8.7.4) tiene que incrementarse en
    cada reprogramación/cancelación para que el cliente del destinatario
    sepa que es una versión más nueva del mismo evento (mismo `UID`) y no
    lo confunda con una invitación distinta -- ver
    `Reserva.calendario_secuencia`.

    `categoria` (`CATEGORIES`, opcional) -- típicamente el nombre del
    laboratorio: Outlook le asigna un color propio a cada categoría nueva
    que ve por primera vez (decisión local de cada persona, no algo que
    este servidor pueda dictar con un color exacto), así que laboratorios
    distintos terminan viéndose con colores distintos en la práctica.
    """
    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    metodo = "CANCEL" if cancelado else "REQUEST"
    estado = "CANCELLED" if cancelado else "CONFIRMED"
    lineas = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Sistema de Reservas de Laboratorios//ES",
        "CALSCALE:GREGORIAN",
        f"METHOD:{metodo}",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART:{inicio.strftime('%Y%m%dT%H%M%S')}",
        f"DTEND:{fin.strftime('%Y%m%dT%H%M%S')}",
        f"SUMMARY:{_escapar(resumen)}",
        f"DESCRIPTION:{_escapar(descripcion)}",
        f"LOCATION:{_escapar(ubicacion)}",
        f"SEQUENCE:{secuencia}",
        f"STATUS:{estado}",
        f"ORGANIZER;CN={_escapar(organizador_nombre)}:mailto:{organizador_email}",
    ]
    if categoria:
        lineas.append(f"CATEGORIES:{_escapar(categoria)}")
    for email, nombre in asistentes:
        lineas.append(f"ATTENDEE;CN={_escapar(nombre)};ROLE=REQ-PARTICIPANT;RSVP=TRUE:mailto:{email}")
    lineas += ["END:VEVENT", "END:VCALENDAR"]
    return (_CRLF.join(lineas) + _CRLF).encode("utf-8")
