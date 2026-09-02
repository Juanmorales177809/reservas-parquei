from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db import Base


class Espacio(Base):
    __tablename__ = "espacios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    laboratorio_id = Column(Integer, ForeignKey("laboratorios.id"), nullable=False, index=True)
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

    laboratorio = relationship("Laboratorio")
    creador = relationship("Personal", foreign_keys=[created_by])
    actualizador = relationship("Personal", foreign_keys=[updated_by])

    # viewonly: la escritura de la asociación sigue pasando exclusivamente
    # por `reemplazar_recursos_de_espacio` (PUT /espacios/{id}/recursos),
    # esto es solo para poder exponer `recurso_ids` en EspacioResponse sin
    # duplicar esa lógica de reemplazo completo.
    recursos = relationship(
        "Recurso",
        secondary="espacio_recursos",
        primaryjoin="Espacio.id == EspacioRecurso.espacio_id",
        secondaryjoin="EspacioRecurso.recurso_id == Recurso.id",
        uselist=True,
        viewonly=True,
    )

    __table_args__ = (
        CheckConstraint("estado IN ('activo', 'inactivo', 'mantenimiento')", name="ck_espacios_estado"),
    )

    def __repr__(self):
        return f"<Espacio {self.nombre}>"

    @property
    def recurso_ids(self) -> list[int]:
        return [r.id for r in self.recursos]
