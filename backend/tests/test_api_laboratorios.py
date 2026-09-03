# -*- coding: utf-8 -*-
"""Pruebas de integración de laboratorios y disponibilidad (api/laboratorios.py).

Reglas cubiertas:
- Listado público de laboratorios sin autenticación.
- Creación/eliminación de laboratorios restringida al rol admin.
- RN-005 (contexto): la disponibilidad refleja el estado del laboratorio.
- Protección de integridad: un laboratorio con dependencias no se elimina.
"""

from tests.conftest import (
    crear_laboratorio,
    crear_recurso,
    crear_usuario,
    fecha_habilitada,
    cookies_para,
    proximo_domingo,
)


def test_listar_espacios_es_publico(client):
    respuesta = client.get("/laboratorios")
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
        client.post("/laboratorios", json=payload, headers=cookies_para(usuario)).status_code
        == 403
    )
    respuesta = client.post("/laboratorios", json=payload, headers=cookies_para(admin))
    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] == "Sala Nueva"


def test_eliminar_espacio_sin_dependencias(client, db):
    admin = crear_usuario(db, username="admin_del", email="admin_del@example.com", rol="admin")
    laboratorio = crear_laboratorio(db, nombre="Sala Borrable")
    respuesta = client.delete(f"/laboratorios/{laboratorio.id}", headers=cookies_para(admin))
    assert respuesta.status_code == 204


def test_eliminar_espacio_con_dependencias_da_409(client, db):
    admin = crear_usuario(db, username="admin_dep", email="admin_dep@example.com", rol="admin")
    laboratorio = crear_laboratorio(db, nombre="Sala Con Recursos")
    crear_recurso(db, laboratorio=laboratorio, usuario=admin)
    respuesta = client.delete(f"/laboratorios/{laboratorio.id}", headers=cookies_para(admin))
    assert respuesta.status_code == 409


class TestConfiguracionNotificarPorCorreo:
    """Correo opcional por laboratorio (2026-09-03) -- roundtrip del campo
    nuevo en `PUT/GET /laboratorios/gestion/configuracion`."""

    def _payload(self, *, notificar_por_correo, aprobacion_automatica=False):
        return {
            "horario_atencion": {str(dia): list(range(7, 20)) for dia in range(6)},
            "horas_antelacion": 24,
            "aprobacion_automatica": aprobacion_automatica,
            "notificar_por_correo": notificar_por_correo,
        }

    def test_default_true_en_laboratorio_nuevo(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Config Correo Default")
        gestor = crear_usuario(
            db, username="gestor_cfg1", email="gestor_cfg1@example.com", rol="gestor", laboratorio_id=laboratorio.id
        )
        respuesta = client.get("/laboratorios/gestion/configuracion", headers=cookies_para(gestor))
        assert respuesta.status_code == 200
        assert respuesta.json()["notificar_por_correo"] is True

    def test_se_puede_apagar_y_prender(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Config Correo Toggle")
        gestor = crear_usuario(
            db, username="gestor_cfg2", email="gestor_cfg2@example.com", rol="gestor", laboratorio_id=laboratorio.id
        )
        apagar = client.put(
            "/laboratorios/gestion/configuracion",
            json=self._payload(notificar_por_correo=False),
            headers=cookies_para(gestor),
        )
        assert apagar.status_code == 200
        assert apagar.json()["notificar_por_correo"] is False
        db.refresh(laboratorio)
        assert laboratorio.notificar_por_correo is False

        prender = client.put(
            "/laboratorios/gestion/configuracion",
            json=self._payload(notificar_por_correo=True),
            headers=cookies_para(gestor),
        )
        assert prender.status_code == 200
        assert prender.json()["notificar_por_correo"] is True

    def test_sin_el_campo_da_422(self, client, db):
        """`notificar_por_correo` es requerido en el Update, mismo criterio
        que `aprobacion_automatica` -- no hay valor implícito seguro."""
        laboratorio = crear_laboratorio(db, nombre="Sala Config Correo Faltante")
        gestor = crear_usuario(
            db, username="gestor_cfg3", email="gestor_cfg3@example.com", rol="gestor", laboratorio_id=laboratorio.id
        )
        payload = self._payload(notificar_por_correo=True)
        del payload["notificar_por_correo"]
        respuesta = client.put(
            "/laboratorios/gestion/configuracion",
            json=payload,
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 422


class TestRN005ListadoPublico:
    def test_espacio_activo_visible_sin_token(self, client, db):
        crear_laboratorio(db, nombre="Sala Activa")
        nombres = [e["nombre"] for e in client.get("/laboratorios").json()]
        assert "Sala Activa" in nombres

    def test_espacio_inactivo_no_visible_sin_token(self, client, db):
        crear_laboratorio(db, nombre="Sala Inactiva", estado="inactivo")
        nombres = [e["nombre"] for e in client.get("/laboratorios").json()]
        assert "Sala Inactiva" not in nombres

    def test_espacio_mantenimiento_no_visible_sin_token(self, client, db):
        crear_laboratorio(db, nombre="Sala Mant", estado="mantenimiento")
        assert all(e["nombre"] != "Sala Mant" for e in client.get("/laboratorios").json())

    def test_mezcla_solo_devuelve_activos(self, client, db):
        crear_laboratorio(db, nombre="A1")
        crear_laboratorio(db, nombre="I1", estado="inactivo")
        crear_laboratorio(db, nombre="M1", estado="mantenimiento")
        nombres = [e["nombre"] for e in client.get("/laboratorios").json()]
        assert nombres == ["A1"]

    def test_todos_inactivos_devuelve_lista_vacia(self, client, db):
        crear_laboratorio(db, nombre="I1", estado="inactivo")
        crear_laboratorio(db, nombre="M1", estado="mantenimiento")
        assert client.get("/laboratorios").json() == []

    def test_skip_y_limit_junto_al_filtro(self, client, db):
        crear_laboratorio(db, nombre="A1")
        crear_laboratorio(db, nombre="I1", estado="inactivo")
        crear_laboratorio(db, nombre="A2")
        nombres = [
            e["nombre"]
            for e in client.get("/laboratorios", params={"skip": 1, "limit": 1}).json()
        ]
        assert nombres == ["A2"]

    def test_usuario_no_recupera_inactivos_con_parametros(self, client, db):
        crear_laboratorio(db, nombre="I1", estado="inactivo")
        usuario = crear_usuario(db, username="user_rn", email="user_rn@example.com")
        respuesta = client.get(
            "/laboratorios", params={"skip": 0, "limit": 100}, headers=cookies_para(usuario)
        )
        assert respuesta.json() == []

    def test_admin_sigue_viendo_todos(self, client, db):
        crear_laboratorio(db, nombre="A1")
        crear_laboratorio(db, nombre="I1", estado="inactivo")
        admin = crear_usuario(db, username="admin_rn", email="admin_rn@example.com", rol="admin")
        nombres = [e["nombre"] for e in client.get("/laboratorios", headers=cookies_para(admin)).json()]
        assert set(nombres) == {"A1", "I1"}


class TestCorreo:
    """RN-007 (correo propio del laboratorio), Fase 12B. La modalidad
    equipos/espacios/mixto (RN-006) se removió por completo -- ver Fase 3 de
    `~/.claude/plans/dazzling-wobbling-zebra.md`."""

    def _payload(self, **overrides):
        payload = {
            "nombre": "Sala Modalidad",
            "ubicacion": "Piso 3",
            "capacidad": 10,
            "estado": "activo",
            "correo": "laboratorio@example.com",
        }
        payload.update(overrides)
        return payload

    def test_correo_valido_se_persiste(self, client, db):
        admin = crear_usuario(db, username="admin_correo1", email="admin_correo1@example.com", rol="admin")
        respuesta = client.post(
            "/laboratorios",
            json=self._payload(nombre="Sala Correo", correo="lab.informatica@example.com"),
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["correo"] == "lab.informatica@example.com"

    def test_correo_vacio_da_422(self, client, db):
        admin = crear_usuario(db, username="admin_correo2", email="admin_correo2@example.com", rol="admin")
        respuesta = client.post(
            "/laboratorios",
            json=self._payload(nombre="Sala Sin Correo", correo=""),
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 422

    def test_correo_ausente_da_422(self, client, db):
        admin = crear_usuario(db, username="admin_correo3", email="admin_correo3@example.com", rol="admin")
        payload = self._payload(nombre="Sala Sin Campo Correo")
        del payload["correo"]
        respuesta = client.post("/laboratorios", json=payload, headers=cookies_para(admin))
        assert respuesta.status_code == 422

    def test_correo_formato_invalido_da_422(self, client, db):
        admin = crear_usuario(db, username="admin_correo4", email="admin_correo4@example.com", rol="admin")
        respuesta = client.post(
            "/laboratorios",
            json=self._payload(nombre="Sala Correo Malo", correo="no-es-un-correo"),
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 422

    def test_espacio_existente_conserva_compatibilidad(self, client, db):
        """Un laboratorio creado antes de esta fase (sin correo explícito) sigue
        sirviéndose sin romper el contrato: correo nulo."""
        laboratorio = crear_laboratorio(db, nombre="Sala Legado")
        respuesta = client.get(f"/laboratorios/{laboratorio.id}")
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["correo"] is None

    def test_admin_puede_actualizar_correo_de_espacio_existente(self, client, db):
        admin = crear_usuario(db, username="admin_correo5", email="admin_correo5@example.com", rol="admin")
        laboratorio = crear_laboratorio(db, nombre="Sala A Completar")
        respuesta = client.put(
            f"/laboratorios/{laboratorio.id}",
            json={"correo": "completado@example.com"},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["correo"] == "completado@example.com"


class TestDisponibilidad:
    def _espacio_con_usuario(self, db, **kwargs):
        laboratorio = crear_laboratorio(db, nombre="Sala Disp", **kwargs)
        usuario = crear_usuario(db, username="user_disp", email="user_disp@example.com")
        crear_recurso(db, laboratorio=laboratorio, usuario=usuario)
        return laboratorio

    def test_dia_habilitado_todos_libres(self, client, db):
        laboratorio = self._espacio_con_usuario(db)
        respuesta = client.get(
            f"/laboratorios/{laboratorio.id}/disponibilidad", params={"fecha": fecha_habilitada().isoformat()}
        )
        assert respuesta.status_code == 200
        slots = respuesta.json()
        assert len(slots) == 13  # 07:00 a 19:00
        assert all(slot["estado"] == "libre" for slot in slots)

    def test_domingo_sin_slots(self, client, db):
        laboratorio = self._espacio_con_usuario(db)
        respuesta = client.get(
            f"/laboratorios/{laboratorio.id}/disponibilidad", params={"fecha": proximo_domingo().isoformat()}
        )
        assert respuesta.status_code == 200
        assert respuesta.json() == []

    def test_espacio_inactivo_muestra_mantenimiento(self, client, db):
        laboratorio = self._espacio_con_usuario(db, estado="inactivo")
        respuesta = client.get(
            f"/laboratorios/{laboratorio.id}/disponibilidad", params={"fecha": fecha_habilitada().isoformat()}
        )
        assert respuesta.status_code == 200
        slots = respuesta.json()
        assert len(slots) == 13
        assert all(slot["estado"] == "mantenimiento" for slot in slots)
