"""HorarioPolicy: comprobaciones reutilizables de fecha y franja (RN-HOR).

Aplica únicamente a los tipos con `hora_inicio`/`hora_fin` (RN-HOR-01):
`ESPACIO` y `RECURSO_INTERNO`. Campus y externo trabajan por fecha completa
y no pasan por aquí.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.core.errors import FueraDeHorario, Validacion

_ZONA_OPERATIVA = ZoneInfo("America/Bogota")


def validar_franja(*, fecha: date, hora_inicio: time, hora_fin: time, config, ahora: datetime) -> None:
    """RN-HOR-02/03/04/05: horario coherente, dentro de la atención de la
    unidad, sin fechas pasadas. `config` es `reservas.laboratorios_config`
    ya cargada por el servicio. `fecha`/`hora_inicio`/`hora_fin` son hora
    local de la unidad (`America/Bogota`, DB-11); `ahora` llega en UTC y se
    convierte aquí para comparar fechas locales correctamente."""
    if hora_inicio >= hora_fin:
        raise Validacion("hora_inicio debe ser anterior a hora_fin.")
    ahora_local = ahora.astimezone(_ZONA_OPERATIVA)
    if fecha < ahora_local.date():
        raise Validacion("No se aceptan fechas pasadas.")

    # dias_atencion usa 0=domingo (convención de resources); date.weekday() usa 0=lunes.
    dia_negocio = (fecha.weekday() + 1) % 7
    if dia_negocio not in (config.dias_atencion or []):
        raise FueraDeHorario("La unidad no atiende ese día.")
    if hora_inicio < config.hora_apertura or hora_fin > config.hora_cierre:
        raise FueraDeHorario("El horario solicitado queda fuera del horario de atención de la unidad.")


def validar_antelacion(*, fecha: date, hora_inicio: time, config, ahora: datetime) -> None:
    """RN-HOR-06: se exige al crear y al reprogramar; no vuelve a exigirse al aprobar."""
    if not config.horas_antelacion:
        return
    limite = ahora + timedelta(hours=config.horas_antelacion)
    inicio_solicitado = datetime.combine(fecha, hora_inicio, tzinfo=_ZONA_OPERATIVA)
    if inicio_solicitado < limite:
        raise FueraDeHorario(f"Se requieren al menos {config.horas_antelacion} horas de antelación.")
