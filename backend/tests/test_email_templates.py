# -*- coding: utf-8 -*-
"""Pruebas de `app/services/email_templates.py`."""

from app.services.email_templates import (
    CID_ICONO_BIENVENIDA,
    CID_LOGO_ITM,
    imagenes_inline_para,
    plantilla_bienvenida_autoregistro,
    plantilla_invitacion,
    plantilla_recuperacion_password,
    plantilla_reserva_actualizada,
    plantilla_reserva_cancelada_por_usuario,
    plantilla_reserva_estado,
    plantilla_reserva_pendiente,
    plantilla_reserva_recibida,
)


class TestPlantillaInvitacion:
    def test_el_boton_apunta_al_link(self):
        link = "https://ejemplo.supabase.co/auth/v1/verify?token=abc"
        html = plantilla_invitacion(link=link, nombre_saludo="ana")
        assert f'href="{link}"' in html

    def test_es_html_valido_basico(self):
        html = plantilla_invitacion(link="https://ejemplo.com/link", nombre_saludo="ana")
        assert html.strip().startswith("<!DOCTYPE html>")
        assert "<html" in html and "</html>" in html
        assert "<body" in html and "</body>" in html

    def test_escapa_el_nombre_de_saludo(self):
        html = plantilla_invitacion(link="https://ejemplo.com/link", nombre_saludo="<script>alert(1)</script>")
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;" in html

    def test_saludo_vacio_no_deja_coma_colgada(self):
        html = plantilla_invitacion(link="https://ejemplo.com/link", nombre_saludo="")
        assert "Hola</p>" in html
        assert "Hola,</p>" not in html
        assert "Hola ," not in html

    def test_saludo_con_nombre_incluye_la_coma(self):
        html = plantilla_invitacion(link="https://ejemplo.com/link", nombre_saludo="ana")
        assert "Hola, <strong" in html

    def test_menciona_itm_y_reservas_parque_i(self):
        html = plantilla_invitacion(link="https://ejemplo.com/link", nombre_saludo="ana")
        assert "Institución Universitaria ITM" in html
        assert "Reservas Parque i" in html

    def test_incluye_bloque_mso_para_outlook_de_escritorio(self):
        """Outlook de escritorio (motor Word) necesita el bloque condicional
        `<!--[if mso]>` para la densidad de píxel -- sin él, el logo y las
        tablas pueden verse desproporcionados en ese cliente."""
        html = plantilla_invitacion(link="https://ejemplo.com/link", nombre_saludo="ana")
        assert "<!--[if mso]>" in html
        assert 'role="presentation"' in html


class TestPlantillaRecuperacionPassword:
    def test_el_boton_apunta_al_link(self):
        link = "https://ejemplo.supabase.co/auth/v1/verify?token=abc"
        html = plantilla_recuperacion_password(link=link, nombre_saludo="ana")
        assert f'href="{link}"' in html

    def test_es_html_valido_basico(self):
        html = plantilla_recuperacion_password(link="https://ejemplo.com/link")
        assert html.strip().startswith("<!DOCTYPE html>")

    def test_saludo_vacio_no_deja_coma_colgada(self):
        html = plantilla_recuperacion_password(link="https://ejemplo.com/link", nombre_saludo="")
        assert "Hola</p>" in html
        assert "Hola,</p>" not in html

    def test_escapa_el_nombre_de_saludo(self):
        html = plantilla_recuperacion_password(link="https://ejemplo.com/link", nombre_saludo="<script>x</script>")
        assert "<script>x</script>" not in html
        assert "&lt;script&gt;" in html


class TestPlantillaReservaPendiente:
    def test_incluye_gestor_espacio_y_horario(self):
        html = plantilla_reserva_pendiente(
            nombre_saludo="gestor_ana", espacio="Auditorio Principal", fecha="2026-09-01", hora_inicio="08:00", hora_fin="10:00"
        )
        assert "gestor_ana" in html
        assert "Auditorio Principal" in html
        assert "2026-09-01" in html
        assert "08:00" in html and "10:00" in html
        # Color de "pendiente" (mismo hex que TipoNotificacion.pendiente en notificaciones_sheet.dart)
        assert "#d97706" in html

    def test_es_html_valido_basico(self):
        html = plantilla_reserva_pendiente(nombre_saludo="a", espacio="b", fecha="c", hora_inicio="d", hora_fin="e")
        assert html.strip().startswith("<!DOCTYPE html>")


class TestPlantillaReservaRecibida:
    def test_incluye_espacio_y_horario(self):
        html = plantilla_reserva_recibida(
            nombre_saludo="ana", espacio="Sala A", fecha="2026-09-01", hora_inicio="08:00", hora_fin="10:00"
        )
        assert "ana" in html
        assert "Sala A" in html
        assert "2026-09-01" in html
        assert "08:00" in html and "10:00" in html
        # Mismo color de "pendiente" que plantilla_reserva_pendiente (aún esperando aprobación)
        assert "#d97706" in html

    def test_es_html_valido_basico(self):
        html = plantilla_reserva_recibida(nombre_saludo="a", espacio="b", fecha="c", hora_inicio="d", hora_fin="e")
        assert html.strip().startswith("<!DOCTYPE html>")


class TestPlantillaReservaEstado:
    def test_aprobada_usa_color_esmeralda_sin_bloque_de_motivo(self):
        html = plantilla_reserva_estado(
            nombre_saludo="ana", reserva_id=42, espacio="Sala A", fecha="2026-09-01", hora_inicio="08:00", hora_fin="10:00", estado="aprobada"
        )
        assert "#10b981" in html
        assert "aprobada" in html
        assert "#42" in html
        assert "Motivo" not in html

    def test_rechazada_incluye_el_motivo_escapado(self):
        html = plantilla_reserva_estado(
            nombre_saludo="ana", reserva_id=1, espacio="Sala A", fecha="2026-09-01", hora_inicio="08:00", hora_fin="10:00",
            estado="rechazada", motivo="No hay <disponibilidad>",
        )
        assert "#dc2626" in html
        assert "Motivo" in html
        assert "No hay &lt;disponibilidad&gt;" in html
        assert "No hay <disponibilidad>" not in html

    def test_rechazada_sin_motivo_no_agrega_bloque_de_motivo(self):
        html = plantilla_reserva_estado(
            nombre_saludo="ana", reserva_id=1, espacio="Sala A", fecha="2026-09-01", hora_inicio="08:00", hora_fin="10:00",
            estado="rechazada", motivo=None,
        )
        assert "Motivo" not in html

    def test_cancelada_usa_color_gris(self):
        html = plantilla_reserva_estado(
            nombre_saludo="ana", reserva_id=1, espacio="Sala A", fecha="2026-09-01", hora_inicio="08:00", hora_fin="10:00", estado="cancelada"
        )
        assert "#6b7280" in html


class TestPlantillaReservaCanceladaPorUsuario:
    def test_no_dice_tu_reserva_al_gestor(self):
        """A diferencia de plantilla_reserva_estado (segunda persona, para
        el propio dueño), esta plantilla va al gestor -- no debe hablarle
        como si la reserva fuera suya."""
        html = plantilla_reserva_cancelada_por_usuario(
            nombre_saludo="gestor_ana", reserva_id=5, espacio="Sala A", fecha="2026-09-01", hora_inicio="08:00", hora_fin="10:00"
        )
        assert "Tu reserva" not in html
        assert "gestor_ana" in html
        assert "#5" in html
        # Mismo color de "cancelada" que plantilla_reserva_estado
        assert "#6b7280" in html

    def test_es_html_valido_basico(self):
        html = plantilla_reserva_cancelada_por_usuario(
            nombre_saludo="a", reserva_id=1, espacio="b", fecha="c", hora_inicio="d", hora_fin="e"
        )
        assert html.strip().startswith("<!DOCTYPE html>")


class TestPlantillaReservaActualizada:
    def test_incluye_detalle_de_lo_agregado(self):
        html = plantilla_reserva_actualizada(
            nombre_saludo="ana", reserva_id=7, espacio="Sala A", fecha="2026-09-01", hora_inicio="08:00", hora_fin="10:00",
            detalle="recursos: Proyector, Micrófono",
        )
        assert "recursos: Proyector, Micrófono" in html
        assert "#7" in html
        # Color de "actualizada" (mismo navy que el resto de la identidad de Ingeniería)
        assert "#102d69" in html


class TestImagenesInline:
    """`imagenes_inline_para` (2026-09-04) -- reemplaza el `data:` embebido
    (Outlook de escritorio no lo renderiza) por adjuntos `cid:` reales."""

    def test_ninguna_plantilla_deja_data_uri_en_el_html(self):
        html = plantilla_invitacion(link="https://ejemplo.com/link", nombre_saludo="ana")
        assert "data:image" not in html
        assert f"cid:{CID_LOGO_ITM}" in html

    def test_plantilla_invitacion_devuelve_logo_y_el_icono_de_bienvenida(self):
        html = plantilla_invitacion(link="https://ejemplo.com/link", nombre_saludo="ana")
        imagenes = imagenes_inline_para(html)
        assert {i.cid for i in imagenes} == {CID_LOGO_ITM, CID_ICONO_BIENVENIDA}
        logo = next(i for i in imagenes if i.cid == CID_LOGO_ITM)
        assert logo.content_type == "image/png"
        assert logo.contenido.startswith(b"\x89PNG")

    def test_plantilla_bienvenida_autoregistro_devuelve_solo_el_logo(self):
        """A diferencia de `plantilla_invitacion`, esta no usa el ícono de
        bienvenida -- solo el logo del encabezado compartido."""
        html = plantilla_bienvenida_autoregistro(nombre_saludo="ana")
        imagenes = imagenes_inline_para(html)
        assert [i.cid for i in imagenes] == [CID_LOGO_ITM]

    def test_html_sin_ninguna_marca_cid_no_devuelve_imagenes(self):
        assert imagenes_inline_para("<p>Sin imagenes</p>") == []
