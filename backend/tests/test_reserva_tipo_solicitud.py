# -*- coding: utf-8 -*-
"""Pruebas del campo `tipo_solicitud` de Reserva (Fase B).

Alcance: el `CheckConstraint` de base de datos (`ck_reservas_tipo_solicitud`)
acotado a los 2 valores que de verdad llegan por `ReservaCreate` hoy
(`reserva_en_laboratorio`, `reserva_fuera_laboratorio`). `orden_salida`
existe en el enum `TipoSolicitud` (Fase C, todavía no implementada) pero
NO está en este CHECK a propósito -- es la garantía estructural de que un
bug de ruteo en la Fase C no pueda colar una fila de ese tipo en `reservas`
sin que la base de datos la rechace. Ver el docstring de `TipoSolicitud`
en `app/domain/enums.py` y la sección "Fase C" del plan.
"""

from datetime import time as time_t

import pytest
from sqlalchemy.exc import IntegrityError

from app.domain.enums import TipoSolicitud
from app.models.reserva import Reserva
from app.services.actores import columnas_actor
from tests.conftest import crear_laboratorio, crear_recurso, crear_usuario, fecha_habilitada


def _crear_reserva_modelo(db, *, usuario, laboratorio, recurso, **kwargs):
    reserva = Reserva(
        **columnas_actor(usuario),
        laboratorio_id=laboratorio.id,
        recurso_id=recurso.id,
        fecha=kwargs.get("fecha", fecha_habilitada()),
        hora_inicio=kwargs.get("hora_inicio", time_t(8, 0)),
        hora_fin=kwargs.get("hora_fin", time_t(10, 0)),
        asistentes=kwargs.get("asistentes", 2),
        estado=kwargs.get("estado", "esperando"),
        tipo_solicitud=kwargs.get("tipo_solicitud", TipoSolicitud.RESERVA_EN_LABORATORIO.value),
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


class TestModelo:
    def test_default_es_reserva_en_laboratorio(self, db):
        laboratorio = crear_laboratorio(db)
        usuario = crear_usuario(db, username="ts_default", email="ts_default@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)
        reserva = Reserva(
            **columnas_actor(usuario),
            laboratorio_id=laboratorio.id,
            recurso_id=recurso.id,
            fecha=fecha_habilitada(),
            hora_inicio=time_t(8, 0),
            hora_fin=time_t(10, 0),
            asistentes=2,
            estado="esperando",
        )
        db.add(reserva)
        db.commit()
        db.refresh(reserva)
        assert reserva.tipo_solicitud == TipoSolicitud.RESERVA_EN_LABORATORIO.value

    @pytest.mark.parametrize(
        "valor",
        [TipoSolicitud.RESERVA_EN_LABORATORIO.value, TipoSolicitud.RESERVA_FUERA_LABORATORIO.value],
    )
    def test_los_dos_valores_del_check_se_aceptan(self, db, valor):
        laboratorio = crear_laboratorio(db)
        usuario = crear_usuario(db, username=f"ts_{valor}", email=f"ts_{valor}@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)
        reserva = _crear_reserva_modelo(db, usuario=usuario, laboratorio=laboratorio, recurso=recurso, tipo_solicitud=valor)
        assert reserva.tipo_solicitud == valor

    def test_orden_salida_rechazado_por_check_constraint(self, db):
        """La pieza central de la Fase B: aunque `TipoSolicitud.ORDEN_SALIDA`
        existe en el enum de dominio, la base de datos todavía no lo acepta
        en `reservas` -- confirma que el CHECK está acotado a 2 valores, no
        a los 3 del enum completo."""
        laboratorio = crear_laboratorio(db)
        usuario = crear_usuario(db, username="ts_orden_salida", email="ts_orden_salida@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)
        reserva = Reserva(
            **columnas_actor(usuario),
            laboratorio_id=laboratorio.id,
            recurso_id=recurso.id,
            fecha=fecha_habilitada(),
            hora_inicio=time_t(8, 0),
            hora_fin=time_t(10, 0),
            asistentes=2,
            estado="esperando",
            tipo_solicitud=TipoSolicitud.ORDEN_SALIDA.value,
        )
        db.add(reserva)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_valor_arbitrario_rechazado_por_check_constraint(self, db):
        laboratorio = crear_laboratorio(db)
        usuario = crear_usuario(db, username="ts_inv", email="ts_inv@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)
        reserva = Reserva(
            **columnas_actor(usuario),
            laboratorio_id=laboratorio.id,
            recurso_id=recurso.id,
            fecha=fecha_habilitada(),
            hora_inicio=time_t(8, 0),
            hora_fin=time_t(10, 0),
            asistentes=2,
            estado="esperando",
            tipo_solicitud="motivo_inventado",
        )
        db.add(reserva)
        with pytest.raises(IntegrityError):
            db.commit()
