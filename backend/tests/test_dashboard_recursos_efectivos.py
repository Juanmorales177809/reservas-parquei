# -*- coding: utf-8 -*-
"""Pruebas de dashboard: `recursos_mas_reservados` cuenta por recurso
efectivo (`reserva_recursos`), no por la columna histórica singular
(Fase 12C-6).

Una reserva de espacio con N recursos efectivos materializa N filas en
`reserva_recursos`; el dashboard debe contar esas N filas (un recurso
reservado por reserva de espacio y luego directamente suma 2).
"""

from tests.conftest import (
    asociar_espacio_recurso,
    crear_laboratorio,
    crear_recurso,
    crear_usuario,
    crear_espacio,
    fecha_habilitada,
    cookies_para,
    payload_reserva_objetivos,
)


def _escenario(db):
    laboratorio = crear_laboratorio(db, nombre="Sala Dash Efectivo")
    admin = crear_usuario(db, username="admin_dash_efec", email="admin_dash_efec@example.com", rol="admin")
    r1 = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Efectivo R1")
    r2 = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Efectivo R2")
    espacio = crear_espacio(db, laboratorio=laboratorio, usuario=admin, nombre="Efectivo Espacio")
    asociar_espacio_recurso(db, espacio, r1)
    asociar_espacio_recurso(db, espacio, r2)
    return laboratorio, admin, r1, r2, espacio


def test_reserva_de_espacio_cuenta_sus_recursos_efectivos(client, db):
    _, admin, r1, r2, espacio = _escenario(db)
    creada = client.post(
        "/reservas",
        json=payload_reserva_objetivos(espacio_ids=[espacio.id], fecha=fecha_habilitada()),
        headers=cookies_para(admin),
    )
    assert creada.status_code == 201

    resumen = client.get("/admin/dashboard/summary", headers=cookies_para(admin)).json()
    conteos = {item["recurso_id"]: item["cantidad"] for item in resumen["recursos_mas_reservados"]}
    assert conteos.get(r1.id) == 1
    assert conteos.get(r2.id) == 1


def test_reserva_directa_adicional_suma_sobre_el_efectivo(client, db):
    laboratorio, admin, r1, r2, espacio = _escenario(db)
    primera = client.post(
        "/reservas",
        json=payload_reserva_objetivos(espacio_ids=[espacio.id], fecha=fecha_habilitada()),
        headers=cookies_para(admin),
    )
    assert primera.status_code == 201
    segunda = client.post(
        "/reservas",
        json=payload_reserva_objetivos(recurso_ids=[r1.id], fecha=fecha_habilitada(dias=12)),
        headers=cookies_para(admin),
    )
    assert segunda.status_code == 201

    resumen = client.get("/admin/dashboard/summary", headers=cookies_para(admin)).json()
    conteos = {item["recurso_id"]: item["cantidad"] for item in resumen["recursos_mas_reservados"]}
    assert conteos.get(r1.id) == 2
    assert conteos.get(r2.id) == 1


def test_reserva_singular_sigue_cuando_por_su_recurso(client, db):
    laboratorio, admin, r1, _, _ = _escenario(db)
    creada = client.post(
        "/reservas",
        json=payload_reserva_objetivos(recurso_ids=[r1.id], fecha=fecha_habilitada()),
        headers=cookies_para(admin),
    )
    assert creada.status_code == 201

    resumen = client.get("/admin/dashboard/summary", headers=cookies_para(admin)).json()
    conteos = {item["recurso_id"]: item["cantidad"] for item in resumen["recursos_mas_reservados"]}
    assert conteos.get(r1.id) == 1