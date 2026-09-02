# -*- coding: utf-8 -*-
"""Pruebas de integración de `ReservaResponse` tras el retiro de
`recurso_id`/`recurso` (Fase 12C-4e-schemas).

Hasta 12C-4e-schemas, este archivo declaraba un schema Pydantic prototipo
(`_ReservaResponseFinal`) para probar por adelantado que los datos que
`crud/reservas.py` enriquece desde las tablas de asociación alcanzaban para
construir la forma final aprobada, sin tocar todavía el contrato real. Esa
forma final ya es el contrato real (`app.schemas.reserva.ReservaResponse`),
así que el prototipo desapareció -- estas pruebas ahora validan
`get_reserva()` + `ReservaResponse.model_validate()` end-to-end.
"""

from app.crud.reservas import get_reserva
from app.schemas.reserva import ReservaResponse
from tests.conftest import (
    asociar_espacio_recurso,
    cookies_para,
    crear_laboratorio,
    crear_recurso,
    crear_usuario,
    crear_espacio,
    fecha_habilitada,
    payload_reserva_objetivos,
)


def _crear_reserva_api(client, usuario, *, recurso_ids=None, espacio_ids=None):
    respuesta = client.post(
        "/reservas",
        json=payload_reserva_objetivos(
            recurso_ids=recurso_ids or [],
            espacio_ids=espacio_ids or [],
            fecha=fecha_habilitada(),
        ),
        headers=cookies_para(usuario),
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["id"]


class TestConstruccionDesdeAsociaciones:
    def test_reserva_de_un_recurso(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Final Un Recurso")
        admin = crear_usuario(db, username="admin_final1", email="admin_final1@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso Final 1")
        reserva_id = _crear_reserva_api(client, admin, recurso_ids=[recurso.id])

        reserva = get_reserva(db, reserva_id)
        final = ReservaResponse.model_validate(reserva)

        assert final.recurso_ids == [recurso.id]
        assert [r.id for r in final.recursos] == [recurso.id]
        assert final.recursos[0].nombre == "Recurso Final 1"
        assert final.espacio_ids == []
        assert final.espacios == []

    def test_serializa_multiples_recursos(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Final Multi Recurso")
        admin = crear_usuario(db, username="admin_final2", email="admin_final2@example.com", rol="admin")
        r1 = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso Final A")
        r2 = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso Final B")
        reserva_id = _crear_reserva_api(client, admin, recurso_ids=[r1.id, r2.id])

        reserva = get_reserva(db, reserva_id)
        final = ReservaResponse.model_validate(reserva)

        assert final.recurso_ids == sorted([r1.id, r2.id])
        assert sorted(r.id for r in final.recursos) == sorted([r1.id, r2.id])
        assert {r.nombre for r in final.recursos} == {"Recurso Final A", "Recurso Final B"}
        assert final.espacio_ids == []
        assert final.espacios == []

    def test_serializa_reserva_solo_espacio_sin_recurso_directo(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Final Solo Espacio")
        admin = crear_usuario(db, username="admin_final3", email="admin_final3@example.com", rol="admin")
        r1 = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso Final Espacio")
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Final")
        asociar_espacio_recurso(db, espacio, r1)
        reserva_id = _crear_reserva_api(client, admin, espacio_ids=[espacio.id])

        reserva = get_reserva(db, reserva_id)
        final = ReservaResponse.model_validate(reserva)

        assert final.espacio_ids == [espacio.id]
        assert final.espacios[0].nombre == "Espacio Final"
        assert final.recurso_ids == [r1.id]
        assert final.recursos[0].id == r1.id

    def test_serializa_reserva_mixta(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Final Mixta")
        admin = crear_usuario(db, username="admin_final4", email="admin_final4@example.com", rol="admin")
        r_directo = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso Directo Final")
        r_espacio = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso De Espacio Final")
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Mixta Final")
        asociar_espacio_recurso(db, espacio, r_espacio)
        reserva_id = _crear_reserva_api(
            client, admin, recurso_ids=[r_directo.id], espacio_ids=[espacio.id]
        )

        reserva = get_reserva(db, reserva_id)
        final = ReservaResponse.model_validate(reserva)

        assert final.espacio_ids == [espacio.id]
        assert final.recurso_ids == sorted([r_directo.id, r_espacio.id])
        assert sorted(r.id for r in final.recursos) == sorted([r_directo.id, r_espacio.id])
        assert len(final.espacios) == 1

    def test_no_expone_campos_singulares(self):
        """`ReservaResponse` real no declara `recurso_id` ni `recurso` --
        por construcción, no por filtrado."""
        assert "recurso_id" not in ReservaResponse.model_fields
        assert "recurso" not in ReservaResponse.model_fields
