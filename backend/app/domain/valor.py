# -*- coding: utf-8 -*-
"""Value objects de la capa de dominio.

`FranjaHoraria` y `HorarioAtencion` encapsulan las invariantes de horario
que hoy viven dispersas en `app/services/horarios.py` y en los validadores
de `app/schemas/espacio.py`. Fase 1 es aditiva: los servicios seguirán con
su lógica actual hasta la Fase 3.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from typing import Mapping, Sequence

HORA_MINIMA = 0
HORA_MAXIMA = 22


@dataclass(frozen=True)
class FranjaHoraria:
    """Intervalo de tiempo compuesto únicamente por bloques de hora completa.

    Invariantes:
    - hora_inicio < hora_fin.
    - minutos y segundos en cero en ambos extremos.
    """

    hora_inicio: time
    hora_fin: time

    def __post_init__(self) -> None:
        if self.hora_inicio >= self.hora_fin:
            raise ValueError("La hora de inicio debe ser menor que la hora de fin")
        if (
            self.hora_inicio.minute != 0
            or self.hora_inicio.second != 0
            or self.hora_fin.minute != 0
            or self.hora_fin.second != 0
        ):
            raise ValueError("La franja debe estar compuesta por bloques de hora completa")

    @property
    def horas(self) -> range:
        """Horas completas cubiertas por la franja (inicio inclusive, fin exclusivo)."""
        return range(self.hora_inicio.hour, self.hora_fin.hour)

    @property
    def duracion_horas(self) -> int:
        return self.hora_fin.hour - self.hora_inicio.hour

    def se_solapa_con(self, otra: FranjaHoraria) -> bool:
        """Solapamiento estricto: la contigüidad NO cuenta como solapamiento."""
        return self.hora_inicio < otra.hora_fin and self.hora_fin > otra.hora_inicio

    def es_contigua_a(self, otra: FranjaHoraria) -> bool:
        return self.hora_fin == otra.hora_inicio or otra.hora_fin == self.hora_inicio


@dataclass(frozen=True)
class HorarioAtencion:
    """Horas de atención por día de la semana.

    Normalización aplicada al construir:
    - Claves `str` o `int` normalizadas a `int` (la base de datos guarda las
      claves del JSON como strings mientras los schemas envían enteros;
      la decisión de fuente única queda pendiente — ver README de la carpeta).
    - Horas ordenadas y sin duplicados.
    - Días sin horas eliminados.

    Invariantes:
    - Debe existir al menos una franja en total.
    - Horas de inicio entre HORA_MINIMA (0) y HORA_MAXIMA (22), replicando el
      rango validado por `ConfiguracionEspacioUpdate` en
      `app/schemas/espacio.py`.
    """

    horas_por_dia: Mapping[int | str, Sequence[int]]

    def __post_init__(self) -> None:
        normalizado: dict[int, tuple[int, ...]] = {}
        for dia, horas in self.horas_por_dia.items():
            dia_int = int(dia)
            horas_unicas = sorted({int(hora) for hora in horas})
            for hora in horas_unicas:
                if hora < HORA_MINIMA or hora > HORA_MAXIMA:
                    raise ValueError(
                        f"Las horas deben estar entre {HORA_MINIMA} y {HORA_MAXIMA}"
                    )
            if horas_unicas:
                normalizado[dia_int] = tuple(horas_unicas)
        if not any(normalizado.values()):
            raise ValueError("Debe existir al menos una franja de atención")
        object.__setattr__(self, "horas_por_dia", normalizado)

    def horas_del_dia(self, dia: int) -> tuple[int, ...]:
        """Horas habilitadas del día; tupla vacía si el día no existe."""
        return self.horas_por_dia.get(dia, ())

    @property
    def dias(self) -> tuple[int, ...]:
        """Días con atención, ordenados de forma ascendente."""
        return tuple(sorted(self.horas_por_dia))

    def cubre_franja(self, dia: int, franja: FranjaHoraria) -> bool:
        """True si la franja (bloques completos) está contenida en el horario
        del día. Equivalente a `horario_cubre_reserva` de
        `app/services/horarios.py`, que lo consumirá en Fase 3."""
        habilitadas = set(self.horas_del_dia(dia))
        return all(hora in habilitadas for hora in franja.horas)
