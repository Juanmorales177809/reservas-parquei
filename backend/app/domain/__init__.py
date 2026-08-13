# -*- coding: utf-8 -*-
"""Capa de dominio tipada: enums, value objects y protocols.

Sin dependencias de FastAPI, SQLAlchemy, `app.db`, modelos de
infraestructura ni HTTP.
"""

from app.domain.enums import (
    DiaSemana,
    ESTADOS_RESERVA_BLOQUEANTES,
    EstadoEntidad,
    EstadoReserva,
    EstadoSlot,
    Rol,
    TipoNotificacion,
    TRANSICIONES_ESTADO_RESERVA,
)
from app.domain.protocols import RegistroAuditoria, Reloj
from app.domain.valor import HORA_MAXIMA, HORA_MINIMA, FranjaHoraria, HorarioAtencion

__all__ = [
    "DiaSemana",
    "ESTADOS_RESERVA_BLOQUEANTES",
    "EstadoEntidad",
    "EstadoReserva",
    "EstadoSlot",
    "FranjaHoraria",
    "HORA_MAXIMA",
    "HORA_MINIMA",
    "HorarioAtencion",
    "RegistroAuditoria",
    "Reloj",
    "Rol",
    "TipoNotificacion",
    "TRANSICIONES_ESTADO_RESERVA",
]
