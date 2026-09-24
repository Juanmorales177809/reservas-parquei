"""Modelos de SQLAlchemy del schema `auth` (BK-08).

Generados desde la base real; no crean ni alteran tablas (regla 1 de
plan.md). El esquema lo gobiernan las migraciones de backend/migrations/."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class CuentaPermisos(Base):
    __tablename__ = "cuenta_permisos"
    __table_args__ = {"schema": "auth"}

    id_cuenta_permiso: Mapped[int] = mapped_column(primary_key=True)
    id_cuenta: Mapped[int] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"))
    permiso_id: Mapped[int] = mapped_column(ForeignKey("auth.permisos.id"))
    id_unidad: Mapped[int | None] = mapped_column(ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"), nullable=True)
    otorgado_por: Mapped[int] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"))
    created_at: Mapped[datetime] = mapped_column()


class Cuentas(Base):
    __tablename__ = "cuentas"
    __table_args__ = {"schema": "auth"}

    id_cuenta: Mapped[int] = mapped_column(primary_key=True)
    correo: Mapped[str] = mapped_column()
    password_hash: Mapped[str] = mapped_column()
    tipo_cuenta: Mapped[str] = mapped_column()
    id_usuario: Mapped[int | None] = mapped_column(ForeignKey("usuarios.usuarios.id_usuario"), nullable=True)
    id_persona: Mapped[int | None] = mapped_column(ForeignKey("personal.personal.id_persona"), nullable=True)
    estado: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()


class Invitaciones(Base):
    __tablename__ = "invitaciones"
    __table_args__ = {"schema": "auth"}

    id: Mapped[int] = mapped_column(primary_key=True)
    correo: Mapped[str] = mapped_column()
    tipo_cuenta: Mapped[str] = mapped_column()
    id_usuario: Mapped[int | None] = mapped_column(ForeignKey("usuarios.usuarios.id_usuario"), nullable=True)
    id_persona: Mapped[int | None] = mapped_column(ForeignKey("personal.personal.id_persona"), nullable=True)
    token_hash: Mapped[str] = mapped_column()
    expira_at: Mapped[datetime] = mapped_column()
    usada_at: Mapped[datetime | None] = mapped_column(nullable=True)
    revocada_at: Mapped[datetime | None] = mapped_column(nullable=True)
    creada_por: Mapped[int] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"))
    created_at: Mapped[datetime] = mapped_column()


class Permisos(Base):
    __tablename__ = "permisos"
    __table_args__ = {"schema": "auth"}

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column()
    nombre: Mapped[str] = mapped_column()
    descripcion: Mapped[str | None] = mapped_column(nullable=True)
    habilitado: Mapped[bool] = mapped_column()


class Sesiones(Base):
    __tablename__ = "sesiones"
    __table_args__ = {"schema": "auth"}

    id_sesion: Mapped[UUID] = mapped_column(primary_key=True)
    id_cuenta: Mapped[int] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"))
    refresh_token_hash: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    expires_at: Mapped[datetime] = mapped_column()
    revoked_at: Mapped[datetime | None] = mapped_column(nullable=True)
    ultima_actividad_at: Mapped[datetime] = mapped_column()
    reautenticado_at: Mapped[datetime | None] = mapped_column(nullable=True)


class TokensRecuperacion(Base):
    __tablename__ = "tokens_recuperacion"
    __table_args__ = {"schema": "auth"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_cuenta: Mapped[int] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"))
    token_hash: Mapped[str] = mapped_column()
    expira_at: Mapped[datetime] = mapped_column()
    usado_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column()


