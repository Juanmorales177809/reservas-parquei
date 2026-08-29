"""Adjunto `.ics` (RFC 5545) para la confirmación de una reserva aprobada
-- texto armado a mano con la stdlib, sin depender del paquete `icalendar`
(mismo criterio que el CSV del export: alcanza con lo mínimo necesario).

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
