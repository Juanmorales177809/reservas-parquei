"""Modelos de SQLAlchemy del schema `administration` (API-08).

Primer modelo del schema, conforme a BK-08: se modela con el primer `API-XX`
de su propio módulo. Solo `auditoria` por ahora: `importaciones` la modela
API-12. Generado desde la base real; no crea ni altera tablas (regla 1 de
plan.md). Las escrituras siguen por `core/audit.py` en cada transacción.
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
