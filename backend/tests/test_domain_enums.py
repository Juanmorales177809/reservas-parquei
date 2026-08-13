# -*- coding: utf-8 -*-
"""Pruebas unitarias de los enums y constantes de la capa de dominio.

Cubre:
- Valores JSON exactos de los 6 enums (compatibilidad de contrato).
- Alineación de DiaSemana con datetime.date.weekday().
- Transiciones válidas e inválidas, no-op y estados terminales.
- Conjunto de estados bloqueantes.
"""

from datetime import date

import pytest

from app.domain.enums import (
    DiaSemana,
    ESTADOS_RESERVA_BLOQUEANTES,
    EstadoEntidad,
    EstadoReserva,
    EstadoSlot,
    Rol,
    TipoNotificacion,
    TRANSICIONES_ESTADO_RESERVA,
)


class TestValoresJson:
    def test_rol_conserva_valores_actuales(self):
        assert {rol.value for rol in Rol} == {"usuario", "gestor", "admin"}

    def test_estado_entidad_conserva_valores_actuales(self):
        assert {e.value for e in EstadoEntidad} == {"activo", "inactivo", "mantenimiento"}

    def test_estado_reserva_conserva_valores_actuales(self):
        assert {e.value for e in EstadoReserva} == {
            "esperando",
            "aprobada",
            "rechazada",
            "cancelada",
        }

    def test_tipo_notificacion_conserva_valores_actuales(self):
        assert {t.value for t in TipoNotificacion} == {
            "Pendiente",
            "Aprobada",
            "Rechazada",
            "Cancelada",
        }

    def test_estado_slot_conserva_valores_actuales(self):
        assert {s.value for s in EstadoSlot} == {"libre", "ocupado", "mantenimiento"}

    def test_enums_son_strings(self):
        assert Rol.USUARIO == "usuario"
        assert EstadoReserva.ESPERANDO == "esperando"
        assert TipoNotificacion.PENDIENTE == "Pendiente"


class TestDiaSemana:
    def test_coincide_con_weekday(self):
        # 2026-08-17 es lunes y 2026-08-23 es domingo
        assert date(2026, 8, 17).weekday() == DiaSemana.LUNES.value == 0
        assert date(2026, 8, 23).weekday() == DiaSemana.DOMINGO.value == 6

    def test_usable_como_clave_entera(self):
        mapa = {DiaSemana.LUNES: "lunes"}
        assert mapa[0] == "lunes"
        assert DiaSemana.LUNES == 0


class TestTransiciones:
    @pytest.mark.parametrize(
        "actual, esperadas",
        [
            (
                EstadoReserva.ESPERANDO,
                {EstadoReserva.APROBADA, EstadoReserva.RECHAZADA, EstadoReserva.CANCELADA},
            ),
            (EstadoReserva.APROBADA, {EstadoReserva.CANCELADA}),
            (EstadoReserva.RECHAZADA, set()),
            (EstadoReserva.CANCELADA, set()),
        ],
    )
    def test_transiciones(self, actual, esperadas):
        assert actual.transiciones() == esperadas

    @pytest.mark.parametrize(
        "actual, nuevo",
        [
            (EstadoReserva.ESPERANDO, EstadoReserva.APROBADA),
            (EstadoReserva.ESPERANDO, EstadoReserva.RECHAZADA),
            (EstadoReserva.ESPERANDO, EstadoReserva.CANCELADA),
            (EstadoReserva.APROBADA, EstadoReserva.CANCELADA),
        ],
    )
    def test_transiciones_validas(self, actual, nuevo):
        assert actual.puede_transicionar_a(nuevo) is True

    @pytest.mark.parametrize(
        "actual, nuevo",
        [
            (EstadoReserva.RECHAZADA, EstadoReserva.APROBADA),
            (EstadoReserva.CANCELADA, EstadoReserva.APROBADA),
            (EstadoReserva.APROBADA, EstadoReserva.RECHAZADA),
        ],
    )
    def test_transiciones_invalidas(self, actual, nuevo):
        assert actual.puede_transicionar_a(nuevo) is False

    @pytest.mark.parametrize("estado", list(EstadoReserva))
    def test_mismo_estado_es_no_op(self, estado):
        assert estado.puede_transicionar_a(estado) is True

    @pytest.mark.parametrize(
        "estado, terminal",
        [
            (EstadoReserva.ESPERANDO, False),
            (EstadoReserva.APROBADA, False),
            (EstadoReserva.RECHAZADA, True),
            (EstadoReserva.CANCELADA, True),
        ],
    )
    def test_estados_terminales(self, estado, terminal):
        assert estado.es_terminal is terminal


class TestEstadosBloqueantes:
    def test_conjunto_bloqueante(self):
        assert ESTADOS_RESERVA_BLOQUEANTES == frozenset(
            {EstadoReserva.ESPERANDO, EstadoReserva.APROBADA}
        )

    def test_claves_del_mapa_de_transiciones(self):
        assert set(TRANSICIONES_ESTADO_RESERVA) == set(EstadoReserva)
