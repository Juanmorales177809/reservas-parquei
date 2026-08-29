from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db import Base


class Zona(Base):
    __tablename__ = "zonas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    espacio_id = Column(Integer, ForeignKey("espacios.id"), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    capacidad = Column(Integer, nullable=True)
    estado = Column(String(20), nullable=False, default="activo")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    # Nullable desde 2026-08-29 (bug real de producción, ver
    # backend/CLAUDE.md): un created_by/updated_by huérfano se limpia a
    # NULL en vez de romper la migración.
    created_by = Column(Integer, ForeignKey("personal.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("personal.id"), nullable=True)

    # Relación unidireccional a propósito: esta subfase (12C-1) no modifica
    # app/models/espacio.py, así que no hay `back_populates` del lado de
    # Espacio todavía. La integración con Reserva queda para subfases
    # posteriores (12C-4).
    espacio = relationship("Espacio")
    creador = relationship("Personal", foreign_keys=[created_by])
    actualizador = relationship("Personal", foreign_keys=[updated_by])

    # viewonly: la escritura de la asociación sigue pasando exclusivamente
    # por `reemplazar_recursos_de_zona` (PUT /zonas/{id}/recursos), esto es
    # solo para poder exponer `recurso_ids` en ZonaResponse sin duplicar esa
    # lógica de reemplazo completo.
    recursos = relationship(
        "Recurso",
        secondary="zona_recursos",
        primaryjoin="Zona.id == ZonaRecurso.zona_id",
        secondaryjoin="ZonaRecurso.recurso_id == Recurso.id",
        uselist=True,
        viewonly=True,
    )

    __table_args__ = (
        CheckConstraint("estado IN ('activo', 'inactivo', 'mantenimiento')", name="ck_zonas_estado"),
    )

    def __repr__(self):
        return f"<Zona {self.nombre}>"

    @property
    def recurso_ids(self) -> list[int]:
        return [r.id for r in self.recursos]
