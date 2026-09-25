"""Esquemas Pydantic del contrato de notifications (API-17)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class TipoEventoItem(BaseModel):
    id: int
    codigo: str
    nombre: str
    descripcion: str | None = None


class TipoEventoRef(BaseModel):
    codigo: str
    nombre: str


class NotificacionItem(BaseModel):
    id: int
    tipo_evento: TipoEventoRef
    titulo: str
    cuerpo: str
    reserva_id: int | None = None
    leida_at: datetime | None = None
    created_at: datetime


class LecturaRespuesta(BaseModel):
    id: int
    leida_at: datetime


class PreferenciaEventoItem(BaseModel):
    tipo_evento_id: int
    correo_habilitado: bool


class PreferenciaGeneral(BaseModel):
    correo_habilitado: bool = True


class PreferenciasCuerpo(BaseModel):
    general: PreferenciaGeneral | None = None
    por_evento: list[PreferenciaEventoItem] = []


class PreferenciaEventoRespuesta(BaseModel):
    tipo_evento: TipoEventoRef
    correo_habilitado: bool


class PreferenciasRespuesta(BaseModel):
    general: dict[str, bool]
    por_evento: list[PreferenciaEventoRespuesta] = []
