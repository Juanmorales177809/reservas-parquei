# -*- coding: utf-8 -*-
"""Pruebas de integración de tipos de reserva (api/tipos_reserva.py) -- Fase 7.

Reglas cubiertas:
- Lectura pública tipo RN-005: anonimo/`usuario` solo ven tipos `activo`;
  `gestor`/`admin` ven todo (para poder gestionarlos, incluidos inactivos).
- Escritura (POST/PUT/DELETE) restringida a `gestor`/`admin`
  (`require_resource_manager`); `usuario` recibe 403.
- Un gestor solo puede crear/editar/eliminar tipos de su propio laboratorio
  asignado, igual que ya rige para Espacio/Recurso.
- `laboratorio_id` inexistente da 404 al crear.
- No se puede eliminar un tipo de reserva en uso por una reserva (409).
"""

from tests.conftest import crear_laboratorio, crear_recurso, crear_usuario, cookies_para


def _crear_tipo_reserva_directo(db, *, laboratorio, usuario, nombre="Trabajo de grado", estado="activo"):
    from app.models.tipo_reserva import TipoReserva

    tipo = TipoReserva(
        laboratorio_id=laboratorio.id,
        nombre=nombre,
        estado=estado,
        created_by=usuario.id,
        updated_by=usuario.id,
    )
    db.add(tipo)
    db.commit()
    db.refresh(tipo)
    return tipo


class TestListarTiposReservaVisibilidadPublica:
    def test_anonimo_ve_solo_tipos_activos(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Lab Tipos Anon")
        admin = crear_usuario(db, username="admin_tr1", email="admin_tr1@example.com", rol="admin")
        _crear_tipo_reserva_directo(db, laboratorio=laboratorio, usuario=admin, nombre="Activo")
        _crear_tipo_reserva_directo(db, laboratorio=laboratorio, usuario=admin, nombre="Inactivo", estado="inactivo")

        nombres = [t["nombre"] for t in client.get("/tipos-reserva").json()]
        assert nombres == ["Activo"]

    def test_admin_ve_todos_incluidos_inactivos(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Lab Tipos Admin")
        admin = crear_usuario(db, username="admin_tr2", email="admin_tr2@example.com", rol="admin")
        _crear_tipo_reserva_directo(db, laboratorio=laboratorio, usuario=admin, nombre="Solo Admin", estado="inactivo")

        nombres = [
            t["nombre"] for t in client.get("/tipos-reserva", headers=cookies_para(admin)).json()
        ]
        assert "Solo Admin" in nombres

    def test_filtra_por_laboratorio_id(self, client, db):
        lab_a = crear_laboratorio(db, nombre="Lab Tipos A")
        lab_b = crear_laboratorio(db, nombre="Lab Tipos B")
        admin = crear_usuario(db, username="admin_tr3", email="admin_tr3@example.com", rol="admin")
        _crear_tipo_reserva_directo(db, laboratorio=lab_a, usuario=admin, nombre="De A")
        _crear_tipo_reserva_directo(db, laboratorio=lab_b, usuario=admin, nombre="De B")

        nombres = [t["nombre"] for t in client.get(f"/tipos-reserva?laboratorio_id={lab_a.id}").json()]
        assert nombres == ["De A"]


class TestCrearTipoReserva:
    def test_usuario_no_puede_crear(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Lab Tipos Crear U")
        usuario = crear_usuario(db, username="user_tr1", email="user_tr1@example.com")

        respuesta = client.post(
            "/tipos-reserva",
            json={"laboratorio_id": laboratorio.id, "nombre": "Trabajo de grado"},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 403

    def test_admin_crea_con_created_by_propio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Lab Tipos Crear Admin")
        admin = crear_usuario(db, username="admin_tr4", email="admin_tr4@example.com", rol="admin")

        respuesta = client.post(
            "/tipos-reserva",
            json={"laboratorio_id": laboratorio.id, "nombre": "Trabajo de grado"},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["created_by"] == admin.id
        assert cuerpo["estado"] == "activo"

    def test_laboratorio_inexistente_da_404(self, client, db):
        admin = crear_usuario(db, username="admin_tr5", email="admin_tr5@example.com", rol="admin")

        respuesta = client.post(
            "/tipos-reserva",
            json={"laboratorio_id": 999999, "nombre": "Trabajo de grado"},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 404

    def test_gestor_no_puede_crear_en_laboratorio_ajeno(self, client, db):
        lab_propio = crear_laboratorio(db, nombre="Lab Tipos Gestor Propio")
        lab_ajeno = crear_laboratorio(db, nombre="Lab Tipos Gestor Ajeno")
        gestor = crear_usuario(
            db, username="gestor_tr1", email="gestor_tr1@example.com", rol="gestor",
            laboratorio_id=lab_propio.id,
        )

        respuesta = client.post(
            "/tipos-reserva",
            json={"laboratorio_id": lab_ajeno.id, "nombre": "Trabajo de grado"},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 403

    def test_gestor_puede_crear_en_su_propio_laboratorio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Lab Tipos Gestor Propio 2")
        gestor = crear_usuario(
            db, username="gestor_tr2", email="gestor_tr2@example.com", rol="gestor",
            laboratorio_id=laboratorio.id,
        )

        respuesta = client.post(
            "/tipos-reserva",
            json={"laboratorio_id": laboratorio.id, "nombre": "Trabajo de grado"},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 201


class TestActualizarYEliminarTipoReserva:
    def test_gestor_no_puede_editar_tipo_de_otro_laboratorio(self, client, db):
        lab_propio = crear_laboratorio(db, nombre="Lab Tipos Editar Propio")
        lab_ajeno = crear_laboratorio(db, nombre="Lab Tipos Editar Ajeno")
        admin = crear_usuario(db, username="admin_tr6", email="admin_tr6@example.com", rol="admin")
        gestor = crear_usuario(
            db, username="gestor_tr3", email="gestor_tr3@example.com", rol="gestor",
            laboratorio_id=lab_propio.id,
        )
        tipo_ajeno = _crear_tipo_reserva_directo(db, laboratorio=lab_ajeno, usuario=admin)

        respuesta = client.put(
            f"/tipos-reserva/{tipo_ajeno.id}",
            json={"nombre": "Renombrado"},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 403

    def test_admin_actualiza_nombre_y_estado(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Lab Tipos Editar Admin")
        admin = crear_usuario(db, username="admin_tr7", email="admin_tr7@example.com", rol="admin")
        tipo = _crear_tipo_reserva_directo(db, laboratorio=laboratorio, usuario=admin, nombre="Original")

        respuesta = client.put(
            f"/tipos-reserva/{tipo.id}",
            json={"nombre": "Renombrado", "estado": "inactivo"},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["nombre"] == "Renombrado"
        assert cuerpo["estado"] == "inactivo"
        assert cuerpo["updated_by"] == admin.id

    def test_eliminar_tipo_sin_uso(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Lab Tipos Eliminar")
        admin = crear_usuario(db, username="admin_tr8", email="admin_tr8@example.com", rol="admin")
        tipo = _crear_tipo_reserva_directo(db, laboratorio=laboratorio, usuario=admin)

        respuesta = client.delete(f"/tipos-reserva/{tipo.id}", headers=cookies_para(admin))
        assert respuesta.status_code == 204

    def test_no_se_puede_eliminar_tipo_en_uso(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Lab Tipos En Uso")
        admin = crear_usuario(db, username="admin_tr9", email="admin_tr9@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        tipo = _crear_tipo_reserva_directo(db, laboratorio=laboratorio, usuario=admin)
        usuario = crear_usuario(db, username="user_tr2", email="user_tr2@example.com")

        respuesta_reserva = client.post(
            "/reservas",
            json={
                "recurso_ids": [recurso.id],
                "espacio_ids": [],
                "tipo_reserva_id": tipo.id,
                "fecha": "2027-01-15",
                "hora_inicio": "08:00",
                "hora_fin": "09:00",
                "asistentes": 2,
            },
            headers=cookies_para(usuario),
        )
        assert respuesta_reserva.status_code == 201
        assert respuesta_reserva.json()["tipo_reserva"]["id"] == tipo.id

        respuesta = client.delete(f"/tipos-reserva/{tipo.id}", headers=cookies_para(admin))
        assert respuesta.status_code == 409


class TestTipoReservaEnReserva:
    def test_tipo_reserva_de_otro_laboratorio_da_400(self, client, db):
        lab_a = crear_laboratorio(db, nombre="Lab Reserva Tipo A")
        lab_b = crear_laboratorio(db, nombre="Lab Reserva Tipo B")
        admin = crear_usuario(db, username="admin_tr10", email="admin_tr10@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=lab_a, usuario=admin)
        tipo_de_b = _crear_tipo_reserva_directo(db, laboratorio=lab_b, usuario=admin)
        usuario = crear_usuario(db, username="user_tr3", email="user_tr3@example.com")

        respuesta = client.post(
            "/reservas",
            json={
                "recurso_ids": [recurso.id],
                "espacio_ids": [],
                "tipo_reserva_id": tipo_de_b.id,
                "fecha": "2027-01-16",
                "hora_inicio": "08:00",
                "hora_fin": "09:00",
                "asistentes": 2,
            },
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_tipo_reserva_inexistente_da_404(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Lab Reserva Tipo Inexistente")
        admin = crear_usuario(db, username="admin_tr11", email="admin_tr11@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        usuario = crear_usuario(db, username="user_tr4", email="user_tr4@example.com")

        respuesta = client.post(
            "/reservas",
            json={
                "recurso_ids": [recurso.id],
                "espacio_ids": [],
                "tipo_reserva_id": 999999,
                "fecha": "2027-01-18",
                "hora_inicio": "08:00",
                "hora_fin": "09:00",
                "asistentes": 2,
            },
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 404
