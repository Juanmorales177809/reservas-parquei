# -*- coding: utf-8 -*-
"""Pruebas de integración del cálculo de ocupación real (Fase 4).

Reglas cubiertas:
- La ocupación usa el horario_atencion real de cada espacio (no range(7,20)).
- Una reserva fuera del horario no aumenta la ocupación (datos legacy).
- Un día sin atención aporta cero horas disponibles y no divide entre cero.
- Las horas atendidas fuera del grid 7-20 del heatmap se cuentan en
  ocupacion_global aunque el gráfico no las muestre (limitación documentada).

Las fechas son fijas (2026-08-17 es lunes) y las reservas se insertan
directamente en la base para simular datos históricos que el servicio
actual ya no permitiría.
"""

from datetime import date, time

from app.models import Reserva
from tests.conftest import crear_espacio, crear_recurso, crear_usuario, cookies_para

LUNES = date(2026, 8, 17)  # weekday 0
DOMINGO = date(2026, 8, 23)  # weekday 6


def _admin_y_headers(db):
    admin = crear_usuario(db, username="admin_dash", email="admin_dash@example.com", rol="admin")
    return admin, cookies_para(admin)


def _reserva_directa(db, usuario, espacio, recurso, fecha, inicio, fin, estado="aprobada"):
    db.add(
        Reserva(
            usuario_id=usuario.id,
            espacio_id=espacio.id,
            recurso_id=recurso.id,
            fecha=fecha,
            hora_inicio=inicio,
            hora_fin=fin,
            estado=estado,
            asistentes=1,
        )
    )
    db.commit()


def _espacio_reducido(db, usuario, horario):
    espacio = crear_espacio(db, nombre="Sala Ocup", horario_atencion=horario)
    recurso = crear_recurso(db, espacio=espacio, usuario=usuario)
    return espacio, recurso


def _resumen(client, headers):
    respuesta = client.get("/admin/dashboard/summary", headers=headers)
    assert respuesta.status_code == 200
    return respuesta.json()["ocupacion_global"]


def test_espacio_horario_reducido_calcula_ocupacion_real(client, db):
    admin, headers = _admin_y_headers(db)
    espacio, recurso = _espacio_reducido(db, admin, {"0": [8, 9]})
    _reserva_directa(db, admin, espacio, recurso, LUNES, time(8, 0), time(10, 0))
    resumen = _resumen(client, headers)
    assert resumen["horas_ocupadas"] == 2.0
    assert resumen["horas_disponibles"] == 2.0
    assert resumen["porcentaje"] == 100.0


def test_reserva_fuera_del_horario_no_cuenta(client, db):
    admin, headers = _admin_y_headers(db)
    espacio, recurso = _espacio_reducido(db, admin, {"0": [8, 9]})
    _reserva_directa(db, admin, espacio, recurso, LUNES, time(7, 0), time(8, 0))
    resumen = _resumen(client, headers)
    assert resumen["horas_ocupadas"] == 0.0


def test_hora_atendida_antes_de_las_7_cuenta(client, db):
    admin, headers = _admin_y_headers(db)
    espacio, recurso = _espacio_reducido(db, admin, {"0": [6]})
    _reserva_directa(db, admin, espacio, recurso, LUNES, time(6, 0), time(7, 0))
    resumen = _resumen(client, headers)
    assert resumen["horas_ocupadas"] == 1.0


def test_dia_sin_atencion_aporta_cero_disponibles_y_no_divide(client, db):
    admin, headers = _admin_y_headers(db)
    espacio, recurso = _espacio_reducido(db, admin, {"0": [8, 9]})
    _reserva_directa(db, admin, espacio, recurso, DOMINGO, time(8, 0), time(10, 0))
    resumen = _resumen(client, headers)
    assert resumen["horas_ocupadas"] == 0.0
    assert resumen["horas_disponibles"] == 0.0
    assert resumen["porcentaje"] == 0.0


def test_sin_reservas_no_hay_division_entre_cero(client, db):
    admin, headers = _admin_y_headers(db)
    _espacio_reducido(db, admin, {"0": [8, 9]})
    resumen = _resumen(client, headers)
    assert resumen["horas_ocupadas"] == 0.0
    assert resumen["horas_disponibles"] == 0.0
    assert resumen["porcentaje"] == 0.0


def test_espacio_con_varias_franjas_suma_horas_atendidas(client, db):
    admin, headers = _admin_y_headers(db)
    espacio, recurso = _espacio_reducido(db, admin, {"0": [8, 9, 12]})
    _reserva_directa(db, admin, espacio, recurso, LUNES, time(8, 0), time(9, 0))
    _reserva_directa(db, admin, espacio, recurso, LUNES, time(12, 0), time(13, 0))
    resumen = _resumen(client, headers)
    assert resumen["horas_ocupadas"] == 2.0
    assert resumen["horas_disponibles"] == 3.0
    assert resumen["porcentaje"] == round(2 / 3 * 100, 2)


def test_conserva_tipos_del_esquema_actual(client, db):
    admin, headers = _admin_y_headers(db)
    _espacio_reducido(db, admin, {"0": [8, 9]})
    resumen = client.get("/admin/dashboard/summary", headers=headers).json()
    global_ = resumen["ocupacion_global"]
    assert isinstance(global_["horas_ocupadas"], float)
    assert isinstance(global_["horas_disponibles"], float)
    assert isinstance(global_["porcentaje"], float)
    assert len(resumen["ocupacion_por_dia_hora"]) == 7 * 13  # grid 7 días x 7..19
