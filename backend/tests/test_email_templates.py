# -*- coding: utf-8 -*-
"""Pruebas de `app/services/email_templates.py`."""

from app.services.email_templates import (
    plantilla_invitacion,
    plantilla_reserva_actualizada,
    plantilla_reserva_estado,
    plantilla_reserva_pendiente,
)


class TestPlantillaInvitacion:
    def test_incluye_el_link_en_el_boton_y_como_fallback_de_texto(self):
        link = "https://ejemplo.supabase.co/auth/v1/verify?token=abc"
        html = plantilla_invitacion(link=link, nombre_saludo="ana")
        assert f'href="{link}"' in html
        assert f">{link}<" in html

    def test_es_html_valido_basico(self):
        html = plantilla_invitacion(link="https://ejemplo.com/link", nombre_saludo="ana")
        assert html.strip().startswith("<!DOCTYPE html>")
        assert "<html" in html and "</html>" in html
        assert "<body" in html and "</body>" in html

    def test_escapa_el_nombre_de_saludo(self):
        html = plantilla_invitacion(link="https://ejemplo.com/link", nombre_saludo="<script>alert(1)</script>")
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;" in html

    def test_saludo_vacio_no_deja_espacio_colgado(self):
        html = plantilla_invitacion(link="https://ejemplo.com/link", nombre_saludo="")
        assert "Hola," in html
        assert "Hola  ," not in html

    def test_menciona_itm_y_reservas_parque_i(self):
        html = plantilla_invitacion(link="https://ejemplo.com/link", nombre_saludo="ana")
        assert "Instituto Tecnologico Metropolitano" in html
        assert "Reservas Parque i" in html

    def test_incluye_fallback_de_color_solido_para_outlook(self):
        """Outlook de escritorio ignora `linear-gradient` -- el bloque con
        gradiente debe tener también un `background-color` sólido."""
        html = plantilla_invitacion(link="https://ejemplo.com/link", nombre_saludo="ana")
        assert "background-image:linear-gradient" in html
        assert "background-color:#1e3a8a" in html


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


class TestPlantillaReservaActualizada:
    def test_incluye_detalle_de_lo_agregado(self):
        html = plantilla_reserva_actualizada(
            nombre_saludo="ana", reserva_id=7, espacio="Sala A", fecha="2026-09-01", hora_inicio="08:00", hora_fin="10:00",
            detalle="recursos: Proyector, Micrófono",
        )
        assert "recursos: Proyector, Micrófono" in html
        assert "#7" in html
        # Color de "actualizada" (mismo hex que AppColors.marca / azul académico)
        assert "#1e3a8a" in html
