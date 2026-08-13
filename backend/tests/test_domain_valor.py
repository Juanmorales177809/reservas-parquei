# -*- coding: utf-8 -*-
"""Pruebas unitarias de los value objects de la capa de dominio.

Cubre:
- Invariantes de FranjaHoraria (bloques de hora completa, inicio < fin).
- Solapamiento total, parcial, ninguno y contigüidad.
- Normalización de HorarioAtencion (claves str/int, orden, dedupe,
  días vacíos, horario vacío, rango 0..22).
"""

from datetime import time

import pytest

from app.domain.valor import FranjaHoraria, HorarioAtencion


class TestFranjaHoraria:
    def test_creacion_valida(self):
        franja = FranjaHoraria(time(8, 0), time(10, 0))
        assert franja.horas == range(8, 10)
        assert franja.duracion_horas == 2

    def test_inicio_igual_a_fin_da_error(self):
        with pytest.raises(ValueError):
            FranjaHoraria(time(8, 0), time(8, 0))

    def test_inicio_mayor_que_fin_da_error(self):
        with pytest.raises(ValueError):
            FranjaHoraria(time(10, 0), time(8, 0))

    @pytest.mark.parametrize(
        "inicio, fin",
        [
            (time(8, 30), time(10, 0)),
            (time(8, 0), time(10, 30)),
            (time(8, 0, 1), time(10, 0)),
            (time(8, 0), time(10, 0, 1)),
        ],
    )
    def test_rechaza_minutos_o_segundos_distintos_de_cero(self, inicio, fin):
        with pytest.raises(ValueError):
            FranjaHoraria(inicio, fin)

    def test_solapamiento_total(self):
        assert FranjaHoraria(time(8, 0), time(10, 0)).se_solapa_con(
            FranjaHoraria(time(8, 0), time(10, 0))
        )

    def test_solapamiento_parcial(self):
        assert FranjaHoraria(time(8, 0), time(10, 0)).se_solapa_con(
            FranjaHoraria(time(9, 0), time(11, 0))
        )

    def test_contiguidad_no_es_solapamiento(self):
        assert (
            FranjaHoraria(time(8, 0), time(10, 0)).se_solapa_con(
                FranjaHoraria(time(10, 0), time(11, 0))
            )
            is False
        )

    def test_sin_solapamiento(self):
        assert (
            FranjaHoraria(time(8, 0), time(9, 0)).se_solapa_con(
                FranjaHoraria(time(10, 0), time(11, 0))
            )
            is False
        )

    def test_es_contigua(self):
        assert FranjaHoraria(time(8, 0), time(10, 0)).es_contigua_a(
            FranjaHoraria(time(10, 0), time(11, 0))
        )

    def test_no_es_contigua(self):
        assert (
            FranjaHoraria(time(8, 0), time(10, 0)).es_contigua_a(
                FranjaHoraria(time(9, 0), time(11, 0))
            )
            is False
        )


class TestHorarioAtencionNormalizacion:
    def test_claves_str_normalizadas_a_int(self):
        horario = HorarioAtencion({"1": [9, 8]})
        assert horario.horas_del_dia(1) == (8, 9)

    def test_claves_int_conservadas(self):
        horario = HorarioAtencion({1: [9, 8]})
        assert horario.horas_del_dia(1) == (8, 9)

    def test_claves_mixtas_normalizadas(self):
        horario = HorarioAtencion({1: [8], "2": [9]})
        assert horario.dias == (1, 2)

    def test_claves_dia_semana_enum(self):
        from app.domain.enums import DiaSemana

        horario = HorarioAtencion({DiaSemana.LUNES: [8]})
        assert horario.horas_del_dia(0) == (8,)

    def test_ordena_y_deduplica_horas(self):
        horario = HorarioAtencion({"1": [9, 8, 8, 7]})
        assert horario.horas_del_dia(1) == (7, 8, 9)

    def test_elimina_dias_sin_horas(self):
        horario = HorarioAtencion({"1": [], "2": [9]})
        assert horario.dias == (2,)

    def test_dias_ordenados(self):
        horario = HorarioAtencion({"2": [8], "1": [9]})
        assert horario.dias == (1, 2)

    def test_horario_totalmente_vacio_da_error(self):
        with pytest.raises(ValueError):
            HorarioAtencion({"1": [], "2": []})

    def test_hora_mayor_a_22_da_error(self):
        with pytest.raises(ValueError):
            HorarioAtencion({"1": [23]})

    def test_hora_negativa_da_error(self):
        with pytest.raises(ValueError):
            HorarioAtencion({"1": [-1]})

    def test_hora_22_aceptada(self):
        horario = HorarioAtencion({"1": [22]})
        assert horario.horas_del_dia(1) == (22,)


class TestHorarioAtencionCobertura:
    def _horario(self):
        return HorarioAtencion({"1": [8, 9, 10]})

    def test_cubre_franja_valida(self):
        assert self._horario().cubre_franja(1, FranjaHoraria(time(8, 0), time(10, 0)))

    def test_no_cubre_hora_fuera_del_horario(self):
        horario = HorarioAtencion({"1": [8, 9]})
        assert horario.cubre_franja(1, FranjaHoraria(time(8, 0), time(11, 0))) is False

    def test_dia_sin_horario_no_cubre(self):
        assert (
            self._horario().cubre_franja(6, FranjaHoraria(time(8, 0), time(9, 0)))
            is False
        )
