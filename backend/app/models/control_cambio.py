from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.db import Base


class ControlCambio(Base):
    __tablename__ = "control_cambios"
    __table_args__ = {"schema": "reservas"}

    id = Column(Integer, primary_key=True)
    actor_tipo = Column(String(30), nullable=False)
    actor_id = Column(Integer, nullable=True)
    actor_nombre = Column(String(255), nullable=False)
    accion = Column(String(30), nullable=False)
    entidad = Column(String(80), nullable=False)
    entidad_id = Column(Integer, nullable=True)
    descripcion = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
