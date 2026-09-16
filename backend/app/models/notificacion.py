from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func, text
from sqlalchemy.orm import relationship

from app.db import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"
    __table_args__ = {"schema": "reservas"}

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("reservas.usuarios.id", ondelete="CASCADE"), nullable=False)
    reserva_id = Column(Integer, ForeignKey("reservas.reservas.id", ondelete="CASCADE"), nullable=True)
    tipo = Column(String(20), nullable=False)
    leida = Column(Boolean, nullable=False, server_default=text("false"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuario = relationship("Usuario", back_populates="notificaciones")
    reserva = relationship("Reserva", back_populates="notificaciones")
