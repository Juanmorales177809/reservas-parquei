"""API-07 — Unidades, cargos y permisos (contrato administration §2 y §3).

Reglas citadas por identificador completo (testing.md). T-ADM-07/08/09 son
API-08 y T-ADM-10..13 son API-12.
"""

from __future__ import annotations

import pytest

from app.core.authz import exigir_permiso
from app.core.deps import ContextoAutenticado
from app.core.errors import NoAutorizado
from app.core.security import hash_contrasena
from app.db.models.auth import Permisos
from app.db.models.identidad import Cargo, Personal, UnidadOrganizacional
from app.modules.administration import service as servicio_admin
from app.modules.administration.schemas import PermisoOtorgar
from app.modules.auth import repository_cuentas as repo_cuentas
from sqlalchemy import select
from tests.conftest import (
    correo_para,
    crear_admin,
    crear_usuario_cuenta,
    headers_autenticados,
    iniciar_sesion,
    otorgar_permiso_global,
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
    admin = crear_admin(db, tag)
    otorgar_permiso_global(db, admin, "unidades.administrar")
    otorgar_permiso_global(db, admin, "permisos.asignar")
    return admin


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


def test_permiso_unidad_exige_cargo_coincidente(client, db, tag):
    """T-ADM-01 · RN-PER-08, RN-PER-09 (administration): 422 y no se guarda."""
    admin = _admin_estructura(db, tag)
    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    auth = headers_autenticados(jar_admin)
    unidad_a, cargo_a = _unidad_cargo(db, tag, "A")
    unidad_b, _ = _unidad_cargo(db, tag, "B")
    _, cuenta = _personal_cuenta(db, tag, "tec", cargo_a)

    ajena = client.post(
        f"/api/permisos/cuentas/{cuenta.id_cuenta}",
        json={"codigo": "reservas.administrar", "id_unidad": unidad_b.id_unidad},
        headers=auth,
    )
    assert ajena.status_code == 422

    propia = client.post(
        f"/api/permisos/cuentas/{cuenta.id_cuenta}",
        json={"codigo": "reservas.administrar", "id_unidad": unidad_a.id_unidad},
        headers=auth,
    )
    assert propia.status_code == 201, propia.text
    assert propia.json()["id_unidad"] == unidad_a.id_unidad


def test_usuario_no_recibe_permisos(client, db, tag):
    """T-ADM-02 · RN-PER-08 (administration): 422 a cuenta USUARIO."""
    admin = _admin_estructura(db, tag)
    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    auth = headers_autenticados(jar_admin)
    _, cuenta = crear_usuario_cuenta(db, tag)

    respuesta = client.post(
        f"/api/permisos/cuentas/{cuenta.id_cuenta}",
        json={"codigo": "reservas.administrar", "id_unidad": None},
        headers=auth,
    )
    assert respuesta.status_code == 422


def test_permiso_no_se_extiende_a_otra_unidad(db, tag):
    """T-ADM-03 · RN-PER-06 (administration), servicio: el ámbito no se amplía."""
    admin = _admin_estructura(db, tag)
    unidad_a, cargo_a = _unidad_cargo(db, tag, "A")
    unidad_b, _ = _unidad_cargo(db, tag, "B")
    _, cuenta = _personal_cuenta(db, tag, "tec", cargo_a)

    servicio_admin.otorgar_permiso(
        db, cuenta.id_cuenta,
        PermisoOtorgar(codigo="reservas.administrar", id_unidad=unidad_a.id_unidad),
        _contexto_de(admin),
    )
    exigir_permiso(db, cuenta.id_cuenta, "reservas.administrar", id_unidad=unidad_a.id_unidad)
    with pytest.raises(NoAutorizado):
        exigir_permiso(db, cuenta.id_cuenta, "reservas.administrar", id_unidad=unidad_b.id_unidad)


def test_retirar_solo_afecta_lo_posterior(db, tag):
    """T-ADM-04 · RN-PER-04, RN-PER-05 (administration), servicio."""
    from sqlalchemy import text

    admin = _admin_estructura(db, tag)
    unidad_a, cargo_a = _unidad_cargo(db, tag, "A")
    _, cuenta = _personal_cuenta(db, tag, "tec", cargo_a)

    servicio_admin.otorgar_permiso(
        db, cuenta.id_cuenta,
        PermisoOtorgar(codigo="reservas.administrar", id_unidad=unidad_a.id_unidad),
        _contexto_de(admin),
    )
    exigir_permiso(db, cuenta.id_cuenta, "reservas.administrar", id_unidad=unidad_a.id_unidad)

    retiradas = servicio_admin.retirar_permiso(db, cuenta.id_cuenta, "reservas.administrar", _contexto_de(admin))
    assert retiradas == 1
    with pytest.raises(NoAutorizado):
        exigir_permiso(db, cuenta.id_cuenta, "reservas.administrar", id_unidad=unidad_a.id_unidad)

    # La historia queda: fila de auditoría con el antes, sin reescribir nada.
    filas = db.execute(
        text(
            "SELECT accion, datos_anteriores FROM administration.auditoria "
            "WHERE actor_cuenta_id = :actor AND accion = 'RETIRAR_PERMISO'"
        ),
        {"actor": admin.id_cuenta},
    ).all()
    assert len(filas) == 1
    assert "reservas.administrar" in str(filas[0][1])


def test_ultimo_global_no_se_retira(client, db, tag):
    """T-ADM-05 · RN-AUTH-ROL-09 (auth): 409; con dos, 204."""
    admin = _admin_estructura(db, tag)
    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    auth = headers_autenticados(jar_admin)

    ultimo = client.delete(f"/api/permisos/cuentas/{admin.id_cuenta}/cuentas.administrar", headers=auth)
    assert ultimo.status_code == 409

    unidad, cargo = _unidad_cargo(db, tag, "Z")
    _, cuenta2 = _personal_cuenta(db, tag, "adm2", cargo)
    otorgar_permiso_global(db, cuenta2, "cuentas.administrar")
    # La unidad del segundo admin es irrelevante para un permiso global.
    _ = (unidad, cargo)
    segundo = client.delete(f"/api/permisos/cuentas/{admin.id_cuenta}/cuentas.administrar", headers=auth)
    assert segundo.status_code == 204, segundo.text


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


def test_catalogo_cerrado_y_codigo_deshabilitado(client, db, tag):
    """Contrato §3.1: 14 códigos sin paginación; deshabilitado no se asigna."""
    admin = _admin_estructura(db, tag)
    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    auth = headers_autenticados(jar_admin)

    catalogo = client.get("/api/permisos", headers=auth)
    assert catalogo.status_code == 200
    assert set(catalogo.json()) == {"datos"}
    assert len(catalogo.json()["datos"]) == 14
    assert all("ambito" in p for p in catalogo.json()["datos"])

    unidad, cargo = _unidad_cargo(db, tag, "A")
    _, cuenta = _personal_cuenta(db, tag, "tec", cargo)
    permiso = db.scalar(select(Permisos).where(Permisos.codigo == "reservas.administrar"))
    permiso.habilitado = False
    db.commit()
    try:
        respuesta = client.post(
            f"/api/permisos/cuentas/{cuenta.id_cuenta}",
            json={"codigo": "reservas.administrar", "id_unidad": unidad.id_unidad},
            headers=auth,
        )
        assert respuesta.status_code == 422
    finally:
        permiso.habilitado = True
        db.commit()


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
