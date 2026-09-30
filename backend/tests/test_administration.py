"""API-07 — Unidades y cargos (contrato administration §2). Los permisos ya no se asignan (decisión 2026-09-30).

Reglas citadas por identificador completo (testing.md). T-ADM-07/08/09 son
API-08 y T-ADM-10..13 son API-12.
"""

from __future__ import annotations

import pytest

from app.core.authz import exigir_permiso
from app.core.deps import ContextoAutenticado
from app.core.errors import NoAutorizado
from app.core.security import generar_token, hash_contrasena, hashear_token
from app.db.models.auth import Permisos
from app.db.models.identidad import Cargo, Personal, UnidadOrganizacional
from app.modules.administration import service as servicio_admin
from app.modules.auth import repository_cuentas as repo_cuentas
from app.modules.auth import service_cuentas
from sqlalchemy import select, text
from tests.conftest import (
    correo_para,
    crear_admin,
    crear_usuario_cuenta,
    headers_autenticados,
    iniciar_sesion,
)


def _unidad_cargo(db, tag: str, sufijo: str):
    unidad = UnidadOrganizacional(nombre=f"Adm Unidad {sufijo} {tag}", tipo="LABORATORIO", estado=True)
    db.add(unidad)
    db.flush()
    cargo = Cargo(nombre_cargo=f"Adm Cargo {sufijo} {tag}", id_unidad=unidad.id_unidad)
    db.add(cargo)
    db.flush()
    db.commit()
    return unidad, cargo


def _personal_cuenta(db, tag: str, prefijo: str, cargo, contrasena: str = "una frase larga de paso"):
    correo = correo_para(tag, prefijo)
    persona = Personal(
        nombre=f"Adm {prefijo} {tag}", id_cargo=cargo.id_cargo, documento=f"80{tag[:8]}",
        correo=correo, telefono=f"316{tag[:7]}", estado=True,
    )
    db.add(persona)
    db.flush()
    cuenta = repo_cuentas.crear_cuenta(
        db, correo=correo, password_hash=hash_contrasena(contrasena),
        tipo_cuenta="PERSONAL", id_persona=persona.id_persona,
    )
    db.commit()
    return persona, cuenta


def _admin_estructura(db, tag: str):
    return crear_admin(db, tag)


def _contexto_de(cuenta) -> ContextoAutenticado:
    return ContextoAutenticado(
        id_cuenta=cuenta.id_cuenta,
        id_sesion="00000000-0000-0000-0000-000000000000",
        tipo_cuenta=cuenta.tipo_cuenta,
        id_usuario=cuenta.id_usuario,
        id_persona=cuenta.id_persona,
        rol="ADMINISTRADOR",
        unidades_autorizadas="GLOBAL",
        autenticacion_reciente=True,
        actualizacion_inicial_pendiente=None,
        correo=cuenta.correo,
    )







def test_deshabilitar_unidad_no_borra_nada(db, tag):
    """T-ADM-06 · RN-UNI-04, RN-UNI-05 (administration), servicio: baja lógica."""
    admin = _admin_estructura(db, tag)
    unidad, cargo = _unidad_cargo(db, tag, "A")
    persona, _ = _personal_cuenta(db, tag, "tec", cargo)

    resultado = servicio_admin.cambiar_estado_unidad(db, unidad.id_unidad, False, _contexto_de(admin))
    assert resultado["estado"] is False
    db.expire_all()

    assert db.get(UnidadOrganizacional, unidad.id_unidad) is not None
    assert db.get(Cargo, cargo.id_cargo) is not None
    assert db.get(Personal, persona.id_persona) is not None


def test_jerarquia_sin_ciclos_ni_duplicados(client, db, tag):
    """Contrato §2.1/§2.3: nombre duplicado y ciclo → 409; padre inexistente → 404."""
    admin = _admin_estructura(db, tag)
    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    auth = headers_autenticados(jar_admin)

    padre = client.post(
        "/api/unidades", json={"nombre": f"Padre {tag}", "tipo": "FACULTAD"}, headers=auth
    )
    assert padre.status_code == 201, padre.text
    id_padre = padre.json()["id_unidad"]

    duplicado = client.post(
        "/api/unidades", json={"nombre": f"Padre {tag}", "tipo": "LABORATORIO"}, headers=auth
    )
    assert duplicado.status_code == 409

    sin_padre = client.post(
        "/api/unidades",
        json={"nombre": f"Huerfana {tag}", "tipo": "LABORATORIO", "id_unidad_padre": 999999999},
        headers=auth,
    )
    assert sin_padre.status_code == 404

    hija = client.post(
        "/api/unidades",
        json={"nombre": f"Hija {tag}", "tipo": "LABORATORIO", "id_unidad_padre": id_padre},
        headers=auth,
    )
    assert hija.status_code == 201, hija.text

    ciclo = client.patch(
        f"/api/unidades/{id_padre}",
        json={"id_unidad_padre": hija.json()["id_unidad"]},
        headers=auth,
    )
    assert ciclo.status_code == 409



def test_cargo_exige_unidad_activa(client, db, tag):
    """RN-UNI-05: ni crear ni mover cargos a unidades deshabilitadas."""
    admin = _admin_estructura(db, tag)
    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    auth = headers_autenticados(jar_admin)

    unidad = client.post(
        "/api/unidades", json={"nombre": f"Cerrada {tag}", "tipo": "LABORATORIO"}, headers=auth
    ).json()
    apagada = client.patch(f"/api/unidades/{unidad['id_unidad']}/estado", json={"estado": False}, headers=auth)
    assert apagada.status_code == 200

    cargo = client.post(
        "/api/cargos", json={"nombre_cargo": f"Cargo {tag}", "id_unidad": unidad["id_unidad"]}, headers=auth
    )
    assert cargo.status_code == 422

    unidad2 = client.post(
        "/api/unidades", json={"nombre": f"Abierta {tag}", "tipo": "LABORATORIO"}, headers=auth
    ).json()
    creado = client.post(
        "/api/cargos", json={"nombre_cargo": f"Cargo {tag}", "id_unidad": unidad2["id_unidad"]}, headers=auth
    )
    assert creado.status_code == 201, creado.text
    mover = client.patch(
        f"/api/cargos/{creado.json()['id_cargo']}", json={"id_unidad": unidad["id_unidad"]}, headers=auth
    )
    assert mover.status_code == 422


# --- API-08 §5 Auditoría ------------------------------------------------------------


def test_operaciones_dejan_registro_consultable(client, db, tag):
    """T-ADM-07 · RN-AUD-01, RN-AUD-02 (administration), servicio."""
    admin = _admin_estructura(db, tag)
    actor = _contexto_de(admin)
    unidad, cargo = _unidad_cargo(db, tag, "A")
    _, cuenta_tec = _personal_cuenta(db, tag, "tec", cargo)
    _, cuenta_usr = crear_usuario_cuenta(db, tag)

    servicio_admin.cambiar_estado_unidad(db, unidad.id_unidad, False, actor)
    service_cuentas.cambiar_estado(db, cuenta_usr.id_cuenta, False, actor)

    filas = db.execute(
        text(
            "SELECT a.accion, a.entidad, a.entidad_id, a.created_at, c.correo "
            "FROM administration.auditoria a JOIN auth.cuentas c "
            "ON c.id_cuenta = a.actor_cuenta_id "
            "WHERE a.actor_cuenta_id = :actor ORDER BY a.id"
        ),
        {"actor": admin.id_cuenta},
    ).all()
    acciones = {(f[0], f[1]) for f in filas}
    assert ("CAMBIAR_ESTADO_UNIDAD", "unidadOrganizacional.unidad_organizacional") in acciones
    assert ("CAMBIO_ESTADO_CUENTA", "auth.cuentas") in acciones
    for _, _, entidad_id, momento, correo in filas:
        assert entidad_id and momento and correo == admin.correo

    # Y se consulta por la API con filtros y paginación.
    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    auth = headers_autenticados(jar_admin)
    consulta = client.get(
        f"/api/auditoria?actor_cuenta_id={admin.id_cuenta}&accion=CAMBIAR_ESTADO_UNIDAD",
        headers=auth,
    )
    assert consulta.status_code == 200, consulta.text
    cuerpo = consulta.json()
    assert cuerpo["paginacion"]["total"] >= 1
    primera = cuerpo["datos"][0]
    assert primera["actor_cuenta_id"] == admin.id_cuenta
    assert primera["accion"] == "CAMBIAR_ESTADO_UNIDAD"
    assert set(primera) == {
        "id", "actor_cuenta_id", "entidad", "entidad_id", "accion",
        "datos_anteriores", "datos_nuevos", "motivo", "created_at",
    }


def test_auditoria_no_se_escribe_por_api(client, db, tag):
    """T-ADM-08 · RN-AUD-05 (administration), contrato: no hay ruta de escritura."""
    admin = _admin_estructura(db, tag)
    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    auth = headers_autenticados(jar_admin)

    for metodo in ("post", "put", "patch", "delete"):
        respuesta = getattr(client, metodo)("/api/auditoria", headers=auth)
        assert respuesta.status_code == 404, metodo
        assert respuesta.json()["error"]["codigo"] == "NO_ENCONTRADO"
        con_id = getattr(client, metodo)("/api/auditoria/1", headers=auth)
        assert con_id.status_code == 404, metodo

    mal_filtro = client.get("/api/auditoria?filtro_inventado=1", headers=auth)
    assert mal_filtro.status_code == 400


def test_registro_sin_secretos(client, db, tag):
    """T-ADM-09 · SEC-AUD-03 (auth), servicio: ni contraseñas ni tokens."""
    contrasena = "frase secreta larga de paso"
    _, cuenta = crear_usuario_cuenta(db, tag, contrasena=contrasena)
    _, jar, _ = iniciar_sesion(client, cuenta.correo, contrasena)

    crudo, _ = generar_token()
    repo_cuentas.crear_token_recuperacion(db, cuenta.id_cuenta, hashear_token(crudo))
    db.commit()
    service_cuentas.restablecer_contrasena(db, crudo, "otra frase secreta larga")

    filas = db.execute(
        text(
            "SELECT accion, datos_anteriores, datos_nuevos FROM administration.auditoria "
            "WHERE actor_cuenta_id = :actor"
        ),
        {"actor": cuenta.id_cuenta},
    ).all()
    assert filas, "la cuenta debió dejar registros de auditoría"
    volcado = " ".join(f"{a} {ant} {nue}" for a, ant, nue in filas)
    assert contrasena not in volcado
    assert "otra frase secreta larga" not in volcado
    assert crudo not in volcado
    _ = jar
