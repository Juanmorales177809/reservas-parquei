# -*- coding: utf-8 -*-
"""Pruebas del contrato estructural de los Protocols de dominio.

Cubre:
- `Reloj` y `RegistroAuditoria` reconocen implementaciones conformes
  mediante isinstance (runtime_checkable).
- Implementaciones sin los métodos requeridos no satisfacen el protocolo.
"""

from datetime import datetime

from app.domain.protocols import RegistroAuditoria, Reloj


class _RelojConforme:
    def ahora(self) -> datetime:
        return datetime(2026, 8, 13, 10, 0)


class _RelojInconforme:
    def otra_cosa(self) -> None:
        return None


class _AuditoriaConforme:
    def __init__(self):
        self.eventos = []

    def registrar(self, *, usuario_id, accion, entidad, entidad_id, descripcion) -> None:
        self.eventos.append((usuario_id, accion, entidad, entidad_id, descripcion))


class _AuditoriaInconforme:
    def registrar_otra_cosa(self) -> None:
        return None


class TestReloj:
    def test_implementacion_conforme(self):
        assert isinstance(_RelojConforme(), Reloj)

    def test_implementacion_inconforme(self):
        assert not isinstance(_RelojInconforme(), Reloj)

    def test_contrato_naive(self):
        reloj = _RelojConforme()
        assert reloj.ahora().tzinfo is None


class TestRegistroAuditoria:
    def test_implementacion_conforme(self):
        assert isinstance(_AuditoriaConforme(), RegistroAuditoria)

    def test_implementacion_inconforme(self):
        assert not isinstance(_AuditoriaInconforme(), RegistroAuditoria)

    def test_registra_evento(self):
        auditoria = _AuditoriaConforme()
        auditoria.registrar(
            usuario_id=1,
            accion="crear",
            entidad="reserva",
            entidad_id=10,
            descripcion="Creó una reserva",
        )
        assert auditoria.eventos == [(1, "crear", "reserva", 10, "Creó una reserva")]
