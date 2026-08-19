# -*- coding: utf-8 -*-
"""Pruebas de integración de zonas (api/zonas.py) -- Fase 12C-2.

Alcance de esta subfase: CRUD y autorización de `Zona`, aislada (sin
asociación con `Recurso`, sin integración con `Reserva`). RN-011/RN-016
(entidad Zona) parcial -- solo la superficie HTTP.

Reglas cubiertas:
- Lectura pública tipo RN-005: anonimo/`usuario` (investigador) solo ven
  zonas en estado `activo` de espacios en estado `activo`; `gestor`
  (laboratorista) y `admin` (administrador tecnico) ven todo.
- Escritura (POST/PUT/DELETE) restringida a `gestor`/`admin`
  (`require_resource_manager`); `usuario` recibe 403.
- Un gestor solo puede crear/editar/eliminar zonas de su propio espacio
  asignado (`get_managed_space_id`), igual que ya rige para Recurso.
- `espacio_id` inexistente da 404; validaciones de schema dan 422.
- `created_by`/`updated_by` siempre reflejan al usuario autenticado, nunca
  un valor inyectado desde el payload.
- No existe `GET /zonas/{id}` en esta subfase (mismo patron que Recurso,
  que tampoco tiene un GET de un solo recurso).
"""

from tests.conftest import crear_espacio, crear_recurso, crear_usuario, cookies_para


def _crear_zona_directa(db, *, espacio, usuario, **kwargs):
    from app.models.zona import Zona

    zona = Zona(
        nombre=kwargs.get("nombre", "Zona de pruebas"),
        espacio_id=espacio.id,
        descripcion=kwargs.get("descripcion"),
        capacidad=kwargs.get("capacidad"),
        estado=kwargs.get("estado", "activo"),
        created_by=usuario.id,
        updated_by=usuario.id,
    )
    db.add(zona)
    db.commit()
    db.refresh(zona)
    return zona


class TestListarZonasVisibilidadPublica:
    def test_anonimo_ve_solo_zonas_activas_de_espacios_activos(self, client, db):
        espacio_activo = crear_espacio(db, nombre="Espacio Activo Zonas")
        espacio_inactivo = crear_espacio(db, nombre="Espacio Inactivo Zonas", estado="inactivo")
        admin = crear_usuario(db, username="admin_zlist1", email="admin_zlist1@example.com", rol="admin")
        _crear_zona_directa(db, espacio=espacio_activo, usuario=admin, nombre="Zona Visible")
        _crear_zona_directa(db, espacio=espacio_activo, usuario=admin, nombre="Zona Inactiva", estado="inactivo")
        _crear_zona_directa(db, espacio=espacio_inactivo, usuario=admin, nombre="Zona De Espacio Inactivo")

        nombres = [z["nombre"] for z in client.get("/zonas").json()]
        assert nombres == ["Zona Visible"]

    def test_usuario_ve_solo_zonas_activas_de_espacios_activos(self, client, db):
        espacio_activo = crear_espacio(db, nombre="Espacio Activo Zonas U")
        admin = crear_usuario(db, username="admin_zlist2", email="admin_zlist2@example.com", rol="admin")
        usuario = crear_usuario(db, username="user_zlist2", email="user_zlist2@example.com")
        _crear_zona_directa(db, espacio=espacio_activo, usuario=admin, nombre="Zona U Visible")
        _crear_zona_directa(db, espacio=espacio_activo, usuario=admin, nombre="Zona U Mantenimiento", estado="mantenimiento")

        nombres = [
            z["nombre"] for z in client.get("/zonas", headers=cookies_para(usuario)).json()
        ]
        assert nombres == ["Zona U Visible"]

    def test_gestor_ve_zonas_inactivas_y_de_espacios_inactivos(self, client, db):
        espacio_inactivo = crear_espacio(db, nombre="Espacio Inactivo Zonas Gestor", estado="inactivo")
        admin = crear_usuario(db, username="admin_zlist3", email="admin_zlist3@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zlist3", email="gestor_zlist3@example.com", rol="gestor",
            espacio_id=espacio_inactivo.id,
        )
        _crear_zona_directa(db, espacio=espacio_inactivo, usuario=admin, nombre="Zona Oculta", estado="inactivo")

        nombres = [
            z["nombre"] for z in client.get("/zonas", headers=cookies_para(gestor)).json()
        ]
        assert "Zona Oculta" in nombres

    def test_admin_ve_todas_las_zonas(self, client, db):
        espacio_inactivo = crear_espacio(db, nombre="Espacio Inactivo Zonas Admin", estado="inactivo")
        admin = crear_usuario(db, username="admin_zlist4", email="admin_zlist4@example.com", rol="admin")
        _crear_zona_directa(db, espacio=espacio_inactivo, usuario=admin, nombre="Zona Solo Admin", estado="mantenimiento")

        nombres = [
            z["nombre"] for z in client.get("/zonas", headers=cookies_para(admin)).json()
        ]
        assert "Zona Solo Admin" in nombres

    def test_filtro_por_espacio_id(self, client, db):
        espacio_a = crear_espacio(db, nombre="Espacio A Filtro Zona")
        espacio_b = crear_espacio(db, nombre="Espacio B Filtro Zona")
        admin = crear_usuario(db, username="admin_zlist5", email="admin_zlist5@example.com", rol="admin")
        _crear_zona_directa(db, espacio=espacio_a, usuario=admin, nombre="Zona A")
        _crear_zona_directa(db, espacio=espacio_b, usuario=admin, nombre="Zona B")

        nombres = [
            z["nombre"]
            for z in client.get("/zonas", params={"espacio_id": espacio_a.id}).json()
        ]
        assert nombres == ["Zona A"]

    def test_respuesta_no_incluye_recursos(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Sin Recursos En Response")
        admin = crear_usuario(db, username="admin_zlist6", email="admin_zlist6@example.com", rol="admin")
        _crear_zona_directa(db, espacio=espacio, usuario=admin, nombre="Zona Sin Recursos")

        cuerpo = client.get("/zonas").json()[0]
        assert "recursos" not in cuerpo


class TestCrearZonaAutorizacion:
    def test_usuario_no_puede_crear_zona(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Crear Zona U")
        usuario = crear_usuario(db, username="user_zcrea1", email="user_zcrea1@example.com")
        respuesta = client.post(
            "/zonas",
            json={"nombre": "Zona Intento", "espacio_id": espacio.id},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 403

    def test_anonimo_no_puede_crear_zona(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Crear Zona Anon")
        respuesta = client.post("/zonas", json={"nombre": "Zona Anon", "espacio_id": espacio.id})
        assert respuesta.status_code == 401

    def test_admin_crea_zona_en_cualquier_espacio(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Crear Zona Admin")
        admin = crear_usuario(db, username="admin_zcrea2", email="admin_zcrea2@example.com", rol="admin")
        respuesta = client.post(
            "/zonas",
            json={"nombre": "Zona Admin", "espacio_id": espacio.id, "capacidad": 5},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["nombre"] == "Zona Admin"
        assert cuerpo["espacio_id"] == espacio.id
        assert cuerpo["capacidad"] == 5
        assert cuerpo["estado"] == "activo"
        assert cuerpo["created_by"] == admin.id
        assert cuerpo["updated_by"] == admin.id

    def test_gestor_crea_zona_en_su_espacio(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Crear Zona Gestor")
        gestor = crear_usuario(
            db, username="gestor_zcrea3", email="gestor_zcrea3@example.com", rol="gestor",
            espacio_id=espacio.id,
        )
        respuesta = client.post(
            "/zonas",
            json={"nombre": "Zona Gestor", "espacio_id": espacio.id},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 201

    def test_gestor_no_puede_crear_zona_en_otro_espacio(self, client, db):
        espacio_propio = crear_espacio(db, nombre="Espacio Propio Gestor Zona")
        espacio_ajeno = crear_espacio(db, nombre="Espacio Ajeno Gestor Zona")
        gestor = crear_usuario(
            db, username="gestor_zcrea4", email="gestor_zcrea4@example.com", rol="gestor",
            espacio_id=espacio_propio.id,
        )
        respuesta = client.post(
            "/zonas",
            json={"nombre": "Zona Ajena", "espacio_id": espacio_ajeno.id},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 403

    def test_espacio_inexistente_da_404(self, client, db):
        admin = crear_usuario(db, username="admin_zcrea5", email="admin_zcrea5@example.com", rol="admin")
        respuesta = client.post(
            "/zonas",
            json={"nombre": "Zona Espacio Falso", "espacio_id": 999999},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 404

    def test_created_by_updated_by_ignoran_valor_inyectado_en_payload(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Inyeccion Auditoria")
        admin = crear_usuario(db, username="admin_zcrea6", email="admin_zcrea6@example.com", rol="admin")
        respuesta = client.post(
            "/zonas",
            json={
                "nombre": "Zona Inyeccion",
                "espacio_id": espacio.id,
                "created_by": 999999,
                "updated_by": 999999,
            },
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["created_by"] == admin.id
        assert cuerpo["updated_by"] == admin.id


class TestCrearZonaValidaciones:
    def test_nombre_vacio_da_422(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Validacion Nombre Vacio")
        admin = crear_usuario(db, username="admin_zval1", email="admin_zval1@example.com", rol="admin")
        respuesta = client.post(
            "/zonas",
            json={"nombre": "", "espacio_id": espacio.id},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 422

    def test_nombre_supera_longitud_maxima_da_422(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Validacion Nombre Largo")
        admin = crear_usuario(db, username="admin_zval2", email="admin_zval2@example.com", rol="admin")
        respuesta = client.post(
            "/zonas",
            json={"nombre": "Z" * 101, "espacio_id": espacio.id},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 422

    def test_capacidad_cero_da_422(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Validacion Capacidad Cero")
        admin = crear_usuario(db, username="admin_zval3", email="admin_zval3@example.com", rol="admin")
        respuesta = client.post(
            "/zonas",
            json={"nombre": "Zona Capacidad Cero", "espacio_id": espacio.id, "capacidad": 0},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 422

    def test_capacidad_nula_es_aceptada(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Validacion Capacidad Nula")
        admin = crear_usuario(db, username="admin_zval4", email="admin_zval4@example.com", rol="admin")
        respuesta = client.post(
            "/zonas",
            json={"nombre": "Zona Capacidad Nula", "espacio_id": espacio.id, "capacidad": None},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["capacidad"] is None

    def test_estado_invalido_da_422(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Validacion Estado Invalido")
        admin = crear_usuario(db, username="admin_zval5", email="admin_zval5@example.com", rol="admin")
        respuesta = client.post(
            "/zonas",
            json={"nombre": "Zona Estado Invalido", "espacio_id": espacio.id, "estado": "bogus"},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 422


class TestActualizarZona:
    def test_admin_actualiza_zona(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Actualizar Zona Admin")
        admin = crear_usuario(db, username="admin_zupd1", email="admin_zupd1@example.com", rol="admin")
        zona = _crear_zona_directa(db, espacio=espacio, usuario=admin, nombre="Zona Original")
        respuesta = client.put(
            f"/zonas/{zona.id}",
            json={"nombre": "Zona Renombrada", "capacidad": 8},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["nombre"] == "Zona Renombrada"
        assert cuerpo["capacidad"] == 8
        assert cuerpo["updated_by"] == admin.id

    def test_gestor_actualiza_zona_de_su_espacio(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Actualizar Zona Gestor")
        admin = crear_usuario(db, username="admin_zupd2", email="admin_zupd2@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zupd2", email="gestor_zupd2@example.com", rol="gestor",
            espacio_id=espacio.id,
        )
        zona = _crear_zona_directa(db, espacio=espacio, usuario=admin, nombre="Zona Gestor Original")
        respuesta = client.put(
            f"/zonas/{zona.id}",
            json={"estado": "mantenimiento"},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["estado"] == "mantenimiento"
        assert respuesta.json()["updated_by"] == gestor.id

    def test_gestor_no_puede_actualizar_zona_de_otro_espacio(self, client, db):
        espacio_propio = crear_espacio(db, nombre="Espacio Propio Update Zona")
        espacio_ajeno = crear_espacio(db, nombre="Espacio Ajeno Update Zona")
        admin = crear_usuario(db, username="admin_zupd3", email="admin_zupd3@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zupd3", email="gestor_zupd3@example.com", rol="gestor",
            espacio_id=espacio_propio.id,
        )
        zona = _crear_zona_directa(db, espacio=espacio_ajeno, usuario=admin, nombre="Zona Ajena Update")
        respuesta = client.put(
            f"/zonas/{zona.id}",
            json={"nombre": "Intento"},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 403

    def test_usuario_no_puede_actualizar_zona(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Update Zona Usuario")
        admin = crear_usuario(db, username="admin_zupd4", email="admin_zupd4@example.com", rol="admin")
        usuario = crear_usuario(db, username="user_zupd4", email="user_zupd4@example.com")
        zona = _crear_zona_directa(db, espacio=espacio, usuario=admin, nombre="Zona Usuario Update")
        respuesta = client.put(
            f"/zonas/{zona.id}",
            json={"nombre": "Intento Usuario"},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 403

    def test_zona_inexistente_da_404(self, client, db):
        admin = crear_usuario(db, username="admin_zupd5", email="admin_zupd5@example.com", rol="admin")
        respuesta = client.put(
            "/zonas/999999",
            json={"nombre": "No existe"},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 404

    def test_mover_a_espacio_inexistente_da_404(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Mover Zona Origen")
        admin = crear_usuario(db, username="admin_zupd6", email="admin_zupd6@example.com", rol="admin")
        zona = _crear_zona_directa(db, espacio=espacio, usuario=admin, nombre="Zona Mover")
        respuesta = client.put(
            f"/zonas/{zona.id}",
            json={"espacio_id": 999999},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 404

    def test_gestor_no_puede_mover_zona_fuera_de_su_espacio(self, client, db):
        espacio_propio = crear_espacio(db, nombre="Espacio Propio Mover Zona")
        espacio_destino = crear_espacio(db, nombre="Espacio Destino Mover Zona")
        admin = crear_usuario(db, username="admin_zupd7", email="admin_zupd7@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zupd7", email="gestor_zupd7@example.com", rol="gestor",
            espacio_id=espacio_propio.id,
        )
        zona = _crear_zona_directa(db, espacio=espacio_propio, usuario=admin, nombre="Zona Propia Mover")
        respuesta = client.put(
            f"/zonas/{zona.id}",
            json={"espacio_id": espacio_destino.id},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 200
        # El espacio_id enviado se ignora para un gestor (no puede mover
        # zonas fuera de su propio espacio) -- mismo criterio que Recurso.
        assert respuesta.json()["espacio_id"] == espacio_propio.id

    def test_capacidad_cero_en_actualizacion_da_422(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Update Capacidad Cero")
        admin = crear_usuario(db, username="admin_zupd8", email="admin_zupd8@example.com", rol="admin")
        zona = _crear_zona_directa(db, espacio=espacio, usuario=admin, nombre="Zona Capacidad Cero Update")
        respuesta = client.put(
            f"/zonas/{zona.id}",
            json={"capacidad": 0},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 422

    def test_created_by_no_se_puede_sobreescribir_en_actualizacion(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Update Sin Sobreescribir Auditoria")
        admin = crear_usuario(db, username="admin_zupd9", email="admin_zupd9@example.com", rol="admin")
        zona = _crear_zona_directa(db, espacio=espacio, usuario=admin, nombre="Zona Auditoria Update")
        respuesta = client.put(
            f"/zonas/{zona.id}",
            json={"nombre": "Zona Auditoria Update 2", "created_by": 999999, "updated_by": 999999},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["created_by"] == admin.id
        assert cuerpo["updated_by"] == admin.id


class TestEliminarZona:
    def test_admin_elimina_zona(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Eliminar Zona Admin")
        admin = crear_usuario(db, username="admin_zdel1", email="admin_zdel1@example.com", rol="admin")
        zona = _crear_zona_directa(db, espacio=espacio, usuario=admin, nombre="Zona A Eliminar")
        respuesta = client.delete(f"/zonas/{zona.id}", headers=cookies_para(admin))
        assert respuesta.status_code == 204
        assert client.get("/zonas", headers=cookies_para(admin)).json() == []

    def test_gestor_elimina_zona_de_su_espacio(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Eliminar Zona Gestor")
        admin = crear_usuario(db, username="admin_zdel2", email="admin_zdel2@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zdel2", email="gestor_zdel2@example.com", rol="gestor",
            espacio_id=espacio.id,
        )
        zona = _crear_zona_directa(db, espacio=espacio, usuario=admin, nombre="Zona Gestor A Eliminar")
        respuesta = client.delete(f"/zonas/{zona.id}", headers=cookies_para(gestor))
        assert respuesta.status_code == 204

    def test_gestor_no_puede_eliminar_zona_de_otro_espacio(self, client, db):
        espacio_propio = crear_espacio(db, nombre="Espacio Propio Eliminar Zona")
        espacio_ajeno = crear_espacio(db, nombre="Espacio Ajeno Eliminar Zona")
        admin = crear_usuario(db, username="admin_zdel3", email="admin_zdel3@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_zdel3", email="gestor_zdel3@example.com", rol="gestor",
            espacio_id=espacio_propio.id,
        )
        zona = _crear_zona_directa(db, espacio=espacio_ajeno, usuario=admin, nombre="Zona Ajena A Eliminar")
        respuesta = client.delete(f"/zonas/{zona.id}", headers=cookies_para(gestor))
        assert respuesta.status_code == 403

    def test_usuario_no_puede_eliminar_zona(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Eliminar Zona Usuario")
        admin = crear_usuario(db, username="admin_zdel4", email="admin_zdel4@example.com", rol="admin")
        usuario = crear_usuario(db, username="user_zdel4", email="user_zdel4@example.com")
        zona = _crear_zona_directa(db, espacio=espacio, usuario=admin, nombre="Zona Usuario No Elimina")
        respuesta = client.delete(f"/zonas/{zona.id}", headers=cookies_para(usuario))
        assert respuesta.status_code == 403

    def test_zona_inexistente_da_404_al_eliminar(self, client, db):
        admin = crear_usuario(db, username="admin_zdel5", email="admin_zdel5@example.com", rol="admin")
        respuesta = client.delete("/zonas/999999", headers=cookies_para(admin))
        assert respuesta.status_code == 404

    def test_eliminacion_bloqueada_con_asociaciones(self, client, db):
        """Fase 12C-3: DELETE /zonas/{id} ahora bloquea si tiene
        asociaciones zona-recurso, igual que eliminar_recurso/
        eliminar_espacio bloquean con sus propias dependencias."""
        from app.models.zona_recurso import ZonaRecurso

        espacio = crear_espacio(db, nombre="Espacio Eliminar Zona Con Asociacion")
        admin = crear_usuario(db, username="admin_zdel6", email="admin_zdel6@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        zona = _crear_zona_directa(db, espacio=espacio, usuario=admin, nombre="Zona Con Recurso")
        db.add(ZonaRecurso(zona_id=zona.id, recurso_id=recurso.id))
        db.commit()

        respuesta = client.delete(f"/zonas/{zona.id}", headers=cookies_para(admin))
        assert respuesta.status_code == 409


class TestSinEndpointDeUnaSolaZona:
    """Decision deliberada de 12C-2: Recurso no tiene GET /recursos/{id} de
    un solo recurso (solo listado, /gestion y /disponibilidad); Zona sigue
    el mismo patron y tampoco lo tiene en esta subfase."""

    def test_get_zona_individual_no_existe(self, client, db):
        espacio = crear_espacio(db, nombre="Espacio Sin Get Individual")
        admin = crear_usuario(db, username="admin_zget1", email="admin_zget1@example.com", rol="admin")
        zona = _crear_zona_directa(db, espacio=espacio, usuario=admin, nombre="Zona Sin Get")
        respuesta = client.get(f"/zonas/{zona.id}")
        assert respuesta.status_code == 405
