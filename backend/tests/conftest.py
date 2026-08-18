# -*- coding: utf-8 -*-
"""Configuración común de la suite de pruebas.

REGLAS CRÍTICAS DE ESTE MÓDULO
-------------------------------
1. El entorno de pruebas (DATABASE_URL y SECRET_KEY) se fija ANTES de
   importar cualquier módulo de la aplicación: `app.config.settings` y
   `app.db.engine` se construyen en el momento del import.
2. Se usa exclusivamente la base `reservas_test` en `localhost:5433`
   (docker-compose.test.yml). Nunca SQLite ni la base de desarrollo.
3. El esquema se crea con `Base.metadata.create_all` y luego se aplican
   las migraciones idempotentes de `app/migrations.py`, que son las que
   instalan la extensión btree_gist y la exclusión
   `reservas_sin_solapamiento`.
4. `TestClient` se usa SIN context manager para no ejecutar los eventos
   de startup (evita sembrar espacios iniciales y el admin inicial).
"""

import os

os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/reservas_test",
)
os.environ["SECRET_KEY"] = os.environ.get(
    "TEST_SECRET_KEY",
    "clave-de-prueba-fase0-minimo-32-caracteres",
)

from datetime import date, timedelta  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.auth.auth import create_access_token, hash_password  # noqa: E402
from app.db import Base, engine  # noqa: E402
from app.migrations import migrate_resource_reservations  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Espacio, Recurso, TipoRecurso, Usuario, UsuarioEspacio  # noqa: E402

TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def truncar_tablas(session) -> None:
    """Vacía todas las tablas entre pruebas (aislamiento sin recrear esquema)."""
    tablas = ", ".join(f'"{tabla.name}"' for tabla in reversed(Base.metadata.sorted_tables))
    session.execute(text(f"TRUNCATE TABLE {tablas} RESTART IDENTITY CASCADE"))
    session.commit()


@pytest.fixture(scope="session", autouse=True)
def preparar_esquema():
    """Crea el esquema y aplica migraciones idempotentes una vez por sesión."""
    Base.metadata.create_all(bind=engine)
    migrate_resource_reservations()
    yield


@pytest.fixture()
def db():
    session = TestingSession()
    truncar_tablas(session)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    """Cliente HTTP síncrono contra la app, sin eventos de startup."""
    return TestClient(app)


# ---------------------------------------------------------------------------
# Helpers reutilizables por los módulos de prueba (importables como
# `from tests.conftest import ...`).
# ---------------------------------------------------------------------------


def crear_usuario(db, *, username, email, password="password123", rol="usuario", espacio_id=None):
    usuario = Usuario(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        rol=rol,
    )
    db.add(usuario)
    db.flush()
    if espacio_id is not None:
        db.add(UsuarioEspacio(usuario_id=usuario.id, espacio_id=espacio_id))
    db.commit()
    db.refresh(usuario)
    return usuario


def crear_espacio(
    db,
    *,
    nombre="Sala de pruebas",
    estado="activo",
    horas_antelacion=24,
    horario_atencion=None,
    modalidad_reserva="equipos",
    correo=None,
):
    espacio = Espacio(
        nombre=nombre,
        ubicacion="Sede de pruebas",
        capacidad=20,
        estado=estado,
        horas_antelacion=horas_antelacion,
        horario_atencion=(
            horario_atencion
            if horario_atencion is not None
            else {str(dia): list(range(7, 20)) for dia in range(6)}
        ),
        modalidad_reserva=modalidad_reserva,
        correo=correo,
    )
    db.add(espacio)
    db.commit()
    db.refresh(espacio)
    return espacio


def crear_recurso(
    db,
    *,
    espacio,
    usuario,
    nombre="Recurso de pruebas",
    capacidad=10,
    estado="activo",
    es_prestacion_servicio=False,
):
    tipo = db.query(TipoRecurso).first()
    if tipo is None:
        tipo = TipoRecurso(nombre="General", descripcion="", activo="activo")
        db.add(tipo)
        db.commit()
        db.refresh(tipo)
    recurso = Recurso(
        nombre=nombre,
        espacio_id=espacio.id,
        tipo_recurso_id=tipo.id,
        descripcion="",
        capacidad=capacidad,
        estado=estado,
        created_by=usuario.id,
        update_by=usuario.id,
        es_prestacion_servicio=es_prestacion_servicio,
    )
    db.add(recurso)
    db.commit()
    db.refresh(recurso)
    return recurso


def headers_para(usuario):
    token = create_access_token(
        data={"sub": str(usuario.id), "rol": usuario.rol, "role": usuario.rol}
    )
    return {"Authorization": f"Bearer {token}"}


def payload_reserva(recurso_id, fecha, hora_inicio="08:00", hora_fin="10:00", asistentes=2):
    return {
        "recurso_id": recurso_id,
        "fecha": fecha.isoformat(),
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "asistentes": asistentes,
    }


def fecha_habilitada(dias=8):
    """Fecha futura que supera la anticipación por defecto (24 h) y cae en
    un día con horario de atención (evita el domingo)."""
    fecha = date.today() + timedelta(days=dias)
    while fecha.weekday() == 6:
        fecha += timedelta(days=1)
    return fecha


def proximo_domingo():
    """Primer domingo futuro (día sin horario de atención por defecto)."""
    fecha = date.today() + timedelta(days=1)
    while fecha.weekday() != 6:
        fecha += timedelta(days=1)
    return fecha
