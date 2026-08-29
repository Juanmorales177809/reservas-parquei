"""Respuesta HTTP de descarga de un archivo CSV/Excel ya construido en
memoria -- helper compartido por los distintos exports del backend
(dashboard, mis-reservas, auditoría). Sin lógica de armado de contenido
acá; eso vive en cada `services/exportar_*.py` específico.
"""

from datetime import date
from typing import Literal

from fastapi.responses import StreamingResponse

_MEDIA_TYPES = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def respuesta_streaming(contenido: bytes, formato: Literal["csv", "xlsx"], nombre_base: str) -> StreamingResponse:
    return StreamingResponse(
        iter([contenido]),
        media_type=_MEDIA_TYPES[formato],
        headers={"Content-Disposition": f"attachment; filename={nombre_base}_{date.today().isoformat()}.{formato}"},
    )
