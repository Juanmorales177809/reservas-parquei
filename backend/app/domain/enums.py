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
    distinto de `tipo` (RN-012, Fase 12D), el tipo de reserva académica de
    `Reserva`, que es un concepto distinto aunque el documento fuente usa
    nombres parecidos para ambos (`tipo_reserva` en el legado).
    """

    EQUIPOS = "equipos"
    ZONAS = "zonas"
    MIXTO = "mixto"


class TipoReserva(str, Enum):
    """Tipo de reserva académica de `Reserva` (RN-012/RN-015, Fase 12D).

    Nombre del campo en `Reserva`: `tipo` — el mismo nombre que ya citaba
    el código y la documentación como punto de extensión pendiente antes de
    existir (services/reservas.py::validar_acceso_ps, models/README.md).
    Tres valores exactos del roadmap aprobado, sin catálogo "otro":
    TRABAJO_INVESTIGACION (investigación), TRABAJO_GRADO (grado,
    proyectos de grado) y SERVICIO_DE_ENSAYO (ensayo, prestación de
    servicios). `servicio_de_ensayo` es el valor que el gate PS de la
    Fase 12D exige para reservar un recurso marcado como PS.
    """

    TRABAJO_INVESTIGACION = "trabajo_investigacion"
    TRABAJO_GRADO = "trabajo_grado"
    SERVICIO_DE_ENSAYO = "servicio_de_ensayo"


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
