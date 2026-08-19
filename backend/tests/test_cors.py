# -*- coding: utf-8 -*-
"""CORS acotado al uso real del frontend (Fase 9A, backend/app/main.py).

El frontend (frontend/src/services/api.ts) solo emite GET/POST/PUT/PATCH/DELETE
con, a lo sumo, la cabecera Content-Type, y nunca usa `credentials: 'include'`
(la sesión viaja en una cookie HttpOnly que el navegador adjunta solo al
mismo origen, a través del proxy `/api` de Next.js; nunca en cross-origin).
Desde la Fase 9G el backend ya no acepta ni anuncia `Authorization`.
"""

ORIGEN_PERMITIDO = "http://localhost:3000"
ORIGEN_NO_PERMITIDO = "http://evil.example"


class TestPreflightPermitido:
    def test_metodo_y_headers_reales_del_frontend(self, client):
        response = client.options(
            "/auth/login",
            headers={
                "Origin": ORIGEN_PERMITIDO,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == ORIGEN_PERMITIDO
        assert "POST" in response.headers["access-control-allow-methods"]
        assert "content-type" in response.headers["access-control-allow-headers"].lower()

    def test_se_acepta_preflight_con_authorization(self, client):
        # regresión 9G: el middleware ya no anuncia Authorization
        response = client.options(
            "/espacios",
            headers={
                "Origin": ORIGEN_PERMITIDO,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization",
            },
        )

        assert response.status_code == 400
        assert "authorization" not in response.headers.get("access-control-allow-headers", "").lower()

    def test_allow_headers_no_anuncia_authorization(self, client):
        response = client.options(
            "/espacios",
            headers={
                "Origin": ORIGEN_PERMITIDO,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "content-type",
            },
        )

        assert response.status_code == 200
        assert "content-type" in response.headers["access-control-allow-headers"].lower()
        assert "authorization" not in response.headers["access-control-allow-headers"].lower()

    def test_no_declara_allow_credentials(self, client):
        # La cookie viaja solo por el proxy same-origin de Next.js; el backend
        # no autoriza credenciales cross-origin de navegador.
        response = client.options(
            "/auth/login",
            headers={
                "Origin": ORIGEN_PERMITIDO,
                "Access-Control-Request-Method": "POST",
            },
        )

        assert "access-control-allow-credentials" not in response.headers


class TestPreflightRechazado:
    def test_metodo_no_usado_por_el_frontend_es_rechazado(self, client):
        response = client.options(
            "/espacios",
            headers={
                "Origin": ORIGEN_PERMITIDO,
                "Access-Control-Request-Method": "TRACE",
            },
        )

        assert response.status_code == 400
        assert "method" in response.text

    def test_header_no_usado_por_el_frontend_es_rechazado(self, client):
        response = client.options(
            "/espacios",
            headers={
                "Origin": ORIGEN_PERMITIDO,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "x-custom-header",
            },
        )

        assert response.status_code == 400
        assert "headers" in response.text

    def test_origen_no_configurado_es_rechazado(self, client):
        response = client.options(
            "/espacios",
            headers={
                "Origin": ORIGEN_NO_PERMITIDO,
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 400
        assert "origin" in response.text


class TestPeticionesReales:
    def test_get_con_origen_permitido_incluye_cabecera_cors(self, client):
        response = client.get("/espacios", headers={"Origin": ORIGEN_PERMITIDO})

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == ORIGEN_PERMITIDO

    def test_get_con_origen_no_permitido_no_incluye_cabecera_cors(self, client):
        # El backend igual responde (CORS lo aplica el navegador, no el
        # servidor), pero sin la cabecera el navegador bloquearía la lectura.
        response = client.get("/espacios", headers={"Origin": ORIGEN_NO_PERMITIDO})

        assert response.status_code == 200
        assert "access-control-allow-origin" not in response.headers

    def test_login_sin_regresion_con_origen_cruzado(self, db, client):
        from tests.conftest import crear_usuario

        crear_usuario(db, username="cors_login", email="cors_login@example.com", password="password123")

        response = client.post(
            "/auth/login",
            json={"username": "cors_login", "password": "password123"},
            headers={"Origin": ORIGEN_PERMITIDO},
        )

        assert response.status_code == 200
        assert "access_token" not in response.json()
        assert response.headers["access-control-allow-origin"] == ORIGEN_PERMITIDO

    def test_reservas_autenticadas_sin_regresion_con_origen_cruzado(self, db, client):
        from tests.conftest import crear_espacio, crear_recurso, crear_usuario, cookies_para

        usuario = crear_usuario(db, username="cors_user", email="cors_user@example.com")
        espacio = crear_espacio(db)
        crear_recurso(db, espacio=espacio, usuario=usuario)

        headers = cookies_para(usuario)
        headers["Origin"] = ORIGEN_PERMITIDO

        response = client.get("/reservas/mis-reservas", headers=headers)

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == ORIGEN_PERMITIDO
