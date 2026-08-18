from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db import Base


class Zona(Base):
    __tablename__ = "zonas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    espacio_id = Column(Integer, ForeignKey("espacios.id"), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    capacidad = Column(Integer, nullable=True)
    estado = Column(String(20), nullable=False, default="activo")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # Relación unidireccional a propósito: esta subfase (12C-1) no modifica
    # app/models/espacio.py, así que no hay `back_populates` del lado de
    # Espacio todavía. La asociación Zona<->Recurso y la integración con
    # Reserva quedan para subfases posteriores (12C-3, 12C-4).
    espacio = relationship("Espacio")
    creador = relationship("Usuario", foreign_keys=[created_by])
    actualizador = relationship("Usuario", foreign_keys=[updated_by])

    __table_args__ = (
        CheckConstraint("estado IN ('activo', 'inactivo', 'mantenimiento')", name="ck_zonas_estado"),
    )

    def __repr__(self):
        return f"<Zona {self.nombre}>"
