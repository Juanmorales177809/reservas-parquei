# -*- coding: utf-8 -*-
"""Pruebas de ensayos en reservas (Fase 12E).

- ensayo_ids válidos → 201 y se materializan
- ensayo fuera de zona → 400
- eje ensayo_ids ausente conserva, presente reemplaza
"""

from app.models.reserva_ensayo import ReservaEnsayo
from tests.conftest import (
    asociar_zona_recurso,
    crear_espacio,
    crear_recurso,
    crear_usuario,
    crear_zona,
    cookies_para,
    fecha_habilitada,
    payload_reserva_objetivos,
)


def _crear_ensayo(db, *, zona, usuario, nombre="Ensayo X"):
    from app.models.ensayo import Ensayo

    ensayo = Ensayo(nombre=nombre, zona_id=zona.id, created_by=usuario.id, updated_by=usuario.id)
    db.add(ensayo)
    db.commit()
    db.refresh(ensayo)
    return ensayo


class TestReservaConEnsayos:
    def test_reserva_zona_con_ensayo_valido_201_y_materializa(self, client, db):
        espacio = crear_espacio(db, nombre="Sala Ens Valido", modalidad_reserva="zonas")
        admin = crear_usuario(db, username="adm_ensv1", email="adm_ensv1@example.com", rol="admin")
        usuario = crear_usuario(db, username="u_ensv1", email="u_ensv1@example.com")
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        asociar_zona_recurso(db, zona, recurso)
        ensayo = _crear_ensayo(db, zona=zona, usuario=admin, nombre="Ens Valido")
        resp = client.post(
            "/reservas",
            json=payload_reserva_objetivos(zona_ids=[zona.id], ensayo_ids=[ensayo.id], fecha=fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 201
        cuerpo = resp.json()
        assert cuerpo["ensayo_ids"] == [ensayo.id]
        assert cuerpo["ensayos"][0]["nombre"] == "Ens Valido"
        assert db.query(ReservaEnsayo).filter(ReservaEnsayo.reserva_id == cuerpo["id"]).count() == 1

    def test_ensayo_fuera_de_zona_400(self, client, db):
        espacio = crear_espacio(db, nombre="Sala Ens Fuera", modalidad_reserva="zonas")
        admin = crear_usuario(db, username="adm_ensf1", email="adm_ensf1@example.com", rol="admin")
        usuario = crear_usuario(db, username="u_ensf1", email="u_ensf1@example.com")
        zona_a = crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona A Ens")
        zona_b = crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona B Ens")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        asociar_zona_recurso(db, zona_a, recurso)
        ensayo_b = _crear_ensayo(db, zona=zona_b, usuario=admin, nombre="Ens B")
        resp = client.post(
            "/reservas",
            json=payload_reserva_objetivos(zona_ids=[zona_a.id], ensayo_ids=[ensayo_b.id], fecha=fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 400
        assert "no pertenece" in resp.json()["detail"].lower()

    def test_actualizar_ensayos_eje_conserva_y_reemplaza(self, client, db):
        espacio = crear_espacio(db, nombre="Sala Ens Eje", modalidad_reserva="mixto")
        admin = crear_usuario(db, username="adm_ense1", email="adm_ense1@example.com", rol="admin")
        usuario = crear_usuario(db, username="u_ense1", email="u_ense1@example.com")
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        asociar_zona_recurso(db, zona, recurso)
        ens_a = _crear_ensayo(db, zona=zona, usuario=admin, nombre="Ens A")
        ens_b = _crear_ensayo(db, zona=zona, usuario=admin, nombre="Ens B")
        creada = client.post(
            "/reservas",
            json=payload_reserva_objetivos(zona_ids=[zona.id], ensayo_ids=[ens_a.id], fecha=fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        # eje ausente conserva
        upd1 = client.patch(f"/reservas/{creada['id']}", json={"asistentes": 3}, headers=cookies_para(usuario))
        assert upd1.status_code == 200
        assert upd1.json()["ensayo_ids"] == [ens_a.id]
        # eje presente reemplaza
        upd2 = client.patch(f"/reservas/{creada['id']}", json={"ensayo_ids": [ens_b.id]}, headers=cookies_para(usuario))
        assert upd2.status_code == 200
        assert upd2.json()["ensayo_ids"] == [ens_b.id]
        # vaciar con []
        upd3 = client.patch(f"/reservas/{creada['id']}", json={"ensayo_ids": []}, headers=cookies_para(usuario))
        assert upd3.status_code == 200
        assert upd3.json()["ensayo_ids"] == []

    def test_get_mis_reservas_devuelve_ensayos(self, client, db):
        espacio = crear_espacio(db, nombre="Sala Ens Get", modalidad_reserva="mixto")
        admin = crear_usuario(db, username="adm_ensg1", email="adm_ensg1@example.com", rol="admin")
        usuario = crear_usuario(db, username="u_ensg1", email="u_ensg1@example.com")
        zona = crear_zona(db, espacio=espacio, usuario=admin)
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        asociar_zona_recurso(db, zona, recurso)
        ensayo = _crear_ensayo(db, zona=zona, usuario=admin)
        creada = client.post(
            "/reservas",
            json=payload_reserva_objetivos(zona_ids=[zona.id], ensayo_ids=[ensayo.id], fecha=fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        resp = client.get("/reservas/mis-reservas", headers=cookies_para(usuario))
        assert resp.status_code == 200
        encontrada = next(r for r in resp.json() if r["id"] == creada["id"])
        assert encontrada["ensayo_ids"] == [ensayo.id]
