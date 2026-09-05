# -*- coding: utf-8 -*-
"""Pruebas de integración de reservas (api/reservas.py + services/reservas.py).

Reglas cubiertas:
- RN-019: reserva de usuario queda en estado esperando (requiere aprobación).
- RN-020: gestor que reserva recurso de otro laboratorio queda en esperando.
- RN-021: gestor que reserva en su propio laboratorio queda aprobada.
- RN-017: confirmación por aprobación o creación directa del gestor.
- Solapamiento (validación + exclusión btree_gist reservas_sin_solapamiento)
  responde 409; bloques contiguos están permitidos.
- Bloques de hora completa, horario de atención y anticipación mínima.
- Capacidad máxima y estado activo del recurso/laboratorio.
- Transiciones de estado y cancelación únicamente por el propietario.
"""

from tests.conftest import (
    asociar_espacio_recurso,
    crear_espacio,
    crear_laboratorio,
    crear_recurso,
    crear_usuario,
    fecha_habilitada,
    cookies_para,
    payload_reserva,
    payload_reserva_objetivos,
    proximo_domingo,
)


def _setup(db, *, rol="usuario", es_gestor_del_espacio=False, nombre_espacio="Sala A"):
    laboratorio = crear_laboratorio(db, nombre=nombre_espacio)
    usuario = crear_usuario(
        db,
        username=f"user_{rol}_{nombre_espacio.replace(' ', '')}",
        email=f"{rol}-{nombre_espacio.replace(' ', '')}@example.com",
        rol=rol,
        laboratorio_id=laboratorio.id if (rol == "gestor" and es_gestor_del_espacio) else None,
    )
    recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)
    return usuario, laboratorio, recurso


class TestCrearReserva:
    def test_usuario_queda_esperando(self, client, db):  # RN-019
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["estado"] == "esperando"

    def test_gestor_de_su_espacio_queda_aprobada(self, client, db):  # RN-021
        usuario, _, recurso = _setup(db, rol="gestor", es_gestor_del_espacio=True)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["estado"] == "aprobada"

    def test_gestor_de_otro_espacio_queda_esperando(self, client, db):  # RN-020
        espacio_a = crear_laboratorio(db, nombre="Sala Gestor")
        usuario = crear_usuario(
            db,
            username="gestor_a",
            email="gestor_a@example.com",
            rol="gestor",
            laboratorio_id=espacio_a.id,
        )
        espacio_b = crear_laboratorio(db, nombre="Sala B")
        recurso_b = crear_recurso(db, laboratorio=espacio_b, usuario=usuario)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso_b.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["estado"] == "esperando"

    def test_bloque_no_completo_da_400(self, client, db):
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada(), hora_inicio="08:30"),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_inicio_posterior_a_fin_da_400(self, client, db):
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(
                recurso.id, fecha_habilitada(), hora_inicio="10:00", hora_fin="08:00"
            ),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_fuera_del_horario_de_atencion_da_400(self, client, db):
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(
                recurso.id, fecha_habilitada(), hora_inicio="20:00", hora_fin="21:00"
            ),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_dia_sin_atencion_da_400(self, client, db):
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, proximo_domingo()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_anticipacion_insuficiente_da_400(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Antelada", horas_antelacion=720)
        usuario = crear_usuario(db, username="user_anti", email="user_anti@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_asistentes_superan_capacidad_da_400(self, client, db):
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada(), asistentes=11),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_asistentes_no_positivos_da_422(self, client, db):
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada(), asistentes=0),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 422

    def test_recurso_inactivo_da_400(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Inactiva Rec")
        usuario = crear_usuario(db, username="user_rec", email="user_rec@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario, estado="inactivo")
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_espacio_inactivo_da_400(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Inactiva Esp", estado="inactivo")
        usuario = crear_usuario(db, username="user_esp", email="user_esp@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 400

    def test_sin_token_da_401(self, client, db):
        _, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada())
        )
        assert respuesta.status_code == 401


class TestRecursosPS:
    """`es_prestacion_servicio` sigue existiendo como dato de catálogo en
    `Recurso` (ver `models/recurso.py`, `api/recursos.py::_puede_ver_ps`),
    pero el gate que antes bloqueaba su reserva por rol/tipo (RN-009, Fase
    12B/12D, `validar_acceso_ps`) se quitó del flujo de reserva: un recurso
    PS se reserva igual que cualquier otro, sin restricción de rol ni de
    `tipo`."""

    def _setup_ps(self, db, *, rol_creador="admin"):
        laboratorio = crear_laboratorio(db, nombre="Sala PS Reserva")
        creador = crear_usuario(
            db, username=f"creador_{rol_creador}", email=f"creador_{rol_creador}@example.com", rol=rol_creador
        )
        recurso_ps = crear_recurso(
            db, laboratorio=laboratorio, usuario=creador, nombre="Equipo PS Reserva", es_prestacion_servicio=True
        )
        return laboratorio, recurso_ps

    def test_usuario_puede_reservar_recurso_ps(self, client, db):
        _, recurso_ps = self._setup_ps(db)
        usuario = crear_usuario(db, username="user_reserva_ps", email="user_reserva_ps@example.com")
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso_ps.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201

    def test_gestor_puede_reservar_ps_sin_declarar_tipo(self, client, db):
        laboratorio, recurso_ps = self._setup_ps(db)
        gestor = crear_usuario(
            db, username="gestor_reserva_ps", email="gestor_reserva_ps@example.com",
            rol="gestor", laboratorio_id=laboratorio.id,
        )
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso_ps.id, fecha_habilitada()),
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 201

    def test_admin_puede_reservar_ps_sin_declarar_tipo(self, client, db):
        _, recurso_ps = self._setup_ps(db)
        admin = crear_usuario(db, username="admin_reserva_ps", email="admin_reserva_ps@example.com", rol="admin")
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso_ps.id, fecha_habilitada()),
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 201

    def test_usuario_puede_editar_reserva_hacia_recurso_ps(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala PS Editar")
        admin = crear_usuario(db, username="admin_edit_ps", email="admin_edit_ps@example.com", rol="admin")
        usuario = crear_usuario(db, username="user_edit_ps", email="user_edit_ps@example.com")
        recurso_normal = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Normal Editar")
        recurso_ps = crear_recurso(
            db, laboratorio=laboratorio, usuario=admin, nombre="PS Editar", es_prestacion_servicio=True
        )
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso_normal.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        respuesta = client.patch(
            f"/reservas/{creada['id']}",
            json={"recurso_ids": [recurso_ps.id]},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 200

    def test_reserva_normal_sin_cambios(self, client, db):
        """Un recurso no-PS sigue reservable por cualquier rol autenticado,
        sin ningún cambio de comportamiento por esta fase."""
        usuario, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["estado"] == "esperando"


class TestSolapamiento:
    def test_solapamiento_exacto_da_409(self, client, db):
        usuario, _, recurso = _setup(db)
        payload = payload_reserva(recurso.id, fecha_habilitada())
        assert (
            client.post("/reservas", json=payload, headers=cookies_para(usuario)).status_code
            == 201
        )
        respuesta = client.post("/reservas", json=payload, headers=cookies_para(usuario))
        assert respuesta.status_code == 409

    def test_solapamiento_parcial_da_409(self, client, db):
        usuario, _, recurso = _setup(db)
        assert (
            client.post(
                "/reservas",
                json=payload_reserva(recurso.id, fecha_habilitada()),
                headers=cookies_para(usuario),
            ).status_code
            == 201
        )
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(
                recurso.id, fecha_habilitada(), hora_inicio="09:00", hora_fin="11:00"
            ),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 409

    def test_bloques_contiguos_permitidos(self, client, db):
        usuario, _, recurso = _setup(db)
        fecha = fecha_habilitada()
        assert (
            client.post(
                "/reservas",
                json=payload_reserva(recurso.id, fecha),
                headers=cookies_para(usuario),
            ).status_code
            == 201
        )
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(
                recurso.id, fecha, hora_inicio="10:00", hora_fin="11:00"
            ),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201


class TestTransiciones:
    def test_flujo_aprobar_y_cancelar(self, client, db):
        usuario, laboratorio, recurso = _setup(db)
        gestor = crear_usuario(
            db, username="gestor_flow", email="gestor_flow@example.com",
            rol="gestor", laboratorio_id=laboratorio.id,
        )
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        aprobada = client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "aprobada"},
            headers=cookies_para(gestor),
        )
        assert aprobada.status_code == 200
        assert aprobada.json()["estado"] == "aprobada"
        cancelada = client.put(
            f"/reservas/{creada['id']}/cancelar", headers=cookies_para(usuario)
        )
        assert cancelada.status_code == 200
        assert cancelada.json()["estado"] == "cancelada"

    def test_rechazada_no_puede_aprobarse(self, client, db):
        usuario, laboratorio, recurso = _setup(db)
        gestor = crear_usuario(
            db, username="gestor_rech", email="gestor_rech@example.com",
            rol="gestor", laboratorio_id=laboratorio.id,
        )
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        rechazada = client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "rechazada", "motivo": "No hay disponibilidad"},
            headers=cookies_para(gestor),
        )
        assert rechazada.status_code == 200
        assert rechazada.json()["motivo_rechazo"] == "No hay disponibilidad"
        aprobar = client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "aprobada"},
            headers=cookies_para(gestor),
        )
        assert aprobar.status_code == 409

    def test_usuario_no_puede_cambiar_estado(self, client, db):
        usuario, _, recurso = _setup(db)
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        respuesta = client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "aprobada"},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 403

    def test_solo_propietario_cancela(self, client, db):
        usuario, laboratorio, recurso = _setup(db)
        gestor = crear_usuario(
            db, username="gestor_canc", email="gestor_canc@example.com",
            rol="gestor", laboratorio_id=laboratorio.id,
        )
        otro = crear_usuario(db, username="otro", email="otro@example.com")
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "aprobada"},
            headers=cookies_para(gestor),
        )
        respuesta = client.put(
            f"/reservas/{creada['id']}/cancelar", headers=cookies_para(otro)
        )
        assert respuesta.status_code == 403

    def test_usuario_no_puede_eliminar(self, client, db):
        usuario, _, recurso = _setup(db)
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        respuesta = client.delete(
            f"/reservas/{creada['id']}", headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 403

    def test_mis_reservas_solo_propias(self, client, db):
        usuario_a, _, recurso = _setup(db, nombre_espacio="Sala A")
        usuario_b = crear_usuario(db, username="user_b", email="user_b@example.com")
        fecha = fecha_habilitada()
        client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha),
            headers=cookies_para(usuario_a),
        )
        client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha, hora_inicio="12:00", hora_fin="13:00"),
            headers=cookies_para(usuario_a),
        )
        client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha, hora_inicio="14:00", hora_fin="15:00"),
            headers=cookies_para(usuario_b),
        )
        respuesta = client.get("/reservas/mis-reservas", headers=cookies_para(usuario_b))
        assert respuesta.status_code == 200
        assert len(respuesta.json()) == 1


class TestMotivoSolicitud:
    """Fase B: `tipo_solicitud`/`ubicacion_uso`/`requiere_apoyo_auxiliar`
    (ramas 1 y 2 del formulario real -- reserva dentro/fuera del
    laboratorio). Las ramas 3 y 4 (orden de salida, mano de obra) no
    existen todavía -- ver TestOrdenSalidaRechazada."""

    def _payload(self, recurso_id, fecha, **extra):
        payload = payload_reserva(recurso_id, fecha)
        payload.update(extra)
        return payload

    def test_post_sin_tipo_solicitud_usa_el_default(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Motivo 0")
        resp = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 201
        assert resp.json()["tipo_solicitud"] == "reserva_en_laboratorio"
        assert resp.json()["requiere_apoyo_auxiliar"] is False
        assert resp.json()["ubicacion_uso"] is None

    def test_post_reserva_fuera_del_laboratorio_con_ubicacion(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Motivo 1")
        resp = client.post(
            "/reservas",
            json=self._payload(
                recurso.id,
                fecha_habilitada(),
                tipo_solicitud="reserva_fuera_laboratorio",
                ubicacion_uso="Auditorio del bloque 5",
                requiere_apoyo_auxiliar=True,
            ),
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 201
        cuerpo = resp.json()
        assert cuerpo["tipo_solicitud"] == "reserva_fuera_laboratorio"
        assert cuerpo["ubicacion_uso"] == "Auditorio del bloque 5"
        assert cuerpo["requiere_apoyo_auxiliar"] is True

    def test_post_ubicacion_uso_sin_reserva_fuera_del_laboratorio_da_422(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Motivo 2")
        resp = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada(), ubicacion_uso="No debería aceptarse"),
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 422

    def test_post_tipo_solicitud_orden_salida_da_422(self, client, db):
        """El endpoint público jamás acepta orden_salida -- solo lo
        materializará internamente la Fase C, nunca ReservaCreate."""
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Motivo 3")
        resp = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada(), tipo_solicitud="orden_salida"),
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 422

    def test_patch_cambia_tipo_solicitud_y_ubicacion_juntos(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Motivo Patch")
        creada = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()

        resp = client.patch(
            f"/reservas/{creada['id']}",
            json={"tipo_solicitud": "reserva_fuera_laboratorio", "ubicacion_uso": "Cancha techada"},
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 200
        assert resp.json()["tipo_solicitud"] == "reserva_fuera_laboratorio"
        assert resp.json()["ubicacion_uso"] == "Cancha techada"

    def test_patch_ubicacion_uso_sola_sin_cambiar_tipo_da_400(self, client, db):
        """La reserva sigue siendo reserva_en_laboratorio (default) -- mandar
        solo ubicacion_uso sin también mover el tipo es la combinación
        inválida, detectada en el servicio (no en el schema, que no ve el
        estado actual de la reserva)."""
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Motivo Patch 400")
        creada = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()

        resp = client.patch(
            f"/reservas/{creada['id']}",
            json={"ubicacion_uso": "Cancha techada"},
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 400

    def test_patch_sin_tipo_solicitud_lo_conserva(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Motivo Conserva")
        creada = client.post(
            "/reservas",
            json=self._payload(
                recurso.id, fecha_habilitada(), tipo_solicitud="reserva_fuera_laboratorio", ubicacion_uso="X"
            ),
            headers=cookies_para(usuario),
        ).json()

        resp = client.patch(
            f"/reservas/{creada['id']}",
            json={"asistentes": 1},
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 200
        assert resp.json()["tipo_solicitud"] == "reserva_fuera_laboratorio"
        assert resp.json()["ubicacion_uso"] == "X"

    def test_patch_tipo_solicitud_con_null_explicito_da_422(self, client, db):
        """A diferencia de `descripcion`/`ubicacion_uso` (columnas nullable,
        donde `null` limpia), `tipo_solicitud` es NOT NULL -- mandarlo en
        `null` debe ser un error de validación, no un intento silencioso de
        romper la constraint de base de datos."""
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Motivo Null")
        creada = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()

        resp = client.patch(
            f"/reservas/{creada['id']}",
            json={"tipo_solicitud": None},
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 422

    def test_patch_tipo_solicitud_orden_salida_da_422(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Motivo Patch Orden")
        creada = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()

        resp = client.patch(
            f"/reservas/{creada['id']}",
            json={"tipo_solicitud": "orden_salida"},
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 422


class TestApoyoAuxiliarForzadoPorRecurso:
    """Un recurso con `requiere_apoyo_auxiliar=True` (catálogo) fuerza ese
    campo en la reserva que lo incluye, sin importar lo que mande el
    cliente -- nunca rechaza, solo lo activa por la persona (mismo criterio
    silencioso que "recursos cubiertos por un espacio se agregan solos")."""

    def test_crear_reserva_con_recurso_directo_fuerza_el_campo(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Apoyo Auxiliar")
        usuario = crear_usuario(db, username="user_apoyo_1", email="user_apoyo_1@example.com")
        recurso = crear_recurso(
            db, laboratorio=laboratorio, usuario=usuario, nombre="Grúa de estudio",
            requiere_apoyo_auxiliar=True,
        )
        payload = payload_reserva_objetivos(recurso_ids=[recurso.id], fecha=fecha_habilitada())
        payload["requiere_apoyo_auxiliar"] = False
        respuesta = client.post("/reservas", json=payload, headers=cookies_para(usuario))
        assert respuesta.status_code == 201
        assert respuesta.json()["requiere_apoyo_auxiliar"] is True

    def test_crear_reserva_con_recurso_cubierto_por_espacio_fuerza_el_campo(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Apoyo Auxiliar Espacio")
        usuario = crear_usuario(db, username="user_apoyo_2", email="user_apoyo_2@example.com")
        recurso = crear_recurso(
            db, laboratorio=laboratorio, usuario=usuario, nombre="Consola de mezcla",
            requiere_apoyo_auxiliar=True,
        )
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=usuario, nombre="Estudio de grabación")
        asociar_espacio_recurso(db, espacio, recurso)
        payload = payload_reserva_objetivos(espacio_ids=[espacio.id], fecha=fecha_habilitada())
        respuesta = client.post("/reservas", json=payload, headers=cookies_para(usuario))
        assert respuesta.status_code == 201
        assert respuesta.json()["requiere_apoyo_auxiliar"] is True

    def test_actualizar_reserva_agregando_recurso_obligatorio_fuerza_el_campo(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Apoyo Auxiliar PATCH")
        usuario = crear_usuario(db, username="user_apoyo_3", email="user_apoyo_3@example.com")
        recurso_normal = crear_recurso(db, laboratorio=laboratorio, usuario=usuario, nombre="Proyector")
        recurso_obligatorio = crear_recurso(
            db, laboratorio=laboratorio, usuario=usuario, nombre="Torno CNC",
            requiere_apoyo_auxiliar=True,
        )
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso_normal.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        assert creada["requiere_apoyo_auxiliar"] is False

        respuesta = client.patch(
            f"/reservas/{creada['id']}",
            json={"recurso_ids": [recurso_normal.id, recurso_obligatorio.id]},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["requiere_apoyo_auxiliar"] is True

    def test_sin_recurso_obligatorio_respeta_lo_que_manda_el_cliente(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Sin Apoyo Auxiliar")
        usuario = crear_usuario(db, username="user_apoyo_4", email="user_apoyo_4@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario, nombre="Cámara")
        payload = payload_reserva_objetivos(recurso_ids=[recurso.id], fecha=fecha_habilitada())
        payload["requiere_apoyo_auxiliar"] = True
        respuesta = client.post("/reservas", json=payload, headers=cookies_para(usuario))
        assert respuesta.status_code == 201
        assert respuesta.json()["requiere_apoyo_auxiliar"] is True

        payload_false = payload_reserva_objetivos(recurso_ids=[recurso.id], fecha=fecha_habilitada(dias=20))
        respuesta_false = client.post("/reservas", json=payload_false, headers=cookies_para(usuario))
        assert respuesta_false.status_code == 201
        assert respuesta_false.json()["requiere_apoyo_auxiliar"] is False


class TestDescripcion:
    """Fase A3: texto libre opcional ('Actividad a realizar' del formulario
    real de solicitud de laboratorios) -- eje simple, mismo criterio que
    `tipo`: ausente en el PATCH conserva, `null` explícito limpia."""

    def _payload(self, recurso_id, fecha, descripcion=None):
        payload = payload_reserva(recurso_id, fecha)
        if descripcion is not None:
            payload["descripcion"] = descripcion
        return payload

    def test_post_sin_descripcion_queda_null(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Desc 0")
        resp = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 201
        assert resp.json()["descripcion"] is None

    def test_post_con_descripcion_la_persiste(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Desc 1")
        resp = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada(), "Grabación del podcast semanal"),
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 201
        assert resp.json()["descripcion"] == "Grabación del podcast semanal"

    def test_patch_modifica_la_descripcion(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Desc Patch")
        creada = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada(), "Original"),
            headers=cookies_para(usuario),
        ).json()

        resp = client.patch(
            f"/reservas/{creada['id']}",
            json={"descripcion": "Actualizada"},
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 200
        assert resp.json()["descripcion"] == "Actualizada"

    def test_patch_sin_descripcion_la_conserva(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Desc Cons")
        creada = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada(), "Se mantiene"),
            headers=cookies_para(usuario),
        ).json()

        resp = client.patch(
            f"/reservas/{creada['id']}",
            json={"asistentes": 1},
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 200
        assert resp.json()["descripcion"] == "Se mantiene"

    def test_patch_con_null_explicito_la_limpia(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Desc Null")
        creada = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada(), "Se borra"),
            headers=cookies_para(usuario),
        ).json()

        resp = client.patch(
            f"/reservas/{creada['id']}",
            json={"descripcion": None},
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 200
        assert resp.json()["descripcion"] is None


class TestAcompanantes:
    def _payload(self, recurso_id, fecha, acompanantes):
        from tests.conftest import payload_reserva_objetivos

        return {
            "recurso_ids": [recurso_id],
            "espacio_ids": [],
            "fecha": fecha.isoformat(),
            "hora_inicio": "08:00",
            "hora_fin": "09:00",
            "asistentes": 2,
            "acompanantes": acompanantes,
        }

    def test_post_con_0_acompanantes(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Ac 0")
        resp = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada(), []),
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 201
        assert resp.json()["acompanantes"] == []

    def test_post_con_1_acompanante(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Ac 1")
        resp = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada(), [{"nombre": "Ana", "correo": "ana@example.com"}]),
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 201
        assert len(resp.json()["acompanantes"]) == 1

    def test_post_con_N_acompanantes(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Ac N")
        resp = client.post(
            "/reservas",
            json=self._payload(
                recurso.id,
                fecha_habilitada(),
                [{"nombre": "Ana", "correo": "ana@example.com"}, {"nombre": "Luis", "correo": "luis@example.com"}],
            ),
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 201
        assert len(resp.json()["acompanantes"]) == 2

    def test_patch_reemplaza_lista_completa(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Ac Patch")
        creada = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada(), [{"nombre": "Ana", "correo": "ana@example.com"}]),
            headers=cookies_para(usuario),
        ).json()
        resp = client.patch(
            f"/reservas/{creada['id']}",
            json={"acompanantes": [{"nombre": "Luis", "correo": "luis@example.com"}]},
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 200
        assert [a["correo"] for a in resp.json()["acompanantes"]] == ["luis@example.com"]

    def test_patch_sin_acompanantes_conserva(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Ac Cons")
        creada = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada(), [{"nombre": "Ana", "correo": "ana@example.com"}]),
            headers=cookies_para(usuario),
        ).json()
        resp = client.patch(f"/reservas/{creada['id']}", json={"asistentes": 3}, headers=cookies_para(usuario))
        assert resp.status_code == 200
        assert len(resp.json()["acompanantes"]) == 1

    def test_patch_con_lista_vacia_la_vacia(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Ac Vacia")
        creada = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada(), [{"nombre": "Ana", "correo": "ana@example.com"}]),
            headers=cookies_para(usuario),
        ).json()
        resp = client.patch(f"/reservas/{creada['id']}", json={"acompanantes": []}, headers=cookies_para(usuario))
        assert resp.status_code == 200
        assert resp.json()["acompanantes"] == []

    def test_correo_formato_invalido_da_422(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Ac Inv")
        resp = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada(), [{"nombre": "Ana", "correo": "nope"}]),
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 422

    def test_extra_forbid_rechaza_campo_desconocido(self, client, db):
        usuario, _, recurso = _setup(db, nombre_espacio="Sala Ac Extra")
        resp = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada(), [{"nombre": "Ana", "correo": "ana@example.com", "cedula": "123"}]),
            headers=cookies_para(usuario),
        )
        assert resp.status_code == 422

    def test_get_devuelve_lista_poblada(self, client, db):
        import time as _time

        usuario, _, recurso = _setup(db, nombre_espacio="Sala Ac Get")
        creada = client.post(
            "/reservas",
            json=self._payload(recurso.id, fecha_habilitada(), [{"nombre": "Ana", "correo": "ana@example.com"}]),
            headers=cookies_para(usuario),
        ).json()
        # mis-reservas
        resp = client.get("/reservas/mis-reservas", headers=cookies_para(usuario))
        assert any(r["id"] == creada["id"] and len(r["acompanantes"]) == 1 for r in resp.json())
        # gestion (admin)
        admin = crear_usuario(db, username="admin_ac_get", email="admin_ac_get@example.com", rol="admin")
        resp2 = client.get("/reservas", headers=cookies_para(admin))
        assert any(r["id"] == creada["id"] for r in resp2.json())


class TestNotificacionAlAgregarRecursos:
    """Feature B (equipos adicionales durante una reserva ya aprobada): un
    gestor/admin que agrega recurso_ids/espacio_ids a una reserva aprobada
    notifica al dueño (Notificacion tipo 'Actualizada' + correo en el
    outbox). Ver services/reservas.py::actualizar_reserva."""

    def test_gestor_agrega_recurso_a_reserva_aprobada_notifica_al_dueno(self, client, db):
        from app.models import CorreoSaliente, Notificacion

        usuario, laboratorio, recurso = _setup(db, nombre_espacio="Sala Notif Add")
        gestor = crear_usuario(
            db, username="gestor_notif_add", email="gestor_notif_add@example.com",
            rol="gestor", laboratorio_id=laboratorio.id,
        )
        recurso2 = crear_recurso(db, laboratorio=laboratorio, usuario=gestor, nombre="Recurso extra")
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "aprobada"},
            headers=cookies_para(gestor),
        )

        respuesta = client.patch(
            f"/reservas/{creada['id']}",
            json={"recurso_ids": [recurso.id, recurso2.id]},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["estado"] == "aprobada"
        assert set(respuesta.json()["recurso_ids"]) == {recurso.id, recurso2.id}

        notificaciones = (
            db.query(Notificacion)
            .filter(Notificacion.usuario_id == usuario.id, Notificacion.tipo == "Actualizada")
            .all()
        )
        assert len(notificaciones) == 1
        assert notificaciones[0].reserva_id == creada["id"]

        # La aprobación previa ya encoló un correo al dueño -- filtramos por
        # asunto para aislar el que corresponde a este PATCH.
        correos = (
            db.query(CorreoSaliente)
            .filter(CorreoSaliente.destinatario == usuario.email)
            .filter(CorreoSaliente.asunto.ilike("%actualizada%"))
            .all()
        )
        assert len(correos) == 1
        assert correos[0].es_html is True
        assert "<!DOCTYPE html>" in correos[0].cuerpo

    def test_no_notifica_si_no_se_agrega_nada_nuevo(self, client, db):
        from app.models import Notificacion

        usuario, laboratorio, recurso = _setup(db, nombre_espacio="Sala Notif NoOp")
        gestor = crear_usuario(
            db, username="gestor_notif_noop", email="gestor_notif_noop@example.com",
            rol="gestor", laboratorio_id=laboratorio.id,
        )
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "aprobada"},
            headers=cookies_para(gestor),
        )

        respuesta = client.patch(
            f"/reservas/{creada['id']}",
            json={"asistentes": 3},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 200

        notificaciones = (
            db.query(Notificacion)
            .filter(Notificacion.usuario_id == usuario.id, Notificacion.tipo == "Actualizada")
            .all()
        )
        assert notificaciones == []

    def test_gestor_editando_su_propia_reserva_no_se_autonotifica(self, client, db):
        from app.models import Notificacion

        laboratorio = crear_laboratorio(db, nombre="Sala Notif Self")
        gestor = crear_usuario(
            db, username="gestor_notif_self", email="gestor_notif_self@example.com",
            rol="gestor", laboratorio_id=laboratorio.id,
        )
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=gestor)
        recurso2 = crear_recurso(db, laboratorio=laboratorio, usuario=gestor, nombre="Recurso extra self")
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(gestor),
        ).json()
        assert creada["estado"] == "aprobada"

        respuesta = client.patch(
            f"/reservas/{creada['id']}",
            json={"recurso_ids": [recurso.id, recurso2.id]},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 200

        notificaciones = (
            db.query(Notificacion)
            .filter(Notificacion.usuario_id == gestor.id, Notificacion.tipo == "Actualizada")
            .all()
        )
        assert notificaciones == []
