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
from app.models import Espacio, EspacioRecurso, Laboratorio, Personal, Recurso, TipoRecurso, Usuario, UsuarioLaboratorio  # noqa: E402

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


def crear_usuario(db, *, username, email, password="password123", rol="usuario", laboratorio_id=None, supabase_id=None):
    """`password` se acepta por compatibilidad con los ~600 sitios de la
    suite que ya lo pasan, pero es vestigial desde la migración a Supabase
    Auth: `hashed_password` no se lee para autenticar. Lo que SÍ autentica
    es `supabase_id` -- se genera uno al azar si no se pasa explícitamente,
    para que `cookies_para(usuario)` siempre tenga algo válido con qué
    firmar.

    Desde la separación `personal`/`usuarios` (2026-08-28, ver
    `~/.claude/plans/dazzling-wobbling-zebra.md`): `rol="admin"` o
    `"gestor"` crea la fila en `Personal`, cualquier otro valor
    (`"usuario"`, el default) la crea en `Usuario` -- misma firma que
    antes, así que los ~330 sitios que ya llaman a este helper no
    necesitan tocarse, solo usan atributos (`.id`, `.username`, `.email`,
    `.supabase_id`, `.rol`) que ambas clases exponen igual."""
    if rol in ("admin", "gestor"):
        entidad = Personal(
            username=username,
            email=email,
            rol=rol,
            supabase_id=supabase_id or uuid.uuid4(),
        )
        db.add(entidad)
        db.flush()
        if laboratorio_id is not None:
            db.add(UsuarioLaboratorio(usuario_id=entidad.id, laboratorio_id=laboratorio_id))
    else:
        entidad = Usuario(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            rol=rol,
            supabase_id=supabase_id or uuid.uuid4(),
        )
        db.add(entidad)
        db.flush()
    db.commit()
    db.refresh(entidad)
    return entidad


def crear_personal(db, *, username, email, rol="gestor", laboratorio_id=None, supabase_id=None):
    """Alias explícito de `crear_usuario(..., rol="gestor"|"admin")` para
    tests nuevos que prefieran dejarlo claro en el nombre -- mismo
    comportamiento, no es obligatorio migrar los sitios existentes."""
    return crear_usuario(db, username=username, email=email, rol=rol, laboratorio_id=laboratorio_id, supabase_id=supabase_id)


def crear_laboratorio(
    db,
    *,
    nombre="Sala de pruebas",
    estado="activo",
    horas_antelacion=24,
    horario_atencion=None,
    correo=None,
    capacidad=20,
):
    laboratorio = Laboratorio(
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
        correo=correo,
    )
    db.add(laboratorio)
    db.commit()
    db.refresh(laboratorio)
    return laboratorio


_USERNAME_PERSONAL_AUTOCREADO = "_personal_autocreado_para_fk"


def _personal_para_fk(db, usuario):
    """`created_by`/`update_by`/`updated_by` de recursos/espacios/
    laboratorios ahora exigen un id de `Personal` (ver
    `~/.claude/plans/dazzling-wobbling-zebra.md`) -- muchos tests pasan
    cómodamente el mismo `usuario` (rol `usuario`) que usan como dueño de
    la reserva a `crear_recurso`/`crear_espacio`, algo que antes de la
    separación no importaba porque era la misma tabla. Si `usuario` ya es
    `Personal`, se usa tal cual; si no, se crea (o reusa, dentro del mismo
    test) un admin de pruebas dedicado, para no obligar a tocar los ~150
    sitios que ya llaman a estos helpers así."""
    if isinstance(usuario, Personal):
        return usuario
    existente = db.query(Personal).filter(Personal.username == _USERNAME_PERSONAL_AUTOCREADO).first()
    if existente is not None:
        return existente
    return crear_usuario(
        db,
        username=_USERNAME_PERSONAL_AUTOCREADO,
        email=f"{_USERNAME_PERSONAL_AUTOCREADO}@example.com",
        rol="admin",
    )


def crear_recurso(
    db,
    *,
    laboratorio,
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
    creador = _personal_para_fk(db, usuario)
    recurso = Recurso(
        nombre=nombre,
        laboratorio_id=laboratorio.id,
        tipo_recurso_id=tipo.id,
        descripcion="",
        capacidad=capacidad,
        estado=estado,
        created_by=creador.id,
        update_by=creador.id,
        es_prestacion_servicio=es_prestacion_servicio,
    )
    db.add(recurso)
    db.commit()
    db.refresh(recurso)
    return recurso


def token_supabase_para(usuario) -> str:
    """JWT con la MISMA forma que emite Supabase (`sub`=UUID, `email`),
    firmado con `SUPABASE_JWT_SECRET` -- exactamente lo que
    `app/deps.py::decode_token` verifica desde la migración a Supabase
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
    `recurso_ids`/`espacio_ids`. Este helper conserva su firma (un recurso)
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
    espacio_ids=None,
    fecha=None,
    hora_inicio="08:00",
    hora_fin="10:00",
    asistentes=2,
    tipo="__ausente__",
    acompanantes=None,
):
    payload = {
        "recurso_ids": recurso_ids or [],
        "espacio_ids": espacio_ids or [],
        "fecha": fecha.isoformat(),
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "asistentes": asistentes,
    }
    # Fase 12D: `tipo` se incluye solo cuando el llamador lo pide (ausencia
    # y `None` explícito son semánticas distintas para el PATCH).
    if tipo != "__ausente__":
        payload["tipo"] = tipo
    if acompanantes is not None:
        payload["acompanantes"] = acompanantes
    return payload


def crear_espacio(
    db,
    *,
    laboratorio,
    usuario,
    nombre="Espacio de pruebas",
    capacidad=None,
    estado="activo",
):
    creador = _personal_para_fk(db, usuario)
    espacio = Espacio(
        nombre=nombre,
        laboratorio_id=laboratorio.id,
        descripcion="",
        capacidad=capacidad,
        estado=estado,
        created_by=creador.id,
        updated_by=creador.id,
    )
    db.add(espacio)
    db.commit()
    db.refresh(espacio)
    return espacio


def asociar_espacio_recurso(db, espacio, recurso):
    db.add(EspacioRecurso(espacio_id=espacio.id, recurso_id=recurso.id))
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
