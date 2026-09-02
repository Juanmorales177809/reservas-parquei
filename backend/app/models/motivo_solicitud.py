from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db import Base


class MotivoSolicitud(Base):
    """Motivo de solicitud por laboratorio (Fase 2, motivos en tabla).
    Reemplaza el enum fijo TipoSolicitud como catálogo real por laboratorio,
    espejo de TipoReserva. Cada laboratorio define sus motivos."""

    __tablename__ = "motivos_solicitud"

    id = Column(Integer, primary_key=True, index=True)
    laboratorio_id = Column(Integer, ForeignKey("laboratorios.id"), nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(30), nullable=False)
    estado = Column(String(20), nullable=False, default="activo")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("personal.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("personal.id"), nullable=True)

    laboratorio = relationship("Laboratorio")
    creador = relationship("Personal", foreign_keys=[created_by])
    actualizador = relationship("Personal", foreign_keys=[updated_by])

    __table_args__ = (
        CheckConstraint("estado IN ('activo', 'inactivo')", name="ck_motivos_solicitud_estado"),
        CheckConstraint("codigo IN ('reserva_en_laboratorio', 'reserva_fuera_laboratorio', 'orden_salida')", name="ck_motivos_solicitud_codigo"),
        UniqueConstraint("laboratorio_id", "nombre", name="uq_motivos_solicitud_laboratorio_nombre"),
        UniqueConstraint("laboratorio_id", "codigo", name="uq_motivos_solicitud_laboratorio_codigo"),
    )

    def __repr__(self):
        return f"<MotivoSolicitud {self.nombre}>"
