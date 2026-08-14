# -*- coding: utf-8 -*-
"""Pruebas de integración de espacios y disponibilidad (api/espacios.py).

Reglas cubiertas:
- Listado público de espacios sin autenticación.
- Creación/eliminación de espacios restringida al rol admin.
- RN-005 (contexto): la disponibilidad refleja el estado del espacio.
- Protección de integridad: un espacio con dependencias no se elimina.
"""

from tests.conftest import (
    crear_espacio,
    crear_recurso,
    crear_usuario,
    fecha_habilitada,
    headers_para,
    proximo_domingo,
)


def test_listar_espacios_es_publico(client):
    respuesta = client.get("/espacios")
    assert respuesta.status_code == 200
    assert isinstance(respuesta.json(), list)


def test_crear_espacio_solo_admin(client, db):
    usuario = crear_usuario(db, username="user_esp", email="user_esp@test.com")
    admin = crear_usuario(db, username="admin_esp", email="admin_esp@test.com", rol="admin")
    payload = {"nombre": "Sala Nueva", "ubicacion": "Piso 2", "capacidad": 15, "estado": "activo"}
    assert (
        client.post("/espacios", json=payload, headers=headers_para(usuario)).status_code
        == 403
    )
    respuesta = client.post("/espacios", json=payload, headers=headers_para(admin))
    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] == "Sala Nueva"


def test_eliminar_espacio_sin_dependencias(client, db):
    admin = crear_usuario(db, username="admin_del", email="admin_del@test.com", rol="admin")
    espacio = crear_espacio(db, nombre="Sala Borrable")
    respuesta = client.delete(f"/espacios/{espacio.id}", headers=headers_para(admin))
    assert respuesta.status_code == 204


def test_eliminar_espacio_con_dependencias_da_409(client, db):
    admin = crear_usuario(db, username="admin_dep", email="admin_dep@test.com", rol="admin")
    espacio = crear_espacio(db, nombre="Sala Con Recursos")
    crear_recurso(db, espacio=espacio, usuario=admin)
    respuesta = client.delete(f"/espacios/{espacio.id}", headers=headers_para(admin))
    assert respuesta.status_code == 409


class TestRN005ListadoPublico:
    def test_espacio_activo_visible_sin_token(self, client, db):
        crear_espacio(db, nombre="Sala Activa")
        nombres = [e["nombre"] for e in client.get("/espacios").json()]
        assert "Sala Activa" in nombres

    def test_espacio_inactivo_no_visible_sin_token(self, client, db):
        crear_espacio(db, nombre="Sala Inactiva", estado="inactivo")
        nombres = [e["nombre"] for e in client.get("/espacios").json()]
        assert "Sala Inactiva" not in nombres

    def test_espacio_mantenimiento_no_visible_sin_token(self, client, db):
        crear_espacio(db, nombre="Sala Mant", estado="mantenimiento")
        assert all(e["nombre"] != "Sala Mant" for e in client.get("/espacios").json())

    def test_mezcla_solo_devuelve_activos(self, client, db):
        crear_espacio(db, nombre="A1")
        crear_espacio(db, nombre="I1", estado="inactivo")
        crear_espacio(db, nombre="M1", estado="mantenimiento")
        nombres = [e["nombre"] for e in client.get("/espacios").json()]
        assert nombres == ["A1"]

    def test_todos_inactivos_devuelve_lista_vacia(self, client, db):
        crear_espacio(db, nombre="I1", estado="inactivo")
        crear_espacio(db, nombre="M1", estado="mantenimiento")
        assert client.get("/espacios").json() == []

    def test_skip_y_limit_junto_al_filtro(self, client, db):
        crear_espacio(db, nombre="A1")
        crear_espacio(db, nombre="I1", estado="inactivo")
        crear_espacio(db, nombre="A2")
        nombres = [
            e["nombre"]
            for e in client.get("/espacios", params={"skip": 1, "limit": 1}).json()
        ]
        assert nombres == ["A2"]

    def test_usuario_no_recupera_inactivos_con_parametros(self, client, db):
        crear_espacio(db, nombre="I1", estado="inactivo")
        usuario = crear_usuario(db, username="user_rn", email="user_rn@test.com")
        respuesta = client.get(
            "/espacios", params={"skip": 0, "limit": 100}, headers=headers_para(usuario)
        )
        assert respuesta.json() == []

    def test_admin_sigue_viendo_todos(self, client, db):
        crear_espacio(db, nombre="A1")
        crear_espacio(db, nombre="I1", estado="inactivo")
        admin = crear_usuario(db, username="admin_rn", email="admin_rn@test.com", rol="admin")
        nombres = [e["nombre"] for e in client.get("/espacios", headers=headers_para(admin)).json()]
        assert set(nombres) == {"A1", "I1"}


class TestDisponibilidad:
    def _espacio_con_usuario(self, db, **kwargs):
        espacio = crear_espacio(db, nombre="Sala Disp", **kwargs)
        usuario = crear_usuario(db, username="user_disp", email="user_disp@test.com")
        crear_recurso(db, espacio=espacio, usuario=usuario)
        return espacio

    def test_dia_habilitado_todos_libres(self, client, db):
        espacio = self._espacio_con_usuario(db)
        respuesta = client.get(
            f"/espacios/{espacio.id}/disponibilidad", params={"fecha": fecha_habilitada().isoformat()}
        )
        assert respuesta.status_code == 200
        slots = respuesta.json()
        assert len(slots) == 13  # 07:00 a 19:00
        assert all(slot["estado"] == "libre" for slot in slots)

    def test_domingo_sin_slots(self, client, db):
        espacio = self._espacio_con_usuario(db)
        respuesta = client.get(
            f"/espacios/{espacio.id}/disponibilidad", params={"fecha": proximo_domingo().isoformat()}
        )
        assert respuesta.status_code == 200
        assert respuesta.json() == []

    def test_espacio_inactivo_muestra_mantenimiento(self, client, db):
        espacio = self._espacio_con_usuario(db, estado="inactivo")
        respuesta = client.get(
            f"/espacios/{espacio.id}/disponibilidad", params={"fecha": fecha_habilitada().isoformat()}
        )
        assert respuesta.status_code == 200
        slots = respuesta.json()
        assert len(slots) == 13
        assert all(slot["estado"] == "mantenimiento" for slot in slots)
