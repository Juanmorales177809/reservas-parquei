# -*- coding: utf-8 -*-
"""Pruebas unitarias de reglas de horario (services/horarios.py).

Reglas cubiertas:
- Bloques de hora completa: solo se admiten horas con minute == 0.
- El intervalo debe estar contenido en horario_atencion del espacio.
- Normalización de claves (str/int) en horas_atencion_dia.
"""

from datetime import time

from app.models import Espacio
from app.services.horarios import horas_atencion_dia, horario_cubre_reserva


def _espacio(horario):
    return Espacio(nombre="Sala", capacidad=5, horario_atencion=horario)


class TestHorarioCubreReserva:
    def test_rechaza_minutos_no_cero_en_inicio(self):
        espacio = _espacio({"1": [8, 9, 10]})
        assert horario_cubre_reserva(espacio, 1, time(8, 30), time(10, 0)) is False

    def test_rechaza_minutos_no_cero_en_fin(self):
        espacio = _espacio({"1": [8, 9, 10]})
        assert horario_cubre_reserva(espacio, 1, time(8, 0), time(10, 30)) is False

    def test_rechaza_inicio_mayor_o_igual_que_fin(self):
        espacio = _espacio({"1": [8, 9, 10]})
        assert horario_cubre_reserva(espacio, 1, time(10, 0), time(8, 0)) is False
        assert horario_cubre_reserva(espacio, 1, time(8, 0), time(8, 0)) is False

    def test_rechaza_hora_fuera_del_horario(self):
        espacio = _espacio({"1": [8, 9]})
        assert horario_cubre_reserva(espacio, 1, time(10, 0), time(11, 0)) is False

    def test_acepta_bloques_completos_dentro_del_horario(self):
        espacio = _espacio({"1": [8, 9, 10]})
        assert horario_cubre_reserva(espacio, 1, time(8, 0), time(10, 0)) is True

    def test_rechaza_dia_sin_horario(self):
        espacio = _espacio({"1": [8, 9]})
        assert horario_cubre_reserva(espacio, 6, time(8, 0), time(9, 0)) is False


class TestHorasAtencionDia:
    def test_claves_str_ordenadas(self):
        espacio = _espacio({"1": [9, 8]})
        assert horas_atencion_dia(espacio, 1) == [8, 9]

    def test_claves_int_ordenadas(self):
        espacio = _espacio({1: [9, 8]})
        assert horas_atencion_dia(espacio, 1) == [8, 9]

    def test_dia_sin_entrada_devuelve_vacio(self):
        espacio = _espacio({"1": [8]})
        assert horas_atencion_dia(espacio, 2) == []
