"""Modelos de SQLAlchemy del schema `administration` (API-08, API-12).

Generado desde la base real; no crea ni altera tablas (regla 1 de
plan.md). Las escrituras de auditoría siguen por `core/audit.py` en cada
transacción; `importaciones`/`importacion_resultados` las escribe
`modules/administration` directamente, porque son su propia entidad, no un
registro de auditoría de otra operación.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Auditoria(Base):
    __tablename__ = "auditoria"
    __table_args__ = {"schema": "administration"}

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_cuenta_id: Mapped[int] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"))
    entidad: Mapped[str] = mapped_column()
    entidad_id: Mapped[str] = mapped_column()
    accion: Mapped[str] = mapped_column()
    datos_anteriores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    datos_nuevos: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    motivo: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column()


class Importaciones(Base):
    __tablename__ = "importaciones"
    __table_args__ = {"schema": "administration"}

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_cuenta_id: Mapped[int] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"))
    catalogo: Mapped[str] = mapped_column()
    archivo_referencia: Mapped[str] = mapped_column()
    registros_creados: Mapped[int] = mapped_column()
    registros_actualizados: Mapped[int] = mapped_column()
    registros_desactivados: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    confirmado_at: Mapped[datetime | None] = mapped_column(nullable=True)


class ImportacionResultados(Base):
    __tablename__ = "importacion_resultados"
    __table_args__ = {"schema": "administration"}

    id: Mapped[int] = mapped_column(primary_key=True)
    importacion_id: Mapped[int] = mapped_column(ForeignKey("administration.importaciones.id"))
    numero_fila: Mapped[int] = mapped_column()
    codigo: Mapped[str | None] = mapped_column(nullable=True)
    resultado: Mapped[str] = mapped_column()
    detalle: Mapped[str | None] = mapped_column(nullable=True)
    datos: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
