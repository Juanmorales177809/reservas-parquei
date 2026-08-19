# -*- coding: utf-8 -*-
"""Pruebas de integración de ensayos (api/ensayos.py) — Fase 12E.

RN-005-like + 2 saltos para gestor + guard 409.
"""

from app.models.reserva_ensayo import ReservaEnsayo
from tests.conftest import (
    asociar_zona_recurso,
    crear_espacio,
    crear_recurso,
    crear_usuario,
    crear_zona,
    cookies_para,
    fecha_habilitada,
    payload_reserva_objetivos,
)


def _crear_ensayo_directo(db, *, zona, usuario, **kwargs):
    from app.models.ensayo import Ensayo

    ensayo = Ensayo(
        nombre=kwargs.get("nombre", "Ensayo de pruebas"),
        zona_id=zona.id,
        estado=kwargs.get("estado", "activo"),
        created_by=usuario.id,
        updated_by=usuario.id,
    )
    db.add(ensayo)
    db.commit()
    db.refresh(ensayo)
    return ensayo


class TestListarEnsayosVisibilidadPublica:
    def test_anonimo_ve_solo_ensayos_activos_de_zonas_y_espacios_activos(self, client, db):
        espacio_activo = crear_espacio(db, nombre="Esp Act Ens Anon")
        espacio_inactivo = crear_espacio(db, nombre="Esp Inact Ens Anon", estado="inactivo")
        admin = crear_usuario(db, username="admin_enslist1", email="admin_enslist1@example.com", rol="admin")
        zona_activa = crear_zona(db, espacio=espacio_activo, usuario=admin, nombre="Zona Act Ens")
        zona_inactiva = crear_zona(db, espacio=espacio_activo, usuario=admin, nombre="Zona Inact Ens", estado="inactivo")
        zona_esp_inactivo = crear_zona(db, espacio=espacio_inactivo, usuario=admin, nombre="Zona Esp Inact")
        _crear_ensayo_directo(db, zona=zona_activa, usuario=admin, nombre="Ens Visible")
        _crear_ensayo_directo(db, zona=zona_activa, usuario=admin, nombre="Ens Inactivo", estado="inactivo")
        _crear_ensayo_directo(db, zona=zona_inactiva, usuario=admin, nombre="Ens Zona Inact")
        _crear_ensayo_directo(db, zona=zona_esp_inactivo, usuario=admin, nombre="Ens Esp Inact")

        nombres = [e["nombre"] for e in client.get("/ensayos").json()]
        assert nombres == ["Ens Visible"]

    def test_usuario_ve_solo_activos(self, client, db):
        espacio = crear_espacio(db, nombre="Esp Act Ens Usuario")
        admin = crear_usuario(db, username="admin_enslist2", email="admin_enslist2@example.com", rol="admin")
        usuario = crear_usuario(db, username="user_enslist2", email="user_enslist2@example.com")
        zona = crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona Ens U")
        _crear_ensayo_directo(db, zona=zona, usuario=admin, nombre="Ens U Vis")
        _crear_ensayo_directo(db, zona=zona, usuario=admin, nombre="Ens U Inact", estado="mantenimiento")
        nombres = [e["nombre"] for e in client.get("/ensayos", headers=cookies_para(usuario)).json()]
        assert nombres == ["Ens U Vis"]

    def test_gestor_ve_inactivos(self, client, db):
        espacio = crear_espacio(db, nombre="Esp Ens Gestor")
        admin = crear_usuario(db, username="admin_enslist3", email="admin_enslist3@example.com", rol="admin")
        gestor = crear_usuario(db, username="gestor_enslist3", email="gestor_enslist3@example.com", rol="gestor", espacio_id=espacio.id)
        zona = crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona Ens Gestor")
        _crear_ensayo_directo(db, zona=zona, usuario=admin, nombre="Ens Gestor Oculta", estado="inactivo")
        nombres = [e["nombre"] for e in client.get("/ensayos", headers=cookies_para(gestor)).json()]
        assert "Ens Gestor Oculta" in nombres

    def test_admin_ve_todo(self, client, db):
        espacio = crear_espacio(db, nombre="Esp Ens Admin", estado="inactivo")
        admin = crear_usuario(db, username="admin_enslist4", email="admin_enslist4@example.com", rol="admin")
        zona = crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona Ens Admin")
        _crear_ensayo_directo(db, zona=zona, usuario=admin, nombre="Ens Solo Admin", estado="mantenimiento")
        nombres = [e["nombre"] for e in client.get("/ensayos", headers=cookies_para(admin)).json()]
        assert "Ens Solo Admin" in nombres

    def test_filtro_por_zona_id(self, client, db):
        espacio = crear_espacio(db, nombre="Esp Filtro Ens")
        admin = crear_usuario(db, username="admin_enslist5", email="admin_enslist5@example.com", rol="admin")
        zona_a = crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona F A Ens")
        zona_b = crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona F B Ens")
        _crear_ensayo_directo(db, zona=zona_a, usuario=admin, nombre="Ens A")
        _crear_ensayo_directo(db, zona=zona_b, usuario=admin, nombre="Ens B")
        nombres = [e["nombre"] for e in client.get("/ensayos", params={"zona_id": zona_a.id}).json()]
        assert nombres == ["Ens A"]


class TestCrearEnsayoAutorizacion:
    def test_usuario_no_puede_crear_ensayo(self, client, db):
        espacio = crear_espacio(db, nombre="Esp Crear Ens U")
        zona = crear_zona(db, espacio=espacio, usuario=crear_usuario(db, username="adm_cu1", email="adm_cu1@example.com", rol="admin"))
        usuario = crear_usuario(db, username="user_ensc1", email="user_ensc1@example.com")
        resp = client.post("/ensayos", json={"nombre": "Ens", "zona_id": zona.id}, headers=cookies_para(usuario))
        assert resp.status_code == 403

    def test_anonimo_no_puede_crear_ensayo(self, client, db):
        espacio = crear_espacio(db, nombre="Esp Crear Ens Anon")
        admin = crear_usuario(db, username="adm_ca1", email="adm_ca1@example.com", rol="admin")
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        resp = client.post("/ensayos", json={"nombre": "Ens", "zona_id": zona.id})
        assert resp.status_code == 401

    def test_admin_crea_ensayo(self, client, db):
        espacio = crear_espacio(db, nombre="Esp Crear Ens Admin")
        admin = crear_usuario(db, username="admin_ensc2", email="admin_ensc2@example.com", rol="admin")
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        resp = client.post("/ensayos", json={"nombre": "Ens Admin", "zona_id": zona.id}, headers=cookies_para(admin))
        assert resp.status_code == 201
        assert resp.json()["nombre"] == "Ens Admin"
        assert resp.json()["zona_id"] == zona.id

    def test_gestor_crea_ensayo_en_su_espacio(self, client, db):
        espacio = crear_espacio(db, nombre="Esp Crear Ens Gestor")
        admin = crear_usuario(db, username="admin_ensc3", email="admin_ensc3@example.com", rol="admin")
        gestor = crear_usuario(db, username="gestor_ensc3", email="gestor_ensc3@example.com", rol="gestor", espacio_id=espacio.id)
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        resp = client.post("/ensayos", json={"nombre": "Ens Gestor", "zona_id": zona.id}, headers=cookies_para(gestor))
        assert resp.status_code == 201

    def test_gestor_no_puede_crear_ensayo_en_otro_espacio(self, client, db):
        propio = crear_espacio(db, nombre="Esp Propio Ens")
        ajeno = crear_espacio(db, nombre="Esp Ajeno Ens")
        admin = crear_usuario(db, username="admin_ensc4", email="admin_ensc4@example.com", rol="admin")
        zona_ajena = crear_zona(db, espacio=ajeno, usuario=admin)
        gestor = crear_usuario(db, username="gestor_ensc4", email="gestor_ensc4@example.com", rol="gestor", espacio_id=propio.id)
        resp = client.post("/ensayos", json={"nombre": "Ens Ajena", "zona_id": zona_ajena.id}, headers=cookies_para(gestor))
        assert resp.status_code == 403

    def test_zona_inexistente_da_404(self, client, db):
        admin = crear_usuario(db, username="admin_ensc5", email="admin_ensc5@example.com", rol="admin")
        resp = client.post("/ensayos", json={"nombre": "Ens", "zona_id": 999999}, headers=cookies_para(admin))
        assert resp.status_code == 404


class TestActualizarEnsayoDosSaltos:
    def test_gestor_no_puede_editar_ensayo_de_otro_espacio(self, client, db):
        propio = crear_espacio(db, nombre="Esp Propio Upd Ens")
        ajeno = crear_espacio(db, nombre="Esp Ajeno Upd Ens")
        admin = crear_usuario(db, username="admin_ensu1", email="admin_ensu1@example.com", rol="admin")
        gestor = crear_usuario(db, username="gestor_ensu1", email="gestor_ensu1@example.com", rol="gestor", espacio_id=propio.id)
        zona_ajena = crear_zona(db, espacio=ajeno, usuario=admin)
        ensayo = _crear_ensayo_directo(db, zona=zona_ajena, usuario=admin)
        resp = client.put(f"/ensayos/{ensayo.id}", json={"nombre": "Hack"}, headers=cookies_para(gestor))
        assert resp.status_code == 403

    def test_gestor_no_puede_mover_ensayo_fuera_de_su_espacio(self, client, db):
        propio = crear_espacio(db, nombre="Esp Propio Mover Ens")
        destino = crear_espacio(db, nombre="Esp Destino Mover Ens")
        admin = crear_usuario(db, username="admin_ensu2", email="admin_ensu2@example.com", rol="admin")
        gestor = crear_usuario(db, username="gestor_ensu2", email="gestor_ensu2@example.com", rol="gestor", espacio_id=propio.id)
        zona_propia = crear_zona(db, espacio=propio, usuario=admin)
        zona_destino = crear_zona(db, espacio=destino, usuario=admin)
        ensayo = _crear_ensayo_directo(db, zona=zona_propia, usuario=admin)
        resp = client.put(f"/ensayos/{ensayo.id}", json={"zona_id": zona_destino.id}, headers=cookies_para(gestor))
        assert resp.status_code == 200
        assert resp.json()["zona_id"] == propio.id or resp.json()["zona_id"] == zona_propia.id

    def test_admin_actualiza_ensayo(self, client, db):
        espacio = crear_espacio(db, nombre="Esp Upd Admin Ens")
        admin = crear_usuario(db, username="admin_ensu3", email="admin_ensu3@example.com", rol="admin")
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        ensayo = _crear_ensayo_directo(db, zona=zona, usuario=admin, nombre="Original")
        resp = client.put(f"/ensayos/{ensayo.id}", json={"nombre": "Renombrado"}, headers=cookies_para(admin))
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Renombrado"


class TestEliminarEnsayoGuard409:
    def test_eliminar_ensayo_referenciado_bloquea_409(self, client, db):
        espacio = crear_espacio(db, nombre="Esp Del Ens 409", modalidad_reserva="zonas")
        admin = crear_usuario(db, username="admin_ensd1", email="admin_ensd1@example.com", rol="admin")
        usuario = crear_usuario(db, username="user_ensd1", email="user_ensd1@example.com")
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        asociar_zona_recurso(db, zona, recurso)
        ensayo = _crear_ensayo_directo(db, zona=zona, usuario=admin)
        # crear reserva que referencia el ensayo
        resp_res = client.post(
            "/reservas",
            json=payload_reserva_objetivos(zona_ids=[zona.id], ensayo_ids=[ensayo.id], fecha=fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert resp_res.status_code == 201
        resp = client.delete(f"/ensayos/{ensayo.id}", headers=cookies_para(admin))
        assert resp.status_code == 409

    def test_eliminar_ensayo_no_referenciado_ok(self, client, db):
        espacio = crear_espacio(db, nombre="Esp Del Ens OK")
        admin = crear_usuario(db, username="admin_ensd2", email="admin_ensd2@example.com", rol="admin")
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        ensayo = _crear_ensayo_directo(db, zona=zona, usuario=admin)
        resp = client.delete(f"/ensayos/{ensayo.id}", headers=cookies_para(admin))
        assert resp.status_code == 204

    def test_gestor_no_puede_eliminar_ensayo_de_otro_espacio(self, client, db):
        propio = crear_espacio(db, nombre="Esp Propio Del Ens")
        ajeno = crear_espacio(db, nombre="Esp Ajeno Del Ens")
        admin = crear_usuario(db, username="admin_ensd3", email="admin_ensd3@example.com", rol="admin")
        gestor = crear_usuario(db, username="gestor_ensd3", email="gestor_ensd3@example.com", rol="gestor", espacio_id=propio.id)
        zona_ajena = crear_zona(db, espacio=ajeno, usuario=admin)
        ensayo = _crear_ensayo_directo(db, zona=zona_ajena, usuario=admin)
        resp = client.delete(f"/ensayos/{ensayo.id}", headers=cookies_para(gestor))
        assert resp.status_code == 403
