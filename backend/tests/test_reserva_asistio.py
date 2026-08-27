# -*- coding: utf-8 -*-
"""Pruebas de `asistio` en Reserva (Fase 12D-bis).

Fuera del roadmap original de 12A (sin RN asociada): `asistio` registra la
asistencia real, separada de `estado`/aprobación. Solo gestor/admin pueden
marcarla (nunca el propietario usuario), vía endpoint dedicado
`PUT /reservas/{id}/asistio` (no vía `PATCH /reservas/{id}`).
"""

from datetime import time as time_t

import pytest
from pydantic import ValidationError

from app.models.control_cambio import ControlCambio
from app.models.reserva import Reserva
from app.schemas.reserva import ReservaAsistioUpdate, ReservaResponse
from tests.conftest import (
    cookies_para,
    crear_espacio,
    crear_recurso,
    crear_usuario,
    fecha_habilitada,
    payload_reserva_objetivos,
)


def _crear_reserva_modelo(db, *, usuario, espacio, recurso, **kwargs):
    reserva = Reserva(
        usuario_id=usuario.id,
        espacio_id=espacio.id,
        recurso_id=recurso.id,
        fecha=kwargs.get("fecha", fecha_habilitada()),
        hora_inicio=kwargs.get("hora_inicio", time_t(8, 0)),
        hora_fin=kwargs.get("hora_fin", time_t(10, 0)),
        asistentes=kwargs.get("asistentes", 2),
        estado=kwargs.get("estado", "esperando"),
        asistio=kwargs.get("asistio"),
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


class TestModelo:
    def test_asistio_nulo_por_defecto(self, db):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username="asist_nulo", email="asist_nulo@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=usuario)
        reserva = _crear_reserva_modelo(db, usuario=usuario, espacio=espacio, recurso=recurso)
        assert reserva.asistio is None

    @pytest.mark.parametrize("valor", [True, False])
    def test_asistio_true_false_se_persisten(self, db, valor):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username=f"asist_{valor}", email=f"asist_{valor}@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=usuario)
        reserva = _crear_reserva_modelo(db, usuario=usuario, espacio=espacio, recurso=recurso, asistio=valor)
        assert reserva.asistio is valor

    def test_asistio_explicito_none_se_persiste_como_null(self, db):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username="asist_none", email="asist_none@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=usuario)
        reserva = _crear_reserva_modelo(db, usuario=usuario, espacio=espacio, recurso=recurso, asistio=None)
        assert reserva.asistio is None


class TestSchemas:
    def test_asistio_update_exige_asistio(self):
        with pytest.raises(ValidationError):
            ReservaAsistioUpdate()  # type: ignore[call-arg]

    @pytest.mark.parametrize("valor", [True, False])
    def test_asistio_update_acepta_bool(self, valor):
        modelo = ReservaAsistioUpdate(asistio=valor)
        assert modelo.asistio is valor

    def test_response_expone_asistio_null(self):
        modelo = ReservaResponse.model_validate(
            {
                "id": 1,
                "usuario_id": 1,
                "espacio_id": 1,
                "fecha": "2026-09-01",
                "hora_inicio": "08:00",
                "hora_fin": "10:00",
                "estado": "esperando",
                "asistentes": 2,
                "tipo_solicitud": "reserva_en_laboratorio",
                "requiere_apoyo_auxiliar": False,
                "tipo": None,
                "asistio": None,
                "created_at": "2026-08-01T10:00:00+00:00",
                "updated_at": "2026-08-01T10:00:00+00:00",
                "usuario": {"id": 1, "username": "u", "email": "u@example.com", "rol": "usuario"},
                "espacio": {"id": 1, "nombre": "Sala", "capacidad": None, "estado": "activo"},
                "recurso_ids": [1],
                "recursos": [],
                "zona_ids": [],
                "zonas": [],
            }
        )
        assert modelo.asistio is None

    @pytest.mark.parametrize("valor", [True, False])
    def test_response_expone_asistio_bool(self, valor):
        modelo = ReservaResponse.model_validate(
            {
                "id": 1,
                "usuario_id": 1,
                "espacio_id": 1,
                "fecha": "2026-09-01",
                "hora_inicio": "08:00",
                "hora_fin": "10:00",
                "estado": "esperando",
                "asistentes": 2,
                "tipo_solicitud": "reserva_en_laboratorio",
                "requiere_apoyo_auxiliar": False,
                "tipo": None,
                "asistio": valor,
                "created_at": "2026-08-01T10:00:00+00:00",
                "updated_at": "2026-08-01T10:00:00+00:00",
                "usuario": {"id": 1, "username": "u", "email": "u@example.com", "rol": "usuario"},
                "espacio": {"id": 1, "nombre": "Sala", "capacidad": None, "estado": "activo"},
                "recurso_ids": [1],
                "recursos": [],
                "zona_ids": [],
                "zonas": [],
            }
        )
        assert modelo.asistio is valor


class TestApi:
    def _crear_reserva(self, client, db, *, usuario):
        espacio = db.query(usuario.__class__).filter_by(id=usuario.id).first()
        # crear una reserva válida para el usuario dado (reusa espacio existente si hay)
        from tests.conftest import crear_espacio as _ce, crear_recurso as _cr

        # reutilizar el espacio del recurso creado para no depender del usuario
        esp = _ce(db, nombre="Sala Asistio")
        rec = _cr(db, espacio=esp, usuario=usuario if usuario.rol == "admin" else crear_usuario(db, username="admin_asist_tmp", email="admin_asist_tmp@example.com", rol="admin"))
        payload = payload_reserva_objetivos(recurso_ids=[rec.id], fecha=fecha_habilitada())
        resp = client.post("/reservas", json=payload, headers=cookies_para(usuario))
        assert resp.status_code == 201, resp.text
        return resp.json(), esp, rec

    def test_usuario_no_puede_marcar_asistencia_incluso_propietario(self, client, db):
        espacio = crear_espacio(db, nombre="Sala Asistio U")
        admin = crear_usuario(db, username="admin_asist_u", email="admin_asist_u@example.com", rol="admin")
        usuario = crear_usuario(db, username="u_asist", email="u_asist@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        creada = client.post(
            "/reservas",
            json=payload_reserva_objetivos(recurso_ids=[recurso.id], fecha=fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        resp = client.put(f"/reservas/{creada['id']}/asistio", json={"asistio": True}, headers=cookies_para(usuario))
        assert resp.status_code == 403

    def test_gestor_de_otro_espacio_no_puede_marcar_asistencia(self, client, db):
        espacio_a = crear_espacio(db, nombre="Sala Asistio A")
        espacio_b = crear_espacio(db, nombre="Sala Asistio B")
        gestor_a = crear_usuario(db, username="gestor_asist_a", email="gestor_asist_a@example.com", rol="gestor", espacio_id=espacio_a.id)
        usuario = crear_usuario(db, username="u_asist_b", email="u_asist_b@example.com")
        recurso_b = crear_recurso(db, espacio=espacio_b, usuario=gestor_a)
        creada = client.post(
            "/reservas",
            json=payload_reserva_objetivos(recurso_ids=[recurso_b.id], fecha=fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        resp = client.put(f"/reservas/{creada['id']}/asistio", json={"asistio": True}, headers=cookies_para(gestor_a))
        assert resp.status_code == 403

    def test_gestor_de_su_espacio_puede_marcar_asistencia(self, client, db):
        espacio = crear_espacio(db, nombre="Sala Asistio Gestor")
        gestor = crear_usuario(db, username="gestor_asist_ok", email="gestor_asist_ok@example.com", rol="gestor", espacio_id=espacio.id)
        usuario = crear_usuario(db, username="u_asist_g", email="u_asist_g@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=gestor)
        creada = client.post(
            "/reservas",
            json=payload_reserva_objetivos(recurso_ids=[recurso.id], fecha=fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        resp = client.put(f"/reservas/{creada['id']}/asistio", json={"asistio": True}, headers=cookies_para(gestor))
        assert resp.status_code == 200
        assert resp.json()["asistio"] is True
        # auditoría
        cambio = db.query(ControlCambio).filter(ControlCambio.entidad == "reserva", ControlCambio.entidad_id == creada["id"]).order_by(ControlCambio.id.desc()).first()
        assert cambio is not None
        assert cambio.accion == "marcar_asistencia"

    def test_admin_puede_marcar_asistencia_sin_restriccion_de_espacio(self, client, db):
        espacio = crear_espacio(db, nombre="Sala Asistio Admin")
        admin = crear_usuario(db, username="admin_asist_ok", email="admin_asist_ok@example.com", rol="admin")
        usuario = crear_usuario(db, username="u_asist_admin", email="u_asist_admin@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        creada = client.post(
            "/reservas",
            json=payload_reserva_objetivos(recurso_ids=[recurso.id], fecha=fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        resp = client.put(f"/reservas/{creada['id']}/asistio", json={"asistio": False}, headers=cookies_para(admin))
        assert resp.status_code == 200
        assert resp.json()["asistio"] is False

    def test_reserva_inexistente_da_404(self, client, db):
        admin = crear_usuario(db, username="admin_asist_404", email="admin_asist_404@example.com", rol="admin")
        resp = client.put("/reservas/999999/asistio", json={"asistio": True}, headers=cookies_para(admin))
        assert resp.status_code == 404

    def test_asistio_se_puede_alternar(self, client, db):
        espacio = crear_espacio(db, nombre="Sala Asistio Toggle")
        admin = crear_usuario(db, username="admin_asist_toggle", email="admin_asist_toggle@example.com", rol="admin")
        usuario = crear_usuario(db, username="u_asist_toggle", email="u_asist_toggle@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        creada = client.post(
            "/reservas",
            json=payload_reserva_objetivos(recurso_ids=[recurso.id], fecha=fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        assert client.put(f"/reservas/{creada['id']}/asistio", json={"asistio": True}, headers=cookies_para(admin)).json()["asistio"] is True
        assert client.put(f"/reservas/{creada['id']}/asistio", json={"asistio": False}, headers=cookies_para(admin)).json()["asistio"] is False
        # GET debe reflejar el último valor
        mis = client.get("/reservas/mis-reservas", headers=cookies_para(usuario)).json()
        encontrada = next(r for r in mis if r["id"] == creada["id"])
        assert encontrada["asistio"] is False
