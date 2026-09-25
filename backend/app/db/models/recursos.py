"""Modelos de SQLAlchemy del schema `recursos` (API-09).

Primer módulo que lo modela, conforme a `BK-08`: no se modeló al cerrar ese
hito porque nada lo consumía todavía. No crea ni altera tablas (regla 1 de
plan.md); el esquema lo gobierna `backend/migrations/004_recursos.sql`.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CategoriasEquipos(Base):
    __tablename__ = "categorias_equipos"
    __table_args__ = {"schema": "recursos"}

    id_categoria: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column()


class Recursos(Base):
    __tablename__ = "recursos"
    __table_args__ = {"schema": "recursos"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_unidad: Mapped[int] = mapped_column(ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"))
    tipo: Mapped[str] = mapped_column()
    habilitado: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()


class Equipos(Base):
    __tablename__ = "equipos"
    __table_args__ = {"schema": "recursos"}

    id: Mapped[int] = mapped_column(ForeignKey("recursos.recursos.id"), primary_key=True)
    nombre_equipo: Mapped[str] = mapped_column()
    placa: Mapped[str | None] = mapped_column(nullable=True)
    serial: Mapped[str | None] = mapped_column(nullable=True)
    marca: Mapped[str | None] = mapped_column(nullable=True)
    modelo: Mapped[str | None] = mapped_column(nullable=True)
    image_path: Mapped[str | None] = mapped_column(nullable=True)
    manual_operacion: Mapped[str | None] = mapped_column(nullable=True)
    requiere_calibracion: Mapped[bool | None] = mapped_column(nullable=True)
    guia_rapida: Mapped[str | None] = mapped_column(nullable=True)
    instalador: Mapped[str | None] = mapped_column(nullable=True)
    estado: Mapped[bool | None] = mapped_column(nullable=True)
    requiere_apoyo: Mapped[bool] = mapped_column()
    acreditado: Mapped[bool] = mapped_column()
    id_categoria: Mapped[int | None] = mapped_column(
        ForeignKey("recursos.categorias_equipos.id_categoria"), nullable=True
    )
    proxima_fecha_calibracion: Mapped[date | None] = mapped_column(nullable=True)
    proxima_fecha_mantenimiento: Mapped[date | None] = mapped_column(nullable=True)
    frecuencia_calibracion: Mapped[int | None] = mapped_column(nullable=True)
    frecuencia_mantenimiento: Mapped[int | None] = mapped_column(nullable=True)
    bodega: Mapped[str | None] = mapped_column(nullable=True)
    centro_costo: Mapped[str | None] = mapped_column(nullable=True)
    fecha_compra: Mapped[date | None] = mapped_column(nullable=True)


class Mobiliarios(Base):
    __tablename__ = "mobiliarios"
    __table_args__ = {"schema": "recursos"}

    id: Mapped[int] = mapped_column(ForeignKey("recursos.recursos.id"), primary_key=True)
    id_unidad: Mapped[int] = mapped_column(ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"))
    nombre: Mapped[str] = mapped_column()
    descripcion: Mapped[str | None] = mapped_column(nullable=True)
    habilitado: Mapped[bool] = mapped_column()


class OtrosRecursos(Base):
    __tablename__ = "otros_recursos"
    __table_args__ = {"schema": "recursos"}

    id: Mapped[int] = mapped_column(ForeignKey("recursos.recursos.id"), primary_key=True)
    id_unidad: Mapped[int] = mapped_column(ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"))
    nombre: Mapped[str] = mapped_column()
    descripcion: Mapped[str | None] = mapped_column(nullable=True)
    habilitado: Mapped[bool] = mapped_column()
