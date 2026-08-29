# -*- coding: utf-8 -*-
"""Pruebas unitarias de `services/ics.py::construir_ics` (2026-08-29,
ronda 2)."""

from datetime import datetime

from app.services.ics import construir_ics


def test_construir_ics_incluye_los_campos_esperados():
    contenido = construir_ics(
        uid="reserva-123@reservas-parquei",
        resumen="Sala A",
        descripcion="Reserva confirmada",
        ubicacion="Sala A",
        inicio=datetime(2026, 9, 1, 8, 0),
        fin=datetime(2026, 9, 1, 10, 0),
    ).decode("utf-8")

    assert contenido.startswith("BEGIN:VCALENDAR\r\n")
    assert contenido.endswith("END:VCALENDAR\r\n")
    assert "BEGIN:VEVENT\r\n" in contenido
    assert "UID:reserva-123@reservas-parquei\r\n" in contenido
    assert "DTSTART:20260901T080000\r\n" in contenido
    assert "DTEND:20260901T100000\r\n" in contenido
    assert "SUMMARY:Sala A\r\n" in contenido
    assert "LOCATION:Sala A\r\n" in contenido


def test_construir_ics_escapa_caracteres_especiales():
    contenido = construir_ics(
        uid="x@y",
        resumen="Reunión, presentación; notas\ncon salto",
        descripcion="Sin caracteres raros",
        ubicacion="Sin caracteres raros",
        inicio=datetime(2026, 9, 1, 8, 0),
        fin=datetime(2026, 9, 1, 9, 0),
    ).decode("utf-8")

    assert "SUMMARY:Reunión\\, presentación\\; notas\\ncon salto\r\n" in contenido
