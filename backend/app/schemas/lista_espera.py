from datetime import date, datetime, time

from pydantic import BaseModel


class ListaEsperaCreate(BaseModel):
    recurso_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time


class ListaEsperaResponse(BaseModel):
    id: int
    recurso_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    estado: str
    created_at: datetime
