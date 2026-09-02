from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db import Base


class TipoReserva(Base):
    """Tipo de reserva definido por laboratorio (Fase 7, reemplaza el enum
    fijo `domain.enums.TipoReserva` como catálogo real). Cada laboratorio da
    de alta sus propios tipos -- no hay valores compartidos entre
    laboratorios ni un catálogo global."""

    __tablename__ = "tipos_reserva"

    id = Column(Integer, primary_key=True, index=True)
    laboratorio_id = Column(Integer, ForeignKey("laboratorios.id"), nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    estado = Column(String(20), nullable=False, default="activo")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("personal.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("personal.id"), nullable=True)

    laboratorio = relationship("Laboratorio")
    creador = relationship("Personal", foreign_keys=[created_by])
    actualizador = relationship("Personal", foreign_keys=[updated_by])

    __table_args__ = (
        CheckConstraint("estado IN ('activo', 'inactivo')", name="ck_tipos_reserva_estado"),
        UniqueConstraint("laboratorio_id", "nombre", name="uq_tipos_reserva_laboratorio_nombre"),
    )

    def __repr__(self):
        return f"<TipoReserva {self.nombre}>"
