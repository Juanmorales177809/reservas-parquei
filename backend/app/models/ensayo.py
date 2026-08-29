from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db import Base


class Ensayo(Base):
    __tablename__ = "ensayos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    zona_id = Column(Integer, ForeignKey("zonas.id"), nullable=False, index=True)
    estado = Column(String(20), nullable=False, default="activo")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    # Nullable desde 2026-08-29 (bug real de producción, ver
    # backend/CLAUDE.md): un created_by/updated_by huérfano se limpia a
    # NULL en vez de romper la migración.
    created_by = Column(Integer, ForeignKey("personal.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("personal.id"), nullable=True)

    # Relación unidireccional a propósito: no se modifica Zona todavía,
    # mismo criterio que Zona.espacio en 12C-1.
    zona = relationship("Zona")
    creador = relationship("Personal", foreign_keys=[created_by])
    actualizador = relationship("Personal", foreign_keys=[updated_by])

    __table_args__ = (
        CheckConstraint("estado IN ('activo', 'inactivo', 'mantenimiento')", name="ck_ensayos_estado"),
    )

    def __repr__(self):
        return f"<Ensayo {self.nombre}>"
