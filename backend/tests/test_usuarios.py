"""API-06 — Identidades funcionales y fichas de Personal (contrato usuarios §2.1, §2.2, §5, §6).

Reglas citadas por identificador completo (testing.md); la cita nombra el
módulo cuando no es el propio. §2.3, §3 y §4 quedan para API-11 (researchs).
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.core.authz import resolver_rol
from app.core.deps import ContextoAutenticado
from app.core.errors import Conflicto
from app.core.security import hash_contrasena
from app.db.models.auth import CuentaPermisos, Permisos
from app.db.models.identidad import Cargo, Personal, UnidadOrganizacional
from app.db.session import engine
from app.modules.auth import repository_cuentas as repo_cuentas
from app.modules.usuarios import schemas as esquemas_usuarios
from app.modules.usuarios import service as servicio_usuarios
from tests.conftest import (
    correo_para,
    crear_admin,
    crear_usuario_cuenta,
    headers_autenticados,
    iniciar_sesion,
    otorgar_permiso_global,
)


def _unidad_cargo(db, tag: str, sufijo: str = "U"):
    unidad = UnidadOrganizacional(nombre=f"Unidad {sufijo} {tag}", tipo="FACULTAD", estado=True)
    db.add(unidad)
    db.flush()
    cargo = Cargo(nombre_cargo=f"Cargo {sufijo} {tag}", id_unidad=unidad.id_unidad)
    db.add(cargo)
    db.flush()
    db.commit()
    return unidad, cargo


def _admin_usuarios(db, tag: str):
    admin = crear_admin(db, tag)
    otorgar_permiso_global(db, admin, "usuarios.administrar")
    return admin


def _ficha_cuerpo(tag: str, id_cargo: int, prefijo: str = "per", doc: str | None = None) -> dict:
    return {
        "nombre": f"Persona {tag}",
        "documento": doc or f"70{tag[:8]}",
        "correo": correo_para(tag, prefijo),
        "telefono": f"306{tag[:7]}",
        "id_cargo": id_cargo,
    }


def test_identidad_documento_duplicado_409(client, db, tag):
    """T-USR-01 · RN-DAT-02 (usuarios): por la restricción de la base.

    En `/api/usuarios` el código es DOCUMENTO_DUPLICADO (§5.1); en
    `/api/personal` es CONFLICTO (§6.1). Ambos llegan por UNIQUE, no por
    consulta previa: la segunda inserción concurrente falla igual.
    """
    admin = _admin_usuarios(db, tag)
    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    auth = headers_autenticados(jar_admin)

    cuerpo = {
        "nombre": f"Persona {tag}",
        "documento": f"71{tag[:8]}",
        "telefono": f"307{tag[:7]}",
        "institucion": "ITM",
        "dependencia": "Facultad",
        "correo": correo_para(tag, "usr"),
    }
    primera = client.post("/api/usuarios", json=cuerpo, headers=auth)
    assert primera.status_code == 201, primera.text

    cuerpo["correo"] = correo_para(tag, "otro")
    cuerpo["telefono"] = f"308{tag[:7]}"
    segunda = client.post("/api/usuarios", json=cuerpo, headers=auth)
    assert segunda.status_code == 409
    assert segunda.json()["error"]["codigo"] == "DOCUMENTO_DUPLICADO"

    _, cargo = _unidad_cargo(db, tag)
    ficha = _ficha_cuerpo(tag, cargo.id_cargo)
    creada = client.post("/api/personal", json=ficha, headers=auth)
    assert creada.status_code == 201, creada.text
    ficha["correo"] = correo_para(tag, "per2")
    ficha["telefono"] = f"309{tag[:7]}"
    duplicada = client.post("/api/personal", json=ficha, headers=auth)
    assert duplicada.status_code == 409
    assert duplicada.json()["error"]["codigo"] == "CONFLICTO"


def test_alta_pide_los_cinco_datos(client, db, tag):
    """T-USR-02 · RN-DAT-01 (usuarios): cada dato omitido da 422."""
    admin = _admin_usuarios(db, tag)
    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    auth = headers_autenticados(jar_admin)

    base = {
        "nombre": f"Persona {tag}",
        "documento": f"72{tag[:8]}",
        "telefono": f"310{tag[:7]}",
        "institucion": "ITM",
        "dependencia": "Facultad",
        "correo": correo_para(tag, "usr"),
    }
    for campo in ("nombre", "documento", "telefono", "institucion", "dependencia", "correo"):
        cuerpo = {k: v for k, v in base.items() if k != campo}
        respuesta = client.post("/api/usuarios", json=cuerpo, headers=auth)
        assert respuesta.status_code == 422, campo
        assert respuesta.json()["error"]["codigo"] == "VALIDACION"


def test_correo_inmutable_con_cuenta(client, db, tag):
    """T-USR-03 · RN-AUTH-ID-02, RN-AUTH-ID-12 (auth): 409 y solo lectura en perfil."""
    admin = _admin_usuarios(db, tag)
    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    auth = headers_autenticados(jar_admin)

    usuario, cuenta = crear_usuario_cuenta(db, tag)
    respuesta = client.patch(
        f"/api/usuarios/{usuario.id_usuario}",
        json={"correo": correo_para(tag, "cambiado")},
        headers=auth,
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "CONFLICTO"

    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso")
    perfil = client.get("/api/perfil", headers=headers_autenticados(jar))
    assert perfil.status_code == 200
    assert perfil.json()["correo"] == cuenta.correo


def test_invitar_personal_exige_ficha_activa(client, db, tag):
    """T-USR-06 · RN-AUTH-ID-07 (auth): sin ficha o inactiva, se rechaza."""
    admin = _admin_usuarios(db, tag)
    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    auth = headers_autenticados(jar_admin)
    unidad, cargo = _unidad_cargo(db, tag)

    sin_ficha = client.post(
        "/api/auth/invitaciones",
        json={"correo": correo_para(tag, "nadie"), "tipo_cuenta": "PERSONAL", "id_unidad": unidad.id_unidad},
        headers=auth,
    )
    assert sin_ficha.status_code == 422


def test_desactivar_ficha_inactiva_deja_sin_rol(client, db, tag):
    """T-USR-06 (2ª parte): con ficha inactiva la invitación se rechaza."""
    admin = _admin_usuarios(db, tag)
    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    auth = headers_autenticados(jar_admin)
    unidad, cargo = _unidad_cargo(db, tag, "V")

    ficha = _ficha_cuerpo(tag, cargo.id_cargo, prefijo="inac")
    creada = client.post("/api/personal", json=ficha, headers=auth)
    assert creada.status_code == 201, creada.text
    apagada = client.patch(
        f"/api/personal/{creada.json()['id_persona']}/estado",
        json={"estado": False},
        headers=auth,
    )
    assert apagada.status_code == 200, apagada.text

    invitar = client.post(
        "/api/auth/invitaciones",
        json={"correo": ficha["correo"], "tipo_cuenta": "PERSONAL", "id_unidad": unidad.id_unidad},
        headers=auth,
    )
    assert invitar.status_code == 422


def test_perfil_personal_no_existe(client, db, tag):
    """API-06: el perfil es concepto de Usuario; PERSONAL recibe 404."""
    admin = _admin_usuarios(db, tag)
    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    perfil = client.get("/api/perfil", headers=headers_autenticados(jar_admin))
    assert perfil.status_code == 404


def test_perfil_nulo_hasta_completarse(db, tag):
    """T-USR-04 · RN-USR-07 (usuarios): se sella al completar, no al crear."""
    usuario, cuenta = crear_usuario_cuenta(db, tag)
    assert usuario.perfil_actualizado_at is None

    contexto = ContextoAutenticado(
        id_cuenta=cuenta.id_cuenta,
        id_sesion="00000000-0000-0000-0000-000000000000",
        tipo_cuenta="USUARIO",
        id_usuario=usuario.id_usuario,
        id_persona=None,
        rol="USUARIO",
        unidades_autorizadas=[],
        autenticacion_reciente=False,
        actualizacion_inicial_pendiente=True,
        correo=cuenta.correo,
    )
    perfil = servicio_usuarios.obtener_perfil(db, contexto)
    assert perfil["actualizacion_inicial_pendiente"] is True
    assert perfil["perfil_actualizado_at"] is None


def test_desactivar_ficha_conserva_historial(db, tag):
    """T-USR-07 · RN-PRS-04 (usuarios): el registro permanece, el rol se pierde."""
    admin = crear_admin(db, tag)
    otorgar_permiso_global(db, admin, "usuarios.administrar")
    _, cargo = _unidad_cargo(db, tag, "W")

    persona = servicio_usuarios.crear_ficha(
        db,
        esquemas_usuarios.PersonalCrear(
            nombre=f"Tecnico {tag}",
            documento=f"73{tag[:8]}",
            correo=correo_para(tag, "tec2"),
            telefono=f"311{tag[:7]}",
            id_cargo=cargo.id_cargo,
        ),
    )
    assert persona["estado"] is True

    resultado = servicio_usuarios.cambiar_estado_ficha(db, persona["id_persona"], False)
    assert resultado["estado"] is False
    conservada = db.get(Personal, persona["id_persona"])
    assert conservada is not None and conservada.estado is False


def test_ultima_ficha_admin_no_se_desactiva(db, tag):
    """RN-AUTH-ROL-09 (auth) vía §6.4: sin administradores no hay sistema."""
    admin = crear_admin(db, tag)
    persona_id = admin.id_persona
    assert persona_id is not None
    with pytest.raises(Conflicto):
        servicio_usuarios.cambiar_estado_ficha(db, persona_id, False)
    db.rollback()


def test_patch_perfil_rechaza_correo(client, db, tag):
    """UF-USR-04: el correo es solo lectura; el resto se edita."""
    _, cuenta = crear_usuario_cuenta(db, tag)
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso")
    auth = headers_autenticados(jar)

    con_correo = client.patch("/api/perfil", json={"correo": correo_para(tag, "otro")}, headers=auth)
    assert con_correo.status_code == 409

    editado = client.patch("/api/perfil", json={"nombre": f"Cambiado {tag}"}, headers=auth)
    assert editado.status_code == 200, editado.text
    assert editado.json()["nombre"] == f"Cambiado {tag}"
    assert editado.json()["correo"] == cuenta.correo


def test_cuenta_exige_exactamente_una_identidad(db, tag):
    """T-USR-08 · RN-AUTH-ID-03, RN-AUTH-ID-04 (auth), nivel base de datos."""
    usuario, _ = crear_usuario_cuenta(db, tag)
    unidad, cargo = _unidad_cargo(db, tag, "X")
    persona = servicio_usuarios.crear_ficha(
        db,
        esquemas_usuarios.PersonalCrear(
            nombre=f"Tecnico {tag}",
            documento=f"74{tag[:8]}",
            correo=correo_para(tag, "ambas"),
            telefono=f"312{tag[:7]}",
            id_cargo=cargo.id_cargo,
        ),
    )
    with engine.begin() as conexion:
        with pytest.raises(IntegrityError):
            conexion.execute(
                text(
                    "INSERT INTO auth.cuentas (correo, password_hash, tipo_cuenta, id_usuario, id_persona) "
                    "VALUES (:correo, 'x', 'USUARIO', :u, :p)"
                ),
                {"correo": correo_para(tag, "doble"), "u": usuario.id_usuario, "p": persona["id_persona"]},
            )
    with engine.begin() as conexion:
        with pytest.raises(IntegrityError):
            conexion.execute(
                text(
                    "INSERT INTO auth.cuentas (correo, password_hash, tipo_cuenta) "
                    "VALUES (:correo, 'x', 'USUARIO')"
                ),
                {"correo": correo_para(tag, "ninguna")},
            )


def test_ficha_sin_estado_nace_activa(db, tag):
    """T-USR-05 · RN-PRS-04 (usuarios), nivel base de datos: sin tercer valor."""
    _, cargo = _unidad_cargo(db, tag, "Y")
    with engine.begin() as conexion:
        fila = conexion.execute(
            text(
                "INSERT INTO personal.personal (nombre, id_cargo, documento, correo, telefono) "
                "VALUES (:n, :c, :d, :m, :t) RETURNING estado"
            ),
            {
                "n": f"Persona {tag}",
                "c": cargo.id_cargo,
                "d": f"75{tag[:8]}",
                "m": correo_para(tag, "defecto"),
                "t": f"313{tag[:7]}",
            },
        ).one()
        assert fila[0] is True
    with engine.begin() as conexion:
        with pytest.raises(IntegrityError):
            conexion.execute(
                text(
                    "INSERT INTO personal.personal (nombre, id_cargo, documento, correo, telefono, estado) "
                    "VALUES (:n, :c, :d, :m, :t, NULL)"
                ),
                {
                    "n": f"Otra {tag}",
                    "c": cargo.id_cargo,
                    "d": f"76{tag[:8]}",
                    "m": correo_para(tag, "nulo"),
                    "t": f"314{tag[:7]}",
                },
            )


def test_rol_cae_a_usuario_con_ficha_inactiva(db, tag):
    """T-USR-07 (rol): la cuenta asociada deja de resolver rol administrativo."""
    admin = crear_admin(db, tag)
    assert resolver_rol(db, admin.id_cuenta).rol == "ADMINISTRADOR"

    # Segunda cuenta administradora para que desactivar la primera no sea 409.
    _, cargo = _unidad_cargo(db, tag, "Z")
    correo2 = correo_para(tag, "admin2")
    persona2 = Personal(
        nombre=f"Admin2 {tag}", id_cargo=cargo.id_cargo, documento=f"77{tag[:8]}",
        correo=correo2, telefono=f"315{tag[:7]}", estado=True,
    )
    db.add(persona2)
    db.flush()
    cuenta2 = repo_cuentas.crear_cuenta(
        db, correo=correo2, password_hash=hash_contrasena("otra frase larga de paso"),
        tipo_cuenta="PERSONAL", id_persona=persona2.id_persona,
    )
    db.flush()
    permiso = db.scalar(select(Permisos).where(Permisos.codigo == "cuentas.administrar"))
    db.add(CuentaPermisos(id_cuenta=cuenta2.id_cuenta, permiso_id=permiso.id, id_unidad=None,
                          otorgado_por=cuenta2.id_cuenta,
                          created_at=datetime.now(timezone.utc)))
    db.commit()

    servicio_usuarios.cambiar_estado_ficha(db, admin.id_persona, False)
    db.expire_all()
    assert resolver_rol(db, admin.id_cuenta).rol == "USUARIO"
