# -*- coding: utf-8 -*-
"""Pruebas del puente temporal de correo por Microsoft Graph con token
delegado cacheado (`app/services/email_graph.py`).

Nunca le pegan a la red real de Graph ni a MSAL de verdad -- `PublicClientApplication`
se reemplaza por dobles de prueba (mismo criterio que `_SMTPFalso` en
`test_correo_saliente.py`), y `httpx.post` también se reemplaza por un doble.
`SerializableTokenCache` sí es real (objeto puro en memoria/disco, sin red),
apuntado a un archivo temporal por test.
"""

from datetime import datetime

import httpx
import pytest

from app.config import settings
from app.services import email_graph


class _AppFalsaSinCuentas:
    def __init__(self, *args, **kwargs):
        pass

    def get_accounts(self):
        return []


class _AppFalsaTokenValido:
    def __init__(self, *args, **kwargs):
        pass

    def get_accounts(self):
        return [object()]

    def acquire_token_silent(self, scopes, account):
        return {"access_token": "token-de-prueba"}


class _AppFalsaTokenVencido:
    def __init__(self, *args, **kwargs):
        pass

    def get_accounts(self):
        return [object()]

    def acquire_token_silent(self, scopes, account):
        return {"error": "invalid_grant", "error_description": "AADSTS700082: token expirado"}


@pytest.fixture()
def config_graph(tmp_path, monkeypatch):
    ruta = tmp_path / "graph_token_cache.json"
    monkeypatch.setattr(settings, "graph_token_cache_path", str(ruta))
    monkeypatch.setattr(settings, "graph_mail_sender", "sgc-lia@itm.edu.co")
    return ruta


class TestTokenSilencioso:
    def test_sin_cuentas_cacheadas_lanza_error_con_instrucciones(self, config_graph, monkeypatch):
        monkeypatch.setattr(email_graph, "PublicClientApplication", _AppFalsaSinCuentas)
        with pytest.raises(RuntimeError, match="graph_login"):
            email_graph._token_silencioso()

    def test_token_vencido_lanza_error_con_instrucciones(self, config_graph, monkeypatch):
        monkeypatch.setattr(email_graph, "PublicClientApplication", _AppFalsaTokenVencido)
        with pytest.raises(RuntimeError, match="graph_login"):
            email_graph._token_silencioso()

    def test_token_valido_se_devuelve(self, config_graph, monkeypatch):
        monkeypatch.setattr(email_graph, "PublicClientApplication", _AppFalsaTokenValido)
        assert email_graph._token_silencioso() == "token-de-prueba"


class TestEnviarGraph:
    def test_envia_con_payload_y_header_correctos(self, config_graph, monkeypatch):
        monkeypatch.setattr(email_graph, "_token_silencioso", lambda: "token-de-prueba")

        llamadas = []

        def _post_falso(url, headers=None, json=None, timeout=None):
            llamadas.append({"url": url, "headers": headers, "json": json})
            return httpx.Response(202, request=httpx.Request("POST", url))

        monkeypatch.setattr(email_graph.httpx, "post", _post_falso)

        email_graph.enviar_graph("destino@example.com", "Asunto de prueba", "Cuerpo de prueba")

        assert len(llamadas) == 1
        llamada = llamadas[0]
        assert llamada["url"] == "https://graph.microsoft.com/v1.0/users/sgc-lia@itm.edu.co/sendMail"
        assert llamada["headers"]["Authorization"] == "Bearer token-de-prueba"
        mensaje = llamada["json"]["message"]
        assert mensaje["subject"] == "Asunto de prueba"
        assert mensaje["body"]["content"] == "Cuerpo de prueba"
        assert mensaje["body"]["contentType"] == "Text"
        assert mensaje["toRecipients"][0]["emailAddress"]["address"] == "destino@example.com"

    def test_es_html_true_manda_contenttype_html(self, config_graph, monkeypatch):
        monkeypatch.setattr(email_graph, "_token_silencioso", lambda: "token-de-prueba")

        llamadas = []

        def _post_falso(url, headers=None, json=None, timeout=None):
            llamadas.append(json)
            return httpx.Response(202, request=httpx.Request("POST", url))

        monkeypatch.setattr(email_graph.httpx, "post", _post_falso)

        email_graph.enviar_graph("destino@example.com", "Asunto", "<p>Cuerpo</p>", es_html=True)

        assert llamadas[0]["message"]["body"]["contentType"] == "HTML"
        assert llamadas[0]["message"]["body"]["content"] == "<p>Cuerpo</p>"

    def test_error_http_lanza_runtimeerror_con_status_y_detalle(self, config_graph, monkeypatch):
        monkeypatch.setattr(email_graph, "_token_silencioso", lambda: "token-de-prueba")

        def _post_falso(url, headers=None, json=None, timeout=None):
            return httpx.Response(403, text="Forbidden: insufficient privileges", request=httpx.Request("POST", url))

        monkeypatch.setattr(email_graph.httpx, "post", _post_falso)

        with pytest.raises(RuntimeError, match="403"):
            email_graph.enviar_graph("destino@example.com", "Asunto", "Cuerpo")

    def test_token_invalido_propaga_sin_llamar_a_graph(self, config_graph, monkeypatch):
        monkeypatch.setattr(email_graph, "PublicClientApplication", _AppFalsaSinCuentas)

        llamadas = []
        monkeypatch.setattr(email_graph.httpx, "post", lambda *a, **kw: llamadas.append(1))

        with pytest.raises(RuntimeError, match="graph_login"):
            email_graph.enviar_graph("destino@example.com", "Asunto", "Cuerpo")
        assert llamadas == []


class TestEventosCalendario:
    """Invitación de Outlook Calendar (2026-09-03) -- las 3 funciones
    nuevas que reusan `_token_silencioso()`, mismo criterio de doble que
    `TestEnviarGraph`: nunca le pegan a Graph real."""

    def test_crear_evento_manda_payload_y_asistentes_correctos(self, config_graph, monkeypatch):
        monkeypatch.setattr(email_graph, "_token_silencioso", lambda: "token-de-prueba")
        llamadas = []

        def _post_falso(url, headers=None, json=None, timeout=None):
            llamadas.append({"url": url, "headers": headers, "json": json})
            return httpx.Response(201, json={"id": "evento-abc123"}, request=httpx.Request("POST", url))

        monkeypatch.setattr(email_graph.httpx, "post", _post_falso)

        event_id = email_graph.crear_evento_calendario_graph(
            asunto="Reserva: Sala 1",
            cuerpo="<p>Confirmada</p>",
            inicio=datetime(2026, 9, 10, 8, 0),
            fin=datetime(2026, 9, 10, 10, 0),
            ubicacion="Sala 1",
            asistentes=[("gestor@example.com", "gestor1"), ("usuario@example.com", "usuario1")],
        )

        assert event_id == "evento-abc123"
        assert len(llamadas) == 1
        llamada = llamadas[0]
        assert llamada["url"] == "https://graph.microsoft.com/v1.0/users/sgc-lia@itm.edu.co/events"
        assert llamada["headers"]["Authorization"] == "Bearer token-de-prueba"
        payload = llamada["json"]
        assert payload["subject"] == "Reserva: Sala 1"
        assert payload["location"]["displayName"] == "Sala 1"
        assert payload["start"]["dateTime"] == "2026-09-10T08:00:00"
        assert payload["end"]["dateTime"] == "2026-09-10T10:00:00"
        asistentes = payload["attendees"]
        assert len(asistentes) == 2
        assert asistentes[0]["emailAddress"] == {"address": "gestor@example.com", "name": "gestor1"}
        assert asistentes[0]["type"] == "required"
        assert asistentes[1]["emailAddress"] == {"address": "usuario@example.com", "name": "usuario1"}

    def test_crear_evento_error_http_lanza_runtimeerror(self, config_graph, monkeypatch):
        monkeypatch.setattr(email_graph, "_token_silencioso", lambda: "token-de-prueba")
        monkeypatch.setattr(
            email_graph.httpx,
            "post",
            lambda url, **kw: httpx.Response(403, text="Forbidden", request=httpx.Request("POST", url)),
        )

        with pytest.raises(RuntimeError, match="403"):
            email_graph.crear_evento_calendario_graph(
                asunto="A", cuerpo="B", inicio=datetime(2026, 9, 10, 8, 0), fin=datetime(2026, 9, 10, 9, 0),
                ubicacion="X", asistentes=[],
            )

    def test_actualizar_evento_manda_patch_con_nuevo_horario(self, config_graph, monkeypatch):
        monkeypatch.setattr(email_graph, "_token_silencioso", lambda: "token-de-prueba")
        llamadas = []

        def _patch_falso(url, headers=None, json=None, timeout=None):
            llamadas.append({"url": url, "json": json})
            return httpx.Response(200, request=httpx.Request("PATCH", url))

        monkeypatch.setattr(email_graph.httpx, "patch", _patch_falso)

        email_graph.actualizar_evento_calendario_graph(
            "evento-abc123", inicio=datetime(2026, 9, 11, 14, 0), fin=datetime(2026, 9, 11, 16, 0)
        )

        assert len(llamadas) == 1
        assert llamadas[0]["url"] == "https://graph.microsoft.com/v1.0/users/sgc-lia@itm.edu.co/events/evento-abc123"
        assert llamadas[0]["json"]["start"]["dateTime"] == "2026-09-11T14:00:00"
        assert llamadas[0]["json"]["end"]["dateTime"] == "2026-09-11T16:00:00"

    def test_actualizar_evento_error_http_lanza_runtimeerror(self, config_graph, monkeypatch):
        monkeypatch.setattr(email_graph, "_token_silencioso", lambda: "token-de-prueba")
        monkeypatch.setattr(
            email_graph.httpx,
            "patch",
            lambda url, **kw: httpx.Response(404, text="Not found", request=httpx.Request("PATCH", url)),
        )

        with pytest.raises(RuntimeError, match="404"):
            email_graph.actualizar_evento_calendario_graph(
                "evento-inexistente", inicio=datetime(2026, 9, 11, 14, 0), fin=datetime(2026, 9, 11, 16, 0)
            )

    def test_cancelar_evento_manda_post_cancel_con_comentario(self, config_graph, monkeypatch):
        monkeypatch.setattr(email_graph, "_token_silencioso", lambda: "token-de-prueba")
        llamadas = []

        def _post_falso(url, headers=None, json=None, timeout=None):
            llamadas.append({"url": url, "json": json})
            return httpx.Response(202, request=httpx.Request("POST", url))

        monkeypatch.setattr(email_graph.httpx, "post", _post_falso)

        email_graph.cancelar_evento_calendario_graph("evento-abc123", comentario="La reserva fue cancelada.")

        assert len(llamadas) == 1
        assert llamadas[0]["url"] == "https://graph.microsoft.com/v1.0/users/sgc-lia@itm.edu.co/events/evento-abc123/cancel"
        assert llamadas[0]["json"] == {"comment": "La reserva fue cancelada."}

    def test_cancelar_evento_error_http_lanza_runtimeerror(self, config_graph, monkeypatch):
        monkeypatch.setattr(email_graph, "_token_silencioso", lambda: "token-de-prueba")
        monkeypatch.setattr(
            email_graph.httpx,
            "post",
            lambda url, **kw: httpx.Response(410, text="Gone", request=httpx.Request("POST", url)),
        )

        with pytest.raises(RuntimeError, match="410"):
            email_graph.cancelar_evento_calendario_graph("evento-abc123")
