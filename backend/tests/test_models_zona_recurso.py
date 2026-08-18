# -*- coding: utf-8 -*-
"""Pruebas del modelo ZonaRecurso (Fase 12C-3).

Asociacion tecnica N:N Zona<->Recurso, con unicidad funcional impuesta en
BD: un recurso pertenece, como maximo, a una zona (UniqueConstraint sobre
recurso_id solo, no sobre el par zona_id+recurso_id -- ver
backend/app/models/README.md).
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.db import Base, engine
from app.models.zona import Zona
from app.models.zona_recurso import ZonaRecurso
from tests.conftest import crear_espacio, crear_recurso, crear_usuario


def _crear_zona(db, *, espacio, usuario, nombre="Zona de pruebas"):
    zona = Zona(nombre=nombre, espacio_id=espacio.id, created_by=usuario.id, updated_by=usuario.id)
    db.add(zona)
    db.commit()
    db.refresh(zona)
    return zona


class TestUnicidadFuncionalPorRecurso:
    def test_un_recurso_no_puede_asociarse_a_dos_zonas(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_zr1", email="admin_zr1@test.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        zona_a = _crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona A")
        zona_b = _crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona B")

        db.add(ZonaRecurso(zona_id=zona_a.id, recurso_id=recurso.id))
        db.commit()

        db.add(ZonaRecurso(zona_id=zona_b.id, recurso_id=recurso.id))
        with pytest.raises(IntegrityError):
            db.commit()

    def test_dos_recursos_distintos_pueden_asociarse_a_la_misma_zona(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_zr2", email="admin_zr2@test.com", rol="admin")
        recurso_a = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso A")
        recurso_b = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso B")
        zona = _crear_zona(db, espacio=espacio, usuario=admin)

        db.add(ZonaRecurso(zona_id=zona.id, recurso_id=recurso_a.id))
        db.add(ZonaRecurso(zona_id=zona.id, recurso_id=recurso_b.id))
        db.commit()

        asociados = db.query(ZonaRecurso).filter(ZonaRecurso.zona_id == zona.id).all()
        assert {a.recurso_id for a in asociados} == {recurso_a.id, recurso_b.id}


class TestCascadaAlEliminar:
    """FKs con ondelete='CASCADE' -- unico patron disponible sin modificar
    app/models/zona.py ni app/models/recurso.py (fuera de alcance de
    12C-3). Ver Riesgos en backend/app/models/README.md."""

    def test_eliminar_zona_elimina_sus_asociaciones(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_zr3", email="admin_zr3@test.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        zona = _crear_zona(db, espacio=espacio, usuario=admin)
        db.add(ZonaRecurso(zona_id=zona.id, recurso_id=recurso.id))
        db.commit()

        db.delete(zona)
        db.commit()

        assert db.query(ZonaRecurso).filter(ZonaRecurso.recurso_id == recurso.id).first() is None

    def test_eliminar_recurso_elimina_su_asociacion(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_zr4", email="admin_zr4@test.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        zona = _crear_zona(db, espacio=espacio, usuario=admin)
        db.add(ZonaRecurso(zona_id=zona.id, recurso_id=recurso.id))
        db.commit()

        db.delete(recurso)
        db.commit()

        assert db.query(ZonaRecurso).filter(ZonaRecurso.zona_id == zona.id).first() is None


class TestCreateAllIdempotente:
    def test_create_all_no_falla_al_ejecutarse_dos_veces(self):
        Base.metadata.create_all(bind=engine)
        Base.metadata.create_all(bind=engine)
