# -*- coding: utf-8 -*-
"""Pruebas unitarias de las validaciones de reserva (services/reservas.py).

Reglas cubiertas:
- Validación de horario: inicio < fin y contención en horario_atencion.
- Anticipación mínima por espacio usando la hora local (reloj inyectable
  vía monkeypatch sobre `app.services.reservas.ahora_local`).
- Máquina de transiciones de estado.
- Capacidad y estado activo del recurso y su espacio.
"""

from datetime import date, datetime, time

import pytest
from fastapi import HTTPException

from app.domain.enums import EstadoReserva
from app.models import Espacio, Recurso
from app.services import reservas as servicios


class _RelojFijo:
    def __init__(self, valor: datetime):
        self._valor = valor

    def ahora(self) -> datetime:
        return self._valor


def _espacio(horario=None, horas_antelacion=24, estado="activo"):
    return Espacio(
        nombre="Sala",
        capacidad=10,
        estado=estado,
        horas_antelacion=horas_antelacion,
        horario_atencion=horario or {str(d): list(range(7, 20)) for d in range(6)},
    )


def _recurso(estado="activo", espacio=None):
    return Recurso(
        nombre="Recurso",
        capacidad=10,
        estado=estado,
        espacio=espacio or _espacio(),
        espacio_id=1,
        tipo_recurso_id=1,
        created_by=1,
        update_by=1,
    )


class TestValidarHorario:
    def test_inicio_mayor_que_fin_da_400(self):
        with pytest.raises(HTTPException) as exc:
            servicios.validar_horario(_espacio(), date(2026, 8, 17), time(10, 0), time(8, 0))
        assert exc.value.status_code == 400

    def test_horario_no_habilitado_da_400(self):
        with pytest.raises(HTTPException) as exc:
            servicios.validar_horario(_espacio(), date(2026, 8, 17), time(20, 0), time(21, 0))
        assert exc.value.status_code == 400

    def test_horario_valido_no_levanta(self):
        servicios.validar_horario(_espacio(), date(2026, 8, 17), time(8, 0), time(10, 0))


class TestValidarAnticipacion:
    def test_dentro_de_antelacion_da_400(self):
        espacio = _espacio(horas_antelacion=24)
        reloj = _RelojFijo(datetime(2026, 8, 17, 10, 0))
        with pytest.raises(HTTPException) as exc:
            servicios.validar_anticipacion(espacio, date(2026, 8, 18), time(9, 0), reloj=reloj)
        assert exc.value.status_code == 400

    def test_fuera_de_antelacion_no_levanta(self):
        espacio = _espacio(horas_antelacion=24)
        reloj = _RelojFijo(datetime(2026, 8, 17, 10, 0))
        servicios.validar_anticipacion(espacio, date(2026, 8, 18), time(11, 0), reloj=reloj)


class TestValidarTransicion:
    @pytest.mark.parametrize(
        "actual, nuevo",
        [
            ("esperando", "aprobada"),
            ("esperando", "rechazada"),
            ("esperando", "cancelada"),
            ("aprobada", "cancelada"),
        ],
    )
    def test_transiciones_validas(self, actual, nuevo):
        servicios.validar_transicion_estado(actual, nuevo)

    @pytest.mark.parametrize(
        "actual, nuevo",
        [
            ("rechazada", "aprobada"),
            ("cancelada", "aprobada"),
            ("aprobada", "rechazada"),
        ],
    )
    def test_transiciones_invalidas_dan_409(self, actual, nuevo):
        with pytest.raises(HTTPException) as exc:
            servicios.validar_transicion_estado(actual, nuevo)
        assert exc.value.status_code == 409

    def test_mismo_estado_es_no_op(self):
        servicios.validar_transicion_estado("esperando", "esperando")

    def test_acepta_estados_del_dominio_y_conserva_mensaje(self):
        with pytest.raises(HTTPException) as exc:
            servicios.validar_transicion_estado(EstadoReserva.RECHAZADA, EstadoReserva.APROBADA)
        assert exc.value.status_code == 409
        assert "de rechazada a aprobada" in exc.value.detail


class TestValidarCapacidad:
    def test_supera_capacidad_da_400(self):
        with pytest.raises(HTTPException) as exc:
            servicios.validar_capacidad(11, 10)
        assert exc.value.status_code == 400

    def test_igual_a_capacidad_no_levanta(self):
        servicios.validar_capacidad(10, 10)


class TestValidarRecursoActivo:
    def test_recurso_inexistente_da_404(self):
        with pytest.raises(HTTPException) as exc:
            servicios.validar_recurso_activo(None)
        assert exc.value.status_code == 404

    def test_recurso_inactivo_da_400(self):
        with pytest.raises(HTTPException) as exc:
            servicios.validar_recurso_activo(_recurso(estado="inactivo"))
        assert exc.value.status_code == 400

    def test_espacio_inactivo_da_400(self):
        espacio = _espacio(estado="inactivo")
        with pytest.raises(HTTPException) as exc:
            servicios.validar_recurso_activo(_recurso(espacio=espacio))
        assert exc.value.status_code == 400

    def test_recurso_y_espacio_activos_no_levantan(self):
        servicios.validar_recurso_activo(_recurso())
