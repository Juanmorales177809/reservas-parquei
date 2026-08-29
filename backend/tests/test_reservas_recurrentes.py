# -*- coding: utf-8 -*-
"""Pruebas de reservas recurrentes (2026-08-29, `repetir_semanas`/
`numero_ocurrencias` en `ReservaCreate`) -- "mejor esfuerzo": se crean las
ocurrencias sin conflicto, se reportan las que se saltaron y por qué.

Sin `repetir_semanas`, `POST /reservas` sigue devolviendo exactamente lo
mismo que antes de esta feature (retrocompatibilidad, ver
`~/.claude/plans/dazzling-wobbling-zebra.md`).
"""

from datetime import time, timedelta

from app.models import Reserva
from app.services.actores import columnas_actor

from tests.conftest import cookies_para, crear_espacio, crear_recurso, crear_usuario, fecha_habilitada, payload_reserva


def _setup(db, *, rol="usuario", es_gestor_del_espacio=False, nombre="Espacio Serie"):
    espacio = crear_espacio(db, nombre=nombre)
    usuario = crear_usuario(
        db,
        username=f"serie_{rol}_{nombre.replace(' ', '')}",
        email=f"serie-{rol}-{nombre.replace(' ', '')}@example.com",
        rol=rol,
        espacio_id=espacio.id if (rol == "gestor" and es_gestor_del_espacio) else None,
    )
    recurso = crear_recurso(db, espacio=espacio, usuario=usuario, nombre=f"Recurso {nombre}")
    return usuario, espacio, recurso


def test_sin_repetir_semanas_devuelve_reserva_unica_como_siempre(client, db):
    usuario, _, recurso = _setup(db)
    respuesta = client.post("/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario))
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert "id" in cuerpo
    assert "creadas" not in cuerpo


def test_crea_todas_las_ocurrencias_sin_conflicto(client, db):
    usuario, _, recurso = _setup(db, rol="gestor", es_gestor_del_espacio=True)
    fecha = fecha_habilitada()
    payload = payload_reserva(recurso.id, fecha)
    payload["repetir_semanas"] = 1
    payload["numero_ocurrencias"] = 3

    respuesta = client.post("/reservas", json=payload, headers=cookies_para(usuario))

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert len(cuerpo["creadas"]) == 3
    assert cuerpo["omitidas"] == []
    fechas = sorted(r["fecha"] for r in cuerpo["creadas"])
    esperadas = sorted((fecha + timedelta(weeks=i)).isoformat() for i in range(3))
    assert fechas == esperadas
    # Auto-aprobación (gestor de su propio espacio) también aplica por
    # ocurrencia, no solo a la primera.
    assert all(r["estado"] == "aprobada" for r in cuerpo["creadas"])


def test_mejor_esfuerzo_reporta_la_ocurrencia_en_conflicto(client, db):
    usuario, espacio, recurso = _setup(db, nombre="Espacio Conflicto Serie")
    otro = crear_usuario(db, username="otro_conflicto_serie", email="otro_conflicto_serie@example.com", rol="usuario")
    fecha = fecha_habilitada()
    fecha_ocupada = fecha + timedelta(weeks=1)

    # Ocupa de antemano, con OTRO actor, exactamente la 2da ocurrencia.
    db.add(
        Reserva(
            **columnas_actor(otro),
            espacio_id=espacio.id,
            recurso_id=recurso.id,
            fecha=fecha_ocupada,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            estado="aprobada",
            asistentes=1,
        )
    )
    db.commit()

    payload = payload_reserva(recurso.id, fecha)
    payload["repetir_semanas"] = 1
    payload["numero_ocurrencias"] = 3
    respuesta = client.post("/reservas", json=payload, headers=cookies_para(usuario))

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert len(cuerpo["creadas"]) == 2
    assert len(cuerpo["omitidas"]) == 1
    assert cuerpo["omitidas"][0]["fecha"] == fecha_ocupada.isoformat()
    fechas_creadas = {r["fecha"] for r in cuerpo["creadas"]}
    assert fecha_ocupada.isoformat() not in fechas_creadas


def test_repetir_semanas_sin_numero_ocurrencias_da_422(client, db):
    usuario, _, recurso = _setup(db, nombre="Espacio Solo Repetir")
    payload = payload_reserva(recurso.id, fecha_habilitada())
    payload["repetir_semanas"] = 1
    respuesta = client.post("/reservas", json=payload, headers=cookies_para(usuario))
    assert respuesta.status_code == 422


def test_numero_ocurrencias_fuera_de_rango_da_422(client, db):
    usuario, _, recurso = _setup(db, nombre="Espacio Rango")
    payload = payload_reserva(recurso.id, fecha_habilitada())
    payload["repetir_semanas"] = 1
    payload["numero_ocurrencias"] = 1
    respuesta = client.post("/reservas", json=payload, headers=cookies_para(usuario))
    assert respuesta.status_code == 422
