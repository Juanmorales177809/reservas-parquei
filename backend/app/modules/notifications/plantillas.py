# -*- coding: utf-8 -*-
"""Plantillas HTML institucionales del correo (neutro, marca ITM).

Portado del sistema anterior (`email_templates.py`): esqueleto Outlook-safe
(tablas `role="presentation"`, estilos inline, bloque `<!--[if mso]>`,
preheader oculto), tarjeta de estado por colores, botón y pie compartidos.
Los textos se reescribieron en tono neutro; la marca y la maquetación se
conservan, incluidos los assets embebidos (`_LOGO_ITM_B64`,
`_ICONO_BIENVENIDA_B64`, referenciados por `cid:` porque Outlook de
escritorio no renderiza `data:`).

Cada función recibe datos ya validados y escapa todo input de usuario
(RN-CNT-02). El HTML resultante es el snapshot que se guarda en
`envios_correo.cuerpo`: una redacción nueva no reinterpreta lo ya enviado
(RN-CNT-04/06, RN-HIS-03).
"""

from __future__ import annotations

import base64
import html

_NAVY = "#102d69"
_TEAL = "#00a0b7"
_SKY = "#56acde"

SOPORTE_EMAIL = "reservaslabparquei@correo.itm.edu.co"

# Recorte real de "Institución Universitaria ITM" (misma institución).
_LOGO_ITM_B64 = (
    "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"
)

# Ilustración plana genérica de bienvenida (sin rostros reales).
_ICONO_BIENVENIDA_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAQQAAADqCAMAAABz78t+AAAAwFBMVEVZmrDH0N+Vo8cemqQhR3osssVmo8hRaqIgPYRDVHo7aJ0IIF+s7vOAjrgABD76+/0XPIPa5vp5wdGUwueQvuWExtUbQIjk6vcUNnau2OgHKW14vc0Spba2xdfM2ecqSYgLmq0uqbtyh6w2VI0qRnequM+OutWqyeaGl7UAGFVOZ5PZ8/eVqMWs1dxFW42O0txme6YJJVrDzNoAHGQiO3QvrcCQo7uu4uhUd6eY2eNkd5p8kbRYc5kUqMEACFJwmcu/YIcWAAAAQHRSTlP/////////////////////////////////////////////////////////////////////////////////////73leyQAAD3JJREFUeNrtnQt/oroSwNF22909916IigmhgPLwge/Hqa1td7//t7qTgIoIvoqa7mZ+Z7tWcSH/zExmkkmOokpRFYlAQpAQJAQJQUKQECQECUFCkBAkBAlBQpAQJAQJQUKQECSELwIBr+SvgwBtRnkiCg/lwj2PDsvtSSi3BSCGSijXNgEROSgXIIDOlVtxUIQhcEMMhUL4JIGbcVCuqQWrOEE0DMrFEeR6vD048JeEgPN7/nAQeXMMygURfC6mwF8KAi6iIzMwXM81KMUzOPfhdzngrwIBF9l/OxzwV4CAi1bhNAYsPISL6G/aS2KxIaQZFPZQ11YGpTAGhT4rvuowoQjaXds2gcWEcHm7vSIFRVQG16SgiPx8+EoUFKH76EoUlKs9Wg/11i61d45/xCJBOIsBGj08VBas8YuKokSvTsWAxYFwFoNX5enj6alhqqrefHp6at4pvTPuh0WBcBaD/ygNDqFh6s1G44lhqJwVMogB4SwGvQpr91PjqXHX5K8+vj3dIVUYXfgEhOO/NLiLIHAd4AJvjFRhKChnx8onfMuA5nMCMYWPj9MgJChcJI9QztUDfBqERkINmHs4DYJ62SFCuQIDDuFpWxqNkSoMBeUKDFSkpBl8NO4WqjAUlLMcwqnP8Z9mI8WgcXygcHkKylWeovcAzvDjIwGhuVBVYSgolx0cNwbx9O0joQpN/VPTODeD8LlHWDQb36JQgTnJu4r6qcQN3wjCZ59g1OQMosFSQZ/MrG8D4fO9YNw1VhBOdoo7T4Fv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"
)

CID_LOGO_ITM = "logo-itm"
CID_ICONO_BIENVENIDA = "icono-bienvenida"

_COLORES_ESTADO = {
    "pendiente": ("#d97706", "#fef3c7", "#92400e"),
    "aprobada": ("#10b981", "#d1fae5", "#065f46"),
    "rechazada": ("#dc2626", "#fee2e2", "#991b1b"),
    "cancelada": ("#6b7280", "#f1f5f9", "#334155"),
    "actualizada": (_NAVY, "#dbeafe", _NAVY),
}


def imagenes_inline_para(cuerpo: str) -> list[tuple[str, str, bytes]]:
    """(cid, content_type, bytes) referenciados por el HTML."""
    imagenes = []
    if f"cid:{CID_LOGO_ITM}" in cuerpo:
        imagenes.append((CID_LOGO_ITM, "image/png", base64.b64decode(_LOGO_ITM_B64)))
    if f"cid:{CID_ICONO_BIENVENIDA}" in cuerpo:
        imagenes.append((CID_ICONO_BIENVENIDA, "image/png", base64.b64decode(_ICONO_BIENVENIDA_B64)))
    return imagenes


def _esc(texto) -> str:
    return html.escape("" if texto is None else str(texto))


def _envoltorio(*, preheader: str, contenido_html: str, disclaimer: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reservas Parque i - Institución Universitaria ITM</title>
<!--[if mso]>
<noscript>
<xml>
<o:OfficeDocumentSettings>
<o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings>
</xml>
</noscript>
<![endif]-->
<style>
body, table, td, a {{ -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }}
table, td {{ mso-table-lspace:0pt; mso-table-rspace:0pt; }}
img {{ -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }}
body {{ margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }}
a {{ text-decoration:none; }}
@media screen and (max-width:600px) {{
  .email-container {{ width:100% !important; }}
  .fluid-padding {{ padding-left:24px !important; padding-right:24px !important; }}
  .stack-col {{ display:block !important; width:100% !important; }}
  .h1-mobile {{ font-size:24px !important; }}
}}
</style>
</head>
<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">{_esc(preheader)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">
<tr>
<td align="center" style="padding:32px 16px;">
<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">
<tr>
<td class="fluid-padding" style="padding:30px 40px 22px 40px;">
<table role="presentation" cellpadding="0" cellspacing="0">
<tr>
<td valign="top" style="padding-right:14px;">
<table role="presentation" cellpadding="0" cellspacing="0">
<tr><td style="width:5px;height:12px;background-color:{_NAVY};font-size:0;line-height:0;">&nbsp;</td></tr>
<tr><td style="width:5px;height:12px;background-color:{_TEAL};font-size:0;line-height:0;">&nbsp;</td></tr>
<tr><td style="width:5px;height:12px;background-color:{_SKY};font-size:0;line-height:0;">&nbsp;</td></tr>
</table>
</td>
<td valign="middle">
<p style="margin:0;font-size:23px;font-weight:800;color:{_NAVY};line-height:1.25;">Reservas Parque i</p>
<p style="margin:2px 0 0 0;font-size:14px;font-weight:600;color:{_TEAL};">Laboratorios de Investigación</p>
</td>
<td valign="middle" align="right" style="padding-left:16px;">
<img src="cid:{CID_LOGO_ITM}" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td style="padding:0 40px;">
<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">
</td>
</tr>
{contenido_html}
<tr>
<td align="center" style="padding:20px 40px 28px 40px;">
<p style="margin:0;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">{_esc(disclaimer)}</p>
<p style="margin:12px 0 0 0;font-size:13px;"><a href="mailto:{SOPORTE_EMAIL}" style="color:{_TEAL};font-weight:600;">{SOPORTE_EMAIL}</a></p>
<p style="margin:4px 0 0 0;font-size:12px;color:#a7adb6;">Institución Universitaria ITM &middot; No responda a este correo.</p>
</td>
</tr>
</table>
</td>
</tr>
</table>
</body>
</html>
"""


def _tarjeta(*, estado: str, titulo: str, lineas: str) -> str:
    borde, tinte, texto = _COLORES_ESTADO[estado]
    return f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;background-color:{tinte};border-left:4px solid {borde};border-radius:8px;">
<tr>
<td style="padding:14px 18px;">
<p style="margin:0;font-size:14px;font-weight:800;color:{texto};">{_esc(titulo)}</p>
<p style="margin:6px 0 0;font-size:14px;color:#4a4f58;">{lineas}</p>
</td>
</tr>
</table>
"""


def _boton(*, texto: str, link: str) -> str:
    link_html = html.escape(link, quote=True)
    return f"""<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;">
<tr>
<td align="center" style="border-radius:8px;background-color:{_NAVY};">
<a href="{link_html}" target="_blank" style="display:block;padding:16px 24px;font-size:15px;font-weight:800;letter-spacing:0.6px;color:#ffffff;text-align:center;text-transform:uppercase;">{_esc(texto)}</a>
</td>
</tr>
</table>
"""


def _bloque_simple(*, saludo: str, titulo: str, cuerpo_html: str, cierre: str) -> str:
    return f"""<tr>
<td class="fluid-padding" style="padding:32px 40px 6px 40px;">
<p style="margin:0 0 6px 0;font-size:20px;color:{_NAVY};font-weight:500;">Hola, <strong style="font-weight:800;">{_esc(saludo)}</strong></p>
<h1 class="h1-mobile" style="margin:14px 0 0 0;font-size:26px;line-height:1.3;color:{_NAVY};font-weight:800;">{titulo}</h1>
<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">
<tr><td style="width:64px;height:4px;background-color:{_TEAL};font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>
</table>
</td>
</tr>
<tr>
<td class="fluid-padding" style="padding:26px 40px 30px 40px;">
{cuerpo_html}
<p style="margin:0;font-size:14px;line-height:1.7;color:#4a4f58;">{_esc(cierre)}</p>
</td>
</tr>"""


_DISCLAIMER = "Este es un correo automático del Sistema de Reservas de Laboratorios."


def invitacion(*, nombre: str, link: str) -> str:
    contenido = f"""<tr>
<td class="fluid-padding" style="padding:32px 40px 6px 40px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
<tr>
<td width="56%" valign="top">
<p style="margin:0 0 6px 0;font-size:20px;color:{_NAVY};font-weight:500;">Hola, <strong style="font-weight:800;">{_esc(nombre)}</strong></p>
<h1 class="h1-mobile" style="margin:14px 0 0 0;font-size:29px;line-height:1.28;color:{_NAVY};font-weight:800;">Bienvenido/a.<br>Ya puede crear su cuenta</h1>
<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">
<tr><td style="width:64px;height:4px;background-color:{_TEAL};font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>
</table>
</td>
<td width="44%" valign="top" align="center">
<img src="cid:{CID_ICONO_BIENVENIDA}" alt="" style="display:block;width:150px;max-width:100%;height:auto;margin:0 auto;">
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td class="fluid-padding" style="padding:26px 40px 6px 40px;">
<p style="margin:0 0 16px 0;font-size:15px;line-height:1.75;color:#4a4f58;">Le invitaron a crear su cuenta en el sistema de reservas de los Laboratorios de Investigación del Parque i.</p>
<p style="margin:0 0 30px 0;font-size:15px;line-height:1.75;color:#4a4f58;">Con ella podrá reservar espacios y equipos, y hacer seguimiento a sus solicitudes.</p>
</td>
</tr>
<tr>
<td align="center" style="padding:0 40px 30px 40px;">
{_boton(texto="Crear mi cuenta", link=link)}
</td>
</tr>"""
    return _envoltorio(
        preheader="Bienvenido/a. Ya puede crear su cuenta en Reservas Parque i.",
        contenido_html=contenido,
        disclaimer=_DISCLAIMER + " Si no solicitó este acceso, puede ignorar este mensaje.",
    )


def recuperacion(*, nombre: str, link: str) -> str:
    contenido = _bloque_simple(
        saludo=nombre,
        titulo="Restablezca<br>su contraseña",
        cuerpo_html=f"""<p style="margin:0 0 30px 0;font-size:15px;line-height:1.75;color:#4a4f58;">Recibimos una solicitud para restablecer la contraseña de su cuenta. Si fue usted, elija una nueva con el botón:</p>
<div style="margin:0 0 10px 0;">{_boton(texto="Restablecer contraseña", link=link)}</div>""",
        cierre="Si no solicitó este cambio, puede ignorar este correo: su contraseña actual sigue siendo válida.",
    )
    return _envoltorio(
        preheader="Restablezca su contraseña en Reservas Parque i.",
        contenido_html=contenido,
        disclaimer=_DISCLAIMER,
    )


def contrasena_actualizada(*, nombre: str) -> str:
    contenido = _bloque_simple(
        saludo=nombre,
        titulo="Su contraseña fue<br>actualizada",
        cuerpo_html="""<p style="margin:0 0 20px 0;font-size:15px;line-height:1.75;color:#4a4f58;">La contraseña de su cuenta en Reservas Parque i se actualizó correctamente.</p>""",
        cierre="Si no hizo este cambio usted, contacte a soporte de inmediato.",
    )
    return _envoltorio(
        preheader="Su contraseña en Reservas Parque i fue actualizada.",
        contenido_html=contenido,
        disclaimer=_DISCLAIMER + " Si no reconoce este cambio, contacte a soporte de inmediato.",
    )


def reserva_estado(*, nombre: str, reserva_id: int, estado: str, titulo_tarjeta: str, detalle: str, motivo: str | None = None) -> str:
    """Aprobada, rechazada, cancelada o registrada: tarjeta de color + motivo si aplica."""
    motivo_html = ""
    if motivo:
        motivo_html = f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 20px;">
<tr>
<td style="padding:12px 18px;background-color:#f8fafc;border-radius:8px;border:1px solid #e9ecf2;">
<p style="margin:0;font-size:11.5px;font-weight:800;text-transform:uppercase;letter-spacing:0.06em;color:#9199a6;">Motivo</p>
<p style="margin:4px 0 0;font-size:14px;color:#4a4f58;">{_esc(motivo)}</p>
</td>
</tr>
</table>
"""
    verbos = {"pendiente": "registrada", "aprobada": "aprobada", "rechazada": "rechazada", "cancelada": "cancelada"}
    verbo = verbos.get(estado, estado)
    cuerpo = f"""<p style="margin:0 0 20px 0;font-size:15px;line-height:1.75;color:#4a4f58;">Su reserva #{reserva_id} fue <strong>{verbo}</strong>:</p>
{_tarjeta(estado=estado, titulo=titulo_tarjeta, lineas=_esc(detalle))}
{motivo_html}"""
    contenido = _bloque_simple(
        saludo=nombre,
        titulo=f"Su reserva fue<br>{verbo}",
        cuerpo_html=cuerpo,
        cierre="Ingrese al sistema de reservas para más detalles.",
    )
    return _envoltorio(
        preheader=f"Su reserva #{reserva_id} fue {verbo}.",
        contenido_html=contenido,
        disclaimer=_DISCLAIMER,
    )


def propuesta(*, nombre: str, reserva_id: int, detalle: str, motivo: str, contraparte_tecnico: bool = False) -> str:
    titulo = "Nueva<br>contrapropuesta" if contraparte_tecnico else "Su reserva tiene<br>una propuesta"
    intro = (
        f"{_esc(nombre)} contrapropuso un nuevo periodo para la reserva #{reserva_id}:"
        if contraparte_tecnico
        else f"El técnico propone un nuevo periodo para su reserva #{reserva_id}:"
    )
    cuerpo = f"""<p style="margin:0 0 20px 0;font-size:15px;line-height:1.75;color:#4a4f58;">{intro}</p>
{_tarjeta(estado="pendiente", titulo=detalle, lineas=_esc(motivo))}"""
    contenido = _bloque_simple(
        saludo=nombre,
        titulo=titulo,
        cuerpo_html=cuerpo,
        cierre="Ingrese al sistema para aceptar, rechazar o contraproponer.",
    )
    return _envoltorio(
        preheader=f"Propuesta de periodo para la reserva #{reserva_id}.",
        contenido_html=contenido,
        disclaimer=_DISCLAIMER,
    )


def recordatorio(*, nombre: str, reserva_id: int, detalle: str) -> str:
    tarjeta = _tarjeta(estado="aprobada", titulo=detalle, lineas="")
    cuerpo = f"""<p style="margin:0 0 20px 0;font-size:15px;line-height:1.75;color:#4a4f58;">Su reserva #{reserva_id} empieza pronto:</p>
{tarjeta}"""
    contenido = _bloque_simple(
        saludo=nombre,
        titulo="Su reserva<br>empieza pronto",
        cuerpo_html=cuerpo,
        cierre="Si ya no la necesita, cancélela desde la app para liberar el cupo.",
    )
    return _envoltorio(
        preheader=f"Su reserva #{reserva_id} empieza pronto.",
        contenido_html=contenido,
        disclaimer=_DISCLAIMER,
    )
