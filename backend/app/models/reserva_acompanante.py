from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base


class ReservaAcompanante(Base):
    __tablename__ = "reserva_acompanantes"

    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre = Column(String(150), nullable=False)
    correo = Column(String(255), nullable=False)

    reserva = relationship("Reserva", overlaps="acompanantes")

    __table_args__ = (UniqueConstraint("reserva_id", "correo", name="uq_reserva_acompanantes_correo"),)
