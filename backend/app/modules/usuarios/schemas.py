"""Esquemas Pydantic del contrato de usuarios (API-06).

Nombres de campo en español, como en el contrato. El correo nunca es editable
en el perfil propio: es solo lectura (UF-USR-04); si el cliente lo envía, el
servicio lo rechaza con 409 en vez de ignorarlo.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


def _no_vacio(v: str, maximo: int) -> str:
    v = v.strip()
    if not v:
        raise ValueError("No puede estar vacío ni compuesto solo por espacios.")
    if len(v) > maximo:
        raise ValueError(f"Supera el máximo de {maximo} caracteres.")
    return v


def _nombre_150(v: str | None) -> str | None:
    return None if v is None else _no_vacio(v, 150)


def _nombre_50(v: str | None) -> str | None:
    return None if v is None else _no_vacio(v, 50)


def _corto_20(v: str | None) -> str | None:
    return None if v is None else _no_vacio(v, 20)


def _largo_255(v: str | None) -> str | None:
    return None if v is None else _no_vacio(v, 255)


# --- §5 Administración de identidades de Usuario ------------------------------


class UsuarioCrear(BaseModel):
    nombre: str = Field(max_length=150)
    documento: str = Field(max_length=20)
    telefono: str = Field(max_length=20)
    institucion: str = Field(max_length=255)
    dependencia: str = Field(max_length=255)
    correo: EmailStr

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        return _no_vacio(v, 150)

    @field_validator("documento", "telefono")
    @classmethod
    def _v_20(cls, v):
        return _no_vacio(v, 20)

    @field_validator("institucion", "dependencia")
    @classmethod
    def _v_255(cls, v):
        return _no_vacio(v, 255)


class UsuarioActualizar(BaseModel):
    nombre: str | None = Field(default=None, max_length=150)
    documento: str | None = Field(default=None, max_length=20)
    telefono: str | None = Field(default=None, max_length=20)
    institucion: str | None = Field(default=None, max_length=255)
    dependencia: str | None = Field(default=None, max_length=255)
    correo: EmailStr | None = None

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        return _nombre_150(v)

    @field_validator("documento", "telefono")
    @classmethod
    def _v_20(cls, v):
        return _corto_20(v)

    @field_validator("institucion", "dependencia")
    @classmethod
    def _v_255(cls, v):
        return _largo_255(v)


class UsuarioRespuesta(BaseModel):
    id_usuario: int
    nombre: str
    documento: str
    telefono: str
    institucion: str
    dependencia: str
    correo: str
    estado: bool
    perfil_actualizado_at: datetime | None


class EstadoSolicitud(BaseModel):
    estado: bool


# --- §6 Fichas de Personal ----------------------------------------------------


class PersonalCrear(BaseModel):
    nombre: str = Field(max_length=50)
    documento: str = Field(max_length=20)
    correo: EmailStr
    telefono: str = Field(max_length=20)
    id_cargo: int

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        return _no_vacio(v, 50)

    @field_validator("documento", "telefono")
    @classmethod
    def _v_20(cls, v):
        return _no_vacio(v, 20)


class PersonalActualizar(BaseModel):
    nombre: str | None = Field(default=None, max_length=50)
    documento: str | None = Field(default=None, max_length=20)
    correo: EmailStr | None = None
    telefono: str | None = Field(default=None, max_length=20)
    id_cargo: int | None = None

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        return _nombre_50(v)

    @field_validator("documento", "telefono")
    @classmethod
    def _v_20(cls, v):
        return _corto_20(v)


class CargoResumen(BaseModel):
    id_cargo: int
    nombre_cargo: str


class UnidadResumen(BaseModel):
    id_unidad: int
    nombre: str


class PersonalRespuesta(BaseModel):
    id_persona: int
    nombre: str
    documento: str
    correo: str
    telefono: str
    estado: bool
    id_cargo: int
    cargo: CargoResumen
    unidad: UnidadResumen


# --- §2 Perfil propio ----------------------------------------------------------


class PerfilActualizar(BaseModel):
    """Sin correo editable: si llega, el servicio responde 409 (UF-USR-04)."""

    nombre: str | None = Field(default=None, max_length=150)
    documento: str | None = Field(default=None, max_length=20)
    telefono: str | None = Field(default=None, max_length=20)
    institucion: str | None = Field(default=None, max_length=255)
    dependencia: str | None = Field(default=None, max_length=255)
    correo: EmailStr | None = None

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        return _nombre_150(v)

    @field_validator("documento", "telefono")
    @classmethod
    def _v_20(cls, v):
        return _corto_20(v)

    @field_validator("institucion", "dependencia")
    @classmethod
    def _v_255(cls, v):
        return _largo_255(v)


class VinculacionesResumen(BaseModel):
    proyectos: list[dict] = []
    semilleros: list[dict] = []
    pasantias: list[dict] = []
    trabajos_grado: list[dict] = []


class PerfilRespuesta(BaseModel):
    id_usuario: int
    nombre: str
    documento: str
    telefono: str
    institucion: str
    dependencia: str
    correo: str
    actualizacion_inicial_pendiente: bool
    perfil_actualizado_at: datetime | None
    perfiles: list[dict] = []
    vinculaciones: VinculacionesResumen = VinculacionesResumen()
