from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True)
    # Polimórfico, mismo motivo/patrón que Reserva.usuario_id/personal_id:
    # el destinatario puede ser rol `usuario` (dueño de la reserva) o
    # `personal` (gestor del espacio). Exactamente uno de los dos.
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True)
    personal_id = Column(Integer, ForeignKey("personal.id", ondelete="CASCADE"), nullable=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id", ondelete="CASCADE"), nullable=True)
    tipo = Column(String(20), nullable=False)
    leida = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuario = relationship("Usuario", back_populates="notificaciones")
    personal = relationship("Personal", back_populates="notificaciones")
    reserva = relationship("Reserva", back_populates="notificaciones")

    __table_args__ = (
        CheckConstraint(
            "tipo IN ('Pendiente', 'Aprobada', 'Rechazada', 'Cancelada', 'Actualizada')",
            name="notificaciones_tipo_check",
        ),
        CheckConstraint(
            "(usuario_id IS NOT NULL) != (personal_id IS NOT NULL)",
            name="ck_notificaciones_actor_unico",
        ),
    )

    @property
    def actor(self):
        return self.usuario or self.personal
