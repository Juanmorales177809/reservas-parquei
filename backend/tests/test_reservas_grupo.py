# -*- coding: utf-8 -*-
"""Pruebas de integración de reservas multi-día agrupadas (2026-09-03,
`POST/GET /reservas/grupo`, `PUT /reservas/grupo/{id}/cancelar`).

Deliberadamente DISTINTO de la feature "reservas recurrentes" (revertida,
commit `f10ad62`): acá cada ocurrencia de la lista lleva su propio
`fecha`/`hora_inicio`/`hora_fin` -- no hay patrón de repetición semanal.
"""

from datetime import timedelta

from tests.conftest import (
    cookies_para,
    crear_laboratorio,
    crear_recurso,
    crear_usuario,
    fecha_habilitada,
    payload_reserva,
)


def _fechas(n: int):
    """`n` fechas espaciadas una semana entre sí (mismo día de la semana),
    para no tener que reevaluar Sábado/Domingo en cada una por separado --
    si la primera no cae en domingo, ninguna de las siguientes tampoco."""
    base = fecha_habilitada(dias=8)
    return [base + timedelta(days=7 * i) for i in range(n)]


def _payload_grupo(recurso_id, fechas, *, hora_inicio="08:00", hora_fin="10:00", asistentes=2):
    return {
        "recurso_ids": [recurso_id],
        "espacio_ids": [],
        "asistentes": asistentes,
        "ocurrencias": [
            {"fecha": f.isoformat(), "hora_inicio": hora_inicio, "hora_fin": hora_fin} for f in fechas
        ],
    }


def _setup(db, *, nombre="Sala Grupo"):
    laboratorio = crear_laboratorio(db, nombre=nombre)
    usuario = crear_usuario(db, username=f"user_{nombre.replace(' ', '')}", email=f"user-{nombre.replace(' ', '')}@example.com")
    recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)
    return usuario, laboratorio, recurso


class TestCrearGrupo:
    def test_crea_todas_las_ocurrencias_con_grupo_id_compartido(self, client, db):
        usuario, _, recurso = _setup(db)
        fechas = _fechas(3)

        respuesta = client.post(
            "/reservas/grupo",
            json=_payload_grupo(recurso.id, fechas),
            headers=cookies_para(usuario),
        )

        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert len(cuerpo["creadas"]) == 3
        assert cuerpo["omitidas"] == []
        grupo_id = cuerpo["grupo_id"]
        assert grupo_id
        assert all(r["grupo_id"] == grupo_id for r in cuerpo["creadas"])
        assert {r["fecha"] for r in cuerpo["creadas"]} == {f.isoformat() for f in fechas}

    def test_auto_aprobacion_se_aplica_por_ocurrencia(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Grupo Auto")
        laboratorio.aprobacion_automatica = True
        db.commit()
        usuario = crear_usuario(db, username="user_grupo_auto", email="user_grupo_auto@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)
        fechas = _fechas(2)

        respuesta = client.post(
            "/reservas/grupo",
            json=_payload_grupo(recurso.id, fechas),
            headers=cookies_para(usuario),
        )

        assert respuesta.status_code == 201
        creadas = respuesta.json()["creadas"]
        assert len(creadas) == 2
        assert all(r["estado"] == "aprobada" for r in creadas)

    def test_mejor_esfuerzo_una_ocurrencia_en_conflicto_no_aborta_las_demas(self, client, db):
        usuario, _, recurso = _setup(db, nombre="Sala Grupo Conflicto")
        fechas = _fechas(3)
        # Ocupa de antemano la fecha del medio con el mismo recurso/horario.
        ocupante = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fechas[1]),
            headers=cookies_para(usuario),
        )
        assert ocupante.status_code == 201

        respuesta = client.post(
            "/reservas/grupo",
            json=_payload_grupo(recurso.id, fechas),
            headers=cookies_para(usuario),
        )

        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert len(cuerpo["creadas"]) == 2
        assert len(cuerpo["omitidas"]) == 1
        assert cuerpo["omitidas"][0]["fecha"] == fechas[1].isoformat()
        assert {r["fecha"] for r in cuerpo["creadas"]} == {fechas[0].isoformat(), fechas[2].isoformat()}

    def test_una_sola_ocurrencia_da_422(self, client, db):
        usuario, _, recurso = _setup(db, nombre="Sala Grupo Una")
        respuesta = client.post(
            "/reservas/grupo",
            json=_payload_grupo(recurso.id, _fechas(1)),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 422

    def test_sin_ocurrencias_da_422(self, client, db):
        usuario, _, recurso = _setup(db, nombre="Sala Grupo Cero")
        payload = _payload_grupo(recurso.id, [])
        respuesta = client.post("/reservas/grupo", json=payload, headers=cookies_para(usuario))
        assert respuesta.status_code == 422

    def test_mas_de_treinta_ocurrencias_da_422(self, client, db):
        usuario, _, recurso = _setup(db, nombre="Sala Grupo Treinta")
        respuesta = client.post(
            "/reservas/grupo",
            json=_payload_grupo(recurso.id, _fechas(31)),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 422

    def test_sin_recurso_ni_espacio_da_422(self, client, db):
        usuario, _, _ = _setup(db, nombre="Sala Grupo Vacia")
        payload = {
            "recurso_ids": [],
            "espacio_ids": [],
            "asistentes": 2,
            "ocurrencias": [
                {"fecha": f.isoformat(), "hora_inicio": "08:00", "hora_fin": "10:00"} for f in _fechas(2)
            ],
        }
        respuesta = client.post("/reservas/grupo", json=payload, headers=cookies_para(usuario))
        assert respuesta.status_code == 422


class TestPostReservasSinCambios:
    """El endpoint existente `POST /reservas` no debe verse afectado por
    esta feature -- sigue devolviendo exactamente la forma de siempre, sin
    `grupo_id` en el payload de entrada."""

    def test_post_reservas_sigue_devolviendo_grupo_id_null(self, client, db):
        usuario, _, recurso = _setup(db, nombre="Sala Sin Grupo")
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["grupo_id"] is None


class TestListarGrupo:
    def test_dueno_ve_su_grupo(self, client, db):
        usuario, _, recurso = _setup(db, nombre="Sala Grupo Listar")
        creado = client.post(
            "/reservas/grupo",
            json=_payload_grupo(recurso.id, _fechas(2)),
            headers=cookies_para(usuario),
        ).json()
        grupo_id = creado["grupo_id"]

        respuesta = client.get(f"/reservas/grupo/{grupo_id}", headers=cookies_para(usuario))
        assert respuesta.status_code == 200
        assert len(respuesta.json()) == 2

    def test_otra_persona_no_ve_el_grupo_ajeno(self, client, db):
        usuario, _, recurso = _setup(db, nombre="Sala Grupo Ajeno")
        otro = crear_usuario(db, username="otro_grupo", email="otro_grupo@example.com")
        creado = client.post(
            "/reservas/grupo",
            json=_payload_grupo(recurso.id, _fechas(2)),
            headers=cookies_para(usuario),
        ).json()
        grupo_id = creado["grupo_id"]

        respuesta = client.get(f"/reservas/grupo/{grupo_id}", headers=cookies_para(otro))
        assert respuesta.status_code == 200
        assert respuesta.json() == []


class TestCancelarGrupo:
    def test_cancela_las_aprobadas_omite_las_esperando(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Grupo Cancelar")
        laboratorio.aprobacion_automatica = True
        db.commit()
        usuario = crear_usuario(db, username="user_grupo_cancelar", email="user_grupo_cancelar@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)
        creado = client.post(
            "/reservas/grupo",
            json=_payload_grupo(recurso.id, _fechas(2)),
            headers=cookies_para(usuario),
        ).json()
        grupo_id = creado["grupo_id"]
        assert all(r["estado"] == "aprobada" for r in creado["creadas"])

        respuesta = client.put(f"/reservas/grupo/{grupo_id}/cancelar", headers=cookies_para(usuario))
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert sorted(cuerpo["canceladas"]) == sorted(r["id"] for r in creado["creadas"])
        assert cuerpo["omitidas"] == []

    def test_ocurrencia_todavia_esperando_queda_omitida(self, client, db):
        usuario, _, recurso = _setup(db, nombre="Sala Grupo Cancelar Pendiente")
        creado = client.post(
            "/reservas/grupo",
            json=_payload_grupo(recurso.id, _fechas(2)),
            headers=cookies_para(usuario),
        ).json()
        grupo_id = creado["grupo_id"]
        assert all(r["estado"] == "esperando" for r in creado["creadas"])

        respuesta = client.put(f"/reservas/grupo/{grupo_id}/cancelar", headers=cookies_para(usuario))
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["canceladas"] == []
        assert len(cuerpo["omitidas"]) == 2

    def test_cancelar_un_solo_dia_no_afecta_al_resto_del_grupo(self, client, db):
        """No hace falta ningún endpoint de grupo para esto -- cada
        ocurrencia sigue siendo una Reserva independiente, cancelable vía
        el PUT /reservas/{id}/cancelar de siempre."""
        laboratorio = crear_laboratorio(db, nombre="Sala Grupo Cancelar Individual")
        laboratorio.aprobacion_automatica = True
        db.commit()
        usuario = crear_usuario(db, username="user_grupo_individual", email="user_grupo_individual@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)
        creado = client.post(
            "/reservas/grupo",
            json=_payload_grupo(recurso.id, _fechas(2)),
            headers=cookies_para(usuario),
        ).json()
        primera_id = creado["creadas"][0]["id"]
        segunda_id = creado["creadas"][1]["id"]

        respuesta = client.put(f"/reservas/{primera_id}/cancelar", headers=cookies_para(usuario))
        assert respuesta.status_code == 200
        assert respuesta.json()["estado"] == "cancelada"

        otra = client.get(f"/reservas/grupo/{creado['grupo_id']}", headers=cookies_para(usuario)).json()
        segunda = next(r for r in otra if r["id"] == segunda_id)
        assert segunda["estado"] == "aprobada"
