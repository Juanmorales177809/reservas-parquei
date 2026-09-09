from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.db import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "reservas"}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    reservas = relationship("Reserva", back_populates="usuario")
    notificaciones = relationship("Notificacion", back_populates="usuario")
