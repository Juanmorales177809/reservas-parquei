# -*- coding: utf-8 -*-
"""Pruebas de integración de espacios (api/espacios.py) -- Fase 12C-2.

Alcance de esta subfase: CRUD y autorización de `Espacio`, aislada (sin
asociación con `Recurso`, sin integración con `Reserva`). RN-011/RN-016
(entidad Espacio) parcial -- solo la superficie HTTP.

Reglas cubiertas:
- Lectura pública tipo RN-005: anonimo/`usuario` (investigador) solo ven
  espacios en estado `activo` de laboratorios en estado `activo`; `gestor`
  (laboratorista) y `admin` (administrador tecnico) ven todo.
- Escritura (POST/PUT/DELETE) restringida a `gestor`/`admin`
  (`require_resource_manager`); `usuario` recibe 403.
- Un gestor solo puede crear/editar/eliminar espacios de su propio laboratorio
  asignado (`get_managed_space_id`), igual que ya rige para Recurso.
- `laboratorio_id` inexistente da 404; validaciones de schema dan 422.
- `created_by`/`updated_by` siempre reflejan al usuario autenticado, nunca
  un valor inyectado desde el payload.
- No existe `GET /espacios/{id}` en esta subfase (mismo patron que Recurso,
  que tampoco tiene un GET de un solo recurso).
"""

from tests.conftest import crear_laboratorio, crear_recurso, crear_usuario, cookies_para


def _crear_espacio_directa(db, *, laboratorio, usuario, **kwargs):
    from app.models.espacio import Espacio

    espacio = Espacio(
        nombre=kwargs.get("nombre", "Espacio de pruebas"),
        laboratorio_id=laboratorio.id,
        descripcion=kwargs.get("descripcion"),
        capacidad=kwargs.get("capacidad"),
        estado=kwargs.get("estado", "activo"),
        created_by=usuario.id,
        updated_by=usuario.id,
    )
    db.add(espacio)
    db.commit()
    db.refresh(espacio)
    return espacio


class TestListarEspaciosVisibilidadPublica:
    def test_anonimo_ve_solo_espacios_activas_de_espacios_activos(self, client, db):
        espacio_activo = crear_laboratorio(db, nombre="Laboratorio Activo Espacios")
        espacio_inactivo = crear_laboratorio(db, nombre="Laboratorio Inactivo Espacios", estado="inactivo")
        admin = crear_usuario(db, username="admin_zlist1", email="admin_zlist1@example.com", rol="admin")
        _crear_espacio_directa(db, laboratorio=espacio_activo, usuario=admin, nombre="Espacio Visible")
        _crear_espacio_directa(db, laboratorio=espacio_activo, usuario=admin, nombre="Espacio Inactiva", estado="inactivo")
        _crear_espacio_directa(db, laboratorio=espacio_inactivo, usuario=admin, nombre="Espacio De Laboratorio Inactivo")

        nombres = [z["nombre"] for z in client.get("/espacios").json()]
        assert nombres == ["Espacio Visible"]

    def test_usuario_ve_solo_espacios_activas_de_espacios_activos(self, client, db):
        espacio_activo = crear_laboratorio(db, nombre="Laboratorio Activo Espacios U")
        admin = crear_usuario(db, username="admin_zlist2", email="admin_zlist2@example.com", rol="admin")
        usuario = crear_usuario(db, username="user_zlist2", email="user_zlist2@example.com")
        _crear_espacio_directa(db, laboratorio=espacio_activo, usuario=admin, nombre="Espacio U Visible")
        _crear_espacio_directa(db, laboratorio=espacio_activo, usuario=admin, nombre="Espacio U Mantenimiento", estado="mantenimiento")

        nombres = [
            z["nombre"] for z in client.get("/espacios", headers=cookies_para(usuario)).json()
        ]
        assert nombres == ["Espacio U Visible"]

    def test_gestor_ve_espacios_inactivas_y_de_espacios_inactivos(self, client, db):
        espacio_inactivo = crear_laboratorio(db, nombre="Laboratorio Inactivo Espacios Gestor", estado="inactivo")
        admin = crear_usuario(db, username="admin_zlist3", email="admin_zlist3@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zlist3", email="gestor_zlist3@example.com", rol="gestor",
            laboratorio_id=espacio_inactivo.id,
        )
        _crear_espacio_directa(db, laboratorio=espacio_inactivo, usuario=admin, nombre="Espacio Oculta", estado="inactivo")

        nombres = [
            z["nombre"] for z in client.get("/espacios", headers=cookies_para(gestor)).json()
        ]
        assert "Espacio Oculta" in nombres

    def test_admin_ve_todas_las_espacios(self, client, db):
        espacio_inactivo = crear_laboratorio(db, nombre="Laboratorio Inactivo Espacios Admin", estado="inactivo")
        admin = crear_usuario(db, username="admin_zlist4", email="admin_zlist4@example.com", rol="admin")
        _crear_espacio_directa(db, laboratorio=espacio_inactivo, usuario=admin, nombre="Espacio Solo Admin", estado="mantenimiento")

        nombres = [
            z["nombre"] for z in client.get("/espacios", headers=cookies_para(admin)).json()
        ]
        assert "Espacio Solo Admin" in nombres

    def test_filtro_por_espacio_id(self, client, db):
        espacio_a = crear_laboratorio(db, nombre="Laboratorio A Filtro Espacio")
        espacio_b = crear_laboratorio(db, nombre="Laboratorio B Filtro Espacio")
        admin = crear_usuario(db, username="admin_zlist5", email="admin_zlist5@example.com", rol="admin")
        _crear_espacio_directa(db, laboratorio=espacio_a, usuario=admin, nombre="Espacio A")
        _crear_espacio_directa(db, laboratorio=espacio_b, usuario=admin, nombre="Espacio B")

        nombres = [
            z["nombre"]
            for z in client.get("/espacios", params={"laboratorio_id": espacio_a.id}).json()
        ]
        assert nombres == ["Espacio A"]

    def test_respuesta_no_incluye_recursos(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Sin Recursos En Response")
        admin = crear_usuario(db, username="admin_zlist6", email="admin_zlist6@example.com", rol="admin")
        _crear_espacio_directa(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Sin Recursos")

        cuerpo = client.get("/espacios").json()[0]
        assert "recursos" not in cuerpo


class TestCrearEspacioAutorizacion:
    def test_usuario_no_puede_crear_espacio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Crear Espacio U")
        usuario = crear_usuario(db, username="user_zcrea1", email="user_zcrea1@example.com")
        respuesta = client.post(
            "/espacios",
            json={"nombre": "Espacio Intento", "laboratorio_id": laboratorio.id},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 403

    def test_anonimo_no_puede_crear_espacio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Crear Espacio Anon")
        respuesta = client.post("/espacios", json={"nombre": "Espacio Anon", "laboratorio_id": laboratorio.id})
        assert respuesta.status_code == 401

    def test_admin_crea_espacio_en_cualquier_espacio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Crear Espacio Admin")
        admin = crear_usuario(db, username="admin_zcrea2", email="admin_zcrea2@example.com", rol="admin")
        respuesta = client.post(
            "/espacios",
            json={"nombre": "Espacio Admin", "laboratorio_id": laboratorio.id, "capacidad": 5},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["nombre"] == "Espacio Admin"
        assert cuerpo["laboratorio_id"] == laboratorio.id
        assert cuerpo["capacidad"] == 5
        assert cuerpo["estado"] == "activo"
        assert cuerpo["created_by"] == admin.id
        assert cuerpo["updated_by"] == admin.id

    def test_gestor_crea_espacio_en_su_espacio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Crear Espacio Gestor")
        gestor = crear_usuario(
            db, username="gestor_zcrea3", email="gestor_zcrea3@example.com", rol="gestor",
            laboratorio_id=laboratorio.id,
        )
        respuesta = client.post(
            "/espacios",
            json={"nombre": "Espacio Gestor", "laboratorio_id": laboratorio.id},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 201

    def test_gestor_no_puede_crear_espacio_en_otro_espacio(self, client, db):
        espacio_propio = crear_laboratorio(db, nombre="Laboratorio Propio Gestor Espacio")
        espacio_ajeno = crear_laboratorio(db, nombre="Laboratorio Ajeno Gestor Espacio")
        gestor = crear_usuario(
            db, username="gestor_zcrea4", email="gestor_zcrea4@example.com", rol="gestor",
            laboratorio_id=espacio_propio.id,
        )
        respuesta = client.post(
            "/espacios",
            json={"nombre": "Espacio Ajena", "laboratorio_id": espacio_ajeno.id},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 403

    def test_espacio_inexistente_da_404(self, client, db):
        admin = crear_usuario(db, username="admin_zcrea5", email="admin_zcrea5@example.com", rol="admin")
        respuesta = client.post(
            "/espacios",
            json={"nombre": "Espacio Laboratorio Falso", "laboratorio_id": 999999},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 404

    def test_created_by_updated_by_ignoran_valor_inyectado_en_payload(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Inyeccion Auditoria")
        admin = crear_usuario(db, username="admin_zcrea6", email="admin_zcrea6@example.com", rol="admin")
        respuesta = client.post(
            "/espacios",
            json={
                "nombre": "Espacio Inyeccion",
                "laboratorio_id": laboratorio.id,
                "created_by": 999999,
                "updated_by": 999999,
            },
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["created_by"] == admin.id
        assert cuerpo["updated_by"] == admin.id


class TestCrearEspacioValidaciones:
    def test_nombre_vacio_da_422(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Validacion Nombre Vacio")
        admin = crear_usuario(db, username="admin_zval1", email="admin_zval1@example.com", rol="admin")
        respuesta = client.post(
            "/espacios",
            json={"nombre": "", "laboratorio_id": laboratorio.id},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 422

    def test_nombre_supera_longitud_maxima_da_422(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Validacion Nombre Largo")
        admin = crear_usuario(db, username="admin_zval2", email="admin_zval2@example.com", rol="admin")
        respuesta = client.post(
            "/espacios",
            json={"nombre": "Z" * 101, "laboratorio_id": laboratorio.id},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 422

    def test_capacidad_cero_da_422(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Validacion Capacidad Cero")
        admin = crear_usuario(db, username="admin_zval3", email="admin_zval3@example.com", rol="admin")
        respuesta = client.post(
            "/espacios",
            json={"nombre": "Espacio Capacidad Cero", "laboratorio_id": laboratorio.id, "capacidad": 0},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 422

    def test_capacidad_nula_es_aceptada(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Validacion Capacidad Nula")
        admin = crear_usuario(db, username="admin_zval4", email="admin_zval4@example.com", rol="admin")
        respuesta = client.post(
            "/espacios",
            json={"nombre": "Espacio Capacidad Nula", "laboratorio_id": laboratorio.id, "capacidad": None},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["capacidad"] is None

    def test_estado_invalido_da_422(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Validacion Estado Invalido")
        admin = crear_usuario(db, username="admin_zval5", email="admin_zval5@example.com", rol="admin")
        respuesta = client.post(
            "/espacios",
            json={"nombre": "Espacio Estado Invalido", "laboratorio_id": laboratorio.id, "estado": "bogus"},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 422


class TestActualizarEspacio:
    def test_admin_actualiza_espacio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Actualizar Espacio Admin")
        admin = crear_usuario(db, username="admin_zupd1", email="admin_zupd1@example.com", rol="admin")
        espacio = _crear_espacio_directa(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Original")
        respuesta = client.put(
            f"/espacios/{espacio.id}",
            json={"nombre": "Espacio Renombrada", "capacidad": 8},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["nombre"] == "Espacio Renombrada"
        assert cuerpo["capacidad"] == 8
        assert cuerpo["updated_by"] == admin.id

    def test_gestor_actualiza_espacio_de_su_espacio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Actualizar Espacio Gestor")
        admin = crear_usuario(db, username="admin_zupd2", email="admin_zupd2@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zupd2", email="gestor_zupd2@example.com", rol="gestor",
            laboratorio_id=laboratorio.id,
        )
        espacio = _crear_espacio_directa(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Gestor Original")
        respuesta = client.put(
            f"/espacios/{espacio.id}",
            json={"estado": "mantenimiento"},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["estado"] == "mantenimiento"
        assert respuesta.json()["updated_by"] == gestor.id

    def test_gestor_no_puede_actualizar_espacio_de_otro_espacio(self, client, db):
        espacio_propio = crear_laboratorio(db, nombre="Laboratorio Propio Update Espacio")
        espacio_ajeno = crear_laboratorio(db, nombre="Laboratorio Ajeno Update Espacio")
        admin = crear_usuario(db, username="admin_zupd3", email="admin_zupd3@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zupd3", email="gestor_zupd3@example.com", rol="gestor",
            laboratorio_id=espacio_propio.id,
        )
        espacio = _crear_espacio_directa(db, laboratorio=espacio_ajeno, usuario=admin, nombre="Espacio Ajena Update")
        respuesta = client.put(
            f"/espacios/{espacio.id}",
            json={"nombre": "Intento"},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 403

    def test_usuario_no_puede_actualizar_espacio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Update Espacio Usuario")
        admin = crear_usuario(db, username="admin_zupd4", email="admin_zupd4@example.com", rol="admin")
        usuario = crear_usuario(db, username="user_zupd4", email="user_zupd4@example.com")
        espacio = _crear_espacio_directa(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Usuario Update")
        respuesta = client.put(
            f"/espacios/{espacio.id}",
            json={"nombre": "Intento Usuario"},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 403

    def test_espacio_inexistente_da_404(self, client, db):
        admin = crear_usuario(db, username="admin_zupd5", email="admin_zupd5@example.com", rol="admin")
        respuesta = client.put(
            "/espacios/999999",
            json={"nombre": "No existe"},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 404

    def test_mover_a_espacio_inexistente_da_404(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Mover Espacio Origen")
        admin = crear_usuario(db, username="admin_zupd6", email="admin_zupd6@example.com", rol="admin")
        espacio = _crear_espacio_directa(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Mover")
        respuesta = client.put(
            f"/espacios/{espacio.id}",
            json={"laboratorio_id": 999999},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 404

    def test_gestor_no_puede_mover_espacio_fuera_de_su_espacio(self, client, db):
        espacio_propio = crear_laboratorio(db, nombre="Laboratorio Propio Mover Espacio")
        espacio_destino = crear_laboratorio(db, nombre="Laboratorio Destino Mover Espacio")
        admin = crear_usuario(db, username="admin_zupd7", email="admin_zupd7@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zupd7", email="gestor_zupd7@example.com", rol="gestor",
            laboratorio_id=espacio_propio.id,
        )
        espacio = _crear_espacio_directa(db, laboratorio=espacio_propio, usuario=admin, nombre="Espacio Propia Mover")
        respuesta = client.put(
            f"/espacios/{espacio.id}",
            json={"laboratorio_id": espacio_destino.id},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 200
        # El laboratorio_id enviado se ignora para un gestor (no puede mover
        # espacios fuera de su propio laboratorio) -- mismo criterio que Recurso.
        assert respuesta.json()["laboratorio_id"] == espacio_propio.id

    def test_capacidad_cero_en_actualizacion_da_422(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Update Capacidad Cero")
        admin = crear_usuario(db, username="admin_zupd8", email="admin_zupd8@example.com", rol="admin")
        espacio = _crear_espacio_directa(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Capacidad Cero Update")
        respuesta = client.put(
            f"/espacios/{espacio.id}",
            json={"capacidad": 0},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 422

    def test_created_by_no_se_puede_sobreescribir_en_actualizacion(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Update Sin Sobreescribir Auditoria")
        admin = crear_usuario(db, username="admin_zupd9", email="admin_zupd9@example.com", rol="admin")
        espacio = _crear_espacio_directa(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Auditoria Update")
        respuesta = client.put(
            f"/espacios/{espacio.id}",
            json={"nombre": "Espacio Auditoria Update 2", "created_by": 999999, "updated_by": 999999},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["created_by"] == admin.id
        assert cuerpo["updated_by"] == admin.id


class TestEliminarEspacio:
    def test_admin_elimina_espacio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Eliminar Espacio Admin")
        admin = crear_usuario(db, username="admin_zdel1", email="admin_zdel1@example.com", rol="admin")
        espacio = _crear_espacio_directa(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio A Eliminar")
        respuesta = client.delete(f"/espacios/{espacio.id}", headers=cookies_para(admin))
        assert respuesta.status_code == 204
        assert client.get("/espacios", headers=cookies_para(admin)).json() == []

    def test_gestor_elimina_espacio_de_su_espacio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Eliminar Espacio Gestor")
        admin = crear_usuario(db, username="admin_zdel2", email="admin_zdel2@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zdel2", email="gestor_zdel2@example.com", rol="gestor",
            laboratorio_id=laboratorio.id,
        )
        espacio = _crear_espacio_directa(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Gestor A Eliminar")
        respuesta = client.delete(f"/espacios/{espacio.id}", headers=cookies_para(gestor))
        assert respuesta.status_code == 204

    def test_gestor_no_puede_eliminar_espacio_de_otro_espacio(self, client, db):
        espacio_propio = crear_laboratorio(db, nombre="Laboratorio Propio Eliminar Espacio")
        espacio_ajeno = crear_laboratorio(db, nombre="Laboratorio Ajeno Eliminar Espacio")
        admin = crear_usuario(db, username="admin_zdel3", email="admin_zdel3@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zdel3", email="gestor_zdel3@example.com", rol="gestor",
            laboratorio_id=espacio_propio.id,
        )
        espacio = _crear_espacio_directa(db, laboratorio=espacio_ajeno, usuario=admin, nombre="Espacio Ajena A Eliminar")
        respuesta = client.delete(f"/espacios/{espacio.id}", headers=cookies_para(gestor))
        assert respuesta.status_code == 403

    def test_usuario_no_puede_eliminar_espacio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Eliminar Espacio Usuario")
        admin = crear_usuario(db, username="admin_zdel4", email="admin_zdel4@example.com", rol="admin")
        usuario = crear_usuario(db, username="user_zdel4", email="user_zdel4@example.com")
        espacio = _crear_espacio_directa(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Usuario No Elimina")
        respuesta = client.delete(f"/espacios/{espacio.id}", headers=cookies_para(usuario))
        assert respuesta.status_code == 403

    def test_espacio_inexistente_da_404_al_eliminar(self, client, db):
        admin = crear_usuario(db, username="admin_zdel5", email="admin_zdel5@example.com", rol="admin")
        respuesta = client.delete("/espacios/999999", headers=cookies_para(admin))
        assert respuesta.status_code == 404

    def test_eliminacion_bloqueada_con_asociaciones(self, client, db):
        """Fase 12C-3: DELETE /espacios/{id} ahora bloquea si tiene
        asociaciones espacio-recurso, igual que eliminar_recurso/
        eliminar_espacio bloquean con sus propias dependencias."""
        from app.models.espacio_recurso import EspacioRecurso

        laboratorio = crear_laboratorio(db, nombre="Laboratorio Eliminar Espacio Con Asociacion")
        admin = crear_usuario(db, username="admin_zdel6", email="admin_zdel6@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        espacio = _crear_espacio_directa(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Con Recurso")
        db.add(EspacioRecurso(espacio_id=espacio.id, recurso_id=recurso.id))
        db.commit()

        respuesta = client.delete(f"/espacios/{espacio.id}", headers=cookies_para(admin))
        assert respuesta.status_code == 409


class TestEspacioResponseRecursoIds:
    """Fase A1 (recursos por espacio): `EspacioResponse.recurso_ids` refleja la
    asociación Espacio<->Recurso vigente -- necesario para que la UI de
    gestión pueda mostrar la selección actual antes de dejarla editar
    (PUT /espacios/{id}/recursos es un reemplazo completo)."""

    def test_espacio_sin_recursos_da_lista_vacia(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Espacio Sin Recursos")
        admin = crear_usuario(db, username="admin_zrid1", email="admin_zrid1@example.com", rol="admin")
        _crear_espacio_directa(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Sin Recursos")

        respuesta = client.get("/espacios", params={"laboratorio_id": laboratorio.id}, headers=cookies_para(admin))

        assert respuesta.status_code == 200
        assert respuesta.json()[0]["recurso_ids"] == []

    def test_espacio_con_recursos_asociados_los_expone(self, client, db):
        from app.models.espacio_recurso import EspacioRecurso

        laboratorio = crear_laboratorio(db, nombre="Laboratorio Espacio Con Recursos")
        admin = crear_usuario(db, username="admin_zrid2", email="admin_zrid2@example.com", rol="admin")
        recurso_a = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso A")
        recurso_b = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso B")
        espacio = _crear_espacio_directa(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Con Recursos")
        db.add_all([
            EspacioRecurso(espacio_id=espacio.id, recurso_id=recurso_a.id),
            EspacioRecurso(espacio_id=espacio.id, recurso_id=recurso_b.id),
        ])
        db.commit()

        respuesta = client.get("/espacios", params={"laboratorio_id": laboratorio.id}, headers=cookies_para(admin))

        assert respuesta.status_code == 200
        assert set(respuesta.json()[0]["recurso_ids"]) == {recurso_a.id, recurso_b.id}


class TestSinEndpointDeUnaSolaEspacio:
    """Decision deliberada de 12C-2: Recurso no tiene GET /recursos/{id} de
    un solo recurso (solo listado, /gestion y /disponibilidad); Espacio sigue
    el mismo patron y tampoco lo tiene en esta subfase."""

    def test_get_espacio_individual_no_existe(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Laboratorio Sin Get Individual")
        admin = crear_usuario(db, username="admin_zget1", email="admin_zget1@example.com", rol="admin")
        espacio = _crear_espacio_directa(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Sin Get")
        respuesta = client.get(f"/espacios/{espacio.id}")
        assert respuesta.status_code == 405
