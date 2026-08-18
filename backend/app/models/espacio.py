from datetime import time

from sqlalchemy import Boolean, JSON, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, Time, func
from sqlalchemy.orm import relationship
from app.db import Base


class Espacio(Base):
    __tablename__ = "espacios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    ubicacion = Column(String(200), nullable=False, default="Principal")
    capacidad = Column(Integer, nullable=False)
    estado = Column(String(20), nullable=False, default="activo")
    descripcion = Column(Text, nullable=True)
    dias_atencion = Column(JSON, nullable=False, default=lambda: [0, 1, 2, 3, 4, 5])
    hora_apertura = Column(Time, nullable=False, default=lambda: time(7, 0))
    hora_cierre = Column(Time, nullable=False, default=lambda: time(20, 0))
    horario_atencion = Column(
        JSON,
        nullable=False,
        default=lambda: {str(dia): list(range(7, 20)) for dia in range(6)},
    )
    horas_antelacion = Column(Integer, nullable=False, default=24)
    aprobacion_automatica = Column(Boolean, nullable=False, default=False)
    modalidad_reserva = Column(String(20), nullable=False, default="equipos")
    correo = Column(String(255), nullable=True)
    create_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    created_by = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    reservas = relationship("Reserva", back_populates="espacio", cascade="all, delete-orphan")
    recursos = relationship("Recurso", back_populates="espacio", cascade="all, delete-orphan")
    gestores = relationship("UsuarioEspacio", back_populates="espacio", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("hora_apertura < hora_cierre", name="ck_espacios_horario_atencion"),
        CheckConstraint("horas_antelacion >= 0", name="ck_espacios_horas_antelacion"),
        CheckConstraint(
            "modalidad_reserva IN ('equipos', 'zonas', 'mixto')",
            name="ck_espacios_modalidad_reserva",
        ),
    )

    def __repr__(self):
        return f"<Espacio {self.nombre}>"
