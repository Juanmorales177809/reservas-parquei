# -*- coding: utf-8 -*-
"""Pruebas del modelo EspacioRecurso (Fase 12C-3).

Asociacion tecnica N:N Espacio<->Recurso, con unicidad funcional impuesta en
BD: un recurso pertenece, como maximo, a una espacio (UniqueConstraint sobre
recurso_id solo, no sobre el par espacio_id+recurso_id -- ver
backend/app/models/README.md).
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.db import Base, engine
from app.models.espacio import Espacio
from app.models.espacio_recurso import EspacioRecurso
from tests.conftest import crear_laboratorio, crear_recurso, crear_usuario


def _crear_espacio(db, *, laboratorio, usuario, nombre="Espacio de pruebas"):
    espacio = Espacio(nombre=nombre, laboratorio_id=laboratorio.id, created_by=usuario.id, updated_by=usuario.id)
    db.add(espacio)
    db.commit()
    db.refresh(espacio)
    return espacio


class TestUnicidadFuncionalPorRecurso:
    def test_un_recurso_no_puede_asociarse_a_dos_espacios(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_zr1", email="admin_zr1@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        espacio_a = _crear_espacio(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio A")
        espacio_b = _crear_espacio(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio B")

        db.add(EspacioRecurso(espacio_id=espacio_a.id, recurso_id=recurso.id))
        db.commit()

        db.add(EspacioRecurso(espacio_id=espacio_b.id, recurso_id=recurso.id))
        with pytest.raises(IntegrityError):
            db.commit()

    def test_dos_recursos_distintos_pueden_asociarse_a_la_misma_espacio(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_zr2", email="admin_zr2@example.com", rol="admin")
        recurso_a = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso A")
        recurso_b = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso B")
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=admin)

        db.add(EspacioRecurso(espacio_id=espacio.id, recurso_id=recurso_a.id))
        db.add(EspacioRecurso(espacio_id=espacio.id, recurso_id=recurso_b.id))
        db.commit()

        asociados = db.query(EspacioRecurso).filter(EspacioRecurso.espacio_id == espacio.id).all()
        assert {a.recurso_id for a in asociados} == {recurso_a.id, recurso_b.id}


class TestCascadaAlEliminar:
    """FKs con ondelete='CASCADE' -- unico patron disponible sin modificar
    app/models/espacio.py ni app/models/recurso.py (fuera de alcance de
    12C-3). Ver Riesgos en backend/app/models/README.md."""

    def test_eliminar_espacio_elimina_sus_asociaciones(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_zr3", email="admin_zr3@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=admin)
        db.add(EspacioRecurso(espacio_id=espacio.id, recurso_id=recurso.id))
        db.commit()

        db.delete(espacio)
        db.commit()

        assert db.query(EspacioRecurso).filter(EspacioRecurso.recurso_id == recurso.id).first() is None

    def test_eliminar_recurso_elimina_su_asociacion(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_zr4", email="admin_zr4@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=admin)
        db.add(EspacioRecurso(espacio_id=espacio.id, recurso_id=recurso.id))
        db.commit()

        db.delete(recurso)
        db.commit()

        assert db.query(EspacioRecurso).filter(EspacioRecurso.espacio_id == espacio.id).first() is None


class TestCreateAllIdempotente:
    def test_create_all_no_falla_al_ejecutarse_dos_veces(self):
        Base.metadata.create_all(bind=engine)
        Base.metadata.create_all(bind=engine)
