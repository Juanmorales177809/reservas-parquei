# -*- coding: utf-8 -*-
"""Pruebas de gestión de la serie completa de una reserva recurrente
(2026-08-29, ronda 2): `GET /reservas/serie/{serie_id}` y
`PUT /reservas/serie/{serie_id}/cancelar`.
"""

from datetime import timedelta

from tests.conftest import cookies_para, crear_espacio, crear_recurso, crear_usuario, fecha_habilitada, payload_reserva


def _setup(db, *, rol="gestor", es_gestor_del_espacio=True, nombre="Espacio Serie Gestion"):
    espacio = crear_espacio(db, nombre=nombre)
    usuario = crear_usuario(
        db,
        username=f"serie_gestion_{nombre.replace(' ', '')}",
        email=f"serie-gestion-{nombre.replace(' ', '')}@example.com",
        rol=rol,
        espacio_id=espacio.id if (rol == "gestor" and es_gestor_del_espacio) else None,
    )
    recurso = crear_recurso(db, espacio=espacio, usuario=usuario, nombre=f"Recurso {nombre}")
    return usuario, espacio, recurso


def _crear_serie(client, usuario, recurso, fecha, ocurrencias=3):
    payload = payload_reserva(recurso.id, fecha)
    payload["repetir_semanas"] = 1
    payload["numero_ocurrencias"] = ocurrencias
    respuesta = client.post("/reservas", json=payload, headers=cookies_para(usuario))
    assert respuesta.status_code == 201
    return respuesta.json()


def test_reserva_no_recurrente_tiene_serie_id_null(client, db):
    usuario, _, recurso = _setup(db, nombre="Espacio Sin Serie")
    respuesta = client.post("/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario))
    assert respuesta.json()["serie_id"] is None


def test_ocurrencias_de_una_serie_comparten_serie_id(client, db):
    usuario, _, recurso = _setup(db, nombre="Espacio Comparte Serie")
    cuerpo = _crear_serie(client, usuario, recurso, fecha_habilitada())
    serie_ids = {r["serie_id"] for r in cuerpo["creadas"]}
    assert len(serie_ids) == 1
    assert None not in serie_ids


def test_listar_serie_devuelve_las_propias_ocurrencias(client, db):
    usuario, _, recurso = _setup(db, nombre="Espacio Listar Serie")
    cuerpo = _crear_serie(client, usuario, recurso, fecha_habilitada())
    serie_id = cuerpo["creadas"][0]["serie_id"]

    respuesta = client.get(f"/reservas/serie/{serie_id}", headers=cookies_para(usuario))

    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 3


def test_listar_serie_no_devuelve_las_de_otra_persona(client, db):
    usuario, _, recurso = _setup(db, nombre="Espacio Serie Ajena")
    otro, _, _ = _setup(db, nombre="Espacio Serie Ajena Otro")
    cuerpo = _crear_serie(client, usuario, recurso, fecha_habilitada())
    serie_id = cuerpo["creadas"][0]["serie_id"]

    respuesta = client.get(f"/reservas/serie/{serie_id}", headers=cookies_para(otro))

    assert respuesta.json() == []


def test_cancelar_serie_cancela_todas_las_aprobadas(client, db):
    usuario, _, recurso = _setup(db, nombre="Espacio Cancelar Serie")
    cuerpo = _crear_serie(client, usuario, recurso, fecha_habilitada())
    serie_id = cuerpo["creadas"][0]["serie_id"]
    assert all(r["estado"] == "aprobada" for r in cuerpo["creadas"])

    respuesta = client.put(f"/reservas/serie/{serie_id}/cancelar", headers=cookies_para(usuario))

    assert respuesta.status_code == 200
    resultado = respuesta.json()
    assert len(resultado["canceladas"]) == 3
    assert resultado["omitidas"] == []
    assert all(r["estado"] == "cancelada" for r in resultado["canceladas"])


def test_cancelar_serie_mejor_esfuerzo_si_una_ya_esta_cancelada(client, db):
    usuario, _, recurso = _setup(db, nombre="Espacio Cancelar Parcial")
    cuerpo = _crear_serie(client, usuario, recurso, fecha_habilitada())
    serie_id = cuerpo["creadas"][0]["serie_id"]
    primera_id = cuerpo["creadas"][0]["id"]
    client.put(f"/reservas/{primera_id}/cancelar", headers=cookies_para(usuario))

    respuesta = client.put(f"/reservas/serie/{serie_id}/cancelar", headers=cookies_para(usuario))

    resultado = respuesta.json()
    assert len(resultado["canceladas"]) == 2
    assert len(resultado["omitidas"]) == 1
    assert resultado["omitidas"][0]["reserva_id"] == primera_id
