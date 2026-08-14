# -*- coding: utf-8 -*-
"""Fuente de la hora actual de negocio.

`RelojLocal` implementa el protocolo `Reloj` del dominio; `ahora_local()` se
conserva como wrapper de compatibilidad para los módulos que ya la importan
(`api/espacios.py`, `api/recursos.py`).
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import settings
from app.domain.protocols import Reloj


class RelojLocal:
    """Implementación por defecto del protocolo Reloj.

    Devuelve un datetime NAIVE (sin tzinfo) en la zona horaria APP_TIMEZONE
    para poder compararlo directamente con las columnas DATE/TIME de la base
    de datos, tal como exige el contrato actual.
    """

    def ahora(self) -> datetime:
        return datetime.now(ZoneInfo(settings.app_timezone)).replace(tzinfo=None)


def ahora_local() -> datetime:
    """Wrapper de compatibilidad: delega en RelojLocal."""
    return RelojLocal().ahora()
