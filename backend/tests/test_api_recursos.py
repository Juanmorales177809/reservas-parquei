# -*- coding: utf-8 -*-
"""Pruebas de integración de recursos (api/recursos.py).

Reglas cubiertas (Fase 12B):
- RN-009: los recursos marcados como PS (prestación de servicios) no son
  visibles para el rol `usuario` (mapeo Word: investigador) en ningún
  listado público -- gate de CATÁLOGO, sin relación con la reserva en sí
  (el gate que antes bloqueaba reservarlos se quitó, ver
  test_api_reservas.py::TestRecursosPS y backend/CLAUDE.md).
- Los roles `gestor` (laboratorista) y `admin` (administrador técnico) sí
  ven y gestionan recursos PS con normalidad.
- Un recurso ya existente sin el campo PS explícito conserva su
  comportamiento (compatibilidad hacia atrás: `es_prestacion_servicio`
  nace en `false`).
"""

from tests.conftest import (
    asociar_espacio_recurso,
    crear_laboratorio,
    crear_recurso,
    crear_usuario,
    crear_espacio,
    fecha_habilitada,
    cookies_para,
    payload_reserva_objetivos,
)


def _escenario(db):
    laboratorio = crear_laboratorio(db, nombre="Sala PS")
    admin = crear_usuario(db, username="admin_ps", email="admin_ps@example.com", rol="admin")
    gestor = crear_usuario(
        db, username="gestor_ps", email="gestor_ps@example.com", rol="gestor", laboratorio_id=laboratorio.id
    )
    usuario = crear_usuario(db, username="user_ps", email="user_ps@example.com")
    recurso_normal = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Microscopio")
    recurso_ps = crear_recurso(
        db, laboratorio=laboratorio, usuario=admin, nombre="Equipo de ensayo", es_prestacion_servicio=True
    )
    return laboratorio, admin, gestor, usuario, recurso_normal, recurso_ps


class TestVisibilidadPS:
    def test_recurso_ps_no_visible_para_anonimo(self, client, db):
        _, _, _, _, _, recurso_ps = _escenario(db)
        nombres = [r["nombre"] for r in client.get("/recursos").json()]
        assert "Equipo de ensayo" not in nombres

    def test_recurso_ps_no_visible_para_usuario(self, client, db):
        _, _, _, usuario, _, _ = _escenario(db)
        nombres = [
            r["nombre"] for r in client.get("/recursos", headers=cookies_para(usuario)).json()
        ]
        assert "Equipo de ensayo" not in nombres

    def test_recurso_normal_si_visible_para_usuario(self, client, db):
        _, _, _, usuario, _, _ = _escenario(db)
        nombres = [
            r["nombre"] for r in client.get("/recursos", headers=cookies_para(usuario)).json()
        ]
        assert "Microscopio" in nombres

    def test_recurso_ps_visible_para_gestor(self, client, db):
        _, _, gestor, _, _, _ = _escenario(db)
        nombres = [
            r["nombre"] for r in client.get("/recursos", headers=cookies_para(gestor)).json()
        ]
        assert "Equipo de ensayo" in nombres

    def test_recurso_ps_visible_para_admin(self, client, db):
        _, admin, _, _, _, _ = _escenario(db)
        nombres = [
            r["nombre"] for r in client.get("/recursos", headers=cookies_para(admin)).json()
        ]
        assert "Equipo de ensayo" in nombres

    def test_recurso_ps_visible_en_gestion_para_gestor(self, client, db):
        _, _, gestor, _, _, _ = _escenario(db)
        nombres = [
            r["nombre"]
            for r in client.get("/recursos/gestion", headers=cookies_para(gestor)).json()
        ]
        assert "Equipo de ensayo" in nombres

    def test_disponibilidad_ps_403_para_usuario(self, client, db):
        from tests.conftest import fecha_habilitada

        _, _, _, usuario, _, recurso_ps = _escenario(db)
        respuesta = client.get(
            f"/recursos/{recurso_ps.id}/disponibilidad",
            params={"fecha": fecha_habilitada().isoformat()},
            headers=cookies_para(usuario),
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
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 200

    def test_disponibilidad_normal_200_para_usuario_sin_cambios(self, client, db):
        from tests.conftest import fecha_habilitada

        _, _, _, usuario, recurso_normal, _ = _escenario(db)
        respuesta = client.get(
            f"/recursos/{recurso_normal.id}/disponibilidad",
            params={"fecha": fecha_habilitada().isoformat()},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 200


class TestGestionPS:
    def test_gestor_crea_recurso_ps(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Crear PS")
        gestor = crear_usuario(
            db, username="gestor_crea_ps", email="gestor_crea_ps@example.com",
            rol="gestor", laboratorio_id=laboratorio.id,
        )
        tipo_id = client.get("/recursos/tipos").json()
        # Asegura que exista al menos un tipo (creado por otro recurso previo si aplica)
        if not tipo_id:
            crear_recurso(db, laboratorio=laboratorio, usuario=gestor)
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
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["es_prestacion_servicio"] is True

    def test_usuario_no_puede_crear_recursos(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Crear PS 2")
        usuario = crear_usuario(db, username="user_crea_ps", email="user_crea_ps@example.com")
        respuesta = client.post(
            "/recursos",
            json={
                "nombre": "Equipo Intento",
                "tipo_recurso_id": 1,
                "capacidad": 1,
                "estado": "activo",
                "laboratorio_id": laboratorio.id,
                "es_prestacion_servicio": True,
            },
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 403

    def test_recurso_sin_campo_ps_explicito_nace_false(self, client, db):
        """Compatibilidad: si el payload no incluye es_prestacion_servicio,
        el recurso nace visible/reservable como antes de esta fase."""
        laboratorio = crear_laboratorio(db, nombre="Sala Default PS")
        admin = crear_usuario(db, username="admin_default_ps", email="admin_default_ps@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso Legado")
        respuesta = client.get(f"/recursos", params={"laboratorio_id": laboratorio.id})
        cuerpo = [r for r in respuesta.json() if r["nombre"] == "Recurso Legado"]
        assert len(cuerpo) == 1
        assert cuerpo[0]["es_prestacion_servicio"] is False


class TestGuardConReservaDeEspacio:
    """Fase 12C-6: los guards de mover/eliminar recurso consultan
    `reserva_recursos`, no solo la columna histórica `Reserva.recurso_id`.
    Un recurso reclamado por una reserva de espacio (fila de asociación sin ser
    el `recurso_id` ancla) debe bloquear el movimiento y la eliminación."""

    def _escenario_reserva_espacio(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Guard Espacio")
        admin = crear_usuario(db, username="admin_guard_espacio", email="admin_guard_espacio@example.com", rol="admin")
        r_ancla = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Ancla Guard")
        r_secundario = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Secundario Guard")
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Guard")
        asociar_espacio_recurso(db, espacio, r_ancla)
        asociar_espacio_recurso(db, espacio, r_secundario)
        creada = client.post(
            "/reservas",
            json=payload_reserva_objetivos(espacio_ids=[espacio.id], fecha=fecha_habilitada()),
            headers=cookies_para(admin),
        )
        assert creada.status_code == 201
        return laboratorio, admin, r_ancla, r_secundario

    def test_eliminar_recurso_no_ancla_reservado_por_espacio_da_409(self, client, db):
        _, admin, _, r_secundario = self._escenario_reserva_espacio(client, db)
        respuesta = client.delete(
            f"/recursos/{r_secundario.id}", headers=cookies_para(admin)
        )
        assert respuesta.status_code == 409

    def test_mover_recurso_no_ancla_reservado_por_espacio_da_409(self, client, db):
        laboratorio, admin, _, r_secundario = self._escenario_reserva_espacio(client, db)
        otro_espacio = crear_laboratorio(db, nombre="Otro Laboratorio Guard")
        respuesta = client.put(
            f"/recursos/{r_secundario.id}",
            json={"laboratorio_id": otro_espacio.id},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 409

    def test_eliminar_recurso_ancla_reservado_sigue_bloqueado(self, client, db):
        _, admin, r_ancla, _ = self._escenario_reserva_espacio(client, db)
        respuesta = client.delete(
            f"/recursos/{r_ancla.id}", headers=cookies_para(admin)
        )
        assert respuesta.status_code == 409


class TestGuardSoloReservaRecursos:
    """Fase 12C-4e-lectores: `_recurso_tiene_reservas` deja de consultar la
    columna histórica `Reserva.recurso_id` como fallback -- solo consulta
    `reserva_recursos`. Caso límite real: el recurso "ancla" de una reserva
    de espacio SIN recursos asociados (ver
    test_reservas_espacios.py::test_espacio_sin_recursos_ancla_al_recurso_de_menor_id)
    no tiene ninguna fila en `reserva_recursos` para esa reserva -- el guard
    de aplicación ya no lo detecta. Pero `reservas.recurso_id` sigue siendo
    NOT NULL con FK real (`fk_reservas_recurso`, sin retirar en esta
    subfase): intentar eliminarlo igual falla, ahora vía la constraint de
    base de datos en vez del guard explícito -- por eso sigue dando 409,
    traducido explícitamente en vez de dejarlo escapar como 500."""

    def test_recurso_ancla_de_espacio_sin_recursos_sigue_bloqueado_por_fk(self, client, db):
        laboratorio = crear_laboratorio(db, nombre="Sala Ancla Sin Recursos")
        admin = crear_usuario(
            db, username="admin_ancla_libre", email="admin_ancla_libre@example.com", rol="admin"
        )
        r_ancla = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso Menor Id Libre")
        espacio = crear_espacio(db, laboratorio=laboratorio, usuario=admin, nombre="Espacio Sin Recursos Libre")
        # La espacio NO tiene ningun recurso asociado.
        creada = client.post(
            "/reservas",
            json=payload_reserva_objetivos(espacio_ids=[espacio.id], fecha=fecha_habilitada()),
            headers=cookies_para(admin),
        )
        assert creada.status_code == 201
        # Fase 12C-4e-schemas: `recurso_id` ya no está en la respuesta; el
        # ancla se confirma contra la columna histórica directamente.
        from app.models.reserva import Reserva

        reserva = db.query(Reserva).filter(Reserva.id == creada.json()["id"]).one()
        assert reserva.recurso_id == r_ancla.id  # confirma el ancla

        respuesta = client.delete(f"/recursos/{r_ancla.id}", headers=cookies_para(admin))
        assert respuesta.status_code == 409
