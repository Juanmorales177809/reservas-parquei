# -*- coding: utf-8 -*-
"""Pruebas de la Fase 12C-6: reservas por recursos directos y/o espacios.

Contrato nuevo (aprobado):
- `ReservaCreate` usa `recurso_ids`/`espacio_ids` (listas); `recurso_id`
  legacy -> 422 (`extra="forbid"`).
- Al menos un recurso o espacio.
- Reservar una espacio crea su fila en `reserva_espacios` y materializa sus
  recursos efectivos en `reserva_recursos` (dedupe); una espacio sin recursos
  asociados sigue siendo válida.
- El solapamiento se valida en cada recurso efectivo y en cada espacio
  (transitividad espacio <-> recursos efectivos).
- Capacidad efectiva = min(laboratorio, espacios definidas, recursos efectivos).
- `reservas.recurso_id` = recurso efectivo canónico (orden estable por id).

RED -> GREEN: estos tests fallan contra el código anterior (schema singular
con `recurso_id`), porque el payload nuevo devuelve 422 y no materializa nada.
"""

from app.models.reserva import Reserva
from app.models.reserva_recurso import ReservaRecurso
from app.models.reserva_espacio import ReservaEspacio
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


def _payload(*, recurso_ids=None, espacio_ids=None, **kw):
    return payload_reserva_objetivos(
        recurso_ids=recurso_ids or [],
        espacio_ids=espacio_ids or [],
        fecha=fecha_habilitada(),
        **kw,
    )


def _setup(db, nombre="Sala Espacios Mixta"):
    laboratorio = crear_laboratorio(db, nombre=nombre)
    usuario = crear_usuario(
        db,
        username=f"u_{nombre.replace(' ', '')}",
        email=f"u_{nombre.replace(' ', '')}@example.com",
    )
    r1 = crear_recurso(db, laboratorio=laboratorio, usuario=usuario, nombre="R1")
    r2 = crear_recurso(db, laboratorio=laboratorio, usuario=usuario, nombre="R2")
    return laboratorio, usuario, r1, r2


class TestContratoEntrada:
    def test_payload_legacy_recurso_id_da_422(self, client, db):
        laboratorio, usuario, recurso, _ = _setup(db)
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
        laboratorio, usuario, recurso, _ = _setup(db)
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


class TestEjesRecursoYEspacio:
    """Sin `ModalidadEspacio` (removido, ver Fase 3 de
    `~/.claude/plans/dazzling-wobbling-zebra.md`): recursos directos y
    espacios son dos ejes siempre disponibles simultáneamente, sin gate por
    configuración del laboratorio."""

    def test_espacios_acepta_espacio(self, client, db):
        laboratorio, usuario, r1, _ = _setup(db, nombre="Sala Solo Espacios B")
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=usuario)
        asociar_espacio_recurso(db, espacio, r1)
        respuesta = client.post(
            "/reservas", json=_payload(espacio_ids=[espacio.id]), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 201

    def test_mixto_acepta_ambos(self, client, db):
        laboratorio, usuario, r1, r2 = _setup(db)
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=usuario)
        asociar_espacio_recurso(db, espacio, r2)
        respuesta = client.post(
            "/reservas",
            json=_payload(recurso_ids=[r1.id], espacio_ids=[espacio.id]),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201


class TestReservasObjetivo:
    def test_recurso_directo_materializa_una_fila(self, client, db):
        laboratorio, usuario, r1, _ = _setup(db, nombre="Sala Directo")
        respuesta = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id]), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["recurso_ids"] == [r1.id]
        assert [r["id"] for r in cuerpo["recursos"]] == [r1.id]
        assert cuerpo["espacio_ids"] == []
        assert db.query(ReservaRecurso).count() == 1
        assert db.query(ReservaEspacio).count() == 0

    def test_espacio_con_recursos_materializa_sus_efectivos(self, client, db):
        laboratorio, usuario, r1, r2 = _setup(db, nombre="Sala Espacio Con Recurso")
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=usuario, nombre="Espacio A")
        asociar_espacio_recurso(db, espacio, r1)
        asociar_espacio_recurso(db, espacio, r2)
        respuesta = client.post(
            "/reservas", json=_payload(espacio_ids=[espacio.id]), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["espacio_ids"] == [espacio.id]
        assert sorted(cuerpo["recurso_ids"]) == sorted([r1.id, r2.id])
        assert len(cuerpo["espacios"]) == 1
        assert cuerpo["espacios"][0]["nombre"] == "Espacio A"
        assert sorted(r["id"] for r in cuerpo["recursos"]) == sorted([r1.id, r2.id])
        reserva = db.query(Reserva).filter(Reserva.id == cuerpo["id"]).one()
        assert reserva.recurso_id == min(r1.id, r2.id)
        assert db.query(ReservaEspacio).count() == 1
        assert sorted(rr.recurso_id for rr in db.query(ReservaRecurso).all()) == sorted([r1.id, r2.id])

    def test_espacio_sin_recursos_sigue_siendo_valida(self, client, db):
        laboratorio, usuario, r1, _ = _setup(db)
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=usuario, nombre="Espacio Vacia")
        respuesta = client.post(
            "/reservas", json=_payload(espacio_ids=[espacio.id]), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["espacio_ids"] == [espacio.id]
        assert cuerpo["recurso_ids"] == []
        assert len(cuerpo["espacios"]) == 1
        assert db.query(ReservaEspacio).count() == 1
        assert db.query(ReservaRecurso).count() == 0
        reserva = db.query(Reserva).filter(Reserva.id == cuerpo["id"]).one()
        assert reserva.recurso_id == r1.id

    def test_reserva_mixta_dedupe_recursos_efectivos(self, client, db):
        laboratorio, usuario, r1, _ = _setup(db)
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=usuario)
        asociar_espacio_recurso(db, espacio, r1)
        respuesta = client.post(
            "/reservas",
            json=_payload(recurso_ids=[r1.id], espacio_ids=[espacio.id]),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["recurso_ids"] == [r1.id]
        assert cuerpo["espacio_ids"] == [espacio.id]
        assert db.query(ReservaRecurso).count() == 1
        assert db.query(ReservaEspacio).count() == 1


class TestActualizacionPorEjes:
    def test_conserva_ejes_ausentes(self, client, db):
        laboratorio, usuario, r1, r2 = _setup(db)
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=usuario)
        creada = client.post(
            "/reservas",
            json=_payload(recurso_ids=[r1.id], espacio_ids=[espacio.id]),
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
        assert cuerpo["espacio_ids"] == [espacio.id]

    def test_reemplaza_eje_recursos(self, client, db):
        laboratorio, usuario, r1, r2 = _setup(db)
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=usuario)
        creada = client.post(
            "/reservas",
            json=_payload(recurso_ids=[r1.id], espacio_ids=[espacio.id]),
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
        assert cuerpo["espacio_ids"] == [espacio.id]
        assert db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == creada["id"]).count() == 1

    def test_reemplaza_eje_espacios(self, client, db):
        laboratorio, usuario, r1, _ = _setup(db)
        espacio_a = crear_espacio(db, laboratorio=laboratorio, usuario=usuario, nombre="Espacio A")
        espacio_b = crear_espacio(db, laboratorio=laboratorio, usuario=usuario, nombre="Espacio B")
        creada = client.post(
            "/reservas",
            json=_payload(espacio_ids=[espacio_a.id]),
            headers=cookies_para(usuario),
        ).json()
        actualizada = client.patch(
            f"/reservas/{creada['id']}",
            json={"espacio_ids": [espacio_b.id]},
            headers=cookies_para(usuario),
        )
        assert actualizada.status_code == 200
        cuerpo = actualizada.json()
        assert cuerpo["espacio_ids"] == [espacio_b.id]
        assert db.query(ReservaEspacio).filter(ReservaEspacio.reserva_id == creada["id"]).count() == 1

    def test_resultado_vacio_rechazado(self, client, db):
        laboratorio, usuario, r1, _ = _setup(db)
        creada = client.post(
            "/reservas",
            json=_payload(recurso_ids=[r1.id]),
            headers=cookies_para(usuario),
        ).json()
        respuesta = client.patch(
            f"/reservas/{creada['id']}",
            json={"recurso_ids": [], "espacio_ids": []},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 400


class TestSolapamientoTransitivo:
    def test_solapamiento_directo_409(self, client, db):
        laboratorio, usuario, r1, _ = _setup(db, nombre="Sala Over Directo")
        primera = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id]), headers=cookies_para(usuario)
        )
        assert primera.status_code == 201
        segunda = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id]), headers=cookies_para(usuario)
        )
        assert segunda.status_code == 409

    def test_espacio_a_recurso_409(self, client, db):
        laboratorio, usuario, r1, _ = _setup(db)
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=usuario)
        asociar_espacio_recurso(db, espacio, r1)
        espacio_reservada = client.post(
            "/reservas", json=_payload(espacio_ids=[espacio.id]), headers=cookies_para(usuario)
        )
        assert espacio_reservada.status_code == 201
        directa = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id]), headers=cookies_para(usuario)
        )
        assert directa.status_code == 409

    def test_recurso_a_espacio_409(self, client, db):
        laboratorio, usuario, r1, _ = _setup(db)
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=usuario)
        asociar_espacio_recurso(db, espacio, r1)
        directa = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id]), headers=cookies_para(usuario)
        )
        assert directa.status_code == 201
        espacio_reservada = client.post(
            "/reservas", json=_payload(espacio_ids=[espacio.id]), headers=cookies_para(usuario)
        )
        assert espacio_reservada.status_code == 409

    def test_espacio_sin_recursos_ancla_al_recurso_de_menor_id(self, client, db):
        laboratorio, usuario, r1, r2 = _setup(db)
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=usuario)
        espacio_reservada = client.post(
            "/reservas", json=_payload(espacio_ids=[espacio.id]), headers=cookies_para(usuario)
        )
        assert espacio_reservada.status_code == 201
        # Fase 12C-4e-schemas: `recurso_id` ya no está en la respuesta; el
        # ancla se confirma contra la columna histórica directamente.
        reserva = db.query(Reserva).filter(Reserva.id == espacio_reservada.json()["id"]).one()
        assert reserva.recurso_id == r1.id
        # Una espacio sin recursos no materializa nada: no bloquea recursos
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
    def test_aprobar_espacio_sincroniza_y_bloquea_transitivamente(self, client, db):
        laboratorio, usuario, r1, r2 = _setup(db, nombre="Sala Aprobar Espacio")
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=usuario, nombre="Espacio Aprobar")
        asociar_espacio_recurso(db, espacio, r1)
        gestor = crear_usuario(
            db, username="gestor_aprob", email="gestor_aprob@example.com",
            rol="gestor", laboratorio_id=laboratorio.id,
        )
        creada = client.post(
            "/reservas", json=_payload(espacio_ids=[espacio.id]), headers=cookies_para(usuario)
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
        fila_espacio = db.query(ReservaEspacio).one()
        fila_recurso = db.query(ReservaRecurso).one()
        assert fila_espacio.estado == "aprobada"
        assert fila_recurso.estado == "aprobada"
        # Transitividad: la espacio aprobada reclama su recurso efectivo (r1) y
        # bloquea una reserva directa de r1 en el mismo horario.
        segunda = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id]), headers=cookies_para(usuario)
        )
        assert segunda.status_code == 409


class TestCapacidad:
    def test_capacidad_efectiva_es_el_minimo(self, client, db):
        laboratorio, usuario, r1, _ = _setup(db)
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=usuario, capacidad=8)
        asociar_espacio_recurso(db, espacio, r1)
        excede = client.post(
            "/reservas", json=_payload(espacio_ids=[espacio.id], asistentes=9), headers=cookies_para(usuario)
        )
        assert excede.status_code == 400
        justo = client.post(
            "/reservas", json=_payload(espacio_ids=[espacio.id], asistentes=8), headers=cookies_para(usuario)
        )
        assert justo.status_code == 201

    def test_capacidad_directa_limitada_tambien_por_espacio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Cap Baja", capacidad=5)
        usuario = crear_usuario(db, username="u_cap", email="u_cap@example.com")
        r1 = crear_recurso(db, laboratorio=laboratorio, usuario=usuario, capacidad=10)
        respuesta = client.post(
            "/reservas", json=_payload(recurso_ids=[r1.id], asistentes=7), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 400


class TestPS:
    """El gate de rol/tipo que antes bloqueaba reservar un recurso PS
    (directo o vía espacio) se quitó del flujo de reserva -- ver `TestRecursosPS`
    en `test_api_reservas.py` y `backend/CLAUDE.md`."""

    def test_usuario_puede_reservar_espacio_con_recurso_ps(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala PS Espacio")
        admin = crear_usuario(db, username="admin_ps_espacios", email="admin_ps_espacios@example.com", rol="admin")
        usuario = crear_usuario(db, username="u_ps_espacios", email="u_ps_espacios@example.com")
        r_ps = crear_recurso(
            db, laboratorio=laboratorio, usuario=admin, nombre="PS", es_prestacion_servicio=True
        )
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=admin)
        asociar_espacio_recurso(db, espacio, r_ps)
        respuesta = client.post(
            "/reservas", json=_payload(espacio_ids=[espacio.id]), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 201

    def test_admin_puede_reservar_espacio_con_ps_sin_declarar_tipo(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala PS Espacio 2")
        admin = crear_usuario(db, username="admin_ps_espacios2", email="admin_ps_espacios2@example.com", rol="admin")
        r_ps = crear_recurso(
            db, laboratorio=laboratorio, usuario=admin, nombre="PS", es_prestacion_servicio=True
        )
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=admin)
        asociar_espacio_recurso(db, espacio, r_ps)
        respuesta = client.post(
            "/reservas", json=_payload(espacio_ids=[espacio.id]), headers=cookies_para(admin)
        )
        assert respuesta.status_code == 201


class TestPermisos:
    def test_recursos_y_espacios_de_espacios_distintos_da_400(self, client, db):
        espacio_a, usuario, r1, _ = _setup(db, nombre="Laboratorio A")
        espacio_b = crear_laboratorio(db, nombre="Laboratorio B")
        espacio_b = crear_espacio(db, laboratorio=espacio_b, usuario=usuario)
        respuesta = client.post(
            "/reservas",
            json=_payload(recurso_ids=[r1.id], espacio_ids=[espacio_b.id]),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_gestor_puede_reservar_espacio_de_otro_espacio_queda_esperando(self, client, db):
        espacio_a = crear_laboratorio(db, nombre="Laboratorio Gestor A")
        gestor = crear_usuario(
            db, username="gestor_espacios_a", email="gestor_espacios_a@example.com",
            rol="gestor", laboratorio_id=espacio_a.id,
        )
        espacio_b = crear_laboratorio(db, nombre="Laboratorio Gestor B")
        recurso_b = crear_recurso(db, laboratorio=espacio_b, usuario=gestor, nombre="RB")
        espacio_b = crear_espacio(db, laboratorio=espacio_b, usuario=gestor)
        asociar_espacio_recurso(db, espacio_b, recurso_b)
        respuesta = client.post(
            "/reservas", json=_payload(espacio_ids=[espacio_b.id]), headers=cookies_para(gestor)
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["estado"] == "esperando"