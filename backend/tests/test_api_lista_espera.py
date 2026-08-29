# -*- coding: utf-8 -*-
"""Pruebas de la API de lista de espera (2026-08-29).

CRUD de `app/api/lista_espera.py` -- la notificación al liberarse un cupo
(el gancho real en `services/reservas.py`) se prueba en
`test_lista_espera_notificacion.py`.
"""

from tests.conftest import cookies_para, crear_espacio, crear_recurso, crear_usuario, fecha_habilitada


def _usuario_y_recurso(db, *, username="lista_espera_user"):
    espacio = crear_espacio(db, nombre=f"Espacio {username}")
    usuario = crear_usuario(db, username=username, email=f"{username}@example.com", rol="usuario")
    recurso = crear_recurso(db, espacio=espacio, usuario=usuario, nombre=f"Recurso {username}")
    return usuario, recurso


def _payload(recurso_id, fecha, hora_inicio="08:00", hora_fin="10:00"):
    return {"recurso_id": recurso_id, "fecha": fecha.isoformat(), "hora_inicio": hora_inicio, "hora_fin": hora_fin}


def test_crear_entrada_devuelve_201(client, db):
    usuario, recurso = _usuario_y_recurso(db)
    respuesta = client.post(
        "/lista-espera", json=_payload(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["recurso_id"] == recurso.id
    assert cuerpo["estado"] == "activa"


def test_crear_entrada_recurso_inexistente_da_404(client, db):
    usuario, _ = _usuario_y_recurso(db)
    respuesta = client.post(
        "/lista-espera", json=_payload(999999, fecha_habilitada()), headers=cookies_para(usuario)
    )
    assert respuesta.status_code == 404


def test_listar_mias_solo_devuelve_las_propias(client, db):
    usuario_a, recurso = _usuario_y_recurso(db, username="lista_espera_a")
    usuario_b, _ = _usuario_y_recurso(db, username="lista_espera_b")
    fecha = fecha_habilitada()

    r1 = client.post("/lista-espera", json=_payload(recurso.id, fecha), headers=cookies_para(usuario_a))
    client.post("/lista-espera", json=_payload(recurso.id, fecha), headers=cookies_para(usuario_b))

    respuesta = client.get("/lista-espera/mias", headers=cookies_para(usuario_a))
    assert respuesta.status_code == 200
    ids = [item["id"] for item in respuesta.json()]
    assert ids == [r1.json()["id"]]


def test_listar_mias_oculta_canceladas(client, db):
    usuario, recurso = _usuario_y_recurso(db, username="lista_espera_oculta")
    fecha = fecha_habilitada()
    creada = client.post(
        "/lista-espera", json=_payload(recurso.id, fecha), headers=cookies_para(usuario)
    ).json()

    client.delete(f"/lista-espera/{creada['id']}", headers=cookies_para(usuario))

    respuesta = client.get("/lista-espera/mias", headers=cookies_para(usuario))
    assert respuesta.json() == []


def test_cancelar_propia_devuelve_204_y_desaparece_de_mias(client, db):
    usuario, recurso = _usuario_y_recurso(db)
    creada = client.post(
        "/lista-espera", json=_payload(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
    ).json()

    respuesta = client.delete(f"/lista-espera/{creada['id']}", headers=cookies_para(usuario))
    assert respuesta.status_code == 204

    mias = client.get("/lista-espera/mias", headers=cookies_para(usuario)).json()
    assert mias == []


def test_cancelar_de_otro_da_403(client, db):
    usuario_a, recurso = _usuario_y_recurso(db, username="lista_espera_c")
    usuario_b, _ = _usuario_y_recurso(db, username="lista_espera_d")
    creada = client.post(
        "/lista-espera", json=_payload(recurso.id, fecha_habilitada()), headers=cookies_para(usuario_a)
    ).json()

    respuesta = client.delete(f"/lista-espera/{creada['id']}", headers=cookies_para(usuario_b))
    assert respuesta.status_code == 403


def test_cancelar_inexistente_da_404(client, db):
    usuario, _ = _usuario_y_recurso(db)
    respuesta = client.delete("/lista-espera/999999", headers=cookies_para(usuario))
    assert respuesta.status_code == 404


def test_sin_sesion_da_401(client, db):
    _, recurso = _usuario_y_recurso(db)
    respuesta = client.post("/lista-espera", json=_payload(recurso.id, fecha_habilitada()))
    assert respuesta.status_code == 401
