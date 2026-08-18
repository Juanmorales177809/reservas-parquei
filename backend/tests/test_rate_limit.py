# -*- coding: utf-8 -*-
"""Pruebas unitarias del limitador de intentos de login (services/rate_limit.py).

Reloj inyectable en vez de sleep real, mismo patrón que _RelojFijo de
test_reservas_validaciones.py, pero mutable para simular el paso del tiempo.
"""

from datetime import datetime, timedelta

from app.services.rate_limit import LimitadorIntentosLogin


class _RelojControlable:
    def __init__(self, valor: datetime):
        self.valor = valor

    def ahora(self) -> datetime:
        return self.valor

    def avanzar(self, delta: timedelta) -> None:
        self.valor += delta


def _limitador(limite=5, ventana=timedelta(minutes=15), max_claves=10_000):
    reloj = _RelojControlable(datetime(2026, 8, 17, 10, 0))
    limitador = LimitadorIntentosLogin(reloj=reloj, limite=limite, ventana=ventana, max_claves=max_claves)
    return limitador, reloj


class TestLimiteBasico:
    def test_no_bloqueado_sin_intentos_previos(self):
        limitador, _ = _limitador()
        assert limitador.bloqueado("1.1.1.1", "ana") is False

    def test_no_bloqueado_por_debajo_del_limite(self):
        limitador, _ = _limitador(limite=5)
        for _ in range(4):
            limitador.registrar_fallo("1.1.1.1", "ana")
        assert limitador.bloqueado("1.1.1.1", "ana") is False

    def test_bloqueado_al_alcanzar_el_limite(self):
        limitador, _ = _limitador(limite=5)
        for _ in range(5):
            limitador.registrar_fallo("1.1.1.1", "ana")
        assert limitador.bloqueado("1.1.1.1", "ana") is True


class TestReinicioTrasExito:
    def test_reiniciar_limpia_el_contador_de_esa_clave(self):
        limitador, _ = _limitador(limite=5)
        for _ in range(5):
            limitador.registrar_fallo("1.1.1.1", "ana")
        assert limitador.bloqueado("1.1.1.1", "ana") is True

        limitador.reiniciar("1.1.1.1", "ana")

        assert limitador.bloqueado("1.1.1.1", "ana") is False

    def test_reiniciar_una_clave_no_afecta_a_otra(self):
        limitador, _ = _limitador(limite=5)
        for _ in range(5):
            limitador.registrar_fallo("1.1.1.1", "ana")
            limitador.registrar_fallo("1.1.1.1", "beto")

        limitador.reiniciar("1.1.1.1", "ana")

        assert limitador.bloqueado("1.1.1.1", "ana") is False
        assert limitador.bloqueado("1.1.1.1", "beto") is True


class TestClavesSeparadas:
    def test_ips_distintas_no_comparten_contador(self):
        limitador, _ = _limitador(limite=5)
        for _ in range(5):
            limitador.registrar_fallo("1.1.1.1", "ana")

        assert limitador.bloqueado("1.1.1.1", "ana") is True
        assert limitador.bloqueado("2.2.2.2", "ana") is False

    def test_usuarios_distintos_misma_ip_no_comparten_contador(self):
        limitador, _ = _limitador(limite=5)
        for _ in range(5):
            limitador.registrar_fallo("1.1.1.1", "ana")

        assert limitador.bloqueado("1.1.1.1", "ana") is True
        assert limitador.bloqueado("1.1.1.1", "beto") is False

    def test_clave_no_normaliza_mayusculas_igual_que_el_login_real(self):
        # get_usuario_by_username hace comparación exacta case-sensitive;
        # la clave del limitador debe respetar la misma semántica.
        limitador, _ = _limitador(limite=5)
        for _ in range(5):
            limitador.registrar_fallo("1.1.1.1", "Ana")

        assert limitador.bloqueado("1.1.1.1", "Ana") is True
        assert limitador.bloqueado("1.1.1.1", "ana") is False


class TestVentanaDeslizante:
    def test_ventana_expirada_permite_nuevos_intentos(self):
        limitador, reloj = _limitador(limite=5, ventana=timedelta(minutes=15))
        for _ in range(5):
            limitador.registrar_fallo("1.1.1.1", "ana")
        assert limitador.bloqueado("1.1.1.1", "ana") is True

        reloj.avanzar(timedelta(minutes=15, seconds=1))

        assert limitador.bloqueado("1.1.1.1", "ana") is False

    def test_intentos_antiguos_se_purgan_y_no_cuentan(self):
        limitador, reloj = _limitador(limite=5, ventana=timedelta(minutes=15))
        for _ in range(4):
            limitador.registrar_fallo("1.1.1.1", "ana")

        reloj.avanzar(timedelta(minutes=16))  # los 4 previos expiran

        limitador.registrar_fallo("1.1.1.1", "ana")  # 1 nuevo, vigente
        assert limitador.bloqueado("1.1.1.1", "ana") is False


class TestCotaDeMemoria:
    def test_no_crece_sin_limite_expulsa_la_clave_mas_antigua(self):
        limitador, _ = _limitador(limite=5, max_claves=3)
        limitador.registrar_fallo("1.1.1.1", "u1")
        limitador.registrar_fallo("1.1.1.1", "u2")
        limitador.registrar_fallo("1.1.1.1", "u3")
        assert len(limitador._intentos) == 3

        limitador.registrar_fallo("1.1.1.1", "u4")

        assert len(limitador._intentos) == 3
        assert "1.1.1.1:u1" not in limitador._intentos
        assert "1.1.1.1:u4" in limitador._intentos
