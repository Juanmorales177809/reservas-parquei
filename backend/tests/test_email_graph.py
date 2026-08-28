# -*- coding: utf-8 -*-
"""Pruebas del puente temporal de correo por Microsoft Graph con token
delegado cacheado (`app/services/email_graph.py`).

Nunca le pegan a la red real de Graph ni a MSAL de verdad -- `PublicClientApplication`
se reemplaza por dobles de prueba (mismo criterio que `_SMTPFalso` en
`test_correo_saliente.py`), y `httpx.post` también se reemplaza por un doble.
`SerializableTokenCache` sí es real (objeto puro en memoria/disco, sin red),
apuntado a un archivo temporal por test.
"""

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
