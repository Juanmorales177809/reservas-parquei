# -*- coding: utf-8 -*-
"""Pruebas de integración de PUT /usuarios/me (Fase A2, perfil de usuario).

Self-service: cualquier usuario autenticado edita su propio perfil
(documento_identificacion, telefono, institucion, vinculacion, dependencia).
El test central de este archivo es el que justifica por qué `PerfilUpdate`
es un schema separado de `UsuarioUpdate` (nunca reusar este último acá):
mandar `rol`/`espacio_id`/`username`/`email` en el body debe dar 422, no
ser ignorado en silencio -- `extra="forbid"` hace la escalada de
privilegios estructuralmente imposible.
"""

from tests.conftest import cookies_para, crear_usuario


class TestActualizarMiPerfil:
    def test_persiste_los_cinco_campos(self, client, db):
        usuario = crear_usuario(db, username="perfil_u1", email="perfil_u1@example.com")

        respuesta = client.put(
            "/usuarios/me",
            json={
                "documento_identificacion": "1034917433",
                "telefono": "3053695592",
                "institucion": "Instituto Tecnológico Metropolitano",
                "vinculacion": "estudiante",
                "dependencia": "Ingenierías",
            },
            headers=cookies_para(usuario),
        )

        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["documento_identificacion"] == "1034917433"
        assert cuerpo["telefono"] == "3053695592"
        assert cuerpo["institucion"] == "Instituto Tecnológico Metropolitano"
        assert cuerpo["vinculacion"] == "estudiante"
        assert cuerpo["dependencia"] == "Ingenierías"

    def test_actualizacion_parcial_conserva_lo_no_enviado(self, client, db):
        usuario = crear_usuario(db, username="perfil_u2", email="perfil_u2@example.com")
        client.put(
            "/usuarios/me",
            json={"telefono": "3000000000", "vinculacion": "docente"},
            headers=cookies_para(usuario),
        )

        respuesta = client.put(
            "/usuarios/me",
            json={"institucion": "ITM"},
            headers=cookies_para(usuario),
        )

        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["institucion"] == "ITM"
        assert cuerpo["telefono"] == "3000000000"
        assert cuerpo["vinculacion"] == "docente"

    def test_rol_en_el_body_da_422_no_se_ignora(self, client, db):
        """El test que justifica PerfilUpdate como schema separado: la
        escalada de privilegios debe ser un error de validación, nunca un
        campo silenciosamente descartado."""
        usuario = crear_usuario(db, username="perfil_u3", email="perfil_u3@example.com", rol="usuario")

        respuesta = client.put(
            "/usuarios/me",
            json={"rol": "admin"},
            headers=cookies_para(usuario),
        )

        assert respuesta.status_code == 422
        db.refresh(usuario)
        assert usuario.rol == "usuario"

    def test_espacio_id_en_el_body_da_422(self, client, db):
        usuario = crear_usuario(db, username="perfil_u4", email="perfil_u4@example.com")

        respuesta = client.put(
            "/usuarios/me",
            json={"espacio_id": 1},
            headers=cookies_para(usuario),
        )

        assert respuesta.status_code == 422

    def test_username_o_email_en_el_body_da_422(self, client, db):
        usuario = crear_usuario(db, username="perfil_u5", email="perfil_u5@example.com")

        respuesta = client.put(
            "/usuarios/me",
            json={"username": "otro_nombre"},
            headers=cookies_para(usuario),
        )

        assert respuesta.status_code == 422
        db.refresh(usuario)
        assert usuario.username == "perfil_u5"

    def test_sin_cookie_da_401(self, client):
        respuesta = client.put("/usuarios/me", json={"telefono": "300"})
        assert respuesta.status_code == 401

    def test_vinculacion_invalida_da_422(self, client, db):
        usuario = crear_usuario(db, username="perfil_u6", email="perfil_u6@example.com")

        respuesta = client.put(
            "/usuarios/me",
            json={"vinculacion": "no-es-una-vinculacion-valida"},
            headers=cookies_para(usuario),
        )

        assert respuesta.status_code == 422

    def test_cualquier_rol_puede_editar_su_propio_perfil(self, client, db):
        """A diferencia de PUT /usuarios/{id} (solo admin), este endpoint
        es self-service para cualquier rol -- usuario, gestor y admin."""
        for rol in ("usuario", "gestor", "admin"):
            usuario = crear_usuario(db, username=f"perfil_rol_{rol}", email=f"perfil_rol_{rol}@example.com", rol=rol)
            respuesta = client.put(
                "/usuarios/me",
                json={"telefono": "3000000001"},
                headers=cookies_para(usuario),
            )
            assert respuesta.status_code == 200, rol

    def test_no_afecta_el_perfil_de_otro_usuario(self, client, db):
        usuario_a = crear_usuario(db, username="perfil_a", email="perfil_a@example.com")
        usuario_b = crear_usuario(db, username="perfil_b", email="perfil_b@example.com")

        client.put("/usuarios/me", json={"telefono": "111"}, headers=cookies_para(usuario_a))

        db.refresh(usuario_b)
        assert usuario_b.telefono is None


class TestPerfilEnUsuarioResponse:
    def test_usuario_recien_creado_tiene_los_cinco_campos_en_null(self, client, db):
        admin = crear_usuario(db, username="perfil_admin1", email="perfil_admin1@example.com", rol="admin")
        respuesta = client.get("/usuarios/me", headers=cookies_para(admin))

        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        for campo in ("documento_identificacion", "telefono", "institucion", "vinculacion", "dependencia"):
            assert cuerpo[campo] is None
