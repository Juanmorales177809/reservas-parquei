"""Esquemas Pydantic del contrato de auth (AUTH-B1, consumido por ambos carriles).

Un esquema por cuerpo de solicitud/respuesta documentado en
`contratos/auth/api-contract.md`. Los nombres de campo son los del contrato,
en español, sin traducir.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

TipoCuenta = Literal["USUARIO", "PERSONAL"]
# La sesión también puede ser de una cuenta de administrador (propia de Reservas); las invitaciones no.
TipoCuentaSesion = Literal["USUARIO", "PERSONAL", "ADMINISTRADOR"]
Rol = Literal["USUARIO", "TECNICO", "ADMINISTRADOR"]

# Rango de contraseña de SEC-PWD-07 / contrato §3.1: 8 a 64 caracteres,
# sin reglas de composición obligatorias.
_MIN_CONTRASENA = 8
_MAX_CONTRASENA = 64


def _validar_contrasena(v: str) -> str:
    if not (_MIN_CONTRASENA <= len(v) <= _MAX_CONTRASENA):
        raise ValueError(f"La contraseña debe tener entre {_MIN_CONTRASENA} y {_MAX_CONTRASENA} caracteres.")
    return v


def _no_vacio(v: str, maximo: int) -> str:
    v = v.strip()
    if not v:
        raise ValueError("No puede estar vacío ni compuesto solo por espacios.")
    if len(v) > maximo:
        raise ValueError(f"Supera el máximo de {maximo} caracteres.")
    return v


# --- §3.1 Autorregistro -----------------------------------------------------


class RegistroSolicitud(BaseModel):
    nombre: str = Field(max_length=150)
    documento: str = Field(max_length=20)
    telefono: str = Field(max_length=20)
    institucion: str = Field(max_length=255)
    dependencia: str = Field(max_length=255)
    correo: EmailStr
    contrasena: str

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

    @field_validator("contrasena")
    @classmethod
    def _v_contrasena(cls, v):
        return _validar_contrasena(v)


class MensajeGenerico(BaseModel):
    mensaje: str


# --- §3.2 Inicio de sesión --------------------------------------------------


class LoginSolicitud(BaseModel):
    correo: EmailStr
    contrasena: str


class SesionIniciada(BaseModel):
    id_cuenta: int
    tipo_cuenta: TipoCuentaSesion
    rol: Rol
    actualizacion_inicial_pendiente: bool | None
    correo: str
    id_sesion: str
    expira_en: datetime


# --- §3.3 Renovación --------------------------------------------------------


class RenovacionRespuesta(BaseModel):
    id_sesion: str
    expira_en: datetime
    actualizacion_inicial_pendiente: bool | None


# --- §3.4 Sesión actual ------------------------------------------------------


class SesionActual(BaseModel):
    id_cuenta: int
    tipo_cuenta: TipoCuentaSesion
    rol: Rol
    correo: str
    actualizacion_inicial_pendiente: bool | None
    id_sesion: str
    unidades_autorizadas: list[int] | Literal["GLOBAL"]
    autenticacion_reciente: bool


# --- §3.6-3.8 Recuperación ---------------------------------------------------


class RecuperacionSolicitud(BaseModel):
    correo: EmailStr


class TokenVigente(BaseModel):
    vigente: bool


class RestablecerContrasena(BaseModel):
    contrasena: str

    @field_validator("contrasena")
    @classmethod
    def _v(cls, v):
        return _validar_contrasena(v)


# --- §3.9 Reautenticación ----------------------------------------------------


class ReautenticacionSolicitud(BaseModel):
    contrasena: str


class ReautenticacionRespuesta(BaseModel):
    autenticacion_reciente_hasta: datetime


# --- §4 Invitaciones ---------------------------------------------------------


class InvitacionSolicitud(BaseModel):
    correo: EmailStr
    tipo_cuenta: TipoCuenta
    id_unidad: int | None = None


class InvitacionCreada(BaseModel):
    id: int
    correo: str
    tipo_cuenta: TipoCuenta
    expira_en: datetime
    estado: Literal["PENDIENTE"]


class InvitacionReenviada(BaseModel):
    id: int
    expira_en: datetime
    estado: Literal["PENDIENTE"]


class InvitacionVigente(BaseModel):
    vigente: bool
    correo: str


class ActivacionSolicitud(BaseModel):
    contrasena: str

    @field_validator("contrasena")
    @classmethod
    def _v(cls, v):
        return _validar_contrasena(v)


# --- §5 Cuenta propia --------------------------------------------------------


class CambioContrasena(BaseModel):
    contrasena: str

    @field_validator("contrasena")
    @classmethod
    def _v(cls, v):
        return _validar_contrasena(v)


# --- §6 Administración de cuentas -------------------------------------------


class CambioEstadoSolicitud(BaseModel):
    estado: bool


class CambioEstadoRespuesta(BaseModel):
    id_cuenta: int
    estado: bool
    sesiones_revocadas: int


class CambioIdentidadSolicitud(BaseModel):
    tipo_cuenta: TipoCuenta
    id_persona: int | None = None
    id_usuario: int | None = None


class CambioIdentidadRespuesta(BaseModel):
    id_cuenta: int
    tipo_cuenta: TipoCuenta
    id_persona: int | None
    id_usuario: int | None
