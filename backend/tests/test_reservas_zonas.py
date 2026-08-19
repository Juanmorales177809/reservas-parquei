# -*- coding: utf-8 -*-
"""Pruebas de la Fase 12C-6: reservas por recursos directos y/o zonas.

Contrato nuevo (aprobado):
- `ReservaCreate` usa `recurso_ids`/`zona_ids` (listas); `recurso_id`
  legacy -> 422 (`extra="forbid"`).
- Al menos un recurso o zona; modalidad `equipos`/`zonas`/`mixto`.
- Reservar una zona crea su fila en `reserva_zonas` y materializa sus
  recursos efectivos en `reserva_recursos` (dedupe); una zona sin recursos
  asociados sigue siendo válida.
- El solapamiento se valida en cada recurso efectivo y en cada zona
  (transitividad zona <-> recursos efectivos).
- Capacidad efectiva = min(espacio, zonas definidas, recursos efectivos).
- `reservas.recurso_id` = recurso efectivo canónico (orden estable por id).

RED -> GREEN: estos tests fallan contra el código anterior (schema singular
con `recurso_id`), porque el payload nuevo devuelve 422 y no materializa nada.
"""

from app.models.reserva import Reserva
from app.models.reserva_recurso import ReservaRecurso
from app.models.reserva_zona import ReservaZona
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


def _payload(*, recurso_ids=None, zona_ids=None, **kw):
    return payload_reserva_objetivos(
        recurso_ids=recurso_ids or [],
        zona_ids=zona_ids or [],
        fecha=fecha_habilitada(),
        **kw,
    )


def _setup(db, modalidad="mixto", nombre="Sala Zonas Mixta"):
    espacio = crear_espacio(db, nombre=nombre, modalidad_reserva=modalidad)
    usuario = crear_usuario(
        db,
        username=f"u_{nombre.replace(' ', '')}",
        email=f"u_{nombre.replace(' ', '')}@example.com",
    )
    r1 = crear_recurso(db, espacio=espacio, usuario=usuario, nombre="R1")
    r2 = crear_recurso(db, espacio=espacio, usuario=usuario, nombre="R2")
    return espacio, usuario, r1, r2


class TestContratoEntrada:
    def test_payload_legacy_recurso_id_da_422(self, client, db):
        espacio, usuario, recurso, _ = _setup(db)
        respuesta = client.post(
            "/reservas",
            json={
                "recurso_id": recurso.id,
                "fecha": fecha_habilitada().isoformat(),
                "hora_inicio": "08:00",
                "hora_fin": "10:00",
                "asistentes": 2,
            },
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 422

    def test_update_legacy_recurso_id_da_422(self, client, db):
        espacio, usuario, recurso, _ = _setup(db)
        creada = client.post(
            "/reservas", json=_payload(recurso_ids=[recurso.id]), headers=cookies_para(usuario)
        ).json()
        respuesta = client.patch(
            f"/reservas/{creada['id']}",
            json={"recurso_id": recurso.id},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 422

    def test_seleccion_vacia_da_422(self, client, db):
        _, usuario, _, _ = _setup(db)
        respuesta = client.post(
            "/reservas", json=_payload(), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 422


class TestModalidad:
    def test_equipos_no_acepta_zonas(self, client, db):
        espacio, usuario, r1, _ = _setup(db, modalidad="equipos", nombre="Sala Equipos")
        zona = crear_zona(db, espacio=espacio, usuario=usuario)
        respuesta = client.post(
            "/reservas", json=_payload(zona_ids=[zona.id]), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 400

    def test_zonas_no_acepta_recursos_directos(self, client, db):
        espacio, usuario, r1, _ = _setup(db, modalidad="zonas", nombre="Sala Solo Zonas")
        respuesta = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id]), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 400

    def test_zonas_acepta_zona(self, client, db):
        espacio, usuario, r1, _ = _setup(db, modalidad="zonas", nombre="Sala Solo Zonas B")
        zona = crear_zona(db, espacio=espacio, usuario=usuario)
        asociar_zona_recurso(db, zona, r1)
        respuesta = client.post(
            "/reservas", json=_payload(zona_ids=[zona.id]), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 201

    def test_mixto_acepta_ambos(self, client, db):
        espacio, usuario, r1, r2 = _setup(db)
        zona = crear_zona(db, espacio=espacio, usuario=usuario)
        asociar_zona_recurso(db, zona, r2)
        respuesta = client.post(
            "/reservas",
            json=_payload(recurso_ids=[r1.id], zona_ids=[zona.id]),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201


class TestReservasObjetivo:
    def test_recurso_directo_materializa_una_fila(self, client, db):
        espacio, usuario, r1, _ = _setup(db, modalidad="equipos", nombre="Sala Directo")
        respuesta = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id]), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["recurso_ids"] == [r1.id]
        assert [r["id"] for r in cuerpo["recursos"]] == [r1.id]
        assert cuerpo["zona_ids"] == []
        assert db.query(ReservaRecurso).count() == 1
        assert db.query(ReservaZona).count() == 0

    def test_zona_con_recursos_materializa_sus_efectivos(self, client, db):
        espacio, usuario, r1, r2 = _setup(db, modalidad="zonas", nombre="Sala Zona Con Recurso")
        zona = crear_zona(db, espacio=espacio, usuario=usuario, nombre="Zona A")
        asociar_zona_recurso(db, zona, r1)
        asociar_zona_recurso(db, zona, r2)
        respuesta = client.post(
            "/reservas", json=_payload(zona_ids=[zona.id]), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["zona_ids"] == [zona.id]
        assert sorted(cuerpo["recurso_ids"]) == sorted([r1.id, r2.id])
        assert len(cuerpo["zonas"]) == 1
        assert cuerpo["zonas"][0]["nombre"] == "Zona A"
        assert sorted(r["id"] for r in cuerpo["recursos"]) == sorted([r1.id, r2.id])
        reserva = db.query(Reserva).filter(Reserva.id == cuerpo["id"]).one()
        assert reserva.recurso_id == min(r1.id, r2.id)
        assert db.query(ReservaZona).count() == 1
        assert sorted(rr.recurso_id for rr in db.query(ReservaRecurso).all()) == sorted([r1.id, r2.id])

    def test_zona_sin_recursos_sigue_siendo_valida(self, client, db):
        espacio, usuario, r1, _ = _setup(db)
        zona = crear_zona(db, espacio=espacio, usuario=usuario, nombre="Zona Vacia")
        respuesta = client.post(
            "/reservas", json=_payload(zona_ids=[zona.id]), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["zona_ids"] == [zona.id]
        assert cuerpo["recurso_ids"] == []
        assert len(cuerpo["zonas"]) == 1
        assert db.query(ReservaZona).count() == 1
        assert db.query(ReservaRecurso).count() == 0
        reserva = db.query(Reserva).filter(Reserva.id == cuerpo["id"]).one()
        assert reserva.recurso_id == r1.id

    def test_reserva_mixta_dedupe_recursos_efectivos(self, client, db):
        espacio, usuario, r1, _ = _setup(db)
        zona = crear_zona(db, espacio=espacio, usuario=usuario)
        asociar_zona_recurso(db, zona, r1)
        respuesta = client.post(
            "/reservas",
            json=_payload(recurso_ids=[r1.id], zona_ids=[zona.id]),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["recurso_ids"] == [r1.id]
        assert cuerpo["zona_ids"] == [zona.id]
        assert db.query(ReservaRecurso).count() == 1
        assert db.query(ReservaZona).count() == 1


class TestActualizacionPorEjes:
    def test_conserva_ejes_ausentes(self, client, db):
        espacio, usuario, r1, r2 = _setup(db)
        zona = crear_zona(db, espacio=espacio, usuario=usuario)
        creada = client.post(
            "/reservas",
            json=_payload(recurso_ids=[r1.id], zona_ids=[zona.id]),
            headers=cookies_para(usuario),
        ).json()
        otra_fecha = fecha_habilitada(dias=12)
        actualizada = client.patch(
            f"/reservas/{creada['id']}",
            json={"fecha": otra_fecha.isoformat()},
            headers=cookies_para(usuario),
        )
        assert actualizada.status_code == 200
        cuerpo = actualizada.json()
        assert cuerpo["recurso_ids"] == [r1.id]
        assert cuerpo["zona_ids"] == [zona.id]

    def test_reemplaza_eje_recursos(self, client, db):
        espacio, usuario, r1, r2 = _setup(db)
        zona = crear_zona(db, espacio=espacio, usuario=usuario)
        creada = client.post(
            "/reservas",
            json=_payload(recurso_ids=[r1.id], zona_ids=[zona.id]),
            headers=cookies_para(usuario),
        ).json()
        actualizada = client.patch(
            f"/reservas/{creada['id']}",
            json={"recurso_ids": [r2.id]},
            headers=cookies_para(usuario),
        )
        assert actualizada.status_code == 200
        cuerpo = actualizada.json()
        assert cuerpo["recurso_ids"] == [r2.id]
        assert cuerpo["zona_ids"] == [zona.id]
        assert db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == creada["id"]).count() == 1

    def test_reemplaza_eje_zonas(self, client, db):
        espacio, usuario, r1, _ = _setup(db)
        zona_a = crear_zona(db, espacio=espacio, usuario=usuario, nombre="Zona A")
        zona_b = crear_zona(db, espacio=espacio, usuario=usuario, nombre="Zona B")
        creada = client.post(
            "/reservas",
            json=_payload(zona_ids=[zona_a.id]),
            headers=cookies_para(usuario),
        ).json()
        actualizada = client.patch(
            f"/reservas/{creada['id']}",
            json={"zona_ids": [zona_b.id]},
            headers=cookies_para(usuario),
        )
        assert actualizada.status_code == 200
        cuerpo = actualizada.json()
        assert cuerpo["zona_ids"] == [zona_b.id]
        assert db.query(ReservaZona).filter(ReservaZona.reserva_id == creada["id"]).count() == 1

    def test_resultado_vacio_rechazado(self, client, db):
        espacio, usuario, r1, _ = _setup(db)
        creada = client.post(
            "/reservas",
            json=_payload(recurso_ids=[r1.id]),
            headers=cookies_para(usuario),
        ).json()
        respuesta = client.patch(
            f"/reservas/{creada['id']}",
            json={"recurso_ids": [], "zona_ids": []},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 400


class TestSolapamientoTransitivo:
    def test_solapamiento_directo_409(self, client, db):
        espacio, usuario, r1, _ = _setup(db, modalidad="equipos", nombre="Sala Over Directo")
        primera = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id]), headers=cookies_para(usuario)
        )
        assert primera.status_code == 201
        segunda = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id]), headers=cookies_para(usuario)
        )
        assert segunda.status_code == 409

    def test_zona_a_recurso_409(self, client, db):
        espacio, usuario, r1, _ = _setup(db)
        zona = crear_zona(db, espacio=espacio, usuario=usuario)
        asociar_zona_recurso(db, zona, r1)
        zona_reservada = client.post(
            "/reservas", json=_payload(zona_ids=[zona.id]), headers=cookies_para(usuario)
        )
        assert zona_reservada.status_code == 201
        directa = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id]), headers=cookies_para(usuario)
        )
        assert directa.status_code == 409

    def test_recurso_a_zona_409(self, client, db):
        espacio, usuario, r1, _ = _setup(db)
        zona = crear_zona(db, espacio=espacio, usuario=usuario)
        asociar_zona_recurso(db, zona, r1)
        directa = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id]), headers=cookies_para(usuario)
        )
        assert directa.status_code == 201
        zona_reservada = client.post(
            "/reservas", json=_payload(zona_ids=[zona.id]), headers=cookies_para(usuario)
        )
        assert zona_reservada.status_code == 409

    def test_zona_sin_recursos_ancla_al_recurso_de_menor_id(self, client, db):
        espacio, usuario, r1, r2 = _setup(db)
        zona = crear_zona(db, espacio=espacio, usuario=usuario)
        zona_reservada = client.post(
            "/reservas", json=_payload(zona_ids=[zona.id]), headers=cookies_para(usuario)
        )
        assert zona_reservada.status_code == 201
        # Fase 12C-4e-schemas: `recurso_id` ya no está en la respuesta; el
        # ancla se confirma contra la columna histórica directamente.
        reserva = db.query(Reserva).filter(Reserva.id == zona_reservada.json()["id"]).one()
        assert reserva.recurso_id == r1.id
        # Una zona sin recursos no materializa nada: no bloquea recursos
        # ajenos al ancla histórico.
        otra = client.post(
            "/reservas", json=_payload(recurso_ids=[r2.id]), headers=cookies_para(usuario)
        )
        assert otra.status_code == 201
        # Riesgo residual documentado (decisión 12C-6): el ancla vive en la
        # columna histórica `reservas.recurso_id` y la EXCLUDE histórica
        # `reservas_sin_solapamiento` sigue activa, así que una reserva
        # directa del recurso ancla en el mismo horario choca con 409.
        ancla = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id]), headers=cookies_para(usuario)
        )
        assert ancla.status_code == 409


class TestAprobacion:
    def test_aprobar_zona_sincroniza_y_bloquea_transitivamente(self, client, db):
        espacio, usuario, r1, r2 = _setup(db, modalidad="mixto", nombre="Sala Aprobar Zona")
        zona = crear_zona(db, espacio=espacio, usuario=usuario, nombre="Zona Aprobar")
        asociar_zona_recurso(db, zona, r1)
        gestor = crear_usuario(
            db, username="gestor_aprob", email="gestor_aprob@example.com",
            rol="gestor", espacio_id=espacio.id,
        )
        creada = client.post(
            "/reservas", json=_payload(zona_ids=[zona.id]), headers=cookies_para(usuario)
        )
        assert creada.status_code == 201
        assert creada.json()["estado"] == "esperando"
        aprobada = client.put(
            f"/reservas/{creada.json()['id']}/estado",
            json={"nuevo_estado": "aprobada"},
            headers=cookies_para(gestor),
        )
        assert aprobada.status_code == 200
        assert aprobada.json()["estado"] == "aprobada"
        fila_zona = db.query(ReservaZona).one()
        fila_recurso = db.query(ReservaRecurso).one()
        assert fila_zona.estado == "aprobada"
        assert fila_recurso.estado == "aprobada"
        # Transitividad: la zona aprobada reclama su recurso efectivo (r1) y
        # bloquea una reserva directa de r1 en el mismo horario.
        segunda = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id]), headers=cookies_para(usuario)
        )
        assert segunda.status_code == 409


class TestCapacidad:
    def test_capacidad_efectiva_es_el_minimo(self, client, db):
        espacio, usuario, r1, _ = _setup(db)
        zona = crear_zona(db, espacio=espacio, usuario=usuario, capacidad=8)
        asociar_zona_recurso(db, zona, r1)
        excede = client.post(
            "/reservas", json=_payload(zona_ids=[zona.id], asistentes=9), headers=cookies_para(usuario)
        )
        assert excede.status_code == 400
        justo = client.post(
            "/reservas", json=_payload(zona_ids=[zona.id], asistentes=8), headers=cookies_para(usuario)
        )
        assert justo.status_code == 201

    def test_capacidad_directa_limitada_tambien_por_espacio(self, client, db):
        espacio = crear_espacio(db, nombre="Sala Cap Baja", modalidad_reserva="mixto", capacidad=5)
        usuario = crear_usuario(db, username="u_cap", email="u_cap@example.com")
        r1 = crear_recurso(db, espacio=espacio, usuario=usuario, capacidad=10)
        respuesta = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id], asistentes=7), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 400


class TestPS:
    def test_zona_con_recurso_ps_bloquea_usuario(self, client, db):
        espacio = crear_espacio(db, nombre="Sala PS Zona", modalidad_reserva="mixto")
        admin = crear_usuario(db, username="admin_ps_zonas", email="admin_ps_zonas@example.com", rol="admin")
        usuario = crear_usuario(db, username="u_ps_zonas", email="u_ps_zonas@example.com")
        r_normal = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Normal")
        r_ps = crear_recurso(
            db, espacio=espacio, usuario=admin, nombre="PS", es_prestacion_servicio=True
        )
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        asociar_zona_recurso(db, zona, r_ps)
        bloqueado = client.post(
            "/reservas", json=_payload(zona_ids=[zona.id]), headers=cookies_para(usuario)
        )
        assert bloqueado.status_code == 403
        permitido = client.post(
            "/reservas", json=_payload(zona_ids=[zona.id]), headers=cookies_para(admin)
        )
        assert permitido.status_code == 201


class TestPermisos:
    def test_recursos_y_zonas_de_espacios_distintos_da_400(self, client, db):
        espacio_a, usuario, r1, _ = _setup(db, modalidad="mixto", nombre="Espacio A")
        espacio_b = crear_espacio(db, nombre="Espacio B", modalidad_reserva="mixto")
        zona_b = crear_zona(db, espacio=espacio_b, usuario=usuario)
        respuesta = client.post(
            "/reservas",
            json=_payload(recurso_ids=[r1.id], zona_ids=[zona_b.id]),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_gestor_puede_reservar_zona_de_otro_espacio_queda_esperando(self, client, db):
        espacio_a = crear_espacio(db, nombre="Espacio Gestor A", modalidad_reserva="zonas")
        gestor = crear_usuario(
            db, username="gestor_zonas_a", email="gestor_zonas_a@example.com",
            rol="gestor", espacio_id=espacio_a.id,
        )
        espacio_b = crear_espacio(db, nombre="Espacio Gestor B", modalidad_reserva="zonas")
        recurso_b = crear_recurso(db, espacio=espacio_b, usuario=gestor, nombre="RB")
        zona_b = crear_zona(db, espacio=espacio_b, usuario=gestor)
        asociar_zona_recurso(db, zona_b, recurso_b)
        respuesta = client.post(
            "/reservas", json=_payload(zona_ids=[zona_b.id]), headers=cookies_para(gestor)
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["estado"] == "esperando"