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
    usuario = crear_usuario(db, username="user_esp", email="user_esp@example.com")
    admin = crear_usuario(db, username="admin_esp", email="admin_esp@example.com", rol="admin")
    payload = {
        "nombre": "Sala Nueva",
        "ubicacion": "Piso 2",
        "capacidad": 15,
        "estado": "activo",
        "correo": "sala.nueva@example.com",
    }
    assert (
        client.post("/espacios", json=payload, headers=headers_para(usuario)).status_code
        == 403
    )
    respuesta = client.post("/espacios", json=payload, headers=headers_para(admin))
    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] == "Sala Nueva"


def test_eliminar_espacio_sin_dependencias(client, db):
    admin = crear_usuario(db, username="admin_del", email="admin_del@example.com", rol="admin")
    espacio = crear_espacio(db, nombre="Sala Borrable")
    respuesta = client.delete(f"/espacios/{espacio.id}", headers=headers_para(admin))
    assert respuesta.status_code == 204


def test_eliminar_espacio_con_dependencias_da_409(client, db):
    admin = crear_usuario(db, username="admin_dep", email="admin_dep@example.com", rol="admin")
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
        usuario = crear_usuario(db, username="user_rn", email="user_rn@example.com")
        respuesta = client.get(
            "/espacios", params={"skip": 0, "limit": 100}, headers=headers_para(usuario)
        )
        assert respuesta.json() == []

    def test_admin_sigue_viendo_todos(self, client, db):
        crear_espacio(db, nombre="A1")
        crear_espacio(db, nombre="I1", estado="inactivo")
        admin = crear_usuario(db, username="admin_rn", email="admin_rn@example.com", rol="admin")
        nombres = [e["nombre"] for e in client.get("/espacios", headers=headers_para(admin)).json()]
        assert set(nombres) == {"A1", "I1"}


class TestModalidadYCorreo:
    """RN-006 (modalidad equipos/zonas/mixto) y RN-007 (correo propio del
    espacio), Fase 12B."""

    def _payload(self, **overrides):
        payload = {
            "nombre": "Sala Modalidad",
            "ubicacion": "Piso 3",
            "capacidad": 10,
            "estado": "activo",
            "modalidad_reserva": "equipos",
            "correo": "laboratorio@example.com",
        }
        payload.update(overrides)
        return payload

    def test_modalidad_equipos_valida(self, client, db):
        admin = crear_usuario(db, username="admin_mod1", email="admin_mod1@example.com", rol="admin")
        respuesta = client.post(
            "/espacios", json=self._payload(nombre="Sala Equipos"), headers=headers_para(admin)
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["modalidad_reserva"] == "equipos"

    def test_modalidad_zonas_valida(self, client, db):
        admin = crear_usuario(db, username="admin_mod2", email="admin_mod2@example.com", rol="admin")
        respuesta = client.post(
            "/espacios",
            json=self._payload(nombre="Sala Zonas", modalidad_reserva="zonas"),
            headers=headers_para(admin),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["modalidad_reserva"] == "zonas"

    def test_modalidad_mixto_valida(self, client, db):
        admin = crear_usuario(db, username="admin_mod3", email="admin_mod3@example.com", rol="admin")
        respuesta = client.post(
            "/espacios",
            json=self._payload(nombre="Sala Mixta", modalidad_reserva="mixto"),
            headers=headers_para(admin),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["modalidad_reserva"] == "mixto"

    def test_modalidad_invalida_da_422(self, client, db):
        admin = crear_usuario(db, username="admin_mod4", email="admin_mod4@example.com", rol="admin")
        respuesta = client.post(
            "/espacios",
            json=self._payload(nombre="Sala Invalida", modalidad_reserva="otra-cosa"),
            headers=headers_para(admin),
        )
        assert respuesta.status_code == 422

    def test_correo_valido_se_persiste(self, client, db):
        admin = crear_usuario(db, username="admin_correo1", email="admin_correo1@example.com", rol="admin")
        respuesta = client.post(
            "/espacios",
            json=self._payload(nombre="Sala Correo", correo="lab.informatica@example.com"),
            headers=headers_para(admin),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["correo"] == "lab.informatica@example.com"

    def test_correo_vacio_da_422(self, client, db):
        admin = crear_usuario(db, username="admin_correo2", email="admin_correo2@example.com", rol="admin")
        respuesta = client.post(
            "/espacios",
            json=self._payload(nombre="Sala Sin Correo", correo=""),
            headers=headers_para(admin),
        )
        assert respuesta.status_code == 422

    def test_correo_ausente_da_422(self, client, db):
        admin = crear_usuario(db, username="admin_correo3", email="admin_correo3@example.com", rol="admin")
        payload = self._payload(nombre="Sala Sin Campo Correo")
        del payload["correo"]
        respuesta = client.post("/espacios", json=payload, headers=headers_para(admin))
        assert respuesta.status_code == 422

    def test_correo_formato_invalido_da_422(self, client, db):
        admin = crear_usuario(db, username="admin_correo4", email="admin_correo4@example.com", rol="admin")
        respuesta = client.post(
            "/espacios",
            json=self._payload(nombre="Sala Correo Malo", correo="no-es-un-correo"),
            headers=headers_para(admin),
        )
        assert respuesta.status_code == 422

    def test_espacio_existente_conserva_compatibilidad(self, client, db):
        """Un espacio creado antes de esta fase (sin modalidad/correo
        explícitos) sigue sirviéndose sin romper el contrato: modalidad por
        defecto 'equipos', correo nulo."""
        espacio = crear_espacio(db, nombre="Sala Legado")
        respuesta = client.get(f"/espacios/{espacio.id}")
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["modalidad_reserva"] == "equipos"
        assert cuerpo["correo"] is None

    def test_admin_puede_actualizar_correo_de_espacio_existente(self, client, db):
        admin = crear_usuario(db, username="admin_correo5", email="admin_correo5@example.com", rol="admin")
        espacio = crear_espacio(db, nombre="Sala A Completar")
        respuesta = client.put(
            f"/espacios/{espacio.id}",
            json={"correo": "completado@example.com"},
            headers=headers_para(admin),
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["correo"] == "completado@example.com"


class TestDisponibilidad:
    def _espacio_con_usuario(self, db, **kwargs):
        espacio = crear_espacio(db, nombre="Sala Disp", **kwargs)
        usuario = crear_usuario(db, username="user_disp", email="user_disp@example.com")
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
