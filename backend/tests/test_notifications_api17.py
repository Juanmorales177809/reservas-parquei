"""Pruebas de contrato de notifications §2-§3 (API-17).

Bandeja propia, lectura sin efectos colaterales y preferencias.
Las filas se siembran directo por repositorio: la generación de
eventos es API-18 y ningún productor existe todavía.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import text

from .conftest import (
    crear_usuario_cuenta,
    headers_autenticados,
    iniciar_sesion,
)


def _sembrar(db, tag: str, cuenta, codigo: str = "RESERVA_APROBADA") -> int:
    ahora = datetime.now(timezone.utc)
    tipo_id = db.scalar(
        text("SELECT id FROM notificaciones.tipos_evento WHERE codigo = :c"),
        {"c": codigo},
    )
    evento_id = db.scalar(
        text(
            "INSERT INTO notificaciones.eventos (tipo_evento_id, ocurrencia_clave, created_at) "
            "VALUES (:t, :o, :a) RETURNING id"
        ),
        {"t": tipo_id, "o": f"api17-{tag}", "a": ahora},
    )
    nid = db.scalar(
        text(
            "INSERT INTO notificaciones.notificaciones "
            "(evento_id, id_cuenta, titulo, cuerpo, created_at) "
            "VALUES (:e, :c, :t, :b, :a) RETURNING id"
        ),
        {"e": evento_id, "c": cuenta.id_cuenta, "t": f"Aviso {tag}",
         "b": f"Cuerpo {tag}", "a": ahora},
    )
    db.commit()
    return nid


def _limpiar(db, cuenta) -> None:
    db.execute(
        text(
            "DELETE FROM notificaciones.notificaciones WHERE id_cuenta = :c"),
        {"c": cuenta.id_cuenta},
    )
    db.execute(
        text(
            "DELETE FROM notificaciones.eventos WHERE ocurrencia_clave LIKE 'api17-%' "
            "AND id NOT IN (SELECT evento_id FROM notificaciones.notificaciones)"
        ),
    )
    db.execute(
        text("DELETE FROM notificaciones.preferencias WHERE id_cuenta = :c"),
        {"c": cuenta.id_cuenta},
    )
    db.commit()


def _login(client, db, tag, prefijo="ntf"):
    from .conftest import correo_para

    _, cuenta = crear_usuario_cuenta(db, tag, correo=correo_para(tag, prefijo))
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso")
    return headers_autenticados(jar), cuenta


def test_bandeja_solo_propia_y_filtros(client, db, tag):
    """§2.1 + T-NOT-06: la bandeja es propia; filtros leida/tipo."""
    h_a, c_a = _login(client, db, f"a{tag}", "ntfa")
    h_b, c_b = _login(client, db, f"b{tag}", "ntfb")
    n1 = _sembrar(db, f"{tag}a", c_a)
    n2 = _sembrar(db, f"{tag}b", c_a, "RESERVA_RECHAZADA")
    _sembrar(db, f"{tag}c", c_b)
    try:
        r = client.get("/api/notificaciones", headers=h_a)
        assert r.status_code == 200, r.text
        assert {n["id"] for n in r.json()["datos"]} == {n1, n2}

        f = client.get("/api/notificaciones?leida=false", headers=h_a)
        assert len(f.json()["datos"]) == 2
        t = client.get(
            "/api/notificaciones?tipo_evento=RESERVA_APROBADA", headers=h_a
        )
        assert [n["id"] for n in t.json()["datos"]] == [n1]
    finally:
        _limpiar(db, c_a)
        _limpiar(db, c_b)


def test_lectura_ajena_no_existe_y_no_toca_nada(client, db, tag):
    """T-NOT-06/07: ajena → 404; leer no altera reserva ni envío."""
    h_a, c_a = _login(client, db, f"a{tag}", "ntfa")
    h_b, c_b = _login(client, db, f"b{tag}", "ntfb")
    nid = _sembrar(db, tag, c_b)
    try:
        ajena = client.post(
            f"/api/notificaciones/{nid}/lectura", headers=h_a
        )
        assert ajena.status_code == 404, ajena.text

        ok = client.post(f"/api/notificaciones/{nid}/lectura", headers=h_b)
        assert ok.status_code == 200, ok.text
        assert ok.json()["id"] == nid
        primera = ok.json()["leida_at"]
        de_nuevo = client.post(
            f"/api/notificaciones/{nid}/lectura", headers=h_b
        )
        assert de_nuevo.json()["leida_at"] == primera

        sin_leer = client.get("/api/notificaciones?leida=false", headers=h_b)
        assert sin_leer.json()["datos"] == []
    finally:
        _limpiar(db, c_a)
        _limpiar(db, c_b)


def test_preferencias(client, db, tag):
    """§3.1/§3.2: defecto general, reemplazo completo, 404 y 422."""
    h, cuenta = _login(client, db, tag)
    try:
        g0 = client.get("/api/notificaciones/preferencias", headers=h)
        assert g0.json() == {
            "general": {"correo_habilitado": True}, "por_evento": []}

        tipo_id = db.scalar(
            text("SELECT id FROM notificaciones.tipos_evento WHERE codigo = 'RESERVA_APROBADA'")
        )
        p = client.put(
            "/api/notificaciones/preferencias",
            json={
                "general": {"correo_habilitado": False},
                "por_evento": [
                    {"tipo_evento_id": tipo_id, "correo_habilitado": True}
                ],
            },
            headers=h,
        )
        assert p.status_code == 200, p.text
        assert p.json()["general"] == {"correo_habilitado": False}
        assert p.json()["por_evento"][0]["tipo_evento"]["codigo"] == "RESERVA_APROBADA"

        inexistente = client.put(
            "/api/notificaciones/preferencias",
            json={"por_evento": [
                {"tipo_evento_id": 999999, "correo_habilitado": True}]},
            headers=h,
        )
        assert inexistente.status_code == 404, inexistente.text

        duplicado = client.put(
            "/api/notificaciones/preferencias",
            json={"por_evento": [
                {"tipo_evento_id": tipo_id, "correo_habilitado": True},
                {"tipo_evento_id": tipo_id, "correo_habilitado": False}]},
            headers=h,
        )
        assert duplicado.status_code == 422, duplicado.text
    finally:
        _limpiar(db, cuenta)


def test_tipos_evento_catalogo_cerrado(client, db, tag):
    """§3.3: solo datos, solo habilitados."""
    h, cuenta = _login(client, db, tag)
    try:
        r = client.get("/api/notificaciones/tipos-evento", headers=h)
        assert r.status_code == 200, r.text
        assert set(r.json().keys()) == {"datos"}
        assert len(r.json()["datos"]) == 9
        assert {"RESERVA_APROBADA", "RESERVA_RECHAZADA"} <= {
            t["codigo"] for t in r.json()["datos"]}
    finally:
        _limpiar(db, cuenta)
