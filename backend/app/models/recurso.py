from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db import Base


class TipoRecurso(Base):
    __tablename__ = "tipos_recursos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), nullable=False)
    descripcion = Column(Text, nullable=False, default="")
    activo = Column(String(50), nullable=False, default="activo")

    recursos = relationship("Recurso", back_populates="tipo")


class Recurso(Base):
    __tablename__ = "recursos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    espacio_id = Column(Integer, ForeignKey("espacios.id"), nullable=False, index=True)
    tipo_recurso_id = Column(Integer, ForeignKey("tipos_recursos.id"), nullable=False)
    descripcion = Column(Text, nullable=True)
    capacidad = Column(Integer, nullable=False)
    estado = Column(String(30), nullable=False, default="activo")
    es_prestacion_servicio = Column(Boolean, nullable=False, default=False)
    # Fase D (import de inventario institucional): identificador de activo
    # físico (ej. "05087964"). Nullable -- solo lo trae el inventario real
    # importado, un recurso creado a mano desde la UI lo deja en null. Sin
    # esto, un reintento del import no es idempotente de verdad: hay
    # descripciones duplicadas entre activos distintos (ej. "MICRÓFONO
    # DINÁMICO SM 57" aparece más de una vez en el mismo laboratorio).
    placa = Column(String(50), nullable=True)
    create_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    update_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    update_by = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    espacio = relationship("Espacio", back_populates="recursos")
    tipo = relationship("TipoRecurso", back_populates="recursos")
    reservas = relationship("Reserva", back_populates="recurso")
    creador = relationship("Usuario", foreign_keys=[created_by], overlaps="recursos_creados")
    actualizador = relationship("Usuario", foreign_keys=[update_by], overlaps="recursos_actualizados")
