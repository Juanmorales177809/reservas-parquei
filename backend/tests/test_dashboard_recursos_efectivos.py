# -*- coding: utf-8 -*-
"""Pruebas de dashboard: `recursos_mas_reservados` cuenta por recurso
efectivo (`reserva_recursos`), no por la columna histórica singular
(Fase 12C-6).

Una reserva de zona con N recursos efectivos materializa N filas en
`reserva_recursos`; el dashboard debe contar esas N filas (un recurso
reservado por reserva de zona y luego directamente suma 2).
"""

from tests.conftest import (
    asociar_zona_recurso,
    crear_espacio,
    crear_recurso,
    crear_usuario,
    crear_zona,
    fecha_habilitada,
    cookies_para,
    payload_reserva_objetivos,
)


def _escenario(db):
    espacio = crear_espacio(db, nombre="Sala Dash Efectivo", modalidad_reserva="mixto")
    admin = crear_usuario(db, username="admin_dash_efec", email="admin_dash_efec@example.com", rol="admin")
    r1 = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Efectivo R1")
    r2 = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Efectivo R2")
    zona = crear_zona(db, espacio=espacio, usuario=admin, nombre="Efectivo Zona")
    asociar_zona_recurso(db, zona, r1)
    asociar_zona_recurso(db, zona, r2)
    return espacio, admin, r1, r2, zona


def test_reserva_de_zona_cuenta_sus_recursos_efectivos(client, db):
    _, admin, r1, r2, zona = _escenario(db)
    creada = client.post(
        "/reservas",
        json=payload_reserva_objetivos(zona_ids=[zona.id], fecha=fecha_habilitada()),
        headers=cookies_para(admin),
    )
    assert creada.status_code == 201

    resumen = client.get("/admin/dashboard/summary", headers=cookies_para(admin)).json()
    conteos = {item["recurso_id"]: item["cantidad"] for item in resumen["recursos_mas_reservados"]}
    assert conteos.get(r1.id) == 1
    assert conteos.get(r2.id) == 1


def test_reserva_directa_adicional_suma_sobre_el_efectivo(client, db):
    espacio, admin, r1, r2, zona = _escenario(db)
    primera = client.post(
        "/reservas",
        json=payload_reserva_objetivos(zona_ids=[zona.id], fecha=fecha_habilitada()),
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
    espacio, admin, r1, _, _ = _escenario(db)
    creada = client.post(
        "/reservas",
        json=payload_reserva_objetivos(recurso_ids=[r1.id], fecha=fecha_habilitada()),
        headers=cookies_para(admin),
    )
    assert creada.status_code == 201

    resumen = client.get("/admin/dashboard/summary", headers=cookies_para(admin)).json()
    conteos = {item["recurso_id"]: item["cantidad"] for item in resumen["recursos_mas_reservados"]}
    assert conteos.get(r1.id) == 1