# -*- coding: utf-8 -*-
"""Pruebas del campo `tipo` de Reserva (Fase 12D, parcial).

Alcance de esta subfase: el campo de tipo de reserva académica
(TRABAJO_INVESTIGACION / TRABAJO_GRADO / SERVICIO_DE_ENSAYO) en Reserva,
el `CheckConstraint` que lo valida en base de datos y el gate PS que exige
`tipo == servicio_de_ensayo` para recursos PS reservados por gestor/admin
(el rol usuario sigue bloqueado antes de llegar a ese chequeo, sin cambios).

Fuera de alcance, incluso aquí: `Proyecto` (entidad, parte de 12D) queda
pendiente como ya estaba; ver CHANGELOG.md.
"""

from datetime import time as time_t

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.domain.enums import TipoReserva
from app.models.reserva import Reserva
from app.schemas.reserva import ReservaCreate, ReservaUpdate
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
        tipo=kwargs.get("tipo"),
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


class TestModelo:
    def test_tipo_nulo_por_defecto(self, db):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username="tipo_nulo", email="tipo_nulo@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=usuario)
        reserva = _crear_reserva_modelo(db, usuario=usuario, espacio=espacio, recurso=recurso)
        assert reserva.tipo is None

    @pytest.mark.parametrize(
        "valor",
        [
            TipoReserva.TRABAJO_INVESTIGACION.value,
            TipoReserva.TRABAJO_GRADO.value,
            TipoReserva.SERVICIO_DE_ENSAYO.value,
        ],
    )
    def test_los_tres_valores_validos_se_aceptan(self, db, valor):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username=f"tipo_{valor}", email=f"tipo_{valor}@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=usuario)
        reserva = _crear_reserva_modelo(db, usuario=usuario, espacio=espacio, recurso=recurso, tipo=valor)
        assert reserva.tipo == valor

    def test_valor_invalido_rechazado_por_check_constraint(self, db):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username="tipo_inv", email="tipo_inv@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=usuario)
        reserva = Reserva(
            usuario_id=usuario.id,
            espacio_id=espacio.id,
            recurso_id=recurso.id,
            fecha=fecha_habilitada(),
            hora_inicio=time_t(8, 0),
            hora_fin=time_t(10, 0),
            asistentes=2,
            estado="esperando",
            tipo="catedra",
        )
        db.add(reserva)
        with pytest.raises(IntegrityError):
            db.commit()


class TestSchemas:
    @pytest.mark.parametrize(
        "valor",
        [
            TipoReserva.TRABAJO_INVESTIGACION.value,
            TipoReserva.TRABAJO_GRADO.value,
            TipoReserva.SERVICIO_DE_ENSAYO.value,
        ],
    )
    def test_create_acepta_cada_valor_del_enum(self, valor):
        modelo = ReservaCreate(
            recurso_ids=[1],
            fecha="2026-09-01",
            hora_inicio="08:00",
            hora_fin="10:00",
            asistentes=2,
            tipo=valor,
        )
        assert isinstance(modelo.tipo, TipoReserva)

    def test_create_sin_tipo_defaults_a_none(self):
        modelo = ReservaCreate(recurso_ids=[1], fecha="2026-09-01", hora_inicio="08:00", hora_fin="10:00", asistentes=2)
        assert modelo.tipo is None

    def test_create_tipo_none_explicito_es_valido(self):
        modelo = ReservaCreate(
            recurso_ids=[1], fecha="2026-09-01", hora_inicio="08:00", hora_fin="10:00", asistentes=2, tipo=None
        )
        assert modelo.tipo is None

    def test_create_valor_fuera_del_enum_rechazado(self):
        with pytest.raises(ValidationError):
            ReservaCreate(
                recurso_ids=[1], fecha="2026-09-01", hora_inicio="08:00", hora_fin="10:00", asistentes=2, tipo="bogus"
            )

    @pytest.mark.parametrize(
        "valor",
        [
            TipoReserva.TRABAJO_INVESTIGACION.value,
            TipoReserva.TRABAJO_GRADO.value,
            TipoReserva.SERVICIO_DE_ENSAYO.value,
        ],
    )
    def test_update_acepta_cada_valor_del_enum(self, valor):
        modelo = ReservaUpdate(tipo=valor)
        assert isinstance(modelo.tipo, TipoReserva)

    def test_update_sin_tipo_defaults_a_none(self):
        modelo = ReservaUpdate(asistentes=5)
        assert modelo.tipo is None

    def test_update_tipo_none_explicito_es_valido(self):
        modelo = ReservaUpdate(tipo=None)
        assert modelo.tipo is None

    def test_update_valor_fuera_del_enum_rechazado(self):
        with pytest.raises(ValidationError):
            ReservaUpdate(tipo="bogus")


class TestApi:
    def test_post_persiste_tipo(self, client, db):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username="api_tipo1", email="api_tipo1@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=usuario)
        payload = payload_reserva_objetivos(recurso_ids=[recurso.id], fecha=fecha_habilitada())
        payload["tipo"] = TipoReserva.TRABAJO_GRADO.value
        respuesta = client.post("/reservas", json=payload, headers=cookies_para(usuario))
        assert respuesta.status_code == 201
        assert respuesta.json()["tipo"] == TipoReserva.TRABAJO_GRADO.value

    def test_post_sin_tipo_deja_tipo_nulo(self, client, db):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username="api_tipo2", email="api_tipo2@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=usuario)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva_objetivos(recurso_ids=[recurso.id], fecha=fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["tipo"] is None

    def test_patch_actualiza_tipo(self, client, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="api_tipo3", email="api_tipo3@example.com", rol="admin")
        usuario = crear_usuario(db, username="api_tipo3b", email="api_tipo3b@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        creada = client.post(
            "/reservas",
            json=payload_reserva_objetivos(recurso_ids=[recurso.id], fecha=fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        respuesta = client.patch(
            f"/reservas/{creada['id']}",
            json={"tipo": TipoReserva.SERVICIO_DE_ENSAYO.value},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["tipo"] == TipoReserva.SERVICIO_DE_ENSAYO.value

    def test_patch_sin_tipo_en_el_payload_lo_deja_sin_cambios(self, client, db):
        """Es el caso que se rompería en silencio si la actualización no
        usara `cambios.get("tipo", reserva.tipo)` (eje ausente = conservar)."""
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="api_tipo4", email="api_tipo4@example.com", rol="admin")
        usuario = crear_usuario(db, username="api_tipo4b", email="api_tipo4b@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        payload = payload_reserva_objetivos(recurso_ids=[recurso.id], fecha=fecha_habilitada())
        payload["tipo"] = TipoReserva.TRABAJO_INVESTIGACION.value
        creada = client.post("/reservas", json=payload, headers=cookies_para(usuario)).json()
        respuesta = client.patch(
            f"/reservas/{creada['id']}",
            json={"asistentes": 3},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["asistentes"] == 3
        assert respuesta.json()["tipo"] == TipoReserva.TRABAJO_INVESTIGACION.value

    def test_patch_con_tipo_nulo_explicito_lo_limpia(self, client, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="api_tipo5", email="api_tipo5@example.com", rol="admin")
        usuario = crear_usuario(db, username="api_tipo5b", email="api_tipo5b@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        payload = payload_reserva_objetivos(recurso_ids=[recurso.id], fecha=fecha_habilitada())
        payload["tipo"] = TipoReserva.TRABAJO_GRADO.value
        creada = client.post("/reservas", json=payload, headers=cookies_para(usuario)).json()
        respuesta = client.patch(
            f"/reservas/{creada['id']}",
            json={"tipo": None},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["tipo"] is None

    def test_post_con_tipo_fuera_del_enum_da_422(self, client, db):
        espacio = crear_espacio(db)
        usuario = crear_usuario(db, username="api_tipo6", email="api_tipo6@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=usuario)
        payload = payload_reserva_objetivos(recurso_ids=[recurso.id], fecha=fecha_habilitada())
        payload["tipo"] = "catedra"
        respuesta = client.post("/reservas", json=payload, headers=cookies_para(usuario))
        assert respuesta.status_code == 422