from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    reserva_id = Column(Integer, ForeignKey("reservas.id", ondelete="CASCADE"), nullable=True)
    tipo = Column(String(20), nullable=False)
    leida = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuario = relationship("Usuario", back_populates="notificaciones")
    reserva = relationship("Reserva", back_populates="notificaciones")

    __table_args__ = (
        CheckConstraint(
            "tipo IN ('Pendiente', 'Aprobada', 'Rechazada', 'Cancelada')",
            name="notificaciones_tipo_check",
        ),
    )
