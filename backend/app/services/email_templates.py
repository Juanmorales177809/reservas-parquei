# -*- coding: utf-8 -*-
"""Plantillas HTML institucionales para el outbox (`app/services/email.py`).

HTML de correo, no de página web: tablas + estilos inline, sin CSS externo
ni gradientes fiables (Outlook de escritorio usa el motor de Word, que
ignora `linear-gradient` -- por eso todo bloque con gradiente lleva también
un `background-color` sólido de respaldo). Colores y wordmark tomados de la
identidad ya establecida de la app (`app_flutter/lib/core/theme/app_theme.dart`
-- azul académico `#1E3A8A` + esmeralda `#10B981`, ícono de calendario en
`BrandMark`); los colores de estado de reserva son los MISMOS hex que ya usa
`app_flutter/.../notificaciones_sheet.dart::_NotificacionTile` para que un
correo y su notificación in-app se sientan del mismo sistema, no de dos
paletas distintas.

Cada `plantilla_*` arma su bloque de contenido y lo envuelve con
`_envoltorio()` (masthead + pie compartidos) -- un solo esqueleto de
documento, no uno repetido por plantilla.
"""

from __future__ import annotations

import html

_AZUL_ACADEMICO = "#1e3a8a"
_ESMERALDA = "#10b981"

# (borde, tinte de fondo, texto del título dentro de la tarjeta) -- mismos
# hex que TipoNotificacion en notificaciones_sheet.dart.
_COLORES_ESTADO = {
    "pendiente": ("#d97706", "#fef3c7", "#92400e"),
    "aprobada": ("#10b981", "#d1fae5", "#065f46"),
    "rechazada": ("#dc2626", "#fee2e2", "#991b1b"),
    "cancelada": ("#6b7280", "#f1f5f9", "#334155"),
    "actualizada": ("#1e3a8a", "#dbeafe", "#1e3a8a"),
}


def _esc(texto: str) -> str:
    return html.escape(texto)


def _envoltorio(*, contenido_html: str) -> str:
    return f"""\
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reservas Parque i</title>
</head>
<body style="margin:0;padding:0;background-color:#f1f5f9;font-family:Arial,Helvetica,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f1f5f9;padding:32px 16px;">
<tr>
<td align="center">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;background-color:#ffffff;border-radius:16px;overflow:hidden;border:1px solid #e2e8f0;">
<tr>
<td style="background-image:linear-gradient(135deg,{_AZUL_ACADEMICO},{_ESMERALDA});background-color:{_AZUL_ACADEMICO};padding:28px 32px;">
<span style="display:block;font-size:11px;letter-spacing:1px;text-transform:uppercase;color:#dbeafe;font-weight:700;">Instituto Tecnologico Metropolitano</span>
<span style="display:block;font-size:20px;font-weight:800;color:#ffffff;margin-top:4px;">Reservas Parque i</span>
</td>
</tr>
<tr>
<td style="padding:32px;">
{contenido_html}
</td>
</tr>
<tr>
<td style="padding:20px 32px;background-color:#f8fafc;border-top:1px solid #e2e8f0;">
<p style="margin:0;font-size:12px;color:#94a3b8;">Este es un mensaje automatico del Sistema de Reservas de Laboratorios - Parque i, ITM. No respondas a este correo.</p>
</td>
</tr>
</table>
</td>
</tr>
</table>
</body>
</html>
"""


def _tarjeta_reserva(*, estado: str, titulo: str, fecha: str, hora_inicio: str, hora_fin: str) -> str:
    borde, tinte, texto = _COLORES_ESTADO[estado]
    return f"""\
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 20px;background-color:{tinte};border-left:4px solid {borde};border-radius:6px;">
<tr>
<td style="padding:14px 16px;">
<p style="margin:0;font-size:14px;font-weight:700;color:{texto};">{_esc(titulo)}</p>
<p style="margin:6px 0 0;font-size:14px;color:#334155;">{_esc(fecha)} &middot; {_esc(hora_inicio)}&ndash;{_esc(hora_fin)}</p>
</td>
</tr>
</table>
"""


def plantilla_invitacion(*, link: str, nombre_saludo: str = "") -> str:
    """Invitación para crear/activar una cuenta (alta inicial o reenvío).

    `nombre_saludo` es texto controlado por el usuario (username) --
    siempre se escapa antes de insertarlo en el HTML.
    """
    saludo = f" {_esc(nombre_saludo)}" if nombre_saludo else ""
    link_html = html.escape(link, quote=True)

    contenido = f"""\
<p style="margin:0 0 16px;font-size:16px;line-height:1.5;color:#0f172a;">Hola{saludo},</p>
<p style="margin:0 0 24px;font-size:15px;line-height:1.6;color:#334155;">
Te invitaron a crear tu cuenta en el <strong>Sistema de Reservas de Laboratorios</strong> del Parque i.
Con ella vas a poder reservar espacios y equipos, y hacer seguimiento a tus solicitudes.
</p>
<table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
<tr>
<td style="border-radius:10px;background-color:{_AZUL_ACADEMICO};">
<a href="{link_html}" style="display:inline-block;padding:14px 28px;font-size:15px;font-weight:700;color:#ffffff;text-decoration:none;border-radius:10px;">Crear mi cuenta</a>
</td>
</tr>
</table>
<p style="margin:0 0 8px;font-size:13px;line-height:1.5;color:#64748b;">Si el boton no funciona, copia y pega este link en tu navegador:</p>
<p style="margin:0 0 24px;font-size:13px;line-height:1.5;word-break:break-all;"><a href="{link_html}" style="color:{_AZUL_ACADEMICO};">{link_html}</a></p>
<p style="margin:0;font-size:13px;line-height:1.5;color:#94a3b8;">Si vos no solicitaste esta cuenta, podes ignorar este correo.</p>\
"""
    return _envoltorio(contenido_html=contenido)


def plantilla_reserva_pendiente(*, nombre_saludo: str, espacio: str, fecha: str, hora_inicio: str, hora_fin: str) -> str:
    """Aviso al gestor: hay una reserva nueva esperando su aprobación."""
    tarjeta = _tarjeta_reserva(estado="pendiente", titulo=espacio, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin)
    contenido = f"""\
<p style="margin:0 0 16px;font-size:16px;line-height:1.5;color:#0f172a;">Hola {_esc(nombre_saludo)},</p>
<p style="margin:0 0 20px;font-size:15px;line-height:1.6;color:#334155;">Hay una nueva reserva pendiente de tu aprobación:</p>
{tarjeta}
<p style="margin:0;font-size:14px;line-height:1.6;color:#334155;">Ingresá al sistema de reservas para aprobarla o rechazarla.</p>\
"""
    return _envoltorio(contenido_html=contenido)


def plantilla_reserva_estado(
    *,
    nombre_saludo: str,
    reserva_id: int,
    espacio: str,
    fecha: str,
    hora_inicio: str,
    hora_fin: str,
    estado: str,
    motivo: str | None = None,
) -> str:
    """Aviso al solicitante: su reserva cambió de estado (aprobada,
    rechazada o cancelada). `estado` es la clave en minúscula de
    `_COLORES_ESTADO` -- ya validada en services/reservas.py antes de
    llegar acá, no repite esa validación."""
    verbo = {"aprobada": "aprobada", "rechazada": "rechazada", "cancelada": "cancelada"}[estado]
    tarjeta = _tarjeta_reserva(estado=estado, titulo=espacio, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin)
    motivo_html = ""
    if estado == "rechazada" and motivo:
        motivo_html = f"""\
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 20px;">
<tr>
<td style="padding:12px 16px;background-color:#f8fafc;border-radius:6px;border:1px solid #e2e8f0;">
<p style="margin:0;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.04em;color:#94a3b8;">Motivo</p>
<p style="margin:4px 0 0;font-size:14px;color:#334155;">{_esc(motivo)}</p>
</td>
</tr>
</table>
"""
    contenido = f"""\
<p style="margin:0 0 16px;font-size:16px;line-height:1.5;color:#0f172a;">Hola {_esc(nombre_saludo)},</p>
<p style="margin:0 0 20px;font-size:15px;line-height:1.6;color:#334155;">Tu reserva #{reserva_id} fue <strong>{verbo}</strong>:</p>
{tarjeta}
{motivo_html}
<p style="margin:0;font-size:14px;line-height:1.6;color:#334155;">Ingresá al sistema de reservas para más detalles.</p>\
"""
    return _envoltorio(contenido_html=contenido)


def plantilla_reserva_actualizada(
    *, nombre_saludo: str, reserva_id: int, espacio: str, fecha: str, hora_inicio: str, hora_fin: str, detalle: str
) -> str:
    """Aviso al solicitante: un gestor le agregó recursos/zonas a una
    reserva ya aprobada (Feature B, ver services/reservas.py::actualizar_reserva)."""
    tarjeta = _tarjeta_reserva(estado="actualizada", titulo=espacio, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin)
    contenido = f"""\
<p style="margin:0 0 16px;font-size:16px;line-height:1.5;color:#0f172a;">Hola {_esc(nombre_saludo)},</p>
<p style="margin:0 0 20px;font-size:15px;line-height:1.6;color:#334155;">Tu reserva #{reserva_id} fue actualizada. Se agregaron {_esc(detalle)}:</p>
{tarjeta}
<p style="margin:0;font-size:14px;line-height:1.6;color:#334155;">Ingresá al sistema de reservas para más detalles.</p>\
"""
    return _envoltorio(contenido_html=contenido)
