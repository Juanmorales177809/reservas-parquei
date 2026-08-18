# -*- coding: utf-8 -*-
"""Enums y constantes de la capa de dominio.

Fase 1: esta capa es estrictamente aditiva; ningún módulo de la aplicación
la consume todavía. Fase 2 alineará los schemas y Fase 3 los services y
models.

Los valores de los enums conservan EXACTAMENTE las cadenas JSON que ya
viajan por la API (esperando/aprobada/rechazada/cancelada, activo/inactivo/
mantenimiento, libre/ocupado, Pendiente/Aprobada/Rechazada/Cancelada,
usuario/gestor/admin) para no cambiar ningún contrato.
"""

from __future__ import annotations

from enum import Enum


class Rol(str, Enum):
    """Rol funcional de un usuario. Espejo del patrón
    `^(admin|gestor|usuario)$` de `app/schemas/usuario.py`."""

    USUARIO = "usuario"
    GESTOR = "gestor"
    ADMIN = "admin"


class ModalidadEspacio(str, Enum):
    """Modalidad de reserva configurada por espacio (RN-006, Fase 12B).

    Nombre del campo en `Espacio`: `modalidad_reserva` — deliberadamente
    distinto de `tipo_reserva` para no colisionar con el futuro campo de
    tipo de reserva académica de `Reserva` (RN-012, Fase 12D), que es un
    concepto distinto aunque el documento fuente usa nombres parecidos
    para ambos.
    """

    EQUIPOS = "equipos"
    ZONAS = "zonas"
    MIXTO = "mixto"


class EstadoEntidad(str, Enum):
    """Estado de entidades gestionables (espacios y recursos)."""

    ACTIVO = "activo"
    INACTIVO = "inactivo"
    MANTENIMIENTO = "mantenimiento"


class EstadoReserva(str, Enum):
    """Estados del ciclo de vida de una reserva."""

    ESPERANDO = "esperando"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    CANCELADA = "cancelada"

    def transiciones(self) -> frozenset[EstadoReserva]:
        """Estados a los que se puede transicionar desde el estado actual."""
        return TRANSICIONES_ESTADO_RESERVA[self]

    def puede_transicionar_a(self, nuevo: EstadoReserva) -> bool:
        """True si la transición es válida. El mismo estado se considera un
        no-op válido (semántica actual de `validar_transicion_estado` en
        `app/services/reservas.py`)."""
        return nuevo == self or nuevo in TRANSICIONES_ESTADO_RESERVA[self]

    @property
    def es_terminal(self) -> bool:
        """Los estados terminales no admiten ninguna transición posterior."""
        return not TRANSICIONES_ESTADO_RESERVA[self]


class TipoNotificacion(str, Enum):
    """Tipos de notificación internos.

    Origen verificado de los valores: el constraint `notificaciones_tipo_check`
    existe en base de datos — declarado en `app/models/notificacion.py`
    (`__table_args__`) y aplicado por `app/migrations.py` (DROP IF EXISTS +
    ADD CHECK `tipo IN ('Pendiente', 'Aprobada', 'Rechazada', 'Cancelada')`).
    Se conservan exactamente esos valores.
    """

    PENDIENTE = "Pendiente"
    APROBADA = "Aprobada"
    RECHAZADA = "Rechazada"
    CANCELADA = "Cancelada"


class EstadoSlot(str, Enum):
    """Estado de una franja horaria en la respuesta de disponibilidad."""

    LIBRE = "libre"
    OCUPADO = "ocupado"
    MANTENIMIENTO = "mantenimiento"


class DiaSemana(int, Enum):
    """Días de la semana alineados con `datetime.date.weekday()` (lunes = 0)."""

    LUNES = 0
    MARTES = 1
    MIERCOLES = 2
    JUEVES = 3
    VIERNES = 4
    SABADO = 5
    DOMINGO = 6


TRANSICIONES_ESTADO_RESERVA: dict[EstadoReserva, frozenset[EstadoReserva]] = {
    EstadoReserva.ESPERANDO: frozenset(
        {EstadoReserva.APROBADA, EstadoReserva.RECHAZADA, EstadoReserva.CANCELADA}
    ),
    EstadoReserva.APROBADA: frozenset({EstadoReserva.CANCELADA}),
    EstadoReserva.RECHAZADA: frozenset(),
    EstadoReserva.CANCELADA: frozenset(),
}

ESTADOS_RESERVA_BLOQUEANTES: frozenset[EstadoReserva] = frozenset(
    {EstadoReserva.ESPERANDO, EstadoReserva.APROBADA}
)
