# -*- coding: utf-8 -*-
"""Pruebas del reloj local y su contrato con el protocolo Reloj del dominio.

Reglas cubiertas:
- RelojLocal implementa el protocolo Reloj (runtime_checkable).
- Devuelve datetime NAIVE en APP_TIMEZONE (contrato actual de ahora_local).
- ahora_local() se conserva como wrapper compatible.
"""

from datetime import datetime

from app.domain.protocols import Reloj
from app.services.reloj import RelojLocal, ahora_local


class TestRelojLocal:
    def test_implementa_protocolo_reloj(self):
        assert isinstance(RelojLocal(), Reloj)

    def test_devuelve_datetime_naive(self):
        valor = RelojLocal().ahora()
        assert isinstance(valor, datetime)
        assert valor.tzinfo is None

    def test_no_decrece_entre_llamadas(self):
        primera = RelojLocal().ahora()
        segunda = RelojLocal().ahora()
        assert segunda >= primera


class TestWrapperCompatibilidad:
    def test_ahora_local_conserva_contrato(self):
        valor = ahora_local()
        assert isinstance(valor, datetime)
        assert valor.tzinfo is None
