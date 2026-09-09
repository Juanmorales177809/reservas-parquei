from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON, String, Text, Time
from sqlalchemy.orm import relationship

from app.db import Base


class LaboratorioConfig(Base):
    __tablename__ = "laboratorios_config"
    __table_args__ = {"schema": "reservas"}

    id = Column(Integer, primary_key=True)
    id_unidad = Column(Integer, ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"), nullable=False, unique=True)
    habilitado_reservas = Column(Boolean, nullable=False, default=True)
    ubicacion = Column(String(255), nullable=True)
    descripcion = Column(Text, nullable=True)
    dias_atencion = Column(JSON, nullable=False)
    hora_apertura = Column(Time, nullable=False)
    hora_cierre = Column(Time, nullable=False)
    horario_atencion = Column(JSON, nullable=False)
    horas_antelacion = Column(Integer, nullable=False)
    aprobacion_automatica = Column(Boolean, nullable=False)
    modalidad_reserva = Column(String(50), nullable=True)
    correo = Column(String(255), nullable=True)
    notificar_por_correo = Column(Boolean, nullable=False)
    unidad = relationship("UnidadOrganizacional")


class Espacio(Base):
    __tablename__ = "espacios"
    __table_args__ = {"schema": "reservas"}

    id = Column(Integer, primary_key=True, index=True)
    id_unidad = Column(Integer, ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"), nullable=False)
    nombre = Column(String(100), nullable=False)
    ubicacion = Column(String(255), nullable=True)
    capacidad = Column(Integer, nullable=False)
    descripcion = Column(Text, nullable=True)
    habilitado = Column(Boolean, nullable=False, default=True)

    unidad = relationship("UnidadOrganizacional")
    reservas = relationship("Reserva", back_populates="espacio")
