"""Infraestructura común de las pruebas formales de auth (AUTH-T1/AUTH-T2).

Cómo se ejecutan (la base de desarrollo nunca se toca, testing.md §"El entorno"):

    docker run --rm --network reservas_database_network \
      -v "D:/Repos/reservas new/backend:/code" -w /code \
      -e DATABASE_URL="postgresql+psycopg://postgres:postgres@db:5432/reservas_test" \
      -e JWT_SECRET="secreto-solo-para-pruebas" \
      python:3.12-slim bash -c "pip install -q -r requirements.txt -r requirements-test.txt && python -m pytest tests/ -q"

`reservas_test` se construye con la misma cadena que la base real, **en
este orden exacto** (verificado reconstruyendo la base desde cero: 011 debe
ir antes de 010 y de 004-008, porque esos tres insertan su propia fila en
`public.schema_migrations`, que 011 es quien crea):

    reconstruccion/000_base_compartida.sql
    reconstruccion/001_shared_postgres.sql
    reconstruccion/001b_transicion_cuenta.sql
    002_reservas_objetivo.sql
    reconstruccion/003_limpieza_heredada.sql
    011_gobierno.sql
    010_auth_objetivo.sql
    seeds/catalogos_reservas.sql
    seeds/permisos.sql
    004_recursos.sql
    005_investigacion.sql
    006_administration.sql
    007_notificaciones.sql
    003_reservas_referencias_externas.sql
    009_concurrencia.sql
    seeds/tipos_evento.sql
    seeds/tipos_evento_auth.sql
    008_identidades.sql
    012_importacion_resultados_datos.sql

Sobre PostgreSQL 13. No se usa `create_all` (regla 1 de plan.md): el
esquema lo gobiernan las migraciones.

Aislamiento: cada prueba usa correos/nombres con una etiqueta única y al
terminar se borran sus filas en orden seguro para FK. `rate_limit` se vacía
antes de cada prueba.
"""

from __future__ import annotations

import os
import re
import uuid
from datetime import datetime, timezone

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@db:5432/reservas_test",
)
os.environ.setdefault("JWT_SECRET", "secreto-solo-para-pruebas-auth")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core import rate_limit  # noqa: E402
from app.core.security import hash_contrasena  # noqa: E402
from app.db.session import SessionLocal, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402


def _anular_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _anular_db


@pytest.fixture(autouse=True)
def _limpiar_rate_limit():
    rate_limit.limpiar_para_pruebas()
    yield


@pytest.fixture
def tag() -> str:
    """Etiqueta única por prueba para aislar sus filas."""
    return uuid.uuid4().hex[:10]


@pytest.fixture
def db():
    sesion = SessionLocal()
    try:
        yield sesion
    finally:
        sesion.close()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _limpiar_filas(tag):
    yield
    patron = f"%{tag}%"
    with engine.begin() as conexion:
        # API-18: los eventos generan in-app y envíos con FK a cuentas.
        # Se retiran primero para que el borrado de cuentas no falle.
        conexion.execute(
            text(
                "DELETE FROM notificaciones.envios_correo WHERE notificacion_id IN "
                "(SELECT n.id FROM notificaciones.notificaciones n JOIN auth.cuentas c "
                "ON c.id_cuenta = n.id_cuenta WHERE c.correo LIKE :pat)"
            ),
            {"pat": patron},
        )
        conexion.execute(
            text(
                "DELETE FROM notificaciones.envios_correo WHERE destinatario_correo LIKE :pat"
            ),
            {"pat": patron},
        )
        conexion.execute(
            text(
                "DELETE FROM notificaciones.notificaciones WHERE id_cuenta IN "
                "(SELECT id_cuenta FROM auth.cuentas WHERE correo LIKE :pat)"
            ),
            {"pat": patron},
        )
        conexion.execute(
            text(
                "DELETE FROM notificaciones.preferencias WHERE id_cuenta IN "
                "(SELECT id_cuenta FROM auth.cuentas WHERE correo LIKE :pat)"
            ),
            {"pat": patron},
        )
        conexion.execute(
            text(
                "DELETE FROM notificaciones.eventos WHERE id NOT IN "
                "(SELECT evento_id FROM notificaciones.notificaciones) "
                "AND id NOT IN (SELECT evento_id FROM notificaciones.envios_correo)"
            ),
        )
        conexion.execute(
            text(
                "DELETE FROM administration.auditoria WHERE actor_cuenta_id IN "
                "(SELECT id_cuenta FROM auth.cuentas WHERE correo LIKE :pat)"
            ),
            {"pat": patron},
        )
        conexion.execute(
            text(
                "DELETE FROM auth.sesiones WHERE id_cuenta IN "
                "(SELECT id_cuenta FROM auth.cuentas WHERE correo LIKE :pat)"
            ),
            {"pat": patron},
        )
        conexion.execute(
            text(
                "DELETE FROM auth.tokens_recuperacion WHERE id_cuenta IN "
                "(SELECT id_cuenta FROM auth.cuentas WHERE correo LIKE :pat)"
            ),
            {"pat": patron},
        )
        conexion.execute(
            text("DELETE FROM auth.invitaciones WHERE correo LIKE :pat"),
            {"pat": patron},
        )
        conexion.execute(
            text(
                "DELETE FROM auth.cuenta_permisos WHERE id_cuenta IN "
                "(SELECT id_cuenta FROM auth.cuentas WHERE correo LIKE :pat)"
            ),
            {"pat": patron},
        )
        conexion.execute(
            text("DELETE FROM auth.cuentas WHERE correo LIKE :pat"),
            {"pat": patron},
        )
        conexion.execute(
            text("DELETE FROM usuarios.usuarios WHERE correo LIKE :pat"),
            {"pat": patron},
        )
        conexion.execute(
            text("DELETE FROM personal.personal WHERE correo LIKE :pat"),
            {"pat": patron},
        )
        conexion.execute(
            text("DELETE FROM cargos.cargo WHERE nombre_cargo LIKE :pat"),
            {"pat": patron},
        )
        conexion.execute(
            text('DELETE FROM "unidadOrganizacional".unidad_organizacional WHERE nombre LIKE :pat'),
            {"pat": patron},
        )


def correo_para(tag: str, prefijo: str = "test") -> str:
    return f"{prefijo}-{tag}@itm.edu.co"


def leer_cookies(respuesta) -> dict[str, str]:
    """Extrae nombre=valor de cada Set-Cookie (evita la política Secure del jar)."""
    jar: dict[str, str] = {}
    for cruda in respuesta.headers.get_list("set-cookie"):
        m = re.match(r"\s*([^=;]+)=([^;]*)", cruda)
        if m:
            jar[m.group(1).strip()] = m.group(2).strip()
    return jar


def cabecera_cookie(jar: dict[str, str], *nombres: str) -> dict[str, str]:
    return {"Cookie": "; ".join(f"{n}={jar[n]}" for n in nombres if n in jar)}


def obtener_csrf(client: TestClient) -> tuple[dict[str, str], str]:
    """Obtiene un CSRF fresco. Vacía el jar para que no haya duplicados."""
    client.cookies.clear()
    respuesta = client.get("/api/auth/csrf")
    assert respuesta.status_code == 204
    jar = leer_cookies(respuesta)
    assert "rp_csrf" in jar
    headers = {"X-CSRF-Token": jar["rp_csrf"]}
    headers.update(cabecera_cookie(jar, "rp_csrf"))
    return headers, jar["rp_csrf"]


def crear_usuario_cuenta(db, tag: str, contrasena: str = "una frase larga de paso", **extras):
    """Crea identidad USUARIO + cuenta activa. Devuelve (usuario, cuenta)."""
    from app.db.models.identidad import Usuarios
    from app.modules.auth import repository_cuentas as repo_cuentas

    correo = extras.pop("correo", correo_para(tag))
    documento = extras.pop("documento", f"10{tag[:8]}")
    telefono = extras.pop("telefono", f"300{tag[:7]}")
    usuario = repo_cuentas.crear_identidad_usuario(
        db,
        nombre=f"Prueba {tag}",
        documento=documento,
        telefono=telefono,
        institucion="ITM",
        dependencia="Facultad",
        correo=correo,
    )
    cuenta = repo_cuentas.crear_cuenta(
        db,
        correo=correo,
        password_hash=hash_contrasena(contrasena),
        tipo_cuenta="USUARIO",
        id_usuario=usuario.id_usuario,
    )
    db.commit()
    return usuario, cuenta


def crear_admin(db, tag: str, contrasena: str = "una frase larga de paso admin"):
    """Crea una cuenta ADMINISTRADOR (propia de Reservas, sin ficha ni laboratorio). Devuelve la cuenta.

    Decisión 2026-09-30: el rol define los permisos; el administrador puede todo.
    """
    from app.modules.auth import repository_cuentas as repo_cuentas

    cuenta = repo_cuentas.crear_cuenta(
        db,
        correo=correo_para(tag, "admin"),
        password_hash=hash_contrasena(contrasena),
        tipo_cuenta="ADMINISTRADOR",
    )
    db.commit()
    return cuenta


def crear_tecnico(db, tag: str, contrasena: str = "una frase larga de paso tec"):
    """Crea PERSONAL activa con un cargo de su laboratorio: es técnico por su rol. Devuelve (cuenta, id_unidad)."""
    from app.db.models.identidad import Cargo, Personal, UnidadOrganizacional
    from app.modules.auth import repository_cuentas as repo_cuentas

    correo = correo_para(tag, "tec")
    unidad = UnidadOrganizacional(nombre=f"Unidad {tag}", tipo="LABORATORIO", estado=True)
    db.add(unidad)
    db.flush()
    cargo = Cargo(nombre_cargo=f"Cargo {tag}", id_unidad=unidad.id_unidad)
    db.add(cargo)
    db.flush()
    persona = Personal(
        nombre=f"Tecnico {tag}",
        id_cargo=cargo.id_cargo,
        documento=f"30{tag[:8]}",
        correo=correo,
        telefono=f"302{tag[:7]}",
        estado=True,
    )
    db.add(persona)
    db.flush()
    cuenta = repo_cuentas.crear_cuenta(
        db,
        correo=correo,
        password_hash=hash_contrasena(contrasena),
        tipo_cuenta="PERSONAL",
        id_persona=persona.id_persona,
    )
    db.flush()
    db.commit()
    return cuenta, unidad.id_unidad


def iniciar_sesion(client: TestClient, correo: str, contrasena: str) -> tuple[dict, dict[str, str], str]:
    """Hace login por API. Devuelve (cuerpo, jar de cookies, csrf usado).

    El jar incluye `rp_csrf` con el valor enviado (el servidor lo conserva,
    no lo reemite): sirve para armar llamadas autenticadas posteriores sin
    pedir otro CSRF que duplique la cookie.
    """
    headers, csrf = obtener_csrf(client)
    respuesta = client.post(
        "/api/auth/sesiones",
        json={"correo": correo, "contrasena": contrasena},
        headers=headers,
    )
    assert respuesta.status_code == 201, respuesta.text
    jar = leer_cookies(respuesta)
    jar.setdefault("rp_csrf", csrf)
    return respuesta.json(), jar, csrf


def headers_autenticados(jar: dict[str, str]) -> dict[str, str]:
    """Cabeceras para endpoints con sesión: cookies + CSRF de doble envío."""
    headers = {"X-CSRF-Token": jar["rp_csrf"]}
    headers.update(cabecera_cookie(jar, "rp_access", "rp_refresh", "rp_csrf"))
    return headers


def otorgar_permiso_global(db, cuenta, codigo: str):
    """Hace administrador a la cuenta (los permisos los define el rol, no se otorgan por código).

    Se conserva el nombre para no reescribir cada prueba que necesita «alguien con permiso global»: el
    argumento `codigo` ya no restringe nada, el administrador puede todo. Devuelve la cuenta.
    """
    cuenta.tipo_cuenta = "ADMINISTRADOR"
    cuenta.id_persona = None
    cuenta.id_usuario = None
    db.commit()
    return cuenta
