"""Roles fijos: el rol define los permisos (decisión 2026-09-30).

- Usuario: solo reserva.
- Técnico (PERSONAL con un cargo de un laboratorio): gestiona únicamente ese laboratorio.
- Administrador (cuenta propia de Reservas, sin ficha en LIA): todo.

Reglas citadas por identificador completo (testing.md): RN-AUTH-ROL-01 a RN-AUTH-ROL-07 de auth.
"""

from __future__ import annotations

import pytest

from app.core.authz import PERMISOS_DEL_TECNICO, exigir_permiso, resolver_rol
from app.core.errors import NoAutorizado
from app.db.models.identidad import Cargo, UnidadOrganizacional
from app.modules.auth import service_cuentas
from tests.conftest import (
    crear_admin,
    crear_tecnico,
    crear_usuario_cuenta,
    headers_autenticados,
    iniciar_sesion,
)

SOLO_ADMINISTRADOR = [
    "unidades.administrar",
    "cuentas.administrar",
    "usuarios.administrar",
    "permisos.asignar",
    "importacion.ejecutar",
    "recursos.administrar_equipos",
    "recursos.reasignar_unidad",
]


def _otro_laboratorio(db, tag: str) -> int:
    unidad = UnidadOrganizacional(nombre=f"Otro lab {tag}", tipo="LABORATORIO", estado=True)
    db.add(unidad)
    db.flush()
    db.add(Cargo(nombre_cargo=f"Otro cargo {tag}", id_unidad=unidad.id_unidad))
    db.commit()
    return unidad.id_unidad


def test_administrador_es_global_y_puede_todo(db, tag):
    """RN-AUTH-ROL-01: el administrador es una cuenta propia y su ámbito es global."""
    admin = crear_admin(db, tag)
    contexto = resolver_rol(db, admin.id_cuenta)
    assert contexto.rol == "ADMINISTRADOR" and contexto.unidades_autorizadas == "GLOBAL"
    otro = _otro_laboratorio(db, tag)
    for codigo in [*PERMISOS_DEL_TECNICO, *SOLO_ADMINISTRADOR]:
        exigir_permiso(db, admin.id_cuenta, codigo)
        exigir_permiso(db, admin.id_cuenta, codigo, id_unidad=otro)


def test_tecnico_gestiona_solo_el_laboratorio_de_su_cargo(db, tag):
    """RN-AUTH-ROL-02, RN-AUTH-ROL-06: el ámbito del técnico sale de su cargo vigente."""
    tecnico, id_unidad = crear_tecnico(db, tag)
    contexto = resolver_rol(db, tecnico.id_cuenta)
    assert contexto.rol == "TECNICO" and contexto.unidades_autorizadas == [id_unidad]

    for codigo in PERMISOS_DEL_TECNICO:
        exigir_permiso(db, tecnico.id_cuenta, codigo, id_unidad=id_unidad)

    # Otro laboratorio: fuera de ámbito, sea cual sea el permiso.
    ajeno = _otro_laboratorio(db, tag)
    for codigo in PERMISOS_DEL_TECNICO:
        with pytest.raises(NoAutorizado):
            exigir_permiso(db, tecnico.id_cuenta, codigo, id_unidad=ajeno)


@pytest.mark.parametrize("codigo", SOLO_ADMINISTRADOR)
def test_el_tecnico_no_ejerce_lo_del_administrador(db, tag, codigo):
    """RN-AUTH-ROL-03: lo global (estructura, cuentas, importaciones, equipos entre laboratorios) es del administrador."""
    tecnico, id_unidad = crear_tecnico(db, f"{tag[:6]}{abs(hash(codigo)) % 1000}")
    with pytest.raises(NoAutorizado):
        exigir_permiso(db, tecnico.id_cuenta, codigo)
    with pytest.raises(NoAutorizado):
        exigir_permiso(db, tecnico.id_cuenta, codigo, id_unidad=id_unidad)


def test_usuario_solo_reserva(db, tag):
    """RN-AUTH-ROL-01: una cuenta USUARIO no tiene ningún permiso administrativo."""
    _, cuenta = crear_usuario_cuenta(db, tag)
    contexto = resolver_rol(db, cuenta.id_cuenta)
    assert contexto.rol == "USUARIO" and contexto.unidades_autorizadas == []
    for codigo in [*PERMISOS_DEL_TECNICO, *SOLO_ADMINISTRADOR]:
        with pytest.raises(NoAutorizado):
            exigir_permiso(db, cuenta.id_cuenta, codigo)


def test_cuenta_inactiva_o_ficha_inactiva_no_administra(db, tag):
    """RN-AUTH-ROL-05: el rol se revalida con datos vigentes en cada operación."""
    admin = crear_admin(db, f"a{tag}")
    admin.estado = False
    db.commit()
    assert resolver_rol(db, admin.id_cuenta).rol == "USUARIO"

    tecnico, _ = crear_tecnico(db, f"t{tag}")
    tecnico.estado = False
    db.commit()
    assert resolver_rol(db, tecnico.id_cuenta).rol == "USUARIO"


def test_sesion_del_administrador_y_acceso_por_rol_en_la_api(client, db, tag):
    """RN-AUTH-ROL-01: el administrador entra sin ficha y `/sesiones/actual` lo dice; el técnico no ve lo global."""
    admin = crear_admin(db, f"x{tag}")
    tecnico, _ = crear_tecnico(db, f"y{tag}")

    cuerpo, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    assert cuerpo["tipo_cuenta"] == "ADMINISTRADOR"
    actual = client.get("/api/auth/sesiones/actual", headers=headers_autenticados(jar_admin))
    assert actual.status_code == 200, actual.text
    assert actual.json()["rol"] == "ADMINISTRADOR" and actual.json()["unidades_autorizadas"] == "GLOBAL"
    assert actual.json()["actualizacion_inicial_pendiente"] is None
    assert client.get("/api/unidades", headers=headers_autenticados(jar_admin)).status_code == 200

    _, jar_tec, _ = iniciar_sesion(client, tecnico.correo, "una frase larga de paso tec")
    h = headers_autenticados(jar_tec)
    assert client.get("/api/auth/sesiones/actual", headers=h).json()["rol"] == "TECNICO"
    assert client.get("/api/unidades", headers=h).status_code == 403
    assert client.get("/api/auditoria", headers=h).status_code == 403


def test_ya_no_se_asignan_permisos_a_mano(client, db, tag):
    """Decisión 2026-09-30: no existe `/api/permisos`; ni siquiera el administrador otorga permisos."""
    admin = crear_admin(db, tag)
    _, jar, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    h = headers_autenticados(jar)
    assert client.get("/api/permisos", headers=h).status_code == 404
    assert client.post(f"/api/permisos/cuentas/{admin.id_cuenta}", json={"codigo": "x"}, headers=h).status_code in (404, 405)


def test_cuenta_de_administrador_no_cambia_de_identidad_ni_se_queda_el_sistema_sin_ella(db, tag):
    """RN-AUTH-ROL-09: el sistema no se queda sin administradores; una cuenta de administrador no tiene identidad."""
    from app.core.errors import Conflicto, Validacion
    from tests.test_administration import _contexto_de

    unico = crear_admin(db, f"u{tag}")
    otro = crear_admin(db, f"o{tag}")
    actor = _contexto_de(otro)

    with pytest.raises(Validacion):
        service_cuentas.cambiar_identidad(db, unico.id_cuenta, "USUARIO", None, 1, actor)
    db.rollback()

    # Con otro administrador activo se puede desactivar uno; al quedar uno solo, ese ya no.
    service_cuentas.cambiar_estado(db, unico.id_cuenta, False, actor)
    with pytest.raises(Conflicto):
        service_cuentas.cambiar_estado(db, otro.id_cuenta, False, actor)
    db.rollback()


def test_script_crea_y_restablece_al_administrador_sin_tocar_otras_cuentas(db, tag, monkeypatch, capsys):
    """El administrador se crea por un script (la interfaz no puede: para entrar ya hace falta uno)."""
    import io

    from sqlalchemy import select

    from app.core.security import verificar_contrasena
    from app.db.models.auth import Cuentas
    from app.scripts import crear_administrador
    from tests.conftest import correo_para

    correo = correo_para(tag, "script")
    monkeypatch.setattr("sys.stdin", io.StringIO("una frase larga de paso uno\n"))
    assert crear_administrador.main(["--correo", correo.upper()]) == 0
    cuenta = db.scalar(select(Cuentas).where(Cuentas.correo == correo))
    assert cuenta is not None and cuenta.tipo_cuenta == "ADMINISTRADOR" and cuenta.estado is True
    assert cuenta.id_usuario is None and cuenta.id_persona is None
    assert verificar_contrasena("una frase larga de paso uno", cuenta.password_hash)
    assert resolver_rol(db, cuenta.id_cuenta).rol == "ADMINISTRADOR"

    # Segunda corrida: restablece y reactiva, no duplica.
    cuenta.estado = False
    db.commit()
    monkeypatch.setattr("sys.stdin", io.StringIO("una frase larga de paso dos\n"))
    assert crear_administrador.main(["--correo", correo]) == 0
    db.expire_all()
    cuenta = db.scalar(select(Cuentas).where(Cuentas.correo == correo))
    assert cuenta.estado is True and verificar_contrasena("una frase larga de paso dos", cuenta.password_hash)

    # Una cuenta de otro tipo no se toca.
    _, usuario = crear_usuario_cuenta(db, f"s{tag}")
    hash_antes = usuario.password_hash
    monkeypatch.setattr("sys.stdin", io.StringIO("una frase larga de paso tres\n"))
    assert crear_administrador.main(["--correo", usuario.correo]) == 1
    db.expire_all()
    assert db.get(Cuentas, usuario.id_cuenta).password_hash == hash_antes

    # Una contraseña corta se rechaza.
    monkeypatch.setattr("sys.stdin", io.StringIO("corta\n"))
    assert crear_administrador.main(["--correo", correo_para(tag, "otro")]) == 2
