# -*- coding: utf-8 -*-
"""Pruebas del adaptador de auditoría del dominio.

Reglas cubiertas:
- AuditoriaSesion implementa el protocolo RegistroAuditoria (solo primitivas).
- Persiste filas ControlCambio en la sesión inyectada.
- registrar_cambio() se conserva como wrapper compatible.
"""

from app.domain.protocols import RegistroAuditoria
from app.models import ControlCambio
from app.services.auditoria import AuditoriaSesion, registrar_cambio
from tests.conftest import crear_usuario


def test_auditoria_sesion_implementa_protocolo(db):
    assert isinstance(AuditoriaSesion(db), RegistroAuditoria)


def test_auditoria_sesion_persiste_con_primitivas(db):
    usuario = crear_usuario(db, username="aud_dominio", email="aud_dominio@example.com")
    AuditoriaSesion(db).registrar(
        usuario_id=usuario.id,
        accion="crear",
        entidad="reserva",
        entidad_id=10,
        descripcion="Prueba de auditoría",
    )
    db.commit()
    cambio = db.query(ControlCambio).filter(ControlCambio.descripcion == "Prueba de auditoría").one()
    assert cambio.accion == "crear"
    assert cambio.entidad == "reserva"
    assert cambio.entidad_id == 10
    assert cambio.usuario_id == usuario.id


def test_registrar_cambio_wrapper_conserva_comportamiento(db):
    usuario = crear_usuario(db, username="auditor", email="auditor@example.com")
    registrar_cambio(db, usuario, "crear", "espacio", 1, "Creó el espacio X")
    db.commit()
    cambio = db.query(ControlCambio).one()
    assert cambio.usuario_id == usuario.id
    assert cambio.descripcion == "Creó el espacio X"
