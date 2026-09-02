# -*- coding: utf-8 -*-
"""Pruebas unitarias de reglas de horario (services/horarios.py).

Reglas cubiertas:
- Bloques de hora completa: solo se admiten horas con minute == 0.
- El intervalo debe estar contenido en horario_atencion del laboratorio.
- Normalización de claves (str/int) en horas_atencion_dia.
"""

from datetime import time

from app.models import Laboratorio
from app.services.horarios import horas_atencion_dia, horario_cubre_reserva


def _laboratorio(horario):
    return Laboratorio(nombre="Sala", capacidad=5, horario_atencion=horario)


class TestHorarioCubreReserva:
    def test_rechaza_minutos_no_cero_en_inicio(self):
        laboratorio = _laboratorio({"1": [8, 9, 10]})
        assert horario_cubre_reserva(laboratorio, 1, time(8, 30), time(10, 0)) is False

    def test_rechaza_minutos_no_cero_en_fin(self):
        laboratorio = _laboratorio({"1": [8, 9, 10]})
        assert horario_cubre_reserva(laboratorio, 1, time(8, 0), time(10, 30)) is False

    def test_rechaza_inicio_mayor_o_igual_que_fin(self):
        laboratorio = _laboratorio({"1": [8, 9, 10]})
        assert horario_cubre_reserva(laboratorio, 1, time(10, 0), time(8, 0)) is False
        assert horario_cubre_reserva(laboratorio, 1, time(8, 0), time(8, 0)) is False

    def test_rechaza_hora_fuera_del_horario(self):
        laboratorio = _laboratorio({"1": [8, 9]})
        assert horario_cubre_reserva(laboratorio, 1, time(10, 0), time(11, 0)) is False

    def test_acepta_bloques_completos_dentro_del_horario(self):
        laboratorio = _laboratorio({"1": [8, 9, 10]})
        assert horario_cubre_reserva(laboratorio, 1, time(8, 0), time(10, 0)) is True

    def test_rechaza_dia_sin_horario(self):
        laboratorio = _laboratorio({"1": [8, 9]})
        assert horario_cubre_reserva(laboratorio, 6, time(8, 0), time(9, 0)) is False


class TestHorasAtencionDia:
    def test_claves_str_ordenadas(self):
        laboratorio = _laboratorio({"1": [9, 8]})
        assert horas_atencion_dia(laboratorio, 1) == [8, 9]

    def test_claves_int_ordenadas(self):
        laboratorio = _laboratorio({1: [9, 8]})
        assert horas_atencion_dia(laboratorio, 1) == [8, 9]

    def test_dia_sin_entrada_devuelve_vacio(self):
        laboratorio = _laboratorio({"1": [8]})
        assert horas_atencion_dia(laboratorio, 2) == []

    def test_horario_totalmente_vacio_devuelve_vacio(self):
        # Guard de compatibilidad: un horario vacío conserva el comportamiento
        # actual (lista vacía) y no se trata como error de configuración.
        laboratorio = _laboratorio({})
        assert horas_atencion_dia(laboratorio, 1) == []


class TestHorarioCubreReservaVacio:
    def test_horario_totalmente_vacio_no_cubre(self):
        laboratorio = _laboratorio({})
        assert horario_cubre_reserva(laboratorio, 1, time(8, 0), time(9, 0)) is False
