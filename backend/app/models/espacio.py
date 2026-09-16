from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Time, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db import Base


class LaboratorioConfig(Base):
    __tablename__ = "laboratorios_config"
    __table_args__ = {"schema": "reservas"}

    id = Column(Integer, primary_key=True)
    id_unidad = Column(Integer, ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"), nullable=False, unique=True)
    habilitado_reservas = Column(Boolean, nullable=False, server_default=text("true"))
    ubicacion = Column(String(255), nullable=True)
    descripcion = Column(Text, nullable=True)
    dias_atencion = Column(JSONB, nullable=False, server_default=text("'[0, 1, 2, 3, 4, 5]'::jsonb"))
    hora_apertura = Column(Time, nullable=False)
    hora_cierre = Column(Time, nullable=False)
    horario_atencion = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    horas_antelacion = Column(Integer, nullable=False, server_default=text("0"))
    aprobacion_automatica = Column(Boolean, nullable=False, server_default=text("false"))
    modalidad_reserva = Column(String(50), nullable=True)
    correo = Column(String(255), nullable=True)
    notificar_por_correo = Column(Boolean, nullable=False, server_default=text("false"))
    unidad = relationship("UnidadOrganizacional")


class Espacio(Base):
    __tablename__ = "espacios"
    __table_args__ = (
        UniqueConstraint("id_unidad", "nombre", name="uq_espacios_unidad_nombre"),
        {"schema": "reservas"},
    )

    id = Column(Integer, primary_key=True)
    id_unidad = Column(Integer, ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"), nullable=False)
    nombre = Column(String(100), nullable=False)
    ubicacion = Column(String(255), nullable=True)
    capacidad = Column(Integer, nullable=False)
    descripcion = Column(Text, nullable=True)
    habilitado = Column(Boolean, nullable=False, server_default=text("true"))

    unidad = relationship("UnidadOrganizacional")
    reservas = relationship("Reserva", back_populates="espacio")
