from datetime import time

from app.models import Espacio


def horas_atencion_dia(espacio: Espacio, dia_semana: int) -> list[int]:
    horario = espacio.horario_atencion or {}
    horas = horario.get(str(dia_semana), horario.get(dia_semana, []))
    return sorted({int(hora) for hora in horas})


def horario_cubre_reserva(
    espacio: Espacio,
    dia_semana: int,
    hora_inicio: time,
    hora_fin: time,
) -> bool:
    if hora_inicio.minute != 0 or hora_inicio.second != 0:
        return False
    if hora_fin.minute != 0 or hora_fin.second != 0:
        return False
    if hora_inicio >= hora_fin:
        return False

    horas_habilitadas = set(horas_atencion_dia(espacio, dia_semana))
    return all(hora in horas_habilitadas for hora in range(hora_inicio.hour, hora_fin.hour))
