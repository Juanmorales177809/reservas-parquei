# -*- coding: utf-8 -*-
"""Pruebas del modelo Zona (Fase 12C-1).

Alcance de esta subfase: la entidad Zona aislada -- sin asociación con
Recurso, sin integración con Reserva, sin schema ni endpoint todavía. Solo
se prueba el modelo SQLAlchemy y su CheckConstraint de estado.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.zona import Zona
from tests.conftest import crear_espacio, crear_usuario


def _crear_zona(db, *, espacio, usuario, **kwargs):
    zona = Zona(
        nombre=kwargs.get("nombre", "Zona de pruebas"),
        espacio_id=espacio.id,
        descripcion=kwargs.get("descripcion"),
        capacidad=kwargs.get("capacidad"),
        estado=kwargs.get("estado", "activo"),
        created_by=usuario.id,
        updated_by=usuario.id,
    )
    db.add(zona)
    db.commit()
    db.refresh(zona)
    return zona


class TestZonaCamposObligatorios:
    def test_se_crea_con_campos_minimos_y_estado_activo_por_defecto(self, db):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username="admin_zona1", email="admin_zona1@test.com", rol="admin")
        zona = _crear_zona(db, espacio=espacio, usuario=usuario)
        assert zona.id is not None
        assert zona.estado == "activo"
        assert zona.capacidad is None
        assert zona.espacio_id == espacio.id
        assert zona.created_by == usuario.id
        assert zona.updated_by == usuario.id

    def test_nombre_obligatorio(self, db):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username="admin_zona2", email="admin_zona2@test.com", rol="admin")
        zona = Zona(espacio_id=espacio.id, created_by=usuario.id, updated_by=usuario.id)
        db.add(zona)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_espacio_id_obligatorio(self, db):
        usuario = crear_usuario(db, username="admin_zona3", email="admin_zona3@test.com", rol="admin")
        zona = Zona(nombre="Zona sin espacio", created_by=usuario.id, updated_by=usuario.id)
        db.add(zona)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_created_by_obligatorio(self, db):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username="admin_zona4", email="admin_zona4@test.com", rol="admin")
        zona = Zona(nombre="Zona sin creador", espacio_id=espacio.id, updated_by=usuario.id)
        db.add(zona)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_updated_by_obligatorio(self, db):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username="admin_zona5", email="admin_zona5@test.com", rol="admin")
        zona = Zona(nombre="Zona sin actualizador", espacio_id=espacio.id, created_by=usuario.id)
        db.add(zona)
        with pytest.raises(IntegrityError):
            db.commit()


class TestZonaEstadoConstraint:
    def test_estado_invalido_es_rechazado_por_check_constraint(self, db):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username="admin_zona6", email="admin_zona6@test.com", rol="admin")
        zona = Zona(
            nombre="Zona estado invalido",
            espacio_id=espacio.id,
            estado="bogus",
            created_by=usuario.id,
            updated_by=usuario.id,
        )
        db.add(zona)
        with pytest.raises(IntegrityError):
            db.commit()

    @pytest.mark.parametrize("estado", ["activo", "inactivo", "mantenimiento"])
    def test_estados_validos_son_aceptados(self, db, estado):
        espacio = crear_espacio(db)
        usuario = crear_usuario(
            db, username=f"admin_zona_{estado}", email=f"admin_zona_{estado}@test.com", rol="admin"
        )
        zona = _crear_zona(db, espacio=espacio, usuario=usuario, estado=estado)
        assert zona.estado == estado


class TestZonaCapacidadOpcional:
    """capacidad es Integer nullable, sin CheckConstraint en BD -- mismo
    criterio que Espacio.capacidad y Recurso.capacidad (>0 se valida en el
    schema Pydantic, no aquí; el schema todavía no existe en esta subfase)."""

    def test_capacidad_nula_permitida(self, db):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username="admin_zona_cap1", email="admin_zona_cap1@test.com", rol="admin")
        zona = _crear_zona(db, espacio=espacio, usuario=usuario, capacidad=None)
        assert zona.capacidad is None

    def test_capacidad_positiva_se_persiste(self, db):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username="admin_zona_cap2", email="admin_zona_cap2@test.com", rol="admin")
        zona = _crear_zona(db, espacio=espacio, usuario=usuario, capacidad=15)
        assert zona.capacidad == 15

    def test_capacidad_no_positiva_no_es_rechazada_a_nivel_de_base_de_datos(self, db):
        """Documenta la decisión explícita de no inventar un CheckConstraint
        de capacidad en BD para Zona, ya que Espacio/Recurso tampoco lo
        tienen (backend/app/models/espacio.py, backend/app/models/recurso.py)."""
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username="admin_zona_cap3", email="admin_zona_cap3@test.com", rol="admin")
        zona = _crear_zona(db, espacio=espacio, usuario=usuario, capacidad=-1)
        assert zona.capacidad == -1


class TestZonaRelacionEspacio:
    def test_zona_expone_su_espacio_sin_modificar_el_modelo_espacio(self, db):
        espacio = crear_espacio(db, nombre="Sala con zona")
        usuario = crear_usuario(db, username="admin_zona_rel", email="admin_zona_rel@test.com", rol="admin")
        zona = _crear_zona(db, espacio=espacio, usuario=usuario)
        db.refresh(zona)
        assert zona.espacio.nombre == "Sala con zona"
