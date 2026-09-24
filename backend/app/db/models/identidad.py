"""Modelos de SQLAlchemy de identidad institucional: usuarios, personal, cargos, unidadOrganizacional (BK-08).

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

class Usuarios(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "usuarios"}

    id_usuario: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column()
    correo: Mapped[str] = mapped_column()
    estado: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()
    perfil_actualizado_at: Mapped[datetime | None] = mapped_column(nullable=True)
    documento: Mapped[str] = mapped_column()
    telefono: Mapped[str] = mapped_column()
    institucion: Mapped[str] = mapped_column()
    dependencia: Mapped[str] = mapped_column()


class Personal(Base):
    __tablename__ = "personal"
    __table_args__ = {"schema": "personal"}

    id_persona: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column()
    id_cargo: Mapped[int] = mapped_column(ForeignKey("cargos.cargo.id_cargo"))
    documento: Mapped[str] = mapped_column()
    correo: Mapped[str] = mapped_column()
    telefono: Mapped[str] = mapped_column()
    estado: Mapped[bool] = mapped_column()


class Cargo(Base):
    __tablename__ = "cargo"
    __table_args__ = {"schema": "cargos"}

    id_cargo: Mapped[int] = mapped_column(primary_key=True)
    nombre_cargo: Mapped[str] = mapped_column()
    id_unidad: Mapped[int] = mapped_column(ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"))


class UnidadOrganizacional(Base):
    __tablename__ = "unidad_organizacional"
    __table_args__ = {"schema": "unidadOrganizacional"}

    id_unidad: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column()
    tipo: Mapped[str] = mapped_column()
    id_unidad_padre: Mapped[int | None] = mapped_column(ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"), nullable=True)
    estado: Mapped[bool] = mapped_column()


