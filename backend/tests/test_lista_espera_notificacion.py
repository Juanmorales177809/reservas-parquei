# -*- coding: utf-8 -*-
"""Pruebas del gancho real: al liberarse un recurso/horario (rechazo,
cancelación o borrado de la reserva que lo ocupaba), se notifica a la
primera persona en la lista de espera para ese mismo recurso/horario
(`services/reservas.py::_notificar_lista_espera_liberados`, FIFO simple --
ver `~/.claude/plans/dazzling-wobbling-zebra.md`).

`settings.email_enabled` es `False` por defecto en el entorno de tests
(igual que en `test_correo_saliente.py`): `encolar_correo` sigue
encolando el `CorreoSaliente` (`estado="pendiente"`) aunque no se llegue a
enviar de verdad -- suficiente para verificar que el gancho corrió.
"""

from app.models import CorreoSaliente

from tests.conftest import cookies_para, crear_laboratorio, crear_recurso, crear_usuario, fecha_habilitada, payload_reserva


def _anotar_en_espera(client, usuario, recurso, fecha, hora_inicio="08:00", hora_fin="10:00"):
    respuesta = client.post(
        "/lista-espera",
        json={"recurso_id": recurso.id, "fecha": fecha.isoformat(), "hora_inicio": hora_inicio, "hora_fin": hora_fin},
        headers=cookies_para(usuario),
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def _correo_cupo_disponible_para(db, email):
    return (
        db.query(CorreoSaliente)
        .filter(CorreoSaliente.destinatario == email, CorreoSaliente.asunto == "Se liberó un cupo que estabas esperando")
        .all()
    )


def test_gestor_cancela_su_reserva_notifica_al_primero_en_espera(client, db):
    laboratorio = crear_laboratorio(db, nombre="Laboratorio Cancelar")
    gestor = crear_usuario(db, username="gestor_cancela", email="gestor_cancela@example.com", rol="gestor", laboratorio_id=laboratorio.id)
    recurso = crear_recurso(db, laboratorio=laboratorio, usuario=gestor, nombre="Recurso Cancelar")
    esperando = crear_usuario(db, username="espera_cancela", email="espera_cancela@example.com", rol="usuario")
    fecha = fecha_habilitada()

    creada = client.post("/reservas", json=payload_reserva(recurso.id, fecha), headers=cookies_para(gestor))
    assert creada.json()["estado"] == "aprobada"
    _anotar_en_espera(client, esperando, recurso, fecha)

    respuesta = client.put(f"/reservas/{creada.json()['id']}/cancelar", headers=cookies_para(gestor))
    assert respuesta.status_code == 200

    assert len(_correo_cupo_disponible_para(db, esperando.email)) == 1
    # La entrada notificada sigue visible en /mias (no se oculta como una
    # cancelada) para que la persona vea el aviso "se liberó" en la app.
    mias = client.get("/lista-espera/mias", headers=cookies_para(esperando)).json()
    assert mias[0]["estado"] == "notificada"


def test_admin_rechaza_reserva_notifica_al_primero_en_espera(client, db):
    laboratorio = crear_laboratorio(db, nombre="Laboratorio Rechazar")
    admin = crear_usuario(db, username="admin_rechaza", email="admin_rechaza@example.com", rol="admin")
    dueno = crear_usuario(db, username="dueno_rechaza", email="dueno_rechaza@example.com", rol="usuario")
    esperando = crear_usuario(db, username="espera_rechaza", email="espera_rechaza@example.com", rol="usuario")
    recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso Rechazar")
    fecha = fecha_habilitada()

    creada = client.post("/reservas", json=payload_reserva(recurso.id, fecha), headers=cookies_para(dueno))
    assert creada.json()["estado"] == "esperando"
    _anotar_en_espera(client, esperando, recurso, fecha)

    respuesta = client.put(
        f"/reservas/{creada.json()['id']}/estado",
        json={"nuevo_estado": "rechazada", "motivo": "No disponible"},
        headers=cookies_para(admin),
    )
    assert respuesta.status_code == 200

    assert len(_correo_cupo_disponible_para(db, esperando.email)) == 1


def test_admin_elimina_reserva_notifica_al_primero_en_espera(client, db):
    laboratorio = crear_laboratorio(db, nombre="Laboratorio Eliminar")
    admin = crear_usuario(db, username="admin_elimina_le", email="admin_elimina_le@example.com", rol="admin")
    dueno = crear_usuario(db, username="dueno_elimina_le", email="dueno_elimina_le@example.com", rol="usuario")
    esperando = crear_usuario(db, username="espera_elimina", email="espera_elimina@example.com", rol="usuario")
    recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso Eliminar")
    fecha = fecha_habilitada()

    creada = client.post("/reservas", json=payload_reserva(recurso.id, fecha), headers=cookies_para(dueno))
    _anotar_en_espera(client, esperando, recurso, fecha)

    respuesta = client.delete(f"/reservas/{creada.json()['id']}", headers=cookies_para(admin))
    assert respuesta.status_code == 204

    assert len(_correo_cupo_disponible_para(db, esperando.email)) == 1


def test_solo_notifica_al_primero_en_anotarse_fifo(client, db):
    laboratorio = crear_laboratorio(db, nombre="Laboratorio FIFO")
    gestor = crear_usuario(db, username="gestor_fifo", email="gestor_fifo@example.com", rol="gestor", laboratorio_id=laboratorio.id)
    primero = crear_usuario(db, username="primero_fifo", email="primero_fifo@example.com", rol="usuario")
    segundo = crear_usuario(db, username="segundo_fifo", email="segundo_fifo@example.com", rol="usuario")
    recurso = crear_recurso(db, laboratorio=laboratorio, usuario=gestor, nombre="Recurso FIFO")
    fecha = fecha_habilitada()

    creada = client.post("/reservas", json=payload_reserva(recurso.id, fecha), headers=cookies_para(gestor))
    _anotar_en_espera(client, primero, recurso, fecha)
    _anotar_en_espera(client, segundo, recurso, fecha)

    client.put(f"/reservas/{creada.json()['id']}/cancelar", headers=cookies_para(gestor))

    assert len(_correo_cupo_disponible_para(db, primero.email)) == 1
    assert len(_correo_cupo_disponible_para(db, segundo.email)) == 0


def test_horario_distinto_no_recibe_el_aviso(client, db):
    laboratorio = crear_laboratorio(db, nombre="Laboratorio Otro Horario")
    gestor = crear_usuario(db, username="gestor_otro_h", email="gestor_otro_h@example.com", rol="gestor", laboratorio_id=laboratorio.id)
    esperando = crear_usuario(db, username="espera_otro_h", email="espera_otro_h@example.com", rol="usuario")
    recurso = crear_recurso(db, laboratorio=laboratorio, usuario=gestor, nombre="Recurso Otro Horario")
    fecha = fecha_habilitada()

    creada = client.post("/reservas", json=payload_reserva(recurso.id, fecha), headers=cookies_para(gestor))
    # Anotado a un horario que NO se solapa con el que se libera (08:00-10:00).
    _anotar_en_espera(client, esperando, recurso, fecha, hora_inicio="14:00", hora_fin="16:00")

    client.put(f"/reservas/{creada.json()['id']}/cancelar", headers=cookies_para(gestor))

    assert len(_correo_cupo_disponible_para(db, esperando.email)) == 0
