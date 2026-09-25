"""Modelos de SQLAlchemy del schema `notificaciones` (API-17).

No crea ni altera tablas (regla 1 de plan.md); el esquema lo gobierna
`backend/migrations/007_notificaciones.sql` y los seeds de tipos de evento.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TiposEvento(Base):
    __tablename__ = "tipos_evento"
    __table_args__ = {"schema": "notificaciones"}

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column()
    nombre: Mapped[str] = mapped_column()
    descripcion: Mapped[str | None] = mapped_column(nullable=True)
    habilitado: Mapped[bool] = mapped_column()


class Eventos(Base):
    __tablename__ = "eventos"
    __table_args__ = {"schema": "notificaciones"}

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_evento_id: Mapped[int] = mapped_column(ForeignKey("notificaciones.tipos_evento.id"))
    reserva_id: Mapped[int | None] = mapped_column(ForeignKey("reservas.reservas.id"), nullable=True)
    ocurrencia_clave: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()


class Notificaciones(Base):
    __tablename__ = "notificaciones"
    __table_args__ = {"schema": "notificaciones"}

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("notificaciones.eventos.id"))
    id_cuenta: Mapped[int] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"))
    titulo: Mapped[str] = mapped_column()
    cuerpo: Mapped[str] = mapped_column()
    leida_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column()


class EnviosCorreo(Base):
    __tablename__ = "envios_correo"
    __table_args__ = {"schema": "notificaciones"}

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("notificaciones.eventos.id"))
    notificacion_id: Mapped[int | None] = mapped_column(
        ForeignKey("notificaciones.notificaciones.id"), nullable=True
    )
    destinatario_correo: Mapped[str] = mapped_column()
    titulo: Mapped[str] = mapped_column()
    cuerpo: Mapped[str] = mapped_column()
    estado: Mapped[str] = mapped_column()
    intentos: Mapped[int] = mapped_column()
    proximo_intento_at: Mapped[datetime | None] = mapped_column(nullable=True)
    ultimo_error: Mapped[str | None] = mapped_column(nullable=True)
    enviado_at: Mapped[datetime | None] = mapped_column(nullable=True)
    anulado_at: Mapped[datetime | None] = mapped_column(nullable=True)
    motivo_anulacion: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column()


class EnvioCorreoAdjuntos(Base):
    __tablename__ = "envio_correo_adjuntos"
    __table_args__ = {"schema": "notificaciones"}

    id: Mapped[int] = mapped_column(primary_key=True)
    envio_correo_id: Mapped[int] = mapped_column(ForeignKey("notificaciones.envios_correo.id"))
    orden: Mapped[int] = mapped_column()
    nombre_original: Mapped[str] = mapped_column()
    storage_key: Mapped[str] = mapped_column()
    content_type: Mapped[str] = mapped_column()
    size_bytes: Mapped[int] = mapped_column()
    contenido_hash: Mapped[str] = mapped_column()


class Preferencias(Base):
    __tablename__ = "preferencias"
    __table_args__ = {"schema": "notificaciones"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_cuenta: Mapped[int] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"))
    tipo_evento_id: Mapped[int | None] = mapped_column(
        ForeignKey("notificaciones.tipos_evento.id"), nullable=True
    )
    correo_habilitado: Mapped[bool] = mapped_column()
