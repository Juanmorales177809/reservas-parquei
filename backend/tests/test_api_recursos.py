# -*- coding: utf-8 -*-
"""Pruebas de integración de recursos (api/recursos.py).

Reglas cubiertas (Fase 12B):
- RN-009: los recursos marcados como PS (prestación de servicios) no son
  visibles para el rol `usuario` (mapeo Word: investigador) en ningún
  listado público, y un intento de reservarlos responde 403 (ver
  test_api_reservas.py::TestRecursosPS para la parte de creación de
  reserva).
- Los roles `gestor` (laboratorista) y `admin` (administrador técnico) sí
  ven y gestionan recursos PS con normalidad.
- Un recurso ya existente sin el campo PS explícito conserva su
  comportamiento (compatibilidad hacia atrás: `es_prestacion_servicio`
  nace en `false`).
"""

from tests.conftest import (
    asociar_zona_recurso,
    crear_espacio,
    crear_recurso,
    crear_usuario,
    crear_zona,
    fecha_habilitada,
    headers_para,
    payload_reserva_objetivos,
)


def _escenario(db):
    espacio = crear_espacio(db, nombre="Sala PS")
    admin = crear_usuario(db, username="admin_ps", email="admin_ps@test.com", rol="admin")
    gestor = crear_usuario(
        db, username="gestor_ps", email="gestor_ps@test.com", rol="gestor", espacio_id=espacio.id
    )
    usuario = crear_usuario(db, username="user_ps", email="user_ps@test.com")
    recurso_normal = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Microscopio")
    recurso_ps = crear_recurso(
        db, espacio=espacio, usuario=admin, nombre="Equipo de ensayo", es_prestacion_servicio=True
    )
    return espacio, admin, gestor, usuario, recurso_normal, recurso_ps


class TestVisibilidadPS:
    def test_recurso_ps_no_visible_para_anonimo(self, client, db):
        _, _, _, _, _, recurso_ps = _escenario(db)
        nombres = [r["nombre"] for r in client.get("/recursos").json()]
        assert "Equipo de ensayo" not in nombres

    def test_recurso_ps_no_visible_para_usuario(self, client, db):
        _, _, _, usuario, _, _ = _escenario(db)
        nombres = [
            r["nombre"] for r in client.get("/recursos", headers=headers_para(usuario)).json()
        ]
        assert "Equipo de ensayo" not in nombres

    def test_recurso_normal_si_visible_para_usuario(self, client, db):
        _, _, _, usuario, _, _ = _escenario(db)
        nombres = [
            r["nombre"] for r in client.get("/recursos", headers=headers_para(usuario)).json()
        ]
        assert "Microscopio" in nombres

    def test_recurso_ps_visible_para_gestor(self, client, db):
        _, _, gestor, _, _, _ = _escenario(db)
        nombres = [
            r["nombre"] for r in client.get("/recursos", headers=headers_para(gestor)).json()
        ]
        assert "Equipo de ensayo" in nombres

    def test_recurso_ps_visible_para_admin(self, client, db):
        _, admin, _, _, _, _ = _escenario(db)
        nombres = [
            r["nombre"] for r in client.get("/recursos", headers=headers_para(admin)).json()
        ]
        assert "Equipo de ensayo" in nombres

    def test_recurso_ps_visible_en_gestion_para_gestor(self, client, db):
        _, _, gestor, _, _, _ = _escenario(db)
        nombres = [
            r["nombre"]
            for r in client.get("/recursos/gestion", headers=headers_para(gestor)).json()
        ]
        assert "Equipo de ensayo" in nombres

    def test_disponibilidad_ps_403_para_usuario(self, client, db):
        from tests.conftest import fecha_habilitada

        _, _, _, usuario, _, recurso_ps = _escenario(db)
        respuesta = client.get(
            f"/recursos/{recurso_ps.id}/disponibilidad",
            params={"fecha": fecha_habilitada().isoformat()},
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 403

    def test_disponibilidad_ps_403_para_anonimo(self, client, db):
        from tests.conftest import fecha_habilitada

        _, _, _, _, _, recurso_ps = _escenario(db)
        respuesta = client.get(
            f"/recursos/{recurso_ps.id}/disponibilidad",
            params={"fecha": fecha_habilitada().isoformat()},
        )
        assert respuesta.status_code == 403

    def test_disponibilidad_ps_200_para_gestor(self, client, db):
        from tests.conftest import fecha_habilitada

        _, _, gestor, _, _, recurso_ps = _escenario(db)
        respuesta = client.get(
            f"/recursos/{recurso_ps.id}/disponibilidad",
            params={"fecha": fecha_habilitada().isoformat()},
            headers=headers_para(gestor),
        )
        assert respuesta.status_code == 200

    def test_disponibilidad_normal_200_para_usuario_sin_cambios(self, client, db):
        from tests.conftest import fecha_habilitada

        _, _, _, usuario, recurso_normal, _ = _escenario(db)
        respuesta = client.get(
            f"/recursos/{recurso_normal.id}/disponibilidad",
            params={"fecha": fecha_habilitada().isoformat()},
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 200


class TestGestionPS:
    def test_gestor_crea_recurso_ps(self, client, db):
        espacio = crear_espacio(db, nombre="Sala Crear PS")
        gestor = crear_usuario(
            db, username="gestor_crea_ps", email="gestor_crea_ps@test.com",
            rol="gestor", espacio_id=espacio.id,
        )
        tipo_id = client.get("/recursos/tipos").json()
        # Asegura que exista al menos un tipo (creado por otro recurso previo si aplica)
        if not tipo_id:
            crear_recurso(db, espacio=espacio, usuario=gestor)
            tipo_id = client.get("/recursos/tipos").json()
        respuesta = client.post(
            "/recursos",
            json={
                "nombre": "Equipo Nuevo PS",
                "tipo_recurso_id": tipo_id[0]["id"],
                "capacidad": 1,
                "estado": "activo",
                "es_prestacion_servicio": True,
            },
            headers=headers_para(gestor),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["es_prestacion_servicio"] is True

    def test_usuario_no_puede_crear_recursos(self, client, db):
        espacio = crear_espacio(db, nombre="Sala Crear PS 2")
        usuario = crear_usuario(db, username="user_crea_ps", email="user_crea_ps@test.com")
        respuesta = client.post(
            "/recursos",
            json={
                "nombre": "Equipo Intento",
                "tipo_recurso_id": 1,
                "capacidad": 1,
                "estado": "activo",
                "espacio_id": espacio.id,
                "es_prestacion_servicio": True,
            },
            headers=headers_para(usuario),
        )
        assert respuesta.status_code == 403

    def test_recurso_sin_campo_ps_explicito_nace_false(self, client, db):
        """Compatibilidad: si el payload no incluye es_prestacion_servicio,
        el recurso nace visible/reservable como antes de esta fase."""
        espacio = crear_espacio(db, nombre="Sala Default PS")
        admin = crear_usuario(db, username="admin_default_ps", email="admin_default_ps@test.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso Legado")
        respuesta = client.get(f"/recursos", params={"espacio_id": espacio.id})
        cuerpo = [r for r in respuesta.json() if r["nombre"] == "Recurso Legado"]
        assert len(cuerpo) == 1
        assert cuerpo[0]["es_prestacion_servicio"] is False


class TestGuardConReservaDeZona:
    """Fase 12C-6: los guards de mover/eliminar recurso consultan
    `reserva_recursos`, no solo la columna histórica `Reserva.recurso_id`.
    Un recurso reclamado por una reserva de zona (fila de asociación sin ser
    el `recurso_id` ancla) debe bloquear el movimiento y la eliminación."""

    def _escenario_reserva_zona(self, client, db):
        espacio = crear_espacio(db, nombre="Sala Guard Zona", modalidad_reserva="mixto")
        admin = crear_usuario(db, username="admin_guard_zona", email="admin_guard_zona@test.com", rol="admin")
        r_ancla = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Ancla Guard")
        r_secundario = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Secundario Guard")
        zona = crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona Guard")
        asociar_zona_recurso(db, zona, r_ancla)
        asociar_zona_recurso(db, zona, r_secundario)
        creada = client.post(
            "/reservas",
            json=payload_reserva_objetivos(zona_ids=[zona.id], fecha=fecha_habilitada()),
            headers=headers_para(admin),
        )
        assert creada.status_code == 201
        return espacio, admin, r_ancla, r_secundario

    def test_eliminar_recurso_no_ancla_reservado_por_zona_da_409(self, client, db):
        _, admin, _, r_secundario = self._escenario_reserva_zona(client, db)
        respuesta = client.delete(
            f"/recursos/{r_secundario.id}", headers=headers_para(admin)
        )
        assert respuesta.status_code == 409

    def test_mover_recurso_no_ancla_reservado_por_zona_da_409(self, client, db):
        espacio, admin, _, r_secundario = self._escenario_reserva_zona(client, db)
        otro_espacio = crear_espacio(db, nombre="Otro Espacio Guard", modalidad_reserva="mixto")
        respuesta = client.put(
            f"/recursos/{r_secundario.id}",
            json={"espacio_id": otro_espacio.id},
            headers=headers_para(admin),
        )
        assert respuesta.status_code == 409

    def test_eliminar_recurso_ancla_reservado_sigue_bloqueado(self, client, db):
        _, admin, r_ancla, _ = self._escenario_reserva_zona(client, db)
        respuesta = client.delete(
            f"/recursos/{r_ancla.id}", headers=headers_para(admin)
        )
        assert respuesta.status_code == 409
