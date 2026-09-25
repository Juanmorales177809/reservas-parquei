"""Esquemas Pydantic del contrato de researchs (API-11)."""

from __future__ import annotations

from pydantic import BaseModel

TipoVinculacionAjena = str  # "proyectos" | "semilleros"; validado en el servicio.


# --- §2 Catálogo de proyectos y semilleros --------------------------------------


class ProyectoResumen(BaseModel):
    id_proyecto: int
    codigo: str
    nombre: str
    estado: bool


class SemilleroResumen(BaseModel):
    id_semillero: int
    codigo: str
    nombre: str
    estado: bool


class EstadoActualizar(BaseModel):
    estado: bool


# --- §3 Actividades institucionales ----------------------------------------------


class ActividadCrear(BaseModel):
    nombre: str
    dependencia: str


class ActividadActualizar(BaseModel):
    nombre: str | None = None
    dependencia: str | None = None


class ActividadResumen(BaseModel):
    id_actividad: int
    nombre: str
    dependencia: str
    estado: bool


# --- §4 Catálogo de perfiles -------------------------------------------------------


class PerfilCrear(BaseModel):
    nombre: str
    descripcion: str | None = None


class PerfilActualizar(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None


class PerfilResumen(BaseModel):
    id_perfil: int
    nombre: str
    descripcion: str | None = None
    estado: bool


# --- §5 Vinculaciones de terceros -------------------------------------------------


class VinculacionAjenaCrear(BaseModel):
    """`tipo` llega por la URL; el cuerpo trae el campo que corresponda."""

    id_proyecto: int | None = None
    id_semillero: int | None = None


class VinculacionesUsuario(BaseModel):
    proyectos: list[dict] = []
    semilleros: list[dict] = []
    pasantias: list[dict] = []
    trabajos_grado: list[dict] = []


class DesactivarVinculacionRespuesta(BaseModel):
    sin_vinculaciones_activas: bool
