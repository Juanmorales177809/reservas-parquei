# -*- coding: utf-8 -*-
"""Pruebas de integración de administración de personal (api/personal.py).

Contraparte de `test_api_usuarios.py` desde la separación en dos tablas
(`personal` para admin/gestor, `usuarios` para rol usuario -- ver
`~/.claude/plans/dazzling-wobbling-zebra.md`). Cubre lo que antes vivía en
`test_api_usuarios.py` para rol admin/gestor (RN-003 laboratorio del gestor,
protección del último admin, reenviar invitación) más lo nuevo: la
promoción de una cuenta `usuario` existente a `personal`.
"""

import uuid

import pytest

from app.models import CorreoSaliente, Notificacion, Personal, Usuario
from app.services.supabase_admin import SupabaseAdminError
from tests.conftest import cookies_para, crear_laboratorio, crear_usuario


@pytest.fixture(autouse=True)
def _supabase_invitar_mockeado(monkeypatch):
    monkeypatch.setattr(
        "app.api.personal.crear_usuario_y_generar_link",
        lambda email: (uuid.uuid4(), f"https://ejemplo.supabase.co/auth/v1/verify?token=fake&type=invite&email={email}"),
    )


def _admin(db):
    return crear_usuario(db, username="admin_per", email="admin_per@example.com", rol="admin")


def test_crear_gestor_sin_espacio_da_400(client, db):
    admin = _admin(db)
    payload = {"username": "gestor_solo", "email": "gestor_solo@example.com", "rol": "gestor"}
    respuesta = client.post("/personal", json=payload, headers=cookies_para(admin))
    assert respuesta.status_code == 400


def test_crear_gestor_con_espacio(client, db):
    admin = _admin(db)
    laboratorio = crear_laboratorio(db, nombre="Sala Gestores")
    payload = {
        "username": "gestor_ok",
        "email": "gestor_ok@example.com",
        "rol": "gestor",
        "laboratorio_id": laboratorio.id,
    }
    respuesta = client.post("/personal", json=payload, headers=cookies_para(admin))
    assert respuesta.status_code == 201
    assert respuesta.json()["laboratorio"]["nombre"] == "Sala Gestores"


def test_crear_personal_rechaza_rol_usuario(client, db):
    """`POST /personal` es admin/gestor únicamente -- usar `POST /usuarios`
    para rol usuario."""
    admin = _admin(db)
    payload = {"username": "no_puede", "email": "no_puede@example.com", "rol": "usuario"}
    respuesta = client.post("/personal", json=payload, headers=cookies_para(admin))
    assert respuesta.status_code == 422


def test_crear_personal_solo_admin(client, db):
    gestor = crear_usuario(db, username="gestor_no_crea", email="gestor_no_crea@example.com", rol="gestor")
    payload = {"username": "otro", "email": "otro@example.com", "rol": "gestor", "laboratorio_id": 1}
    respuesta = client.post("/personal", json=payload, headers=cookies_para(gestor))
    assert respuesta.status_code == 403


def test_admin_no_puede_eliminarse_a_si_mismo(client, db):
    admin = _admin(db)
    respuesta = client.delete(f"/personal/{admin.id}", headers=cookies_para(admin))
    assert respuesta.status_code == 409


def test_admin_no_puede_degradarse_a_si_mismo(client, db):
    """Degradar (rol=usuario en PUT /personal/{id}) es una eliminación de
    `personal` desde el punto de vista de `proteger_administradores` --
    mismo 409 que eliminar."""
    admin = _admin(db)
    respuesta = client.put(f"/personal/{admin.id}", json={"rol": "usuario"}, headers=cookies_para(admin))
    assert respuesta.status_code == 409


def test_ultimo_admin_no_puede_eliminarse(client, db, monkeypatch):
    monkeypatch.setattr("app.api.personal.eliminar_usuario_supabase", lambda supabase_id: None)
    admin = _admin(db)
    otro_admin = crear_usuario(db, username="admin2_per", email="admin2_per@example.com", rol="admin")
    respuesta = client.delete(f"/personal/{admin.id}", headers=cookies_para(otro_admin))
    assert respuesta.status_code == 204
    # Ya no queda más que un admin -- eliminarlo (a sí mismo) da 409 antes
    # de siquiera llegar al conteo, por la regla de "no tu propia cuenta".
    respuesta2 = client.delete(f"/personal/{otro_admin.id}", headers=cookies_para(otro_admin))
    assert respuesta2.status_code == 409


def test_listar_personal_solo_admin(client, db):
    usuario = crear_usuario(db, username="user_no_ve_personal", email="user_no_ve_personal@example.com")
    admin = _admin(db)
    crear_usuario(db, username="gestor_listado", email="gestor_listado@example.com", rol="gestor")
    assert client.get("/personal", headers=cookies_para(usuario)).status_code == 403
    respuesta = client.get("/personal", headers=cookies_para(admin))
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 2


def test_eliminar_personal_borra_tambien_su_identidad_de_supabase(client, db, monkeypatch):
    admin = _admin(db)
    objetivo = crear_usuario(db, username="gestor_a_borrar", email="gestor_a_borrar@example.com", rol="gestor")

    llamadas = []
    monkeypatch.setattr("app.api.personal.eliminar_usuario_supabase", lambda supabase_id: llamadas.append(supabase_id))

    respuesta = client.delete(f"/personal/{objetivo.id}", headers=cookies_para(admin))

    assert respuesta.status_code == 204
    assert llamadas == [objetivo.supabase_id]
    assert db.query(Personal).filter(Personal.id == objetivo.id).first() is None


def test_eliminar_personal_si_supabase_falla_da_502_y_no_borra_la_fila_local(client, db, monkeypatch):
    admin = _admin(db)
    objetivo = crear_usuario(db, username="gestor_no_se_borra", email="gestor_no_se_borra@example.com", rol="gestor")

    def _falla(supabase_id):
        raise SupabaseAdminError("simulado: Supabase Cloud no responde")

    monkeypatch.setattr("app.api.personal.eliminar_usuario_supabase", _falla)

    respuesta = client.delete(f"/personal/{objetivo.id}", headers=cookies_para(admin))

    assert respuesta.status_code == 502
    assert db.query(Personal).filter(Personal.id == objetivo.id).first() is not None


def test_reenviar_invitacion_devuelve_el_link(client, db, monkeypatch):
    admin = _admin(db)
    objetivo = crear_usuario(db, username="gestor_a_reinvitar", email="gestor_a_reinvitar@example.com", rol="gestor")

    monkeypatch.setattr(
        "app.api.personal.generar_link_invitacion",
        lambda email: f"https://ejemplo.supabase.co/auth/v1/verify?token=fake&type=invite&email={email}",
    )

    respuesta = client.post(f"/personal/{objetivo.id}/reenviar-invitacion", headers=cookies_para(admin))

    assert respuesta.status_code == 200
    data = respuesta.json()
    assert "gestor_a_reinvitar@example.com" in data["link"]
    assert data["correo_enviado"] is False

    correo = db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == "gestor_a_reinvitar@example.com").one()
    assert correo.es_html is True


def test_actualizar_rol_de_gestor_a_admin_dentro_de_personal(client, db):
    admin = _admin(db)
    gestor = crear_usuario(db, username="gestor_a_ascender", email="gestor_a_ascender@example.com", rol="gestor")

    respuesta = client.put(f"/personal/{gestor.id}", json={"rol": "admin"}, headers=cookies_para(admin))

    assert respuesta.status_code == 200
    assert respuesta.json()["rol"] == "admin"


def test_admin_puede_ajustar_recibir_correos_de_un_gestor(client, db):
    """Correo opcional por persona (2026-09-03): un admin puede tocar la
    preferencia de otra cuenta de personal, no solo la propia (a diferencia
    de PUT /usuarios/me, que es self-service)."""
    admin = _admin(db)
    laboratorio = crear_laboratorio(db, nombre="Sala Correo Pref Personal")
    gestor = crear_usuario(
        db, username="gestor_correo_pref", email="gestor_correo_pref@example.com", rol="gestor", laboratorio_id=laboratorio.id
    )
    assert gestor.recibir_correos is True

    respuesta = client.put(f"/personal/{gestor.id}", json={"recibir_correos": False}, headers=cookies_para(admin))

    assert respuesta.status_code == 200
    assert respuesta.json()["recibir_correos"] is False
    db.refresh(gestor)
    assert gestor.recibir_correos is False


class TestPromoverUsuarioAPersonal:
    def test_promover_usuario_existente_a_gestor(self, client, db):
        admin = _admin(db)
        laboratorio = crear_laboratorio(db, nombre="Sala Ascenso")
        usuario = crear_usuario(db, username="usuario_a_ascender", email="usuario_a_ascender@example.com")
        supabase_id_original = usuario.supabase_id

        respuesta = client.post(
            f"/personal/promover/{usuario.id}",
            json={"username": usuario.username, "email": usuario.email, "rol": "gestor", "laboratorio_id": laboratorio.id},
            headers=cookies_para(admin),
        )

        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["rol"] == "gestor"
        assert cuerpo["laboratorio"]["nombre"] == "Sala Ascenso"
        # El id CAMBIA (personal/usuarios tienen secuencias independientes
        # que pueden colisionar, ver services/migrar_actor.py) -- lo que se
        # preserva es la identidad de Supabase y el resto de los datos.
        assert cuerpo["id"] != usuario.id
        personal = db.query(Personal).filter(Personal.id == cuerpo["id"]).first()
        assert personal is not None
        assert personal.supabase_id == supabase_id_original
        assert db.query(Usuario).filter(Usuario.id == usuario.id).first() is None

    def test_promover_repunta_reservas_notificaciones_y_auditoria_existentes(self, client, db):
        from app.models import ControlCambio, Reserva
        from app.services.actores import columnas_actor
        from tests.conftest import crear_recurso, fecha_habilitada
        from datetime import time as time_t

        admin = _admin(db)
        laboratorio = crear_laboratorio(db, nombre="Sala Repunte")
        usuario = crear_usuario(db, username="usuario_con_historial", email="usuario_con_historial@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)

        reserva = Reserva(
            **columnas_actor(usuario),
            laboratorio_id=laboratorio.id,
            recurso_id=recurso.id,
            fecha=fecha_habilitada(),
            hora_inicio=time_t(8, 0),
            hora_fin=time_t(9, 0),
            estado="esperando",
            asistentes=1,
        )
        db.add(reserva)
        db.add(Notificacion(**columnas_actor(usuario), reserva_id=None, tipo="Pendiente"))
        db.add(ControlCambio(**columnas_actor(usuario), accion="crear", entidad="reserva", entidad_id=1, descripcion="hist"))
        db.commit()

        respuesta = client.post(
            f"/personal/promover/{usuario.id}",
            json={"username": usuario.username, "email": usuario.email, "rol": "gestor", "laboratorio_id": laboratorio.id},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 200
        nuevo_id = respuesta.json()["id"]

        db.expire_all()
        reserva_movida = db.query(Reserva).filter(Reserva.id == reserva.id).one()
        assert reserva_movida.usuario_id is None
        assert reserva_movida.personal_id == nuevo_id
        notif = db.query(Notificacion).filter(Notificacion.tipo == "Pendiente").one()
        assert notif.usuario_id is None
        assert notif.personal_id == nuevo_id
