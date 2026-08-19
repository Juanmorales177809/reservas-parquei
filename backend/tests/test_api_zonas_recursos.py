# -*- coding: utf-8 -*-
"""Pruebas de integracion de PUT /zonas/{zona_id}/recursos (Fase 12C-3).

Reemplazo completo de la asociacion Zona<->Recurso: elimina las
asociaciones ausentes de la lista recibida, inserta las nuevas, y aplica
la unicidad funcional por recurso (un recurso pertenece, como maximo, a
una zona) como 409 sin dejar cambios parciales.
"""

from app.models.zona import Zona
from app.models.zona_recurso import ZonaRecurso
from tests.conftest import crear_espacio, crear_recurso, crear_usuario, cookies_para


def _crear_zona(db, *, espacio, usuario, nombre="Zona de pruebas"):
    zona = Zona(nombre=nombre, espacio_id=espacio.id, created_by=usuario.id, updated_by=usuario.id)
    db.add(zona)
    db.commit()
    db.refresh(zona)
    return zona


def _asociados(db, zona_id):
    return {
        zr.recurso_id
        for zr in db.query(ZonaRecurso).filter(ZonaRecurso.zona_id == zona_id).all()
    }


class TestReemplazoDeAsociacion:
    def test_asociacion_valida(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Asoc 1")
        admin = crear_usuario(db, username="admin_zra1", email="admin_zra1@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        zona = _crear_zona(db, espacio=espacio, usuario=admin)

        respuesta = client.put(
            f"/zonas/{zona.id}/recursos",
            json={"recurso_ids": [recurso.id]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["recurso_ids"] == [recurso.id]
        assert _asociados(db, zona.id) == {recurso.id}

    def test_lista_vacia_desasocia_todo(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Asoc Vacia")
        admin = crear_usuario(db, username="admin_zra2", email="admin_zra2@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        zona = _crear_zona(db, espacio=espacio, usuario=admin)
        db.add(ZonaRecurso(zona_id=zona.id, recurso_id=recurso.id))
        db.commit()

        respuesta = client.put(
            f"/zonas/{zona.id}/recursos",
            json={"recurso_ids": []},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["recurso_ids"] == []
        assert _asociados(db, zona.id) == set()

    def test_recurso_inexistente_da_404(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Asoc Recurso Falso")
        admin = crear_usuario(db, username="admin_zra3", email="admin_zra3@example.com", rol="admin")
        zona = _crear_zona(db, espacio=espacio, usuario=admin)

        respuesta = client.put(
            f"/zonas/{zona.id}/recursos",
            json={"recurso_ids": [999999]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 404
        assert _asociados(db, zona.id) == set()

    def test_zona_inexistente_da_404(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Asoc Zona Falsa")
        admin = crear_usuario(db, username="admin_zra4", email="admin_zra4@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)

        respuesta = client.put(
            "/zonas/999999/recursos",
            json={"recurso_ids": [recurso.id]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 404

    def test_recurso_de_otro_espacio_da_400(self, client, db):
        espacio_a = crear_espacio(db, nombre="Espacio Asoc A")
        espacio_b = crear_espacio(db, nombre="Espacio Asoc B")
        admin = crear_usuario(db, username="admin_zra5", email="admin_zra5@example.com", rol="admin")
        recurso_b = crear_recurso(db, espacio=espacio_b, usuario=admin)
        zona_a = _crear_zona(db, espacio=espacio_a, usuario=admin)

        respuesta = client.put(
            f"/zonas/{zona_a.id}/recursos",
            json={"recurso_ids": [recurso_b.id]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 400
        assert _asociados(db, zona_a.id) == set()

    def test_recurso_ya_asignado_a_otra_zona_da_409(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Asoc Conflicto")
        admin = crear_usuario(db, username="admin_zra6", email="admin_zra6@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        zona_a = _crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona Conflicto A")
        zona_b = _crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona Conflicto B")
        db.add(ZonaRecurso(zona_id=zona_a.id, recurso_id=recurso.id))
        db.commit()

        respuesta = client.put(
            f"/zonas/{zona_b.id}/recursos",
            json={"recurso_ids": [recurso.id]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 409
        assert _asociados(db, zona_b.id) == set()
        assert _asociados(db, zona_a.id) == {recurso.id}

    def test_reemplazo_completo_quita_y_agrega(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Asoc Reemplazo")
        admin = crear_usuario(db, username="admin_zra7", email="admin_zra7@example.com", rol="admin")
        recurso_viejo = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso Viejo")
        recurso_nuevo = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso Nuevo")
        zona = _crear_zona(db, espacio=espacio, usuario=admin)
        db.add(ZonaRecurso(zona_id=zona.id, recurso_id=recurso_viejo.id))
        db.commit()

        respuesta = client.put(
            f"/zonas/{zona.id}/recursos",
            json={"recurso_ids": [recurso_nuevo.id]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 200
        assert _asociados(db, zona.id) == {recurso_nuevo.id}

    def test_atomicidad_ante_error_no_deja_cambios_parciales(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Asoc Atomicidad")
        admin = crear_usuario(db, username="admin_zra8", email="admin_zra8@example.com", rol="admin")
        recurso_valido = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso Valido")
        recurso_conflictivo = crear_recurso(
            db, espacio=espacio, usuario=admin, nombre="Recurso Conflictivo"
        )
        zona_a = _crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona Atomicidad A")
        zona_b = _crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona Atomicidad B")
        db.add(ZonaRecurso(zona_id=zona_a.id, recurso_id=recurso_conflictivo.id))
        db.commit()

        respuesta = client.put(
            f"/zonas/{zona_b.id}/recursos",
            json={"recurso_ids": [recurso_valido.id, recurso_conflictivo.id]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 409
        # Ninguno de los dos queda asociado a zona_b: ni siquiera el valido.
        assert _asociados(db, zona_b.id) == set()

    def test_gestor_limitado_a_su_espacio(self, client, db):
        espacio_propio = crear_espacio(db, nombre="Espacio Propio Asoc Gestor")
        espacio_ajeno = crear_espacio(db, nombre="Espacio Ajeno Asoc Gestor")
        admin = crear_usuario(db, username="admin_zra9", email="admin_zra9@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zra9", email="gestor_zra9@example.com", rol="gestor",
            espacio_id=espacio_propio.id,
        )
        recurso = crear_recurso(db, espacio=espacio_propio, usuario=admin)
        zona_ajena = _crear_zona(db, espacio=espacio_ajeno, usuario=admin)

        respuesta = client.put(
            f"/zonas/{zona_ajena.id}/recursos",
            json={"recurso_ids": [recurso.id]},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 403

    def test_gestor_asocia_en_su_propio_espacio(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Propio Asoc Gestor Ok")
        admin = crear_usuario(db, username="admin_zra10", email="admin_zra10@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zra10", email="gestor_zra10@example.com", rol="gestor",
            espacio_id=espacio.id,
        )
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        zona = _crear_zona(db, espacio=espacio, usuario=admin)

        respuesta = client.put(
            f"/zonas/{zona.id}/recursos",
            json={"recurso_ids": [recurso.id]},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 200

    def test_admin_sin_restriccion_de_espacio(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Asoc Admin Libre")
        admin = crear_usuario(db, username="admin_zra11", email="admin_zra11@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        zona = _crear_zona(db, espacio=espacio, usuario=admin)

        respuesta = client.put(
            f"/zonas/{zona.id}/recursos",
            json={"recurso_ids": [recurso.id]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 200

    def test_usuario_sin_permisos(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Asoc Usuario")
        admin = crear_usuario(db, username="admin_zra12", email="admin_zra12@example.com", rol="admin")
        usuario = crear_usuario(db, username="user_zra12", email="user_zra12@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        zona = _crear_zona(db, espacio=espacio, usuario=admin)

        respuesta = client.put(
            f"/zonas/{zona.id}/recursos",
            json={"recurso_ids": [recurso.id]},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 403
