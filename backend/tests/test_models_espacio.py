# -*- coding: utf-8 -*-
"""Pruebas del modelo Espacio (Fase 12C-1).

Alcance de esta subfase: la entidad Espacio aislada -- sin asociación con
Recurso, sin integración con Reserva, sin schema ni endpoint todavía. Solo
se prueba el modelo SQLAlchemy y su CheckConstraint de estado.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.espacio import Espacio
from tests.conftest import crear_laboratorio, crear_usuario


def _crear_espacio(db, *, laboratorio, usuario, **kwargs):
    espacio = Espacio(
        nombre=kwargs.get("nombre", "Espacio de pruebas"),
        laboratorio_id=laboratorio.id,
        descripcion=kwargs.get("descripcion"),
        capacidad=kwargs.get("capacidad"),
        estado=kwargs.get("estado", "activo"),
        created_by=usuario.id,
        updated_by=usuario.id,
    )
    db.add(espacio)
    db.commit()
    db.refresh(espacio)
    return espacio


class TestEspacioCamposObligatorios:
    def test_se_crea_con_campos_minimos_y_estado_activo_por_defecto(self, db):
        laboratorio = crear_laboratorio(db)
        usuario = crear_usuario(db, username="admin_espacio1", email="admin_espacio1@example.com", rol="admin")
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=usuario)
        assert espacio.id is not None
        assert espacio.estado == "activo"
        assert espacio.capacidad is None
        assert espacio.laboratorio_id == laboratorio.id
        assert espacio.created_by == usuario.id
        assert espacio.updated_by == usuario.id

    def test_nombre_obligatorio(self, db):
        laboratorio = crear_laboratorio(db)
        usuario = crear_usuario(db, username="admin_espacio2", email="admin_espacio2@example.com", rol="admin")
        espacio = Espacio(laboratorio_id=laboratorio.id, created_by=usuario.id, updated_by=usuario.id)
        db.add(espacio)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_espacio_id_obligatorio(self, db):
        usuario = crear_usuario(db, username="admin_espacio3", email="admin_espacio3@example.com", rol="admin")
        espacio = Espacio(nombre="Espacio sin laboratorio", created_by=usuario.id, updated_by=usuario.id)
        db.add(espacio)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_created_by_nullable_desde_2026_08_29(self, db):
        """Nullable a propósito desde el bug real de producción (ver
        backend/CLAUDE.md, "Nullable created_by/updated_by..."): un
        created_by huérfano (usuario degradado antes de la separación
        personal/usuarios) se limpia a NULL en la migración en vez de
        romperla -- ya no es NOT NULL como antes."""
        laboratorio = crear_laboratorio(db)
        usuario = crear_usuario(db, username="admin_espacio4", email="admin_espacio4@example.com", rol="admin")
        espacio = Espacio(nombre="Espacio sin creador", laboratorio_id=laboratorio.id, updated_by=usuario.id)
        db.add(espacio)
        db.commit()
        db.refresh(espacio)
        assert espacio.created_by is None

    def test_updated_by_nullable_desde_2026_08_29(self, db):
        laboratorio = crear_laboratorio(db)
        usuario = crear_usuario(db, username="admin_espacio5", email="admin_espacio5@example.com", rol="admin")
        espacio = Espacio(nombre="Espacio sin actualizador", laboratorio_id=laboratorio.id, created_by=usuario.id)
        db.add(espacio)
        db.commit()
        db.refresh(espacio)
        assert espacio.updated_by is None


class TestEspacioEstadoConstraint:
    def test_estado_invalido_es_rechazado_por_check_constraint(self, db):
        laboratorio = crear_laboratorio(db)
        usuario = crear_usuario(db, username="admin_espacio6", email="admin_espacio6@example.com", rol="admin")
        espacio = Espacio(
            nombre="Espacio estado invalido",
            laboratorio_id=laboratorio.id,
            estado="bogus",
            created_by=usuario.id,
            updated_by=usuario.id,
        )
        db.add(espacio)
        with pytest.raises(IntegrityError):
            db.commit()

    @pytest.mark.parametrize("estado", ["activo", "inactivo", "mantenimiento"])
    def test_estados_validos_son_aceptados(self, db, estado):
        laboratorio = crear_laboratorio(db)
        usuario = crear_usuario(
            db, username=f"admin_espacio_{estado}", email=f"admin_espacio_{estado}@example.com", rol="admin"
        )
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=usuario, estado=estado)
        assert espacio.estado == estado


class TestEspacioCapacidadOpcional:
    """capacidad es Integer nullable, sin CheckConstraint en BD -- mismo
    criterio que Laboratorio.capacidad y Recurso.capacidad (>0 se valida en el
    schema Pydantic, no aquí; el schema todavía no existe en esta subfase)."""

    def test_capacidad_nula_permitida(self, db):
        laboratorio = crear_laboratorio(db)
        usuario = crear_usuario(db, username="admin_espacio_cap1", email="admin_espacio_cap1@example.com", rol="admin")
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=usuario, capacidad=None)
        assert espacio.capacidad is None

    def test_capacidad_positiva_se_persiste(self, db):
        laboratorio = crear_laboratorio(db)
        usuario = crear_usuario(db, username="admin_espacio_cap2", email="admin_espacio_cap2@example.com", rol="admin")
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=usuario, capacidad=15)
        assert espacio.capacidad == 15

    def test_capacidad_no_positiva_no_es_rechazada_a_nivel_de_base_de_datos(self, db):
        """Documenta la decisión explícita de no inventar un CheckConstraint
        de capacidad en BD para Espacio, ya que Laboratorio/Recurso tampoco lo
        tienen (backend/app/models/laboratorio.py, backend/app/models/recurso.py)."""
        laboratorio = crear_laboratorio(db)
        usuario = crear_usuario(db, username="admin_espacio_cap3", email="admin_espacio_cap3@example.com", rol="admin")
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=usuario, capacidad=-1)
        assert espacio.capacidad == -1


class TestEspacioRelacionEspacio:
    def test_espacio_expone_su_espacio_sin_modificar_el_modelo_espacio(self, db):
        laboratorio = crear_laboratorio(db, nombre="Sala con espacio")
        usuario = crear_usuario(db, username="admin_espacio_rel", email="admin_espacio_rel@example.com", rol="admin")
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=usuario)
        db.refresh(espacio)
        assert espacio.laboratorio.nombre == "Sala con espacio"
