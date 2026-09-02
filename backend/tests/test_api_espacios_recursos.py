# -*- coding: utf-8 -*-
"""Pruebas de integracion de PUT /espacios/{espacio_id}/recursos (Fase 12C-3).

Reemplazo completo de la asociacion Espacio<->Recurso: elimina las
asociaciones ausentes de la lista recibida, inserta las nuevas, y aplica
la unicidad funcional por recurso (un recurso pertenece, como maximo, a
una espacio) como 409 sin dejar cambios parciales.
"""

from app.models.espacio import Espacio
from app.models.espacio_recurso import EspacioRecurso
from tests.conftest import crear_laboratorio, crear_recurso, crear_usuario, cookies_para


def _crear_espacio(db, *, laboratorio, usuario, nombre="Espacio de pruebas"):
    espacio = Espacio(nombre=nombre, laboratorio_id=laboratorio.id, created_by=usuario.id, updated_by=usuario.id)
    db.add(espacio)
    db.commit()
    db.refresh(espacio)
    return espacio


def _asociados(db, espacio_id):
    return {
        zr.recurso_id
        for zr in db.query(EspacioRecurso).filter(EspacioRecurso.espacio_id == espacio_id).all()
    }


class TestReemplazoDeAsociacion:
    def test_asociacion_valida(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Asoc 1")
        admin = crear_usuario(db, username="admin_zra1", email="admin_zra1@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=admin)

        respuesta = client.put(
            f"/espacios/{espacio.id}/recursos",
            json={"recurso_ids": [recurso.id]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["recurso_ids"] == [recurso.id]
        assert _asociados(db, espacio.id) == {recurso.id}

    def test_lista_vacia_desasocia_todo(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Asoc Vacia")
        admin = crear_usuario(db, username="admin_zra2", email="admin_zra2@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=admin)
        db.add(EspacioRecurso(espacio_id=espacio.id, recurso_id=recurso.id))
        db.commit()

        respuesta = client.put(
            f"/espacios/{espacio.id}/recursos",
            json={"recurso_ids": []},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["recurso_ids"] == []
        assert _asociados(db, espacio.id) == set()

    def test_recurso_inexistente_da_404(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Asoc Recurso Falso")
        admin = crear_usuario(db, username="admin_zra3", email="admin_zra3@example.com", rol="admin")
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=admin)

        respuesta = client.put(
            f"/espacios/{espacio.id}/recursos",
            json={"recurso_ids": [999999]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 404
        assert _asociados(db, espacio.id) == set()

    def test_espacio_inexistente_da_404(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Asoc Espacio Falsa")
        admin = crear_usuario(db, username="admin_zra4", email="admin_zra4@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)

        respuesta = client.put(
            "/espacios/999999/recursos",
            json={"recurso_ids": [recurso.id]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 404

    def test_recurso_de_otro_espacio_da_400(self, client, db):
        espacio_a = crear_laboratorio(db, nombre="Laboratorio Asoc A")
        espacio_b = crear_laboratorio(db, nombre="Laboratorio Asoc B")
        admin = crear_usuario(db, username="admin_zra5", email="admin_zra5@example.com", rol="admin")
        recurso_b = crear_recurso(db, laboratorio=espacio_b, usuario=admin)
        espacio_a = _crear_espacio(db, laboratorio=espacio_a, usuario=admin)

        respuesta = client.put(
            f"/espacios/{espacio_a.id}/recursos",
            json={"recurso_ids": [recurso_b.id]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 400
        assert _asociados(db, espacio_a.id) == set()

    def test_recurso_ya_asignado_a_otra_espacio_da_409(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Asoc Conflicto")
        admin = crear_usuario(db, username="admin_zra6", email="admin_zra6@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        espacio_a = _crear_espacio(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Conflicto A")
        espacio_b = _crear_espacio(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Conflicto B")
        db.add(EspacioRecurso(espacio_id=espacio_a.id, recurso_id=recurso.id))
        db.commit()

        respuesta = client.put(
            f"/espacios/{espacio_b.id}/recursos",
            json={"recurso_ids": [recurso.id]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 409
        assert _asociados(db, espacio_b.id) == set()
        assert _asociados(db, espacio_a.id) == {recurso.id}

    def test_reemplazo_completo_quita_y_agrega(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Asoc Reemplazo")
        admin = crear_usuario(db, username="admin_zra7", email="admin_zra7@example.com", rol="admin")
        recurso_viejo = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso Viejo")
        recurso_nuevo = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso Nuevo")
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=admin)
        db.add(EspacioRecurso(espacio_id=espacio.id, recurso_id=recurso_viejo.id))
        db.commit()

        respuesta = client.put(
            f"/espacios/{espacio.id}/recursos",
            json={"recurso_ids": [recurso_nuevo.id]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 200
        assert _asociados(db, espacio.id) == {recurso_nuevo.id}

    def test_atomicidad_ante_error_no_deja_cambios_parciales(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Asoc Atomicidad")
        admin = crear_usuario(db, username="admin_zra8", email="admin_zra8@example.com", rol="admin")
        recurso_valido = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso Valido")
        recurso_conflictivo = crear_recurso(
            db, laboratorio=laboratorio, usuario=admin, nombre="Recurso Conflictivo"
        )
        espacio_a = _crear_espacio(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Atomicidad A")
        espacio_b = _crear_espacio(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Atomicidad B")
        db.add(EspacioRecurso(espacio_id=espacio_a.id, recurso_id=recurso_conflictivo.id))
        db.commit()

        respuesta = client.put(
            f"/espacios/{espacio_b.id}/recursos",
            json={"recurso_ids": [recurso_valido.id, recurso_conflictivo.id]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 409
        # Ninguno de los dos queda asociado a espacio_b: ni siquiera el valido.
        assert _asociados(db, espacio_b.id) == set()

    def test_gestor_limitado_a_su_espacio(self, client, db):
        espacio_propio = crear_laboratorio(db, nombre="Laboratorio Propio Asoc Gestor")
        espacio_ajeno = crear_laboratorio(db, nombre="Laboratorio Ajeno Asoc Gestor")
        admin = crear_usuario(db, username="admin_zra9", email="admin_zra9@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zra9", email="gestor_zra9@example.com", rol="gestor",
            laboratorio_id=espacio_propio.id,
        )
        recurso = crear_recurso(db, laboratorio=espacio_propio, usuario=admin)
        espacio_ajena = _crear_espacio(db, laboratorio=espacio_ajeno, usuario=admin)

        respuesta = client.put(
            f"/espacios/{espacio_ajena.id}/recursos",
            json={"recurso_ids": [recurso.id]},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 403

    def test_gestor_asocia_en_su_propio_espacio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Propio Asoc Gestor Ok")
        admin = crear_usuario(db, username="admin_zra10", email="admin_zra10@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zra10", email="gestor_zra10@example.com", rol="gestor",
            laboratorio_id=laboratorio.id,
        )
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=admin)

        respuesta = client.put(
            f"/espacios/{espacio.id}/recursos",
            json={"recurso_ids": [recurso.id]},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 200

    def test_admin_sin_restriccion_de_espacio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Asoc Admin Libre")
        admin = crear_usuario(db, username="admin_zra11", email="admin_zra11@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=admin)

        respuesta = client.put(
            f"/espacios/{espacio.id}/recursos",
            json={"recurso_ids": [recurso.id]},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 200

    def test_usuario_sin_permisos(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Asoc Usuario")
        admin = crear_usuario(db, username="admin_zra12", email="admin_zra12@example.com", rol="admin")
        usuario = crear_usuario(db, username="user_zra12", email="user_zra12@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=admin)

        respuesta = client.put(
            f"/espacios/{espacio.id}/recursos",
            json={"recurso_ids": [recurso.id]},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 403
