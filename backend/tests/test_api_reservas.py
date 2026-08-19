# -*- coding: utf-8 -*-
"""Pruebas de integración de reservas (api/reservas.py + services/reservas.py).

Reglas cubiertas:
- RN-019: reserva de usuario queda en estado esperando (requiere aprobación).
- RN-020: gestor que reserva recurso de otro espacio queda en esperando.
- RN-021: gestor que reserva en su propio espacio queda aprobada.
- RN-017: confirmación por aprobación o creación directa del gestor.
- Solapamiento (validación + exclusión btree_gist reservas_sin_solapamiento)
  responde 409; bloques contiguos están permitidos.
- Bloques de hora completa, horario de atención y anticipación mínima.
- Capacidad máxima y estado activo del recurso/espacio.
- Transiciones de estado y cancelación únicamente por el propietario.
"""

from tests.conftest import (
    crear_espacio,
    crear_recurso,
    crear_usuario,
    fecha_habilitada,
    headers_para,
    payload_reserva,
    proximo_domingo,
)


def _setup(db, *, rol="usuario", es_gestor_del_espacio=False, nombre_espacio="Sala A"):
    espacio = crear_espacio(db, nombre=nombre_espacio)
    usuario = crear_usuario(
        db,
        username=f"user_{rol}_{nombre_espacio.replace(' ', '')}",
        email=f"{rol}-{nombre_espacio.replace(' ', '')}@example.com",
        rol=rol,
        espacio_id=espacio.id if (rol == "gestor" and es_gestor_del_espacio) else None,
    )
    recurso = crear_recurso(db, espacio=espacio, usuario=usuario)
    return usuario, espacio, recurso


class TestCrearReserva:
    def test_usuario_queda_esperando(self, client, db):  # RN-019
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["estado"] == "esperando"

    def test_gestor_de_su_espacio_queda_aprobada(self, client, db):  # RN-021
        usuario, _, recurso = _setup(db, rol="gestor", es_gestor_del_espacio=True)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["estado"] == "aprobada"

    def test_gestor_de_otro_espacio_queda_esperando(self, client, db):  # RN-020
        espacio_a = crear_espacio(db, nombre="Sala Gestor")
        usuario = crear_usuario(
            db,
            username="gestor_a",
            email="gestor_a@example.com",
            rol="gestor",
            espacio_id=espacio_a.id,
        )
        espacio_b = crear_espacio(db, nombre="Sala B")
        recurso_b = crear_recurso(db, espacio=espacio_b, usuario=usuario)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso_b.id, fecha_habilitada()),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["estado"] == "esperando"

    def test_bloque_no_completo_da_400(self, client, db):
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada(), hora_inicio="08:30"),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_inicio_posterior_a_fin_da_400(self, client, db):
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(
                recurso.id, fecha_habilitada(), hora_inicio="10:00", hora_fin="08:00"
            ),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_fuera_del_horario_de_atencion_da_400(self, client, db):
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(
                recurso.id, fecha_habilitada(), hora_inicio="20:00", hora_fin="21:00"
            ),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_dia_sin_atencion_da_400(self, client, db):
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, proximo_domingo()),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_anticipacion_insuficiente_da_400(self, client, db):
        espacio = crear_espacio(db, nombre="Sala Antelada", horas_antelacion=720)
        usuario = crear_usuario(db, username="user_anti", email="user_anti@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=usuario)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_asistentes_superan_capacidad_da_400(self, client, db):
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada(), asistentes=11),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_asistentes_no_positivos_da_422(self, client, db):
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada(), asistentes=0),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 422

    def test_recurso_inactivo_da_400(self, client, db):
        espacio = crear_espacio(db, nombre="Sala Inactiva Rec")
        usuario = crear_usuario(db, username="user_rec", email="user_rec@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=usuario, estado="inactivo")
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_espacio_inactivo_da_400(self, client, db):
        espacio = crear_espacio(db, nombre="Sala Inactiva Esp", estado="inactivo")
        usuario = crear_usuario(db, username="user_esp", email="user_esp@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=usuario)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_sin_token_da_401(self, client, db):
        _, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada())
        )
        assert respuesta.status_code == 401


class TestRecursosPS:
    """RN-009 (Fase 12B): un recurso marcado como PS (prestación de
    servicios) no puede reservarse por el rol `usuario`. `gestor`/`admin`
    sí pueden reservarlo directamente en esta fase — el condicionamiento a
    un tipo de reserva "servicio de ensayo" (RN-015) queda para la Fase
    12D, que debe integrarse sin duplicar este gate de rol."""

    def _setup_ps(self, db, *, rol_creador="admin"):
        espacio = crear_espacio(db, nombre="Sala PS Reserva")
        creador = crear_usuario(
            db, username=f"creador_{rol_creador}", email=f"creador_{rol_creador}@example.com", rol=rol_creador
        )
        recurso_ps = crear_recurso(
            db, espacio=espacio, usuario=creador, nombre="Equipo PS Reserva", es_prestacion_servicio=True
        )
        return espacio, recurso_ps

    def test_usuario_no_puede_reservar_recurso_ps(self, client, db):
        _, recurso_ps = self._setup_ps(db)
        usuario = crear_usuario(db, username="user_reserva_ps", email="user_reserva_ps@example.com")
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso_ps.id, fecha_habilitada()),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 403

    def test_gestor_puede_reservar_recurso_ps_de_su_espacio(self, client, db):
        espacio, recurso_ps = self._setup_ps(db)
        gestor = crear_usuario(
            db, username="gestor_reserva_ps", email="gestor_reserva_ps@example.com",
            rol="gestor", espacio_id=espacio.id,
        )
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso_ps.id, fecha_habilitada()),
            headers=headers_para(gestor),
        )
        assert respuesta.status_code == 201

    def test_admin_puede_reservar_recurso_ps(self, client, db):
        _, recurso_ps = self._setup_ps(db)
        admin = crear_usuario(db, username="admin_reserva_ps", email="admin_reserva_ps@example.com", rol="admin")
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso_ps.id, fecha_habilitada()),
            headers=headers_para(admin),
        )
        assert respuesta.status_code == 201

    def test_usuario_no_puede_editar_reserva_hacia_recurso_ps(self, client, db):
        espacio = crear_espacio(db, nombre="Sala PS Editar")
        admin = crear_usuario(db, username="admin_edit_ps", email="admin_edit_ps@example.com", rol="admin")
        usuario = crear_usuario(db, username="user_edit_ps", email="user_edit_ps@example.com")
        recurso_normal = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Normal Editar")
        recurso_ps = crear_recurso(
            db, espacio=espacio, usuario=admin, nombre="PS Editar", es_prestacion_servicio=True
        )
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso_normal.id, fecha_habilitada()),
            headers=headers_para(usuario),
        ).json()
        respuesta = client.patch(
            f"/reservas/{creada['id']}",
            json={"recurso_ids": [recurso_ps.id]},
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 403

    def test_reserva_normal_sin_cambios(self, client, db):
        """Un recurso no-PS sigue reservable por cualquier rol autenticado,
        sin ningún cambio de comportamiento por esta fase."""
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["estado"] == "esperando"


class TestSolapamiento:
    def test_solapamiento_exacto_da_409(self, client, db):
        usuario, _, recurso = _setup(db)
        payload = payload_reserva(recurso.id, fecha_habilitada())
        assert (
            client.post("/reservas", json=payload, headers=headers_para(usuario)).status_code
            == 201
        )
        respuesta = client.post("/reservas", json=payload, headers=headers_para(usuario))
        assert respuesta.status_code == 409

    def test_solapamiento_parcial_da_409(self, client, db):
        usuario, _, recurso = _setup(db)
        assert (
            client.post(
                "/reservas",
                json=payload_reserva(recurso.id, fecha_habilitada()),
                headers=headers_para(usuario),
            ).status_code
            == 201
        )
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(
                recurso.id, fecha_habilitada(), hora_inicio="09:00", hora_fin="11:00"
            ),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 409

    def test_bloques_contiguos_permitidos(self, client, db):
        usuario, _, recurso = _setup(db)
        fecha = fecha_habilitada()
        assert (
            client.post(
                "/reservas",
                json=payload_reserva(recurso.id, fecha),
                headers=headers_para(usuario),
            ).status_code
            == 201
        )
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(
                recurso.id, fecha, hora_inicio="10:00", hora_fin="11:00"
            ),
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 201


class TestTransiciones:
    def test_flujo_aprobar_y_cancelar(self, client, db):
        usuario, espacio, recurso = _setup(db)
        gestor = crear_usuario(
            db, username="gestor_flow", email="gestor_flow@example.com",
            rol="gestor", espacio_id=espacio.id,
        )
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=headers_para(usuario),
        ).json()
        aprobada = client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "aprobada"},
            headers=headers_para(gestor),
        )
        assert aprobada.status_code == 200
        assert aprobada.json()["estado"] == "aprobada"
        cancelada = client.put(
            f"/reservas/{creada['id']}/cancelar", headers=headers_para(usuario)
        )
        assert cancelada.status_code == 200
        assert cancelada.json()["estado"] == "cancelada"

    def test_rechazada_no_puede_aprobarse(self, client, db):
        usuario, espacio, recurso = _setup(db)
        gestor = crear_usuario(
            db, username="gestor_rech", email="gestor_rech@example.com",
            rol="gestor", espacio_id=espacio.id,
        )
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=headers_para(usuario),
        ).json()
        rechazada = client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "rechazada"},
            headers=headers_para(gestor),
        )
        assert rechazada.status_code == 200
        aprobar = client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "aprobada"},
            headers=headers_para(gestor),
        )
        assert aprobar.status_code == 409

    def test_usuario_no_puede_cambiar_estado(self, client, db):
        usuario, _, recurso = _setup(db)
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=headers_para(usuario),
        ).json()
        respuesta = client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "aprobada"},
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 403

    def test_solo_propietario_cancela(self, client, db):
        usuario, espacio, recurso = _setup(db)
        gestor = crear_usuario(
            db, username="gestor_canc", email="gestor_canc@example.com",
            rol="gestor", espacio_id=espacio.id,
        )
        otro = crear_usuario(db, username="otro", email="otro@example.com")
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=headers_para(usuario),
        ).json()
        client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "aprobada"},
            headers=headers_para(gestor),
        )
        respuesta = client.put(
            f"/reservas/{creada['id']}/cancelar", headers=headers_para(otro)
        )
        assert respuesta.status_code == 403

    def test_usuario_no_puede_eliminar(self, client, db):
        usuario, _, recurso = _setup(db)
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=headers_para(usuario),
        ).json()
        respuesta = client.delete(
            f"/reservas/{creada['id']}", headers=headers_para(usuario)
        )
        assert respuesta.status_code == 403

    def test_mis_reservas_solo_propias(self, client, db):
        usuario_a, _, recurso = _setup(db, nombre_espacio="Sala A")
        usuario_b = crear_usuario(db, username="user_b", email="user_b@example.com")
        fecha = fecha_habilitada()
        client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha),
            headers=headers_para(usuario_a),
        )
        client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha, hora_inicio="12:00", hora_fin="13:00"),
            headers=headers_para(usuario_a),
        )
        client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha, hora_inicio="14:00", hora_fin="15:00"),
            headers=headers_para(usuario_b),
        )
        respuesta = client.get("/reservas/mis-reservas", headers=headers_para(usuario_b))
        assert respuesta.status_code == 200
        assert len(respuesta.json()) == 1
