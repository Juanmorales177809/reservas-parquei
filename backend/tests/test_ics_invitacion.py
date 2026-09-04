# -*- coding: utf-8 -*-
"""Pruebas unitarias de `services/ics.py::construir_ics_invitacion`
(2026-09-03) -- invitación real de reunión (`METHOD:REQUEST`/`CANCEL`),
distinta de `construir_ics` (`METHOD:PUBLISH`, pasivo, ver `test_ics.py`)."""

from datetime import datetime

from app.services.ics import construir_ics_invitacion


def _base(**overrides):
    valores = dict(
        uid="reserva-1@reservas-parquei",
        secuencia=0,
        resumen="Reserva: Sala A",
        descripcion="Reserva en Sala A, 2026-09-10 08:00-10:00.",
        ubicacion="Sala A",
        inicio=datetime(2026, 9, 10, 8, 0),
        fin=datetime(2026, 9, 10, 10, 0),
        organizador_email="sgc-lia@itm.edu.co",
        organizador_nombre="Sistema de Reservas",
        asistentes=[("gestor@example.com", "Gestor Uno"), ("usuario@example.com", "Usuario Uno")],
    )
    valores.update(overrides)
    return valores


def test_invitacion_nueva_es_method_request_con_secuencia_cero():
    contenido = construir_ics_invitacion(**_base()).decode("utf-8")

    assert "METHOD:REQUEST\r\n" in contenido
    assert "STATUS:CONFIRMED\r\n" in contenido
    assert "SEQUENCE:0\r\n" in contenido
    assert "UID:reserva-1@reservas-parquei\r\n" in contenido


def test_incluye_organizador_y_todos_los_asistentes():
    contenido = construir_ics_invitacion(**_base()).decode("utf-8")

    assert "ORGANIZER;CN=Sistema de Reservas:mailto:sgc-lia@itm.edu.co\r\n" in contenido
    assert "ATTENDEE;CN=Gestor Uno;ROLE=REQ-PARTICIPANT;RSVP=TRUE:mailto:gestor@example.com\r\n" in contenido
    assert "ATTENDEE;CN=Usuario Uno;ROLE=REQ-PARTICIPANT;RSVP=TRUE:mailto:usuario@example.com\r\n" in contenido


def test_categoria_opcional_se_incluye_solo_si_se_pasa():
    con_categoria = construir_ics_invitacion(**_base(categoria="Sala A")).decode("utf-8")
    sin_categoria = construir_ics_invitacion(**_base()).decode("utf-8")

    assert "CATEGORIES:Sala A\r\n" in con_categoria
    assert "CATEGORIES:" not in sin_categoria


def test_cancelado_es_method_cancel_con_status_cancelled():
    contenido = construir_ics_invitacion(**_base(secuencia=2, cancelado=True)).decode("utf-8")

    assert "METHOD:CANCEL\r\n" in contenido
    assert "STATUS:CANCELLED\r\n" in contenido
    assert "SEQUENCE:2\r\n" in contenido
    # Mismo UID que la invitación original -- el cliente del destinatario
    # tiene que reconocer que es el mismo evento, no uno nuevo.
    assert "UID:reserva-1@reservas-parquei\r\n" in contenido


def test_secuencia_incrementada_se_refleja_en_el_contenido():
    contenido = construir_ics_invitacion(**_base(secuencia=3)).decode("utf-8")
    assert "SEQUENCE:3\r\n" in contenido
