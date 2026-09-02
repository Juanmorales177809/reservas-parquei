# -*- coding: utf-8 -*-
"""Reglas de horario de atención, delegadas a los value objects del dominio.

Guard de compatibilidad: un horario totalmente vacío conserva el
comportamiento actual (lista vacía / False) y NO se trata como error; un
horario con horas fuera de rango (0..22) se deja propagar como error de
configuración, sin ocultarlo.
"""

from datetime import time

from app.domain.valor import FranjaHoraria, HorarioAtencion
from app.models import Laboratorio


def horas_atencion_dia(laboratorio: Laboratorio, dia_semana: int) -> list[int]:
    horario_dict = laboratorio.horario_atencion or {}
    if not any(horario_dict.values()):
        return []
    horario = HorarioAtencion(horario_dict)
    return list(horario.horas_del_dia(dia_semana))


def horario_cubre_reserva(
    laboratorio: Laboratorio,
    dia_semana: int,
    hora_inicio: time,
    hora_fin: time,
) -> bool:
    try:
        franja = FranjaHoraria(hora_inicio, hora_fin)
    except ValueError:
        return False
    horario_dict = laboratorio.horario_atencion or {}
    if not any(horario_dict.values()):
        return False
    return HorarioAtencion(horario_dict).cubre_franja(dia_semana, franja)
