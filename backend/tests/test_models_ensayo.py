# -*- coding: utf-8 -*-
"""Pruebas del modelo Ensayo (Fase 12E, N:1 Zona).

Calco de `test_models_zona.py` (Fase 12C-1) con padre Zona.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.ensayo import Ensayo
from tests.conftest import crear_espacio, crear_usuario, crear_zona


def _crear_ensayo(db, *, zona, usuario, **kwargs):
    ensayo = Ensayo(
        nombre=kwargs.get("nombre", "Ensayo de pruebas"),
        zona_id=zona.id,
        estado=kwargs.get("estado", "activo"),
        created_by=usuario.id,
        updated_by=usuario.id,
    )
    db.add(ensayo)
    db.commit()
    db.refresh(ensayo)
    return ensayo


class TestEnsayoCamposObligatorios:
    def test_se_crea_con_campos_minimos_y_estado_activo_por_defecto(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_ens1", email="admin_ens1@example.com", rol="admin")
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        ensayo = _crear_ensayo(db, zona=zona, usuario=admin)
        assert ensayo.id is not None
        assert ensayo.estado == "activo"
        assert ensayo.zona_id == zona.id
        assert ensayo.created_by == admin.id
        assert ensayo.updated_by == admin.id

    def test_nombre_obligatorio(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_ens2", email="admin_ens2@example.com", rol="admin")
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        ensayo = Ensayo(zona_id=zona.id, created_by=admin.id, updated_by=admin.id)
        db.add(ensayo)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_zona_id_obligatorio(self, db):
        admin = crear_usuario(db, username="admin_ens3", email="admin_ens3@example.com", rol="admin")
        ensayo = Ensayo(nombre="Sin zona", created_by=admin.id, updated_by=admin.id)
        db.add(ensayo)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_created_by_obligatorio(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_ens4", email="admin_ens4@example.com", rol="admin")
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        ensayo = Ensayo(nombre="Sin creador", zona_id=zona.id, updated_by=admin.id)
        db.add(ensayo)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_updated_by_obligatorio(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_ens5", email="admin_ens5@example.com", rol="admin")
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        ensayo = Ensayo(nombre="Sin actualizador", zona_id=zona.id, created_by=admin.id)
        db.add(ensayo)
        with pytest.raises(IntegrityError):
            db.commit()


class TestEnsayoEstadoConstraint:
    def test_estado_invalido_rechazado_por_check_constraint(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_ens6", email="admin_ens6@example.com", rol="admin")
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        ensayo = Ensayo(
            nombre="Estado invalido",
            zona_id=zona.id,
            estado="bogus",
            created_by=admin.id,
            updated_by=admin.id,
        )
        db.add(ensayo)
        with pytest.raises(IntegrityError):
            db.commit()

    @pytest.mark.parametrize("estado", ["activo", "inactivo", "mantenimiento"])
    def test_estados_validos_aceptados(self, db, estado):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username=f"admin_ens_{estado}", email=f"admin_ens_{estado}@example.com", rol="admin")
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        ensayo = _crear_ensayo(db, zona=zona, usuario=admin, estado=estado)
        assert ensayo.estado == estado


class TestEnsayoRelacionZona:
    def test_ensayo_expone_su_zona_sin_modificar_modelo_zona(self, db):
        espacio = crear_espacio(db, nombre="Sala con ensayo zona")
        admin = crear_usuario(db, username="admin_ens_rel", email="admin_ens_rel@example.com", rol="admin")
        zona = crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona ensayo rel")
        ensayo = _crear_ensayo(db, zona=zona, usuario=admin)
        db.refresh(ensayo)
        assert ensayo.zona.nombre == "Zona ensayo rel"
        assert ensayo.zona.espacio_id == espacio.id
