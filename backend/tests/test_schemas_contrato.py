# -*- coding: utf-8 -*-
"""Pruebas de contrato de los schemas Pydantic tras alinearlos con el dominio.

Fase 2. Estrategia TDD: los tests de tipo-enum (`isinstance`) deben FALLAR
antes del refactor (los campos hoy son `str`) y pasar después, mientras los
tests de contrato JSON deben pasar SIEMPRE (antes y después).
"""

import pytest
from pydantic import ValidationError

from app.domain.enums import EstadoEntidad, EstadoReserva, EstadoSlot, Rol, TipoNotificacion
from app.schemas.disponibilidad import DisponibilidadSlot
from app.schemas.espacio import ConfiguracionEspacioUpdate, EspacioCreate, EspacioResponse
from app.schemas.notificacion import NotificacionResponse
from app.schemas.recurso import RecursoCreate
from app.schemas.reserva import (
    ReservaCreate,
    ReservaEstadoUpdate,
    ReservaResponse,
    ReservaUpdate,
    ZonaReservaResponse,
)
from app.schemas.usuario import AdminUsuarioCreate, UsuarioResponse, UsuarioUpdate


def _validacion_exc(modelo, **datos):
    with pytest.raises(ValidationError):
        modelo(**datos)


class TestCamposTipadosConEnums:
    def test_admin_usuario_create_rol_es_enum(self):
        modelo = AdminUsuarioCreate(
            username="usuario1", email="usuario1@example.com", password="secret123"
        )
        assert isinstance(modelo.rol, Rol)
        assert modelo.rol == Rol.USUARIO

    def test_usuario_update_rol_es_enum(self):
        modelo = UsuarioUpdate(rol="gestor")
        assert isinstance(modelo.rol, Rol)

    def test_usuario_response_rol_es_enum(self):
        modelo = UsuarioResponse.model_validate(
            {"id": 1, "username": "u", "email": "u@example.com", "rol": "admin"}
        )
        assert isinstance(modelo.rol, Rol)

    def test_espacio_create_estado_es_enum(self):
        modelo = EspacioCreate(nombre="Sala", capacidad=10, correo="sala@example.com")
        assert isinstance(modelo.estado, EstadoEntidad)
        assert modelo.estado == EstadoEntidad.ACTIVO

    def test_espacio_response_estado_es_enum(self):
        modelo = EspacioResponse.model_validate(
            {
                "id": 1,
                "nombre": "Sala",
                "ubicacion": "X",
                "capacidad": 10,
                "estado": "inactivo",
                "dias_atencion": [0],
                "hora_apertura": "07:00:00",
                "hora_cierre": "20:00:00",
                "horario_atencion": {"0": [7, 8]},
                "horas_antelacion": 24,
                "modalidad_reserva": "equipos",
                "correo": None,
            }
        )
        assert isinstance(modelo.estado, EstadoEntidad)

    def test_recurso_create_estado_es_enum(self):
        modelo = RecursoCreate(
            nombre="Recurso", tipo_recurso_id=1, capacidad=5, espacio_id=1
        )
        assert isinstance(modelo.estado, EstadoEntidad)

    def test_reserva_estado_update_es_enum(self):
        modelo = ReservaEstadoUpdate(nuevo_estado="aprobada")
        assert isinstance(modelo.nuevo_estado, EstadoReserva)
        assert modelo.nuevo_estado == EstadoReserva.APROBADA

    def test_reserva_response_estado_es_enum(self):
        datos = {
            "id": 1,
            "usuario_id": 1,
            "espacio_id": 1,
            "recurso_id": 1,
            "fecha": "2026-08-17",
            "hora_inicio": "08:00:00",
            "hora_fin": "10:00:00",
            "estado": "esperando",
            "asistentes": 2,
            "created_at": "2026-08-13T10:00:00",
            "updated_at": "2026-08-13T10:00:00",
            "usuario": {"id": 1, "username": "u", "email": "u@example.com", "rol": "usuario"},
            "espacio": {"id": 1, "nombre": "S", "capacidad": 10, "estado": "activo"},
            "recurso": {
                "id": 1,
                "nombre": "R",
                "capacidad": 10,
                "estado": "activo",
                "espacio": {"id": 1, "nombre": "S", "capacidad": 10, "estado": "activo"},
            },
        }
        modelo = ReservaResponse.model_validate(datos)
        assert isinstance(modelo.estado, EstadoReserva)

    def test_notificacion_tipo_es_enum(self):
        modelo = NotificacionResponse(
            id=1,
            usuario_id=1,
            reserva_id=1,
            tipo="Pendiente",
            leida=False,
            created_at="2026-08-13T10:00:00",
            mensaje="Nueva reserva",
        )
        assert isinstance(modelo.tipo, TipoNotificacion)

    def test_disponibilidad_estado_es_enum(self):
        modelo = DisponibilidadSlot(hora_inicio="08:00", hora_fin="09:00", estado="libre")
        assert isinstance(modelo.estado, EstadoSlot)


class TestContratoJsonConservado:
    def test_rol_serializa_como_string_actual(self):
        modelo = UsuarioResponse.model_validate(
            {"id": 1, "username": "u", "email": "u@example.com", "rol": "gestor"}
        )
        assert modelo.model_dump()["rol"] == "gestor"
        assert modelo.model_dump_json() == (
            '{"id":1,"username":"u","email":"u@example.com","rol":"gestor","espacio":null}'
        )

    def test_estados_serializan_como_strings_actuales(self):
        assert (
            EspacioCreate(nombre="S", capacidad=1, correo="s@example.com").model_dump()["estado"]
            == "activo"
        )
        reserva = ReservaResponse.model_validate(
            {
                "id": 1,
                "usuario_id": 1,
                "espacio_id": 1,
                "recurso_id": 1,
                "fecha": "2026-08-17",
                "hora_inicio": "08:00:00",
                "hora_fin": "10:00:00",
                "estado": "aprobada",
                "asistentes": 2,
                "created_at": "2026-08-13T10:00:00",
                "updated_at": "2026-08-13T10:00:00",
                "usuario": {"id": 1, "username": "u", "email": "u@example.com", "rol": "usuario"},
                "espacio": {"id": 1, "nombre": "S", "capacidad": 10, "estado": "activo"},
                "recurso": {
                    "id": 1,
                    "nombre": "R",
                    "capacidad": 10,
                    "estado": "activo",
                    "espacio": {"id": 1, "nombre": "S", "capacidad": 10, "estado": "activo"},
                },
            }
        )
        assert reserva.model_dump()["estado"] == "aprobada"
        assert DisponibilidadSlot(hora_inicio="08:00", hora_fin="09:00", estado="ocupado").model_dump()["estado"] == "ocupado"
        assert NotificacionResponse(
            id=1, usuario_id=1, reserva_id=1, tipo="Rechazada", leida=False,
            created_at="2026-08-13T10:00:00", mensaje="m",
        ).model_dump()["tipo"] == "Rechazada"


class TestValoresRechazados:
    def test_rol_invalido_rechazado(self):
        _validacion_exc(
            AdminUsuarioCreate, username="u1", email="u1@example.com", password="secret123", rol="superadmin"
        )
        _validacion_exc(UsuarioUpdate, rol="superadmin")

    def test_estado_invalido_rechazado(self):
        _validacion_exc(EspacioCreate, nombre="S", capacidad=1, estado="roto")
        _validacion_exc(RecursoCreate, nombre="R", tipo_recurso_id=1, capacidad=1, estado="roto")

    def test_nuevo_estado_esperando_rechazado(self):
        _validacion_exc(ReservaEstadoUpdate, nuevo_estado="esperando")

    def test_nuevo_estado_valido(self):
        for valor in ("aprobada", "rechazada", "cancelada"):
            modelo = ReservaEstadoUpdate(nuevo_estado=valor)
            assert modelo.nuevo_estado.value == valor


class TestContratoReservasPorObjetivos:
    """Fase 12C-6: `ReservaCreate`/`ReservaUpdate` usan `recurso_ids`/
    `zona_ids`; `recurso_id` legacy se rechaza (`extra="forbid")."""

    def test_zona_reserva_response_acepta_estado_como_enum(self):
        modelo = ZonaReservaResponse.model_validate(
            {
                "id": 1,
                "nombre": "Z",
                "espacio_id": 1,
                "descripcion": None,
                "capacidad": 5,
                "estado": "activo",
            }
        )
        assert isinstance(modelo.estado, EstadoEntidad)
        assert modelo.capacidad == 5

    def test_reserva_create_acepta_listas_y_exige_al_menos_una(self):
        modelo = ReservaCreate(
            recurso_ids=[1],
            zona_ids=[],
            fecha="2026-08-17",
            hora_inicio="08:00",
            hora_fin="09:00",
            asistentes=2,
        )
        assert modelo.recurso_ids == [1]
        assert modelo.zona_ids == []
        _validacion_exc(
            ReservaCreate,
            recurso_ids=[],
            zona_ids=[],
            fecha="2026-08-17",
            hora_inicio="08:00",
            hora_fin="09:00",
            asistentes=2,
        )

    def test_reserva_create_rechaza_recurso_id_legacy(self):
        _validacion_exc(
            ReservaCreate,
            recurso_id=1,
            fecha="2026-08-17",
            hora_inicio="08:00",
            hora_fin="09:00",
            asistentes=2,
        )

    def test_reserva_update_rechaza_recurso_id_legacy(self):
        _validacion_exc(ReservaUpdate, recurso_id=1)

    def test_reserva_response_acepta_listas_y_zonas(self):
        datos = _datos_reserva_response()
        datos["recurso_ids"] = [1]
        datos["zona_ids"] = [5]
        datos["zonas"] = [
            {"id": 5, "nombre": "Z", "espacio_id": 1, "descripcion": None, "capacidad": 5, "estado": "activo"}
        ]
        modelo = ReservaResponse.model_validate(datos)
        assert modelo.recurso_ids == [1]
        assert modelo.zona_ids == [5]
        assert modelo.zonas[0].nombre == "Z"

    def test_reserva_response_sin_campos_nuevos_usa_defaults(self):
        modelo = ReservaResponse.model_validate(_datos_reserva_response())
        assert modelo.recurso_ids == []
        assert modelo.zona_ids == []
        assert modelo.zonas == []


def _datos_reserva_response():
    return {
        "id": 1,
        "usuario_id": 1,
        "espacio_id": 1,
        "recurso_id": 1,
        "fecha": "2026-08-17",
        "hora_inicio": "08:00:00",
        "hora_fin": "10:00:00",
        "estado": "aprobada",
        "asistentes": 2,
        "created_at": "2026-08-13T10:00:00",
        "updated_at": "2026-08-13T10:00:00",
        "usuario": {"id": 1, "username": "u", "email": "u@example.com", "rol": "usuario"},
        "espacio": {"id": 1, "nombre": "S", "capacidad": 10, "estado": "activo"},
        "recurso": {
            "id": 1,
            "nombre": "R",
            "capacidad": 10,
            "estado": "activo",
            "espacio": {"id": 1, "nombre": "S", "capacidad": 10, "estado": "activo"},
        },
    }


class TestValidacionHorarioConservada:
    def test_normalizacion_orden_y_dedupe(self):
        modelo = ConfiguracionEspacioUpdate(
            horario_atencion={1: [9, 8, 8, 7]}, horas_antelacion=24, aprobacion_automatica=False
        )
        assert modelo.horario_atencion == {1: [7, 8, 9]}

    def test_mensaje_dia_fuera_de_rango(self):
        with pytest.raises(ValidationError) as exc:
            ConfiguracionEspacioUpdate(
                horario_atencion={7: [8]}, horas_antelacion=24, aprobacion_automatica=False
            )
        assert "Los días de atención deben estar entre 0 y 6" in str(exc.value)

    def test_mensaje_hora_fuera_de_rango(self):
        with pytest.raises(ValidationError) as exc:
            ConfiguracionEspacioUpdate(
                horario_atencion={1: [23]}, horas_antelacion=24, aprobacion_automatica=False
            )
        assert "Las horas deben estar entre 0 y 22" in str(exc.value)

    def test_mensaje_sin_franjas(self):
        with pytest.raises(ValidationError) as exc:
            ConfiguracionEspacioUpdate(
                horario_atencion={1: [], 2: []}, horas_antelacion=24, aprobacion_automatica=False
            )
        assert "Debes seleccionar al menos una franja de atención" in str(exc.value)

    def test_dias_vacios_conservados_por_compatibilidad(self):
        # Opción A (compatibilidad de contrato): el schema conserva las claves
        # de días vacíos con listas []; HorarioAtencion elimina los días vacíos
        # solo en su normalización interna y NO reemplaza la salida pública.
        modelo = ConfiguracionEspacioUpdate(
            horario_atencion={1: [], 2: [9]}, horas_antelacion=24, aprobacion_automatica=False
        )
        assert modelo.horario_atencion == {1: [], 2: [9]}
        from app.domain.valor import HorarioAtencion

        dominio = HorarioAtencion(modelo.horario_atencion)
        assert dominio.dias == (2,)  # el dominio sí elimina el día vacío internamente
