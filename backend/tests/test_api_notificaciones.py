# -*- coding: utf-8 -*-
"""Pruebas de integración de notificaciones (api/notificaciones.py).

Reglas cubiertas:
- Una reserva esperando notifica a los gestores del espacio (Pendiente).
- La aprobación notifica al solicitante (Aprobada).
- Conteo de no leídas, marcar una y marcar todas.
"""

from tests.conftest import (
    asociar_zona_recurso,
    crear_espacio,
    crear_recurso,
    crear_usuario,
    crear_zona,
    fecha_habilitada,
    cookies_para,
    payload_reserva,
    payload_reserva_objetivos,
)


def _reserva_pendiente(client, db):
    espacio = crear_espacio(db, nombre="Sala Notif")
    gestor = crear_usuario(
        db, username="gestor_notif", email="gestor_notif@example.com",
        rol="gestor", espacio_id=espacio.id,
    )
    solicitante = crear_usuario(db, username="solicitante", email="solicitante@example.com")
    recurso = crear_recurso(db, espacio=espacio, usuario=solicitante)
    creada = client.post(
        "/reservas",
        json=payload_reserva(recurso.id, fecha_habilitada()),
        headers=cookies_para(solicitante),
    )
    return gestor, solicitante, creada


def test_reserva_pendiente_notifica_al_gestor(client, db):
    gestor, _, creada = _reserva_pendiente(client, db)
    assert creada.status_code == 201
    respuesta = client.get("/notificaciones", headers=cookies_para(gestor))
    assert respuesta.status_code == 200
    items = respuesta.json()
    assert len(items) == 1
    assert items[0]["tipo"] == "Pendiente"
    assert items[0]["leida"] is False


def test_conteo_sin_leer(client, db):
    gestor, _, _ = _reserva_pendiente(client, db)
    respuesta = client.get(
        "/notificaciones/sin-leer/count", headers=cookies_para(gestor)
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["cantidad"] == 1


def test_marcar_una_como_leida(client, db):
    gestor, _, _ = _reserva_pendiente(client, db)
    notificacion = client.get(
        "/notificaciones", headers=cookies_para(gestor)
    ).json()[0]
    respuesta = client.patch(
        f"/notificaciones/{notificacion['id']}/leer", headers=cookies_para(gestor)
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["leida"] is True
    conteo = client.get(
        "/notificaciones/sin-leer/count", headers=cookies_para(gestor)
    ).json()
    assert conteo["cantidad"] == 0


def test_marcar_todas_como_leidas(client, db):
    gestor, _, _ = _reserva_pendiente(client, db)
    respuesta = client.patch(
        "/notificaciones/leer-todas", headers=cookies_para(gestor)
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["cantidad"] == 1
    conteo = client.get(
        "/notificaciones/sin-leer/count", headers=cookies_para(gestor)
    ).json()
    assert conteo["cantidad"] == 0


def test_aprobacion_notifica_al_solicitante(client, db):
    gestor, solicitante, creada = _reserva_pendiente(client, db)
    respuesta = client.put(
        f"/reservas/{creada.json()['id']}/estado",
        json={"nuevo_estado": "aprobada"},
        headers=cookies_para(gestor),
    )
    assert respuesta.status_code == 200
    items = client.get("/notificaciones", headers=cookies_para(solicitante)).json()
    assert len(items) == 1
    assert items[0]["tipo"] == "Aprobada"


def test_cancelacion_por_usuario_notifica_al_gestor_sin_decir_tu_reserva(client, db):
    """Gap real: el gestor no es dueño de la reserva que el usuario canceló,
    así que el mensaje no puede ser el mismo "Tu reserva..." que recibe el
    solicitante cuando es el gestor quien cambia el estado."""
    gestor, solicitante, creada = _reserva_pendiente(client, db)
    reserva_id = creada.json()["id"]
    client.put(
        f"/reservas/{reserva_id}/estado",
        json={"nuevo_estado": "aprobada"},
        headers=cookies_para(gestor),
    )
    client.patch("/notificaciones/leer-todas", headers=cookies_para(gestor))

    respuesta = client.put(f"/reservas/{reserva_id}/cancelar", headers=cookies_para(solicitante))
    assert respuesta.status_code == 200

    items = client.get("/notificaciones", headers=cookies_para(gestor)).json()
    cancelada = next(item for item in items if item["tipo"] == "Cancelada")
    assert cancelada["mensaje"].startswith("Se canceló la reserva")
    assert "Tu reserva" not in cancelada["mensaje"]


def test_reserva_de_zona_notifica_la_zona(client, db):
    """Fase 12C-6: una reserva por zona menciona la zona en el mensaje al
    gestor, no el recurso ancla."""
    espacio = crear_espacio(db, nombre="Sala Notif Zona", modalidad_reserva="zonas")
    gestor = crear_usuario(
        db, username="gestor_notif_zona", email="gestor_notif_zona@example.com",
        rol="gestor", espacio_id=espacio.id,
    )
    solicitante = crear_usuario(db, username="solicitante_zona", email="solicitante_zona@example.com")
    recurso = crear_recurso(db, espacio=espacio, usuario=solicitante, nombre="Recurso Zona")
    zona = crear_zona(db, espacio=espacio, usuario=solicitante, nombre="Zona Notif")
    asociar_zona_recurso(db, zona, recurso)

    creada = client.post(
        "/reservas",
        json=payload_reserva_objetivos(zona_ids=[zona.id], fecha=fecha_habilitada()),
        headers=cookies_para(solicitante),
    )
    assert creada.status_code == 201

    items = client.get("/notificaciones", headers=cookies_para(gestor)).json()
    assert len(items) == 1
    assert "Zona Notif" in items[0]["mensaje"]


def test_reserva_de_multiples_recursos_menciona_todos_en_el_mensaje(client, db):
    """Fase 12C-4e-lectores: una reserva de varios recursos directos (sin
    zona) menciona TODOS los recursos en el mensaje -- antes de esta
    subfase, el mensaje solo mostraba el recurso ancla (el de menor id),
    ocultando los demás."""
    espacio = crear_espacio(db, nombre="Sala Notif Multi Recurso", modalidad_reserva="mixto")
    gestor = crear_usuario(
        db, username="gestor_notif_multi", email="gestor_notif_multi@example.com",
        rol="gestor", espacio_id=espacio.id,
    )
    solicitante = crear_usuario(db, username="solicitante_multi", email="solicitante_multi@example.com")
    r1 = crear_recurso(db, espacio=espacio, usuario=solicitante, nombre="Proyector Notif")
    r2 = crear_recurso(db, espacio=espacio, usuario=solicitante, nombre="Cámara Notif")

    creada = client.post(
        "/reservas",
        json=payload_reserva_objetivos(recurso_ids=[r1.id, r2.id], fecha=fecha_habilitada()),
        headers=cookies_para(solicitante),
    )
    assert creada.status_code == 201

    items = client.get("/notificaciones", headers=cookies_para(gestor)).json()
    assert len(items) == 1
    assert "Proyector Notif" in items[0]["mensaje"]
    assert "Cámara Notif" in items[0]["mensaje"]
