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
# Supabase Auth es obligatorio desde la migración (settings.validate() exige
# las tres) -- valores ficticios, ningún test le pega a la red real de
# Supabase: `cookies_para` firma tokens localmente con este mismo secreto, y
# `SupabaseAdminError`/`invitar_usuario` se mockean donde hace falta (ver
# test_api_usuarios.py) en vez de llamar a `httpx.post` de verdad.
os.environ["SUPABASE_URL"] = os.environ.get(
    "TEST_SUPABASE_URL", "https://proyecto-de-prueba.supabase.co"
)
os.environ["SUPABASE_JWT_SECRET"] = os.environ.get(
    "TEST_SUPABASE_JWT_SECRET", "clave-jwt-de-prueba-fase0-minimo-32-caracteres"
)
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = os.environ.get(
    "TEST_SUPABASE_SERVICE_ROLE_KEY", "clave-service-role-de-prueba"
)

import uuid  # noqa: E402
from datetime import date, timedelta  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from jose import jwt as jose_jwt  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.auth.auth import NOMBRE_COOKIE_ACCESO, create_access_token, hash_password  # noqa: E402
from app.config import settings  # noqa: E402
from app.db import Base, engine  # noqa: E402
from app.migrations import migrate_resource_reservations  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Espacio, Recurso, TipoRecurso, Usuario, UsuarioEspacio, Zona, ZonaRecurso  # noqa: E402

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


def crear_usuario(db, *, username, email, password="password123", rol="usuario", espacio_id=None, supabase_id=None):
    """`password` se acepta por compatibilidad con los ~600 sitios de la
    suite que ya lo pasan, pero es vestigial desde la migración a Supabase
    Auth: `hashed_password` no se lee para autenticar (ver
    app/crud/usuarios.py::create_usuario). Lo que SÍ autentica es
    `supabase_id` -- se genera uno al azar si no se pasa explícitamente,
    para que `cookies_para(usuario)` siempre tenga algo válido con qué
    firmar."""
    usuario = Usuario(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        rol=rol,
        supabase_id=supabase_id or uuid.uuid4(),
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
    capacidad=20,
):
    espacio = Espacio(
        nombre=nombre,
        ubicacion="Sede de pruebas",
        capacidad=capacidad,
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


def token_supabase_para(usuario) -> str:
    """JWT con la MISMA forma que emite Supabase (`sub`=UUID, `email`),
    firmado con `SUPABASE_JWT_SECRET` -- exactamente lo que
    `app/deps.py::_decode_token` verifica desde la migración a Supabase
    Auth. Nunca se le pega a la red real de Supabase para esto."""
    if usuario.supabase_id is None:
        raise ValueError(
            f"El usuario de prueba {usuario.username!r} no tiene supabase_id "
            "-- crear con crear_usuario(...), que le asigna uno por defecto."
        )
    return jose_jwt.encode(
        {"sub": str(usuario.supabase_id), "email": usuario.email, "aud": "authenticated"},
        settings.supabase_jwt_secret,
        algorithm=settings.algorithm,
    )


def cookies_para(usuario):
    """Header `Cookie` con el token de sesión.

    La sesión viaja únicamente en la cookie `access_token` (la leen los
    dependientes de `app/deps.py` de `request.cookies`); el header
    `Authorization` ya no se acepta. Desde la migración a Supabase Auth, el
    valor de la cookie es un JWT de Supabase (ver `token_supabase_para`),
    no uno propio.
    """
    return {"Cookie": f"{NOMBRE_COOKIE_ACCESO}={token_supabase_para(usuario)}"}


def bearer_para(usuario):
    """Header `Authorization: Bearer` — SOLO para pruebas negativas que
    confirman que el backend no lo acepta como mecanismo de sesión. No hace
    falta que el token sea válido bajo el esquema vigente: estas pruebas
    verifican que el header se ignora sea cual sea su contenido, así que se
    mantiene el JWT propio (SECRET_KEY) de siempre."""
    token = create_access_token(
        data={"sub": str(usuario.id), "rol": usuario.rol, "role": usuario.rol}
    )
    return {"Authorization": f"Bearer {token}"}


def payload_reserva(recurso_id, fecha, hora_inicio="08:00", hora_fin="10:00", asistentes=2):
    """Payload de reserva por recursos directos (Fase 12C-6).

    `recurso_id` desaparece del contrato: la reserva se expresa con
    `recurso_ids`/`zona_ids`. Este helper conserva su firma (un recurso)
    y lo traduce al nuevo payload.
    """
    return payload_reserva_objetivos(
        recurso_ids=[recurso_id],
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        asistentes=asistentes,
    )


def payload_reserva_objetivos(
    recurso_ids=None,
    zona_ids=None,
    fecha=None,
    hora_inicio="08:00",
    hora_fin="10:00",
    asistentes=2,
    tipo="__ausente__",
    ensayo_ids=None,
    acompanantes=None,
):
    payload = {
        "recurso_ids": recurso_ids or [],
        "zona_ids": zona_ids or [],
        "fecha": fecha.isoformat(),
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "asistentes": asistentes,
    }
    # Fase 12D: `tipo` se incluye solo cuando el llamador lo pide (ausencia
    # y `None` explícito son semánticas distintas para el PATCH).
    if tipo != "__ausente__":
        payload["tipo"] = tipo
    if ensayo_ids is not None:
        payload["ensayo_ids"] = ensayo_ids
    if acompanantes is not None:
        payload["acompanantes"] = acompanantes
    return payload


def crear_zona(
    db,
    *,
    espacio,
    usuario,
    nombre="Zona de pruebas",
    capacidad=None,
    estado="activo",
):
    zona = Zona(
        nombre=nombre,
        espacio_id=espacio.id,
        descripcion="",
        capacidad=capacidad,
        estado=estado,
        created_by=usuario.id,
        updated_by=usuario.id,
    )
    db.add(zona)
    db.commit()
    db.refresh(zona)
    return zona


def asociar_zona_recurso(db, zona, recurso):
    db.add(ZonaRecurso(zona_id=zona.id, recurso_id=recurso.id))
    db.commit()


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
