from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class UnidadOrganizacional(Base):
    __tablename__ = "unidad_organizacional"
    __table_args__ = {"schema": "unidadOrganizacional"}

    id_unidad = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    id_unidad_padre = Column(
        Integer,
        ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"),
        nullable=True,
    )


class Cargo(Base):
    __tablename__ = "cargo"
    __table_args__ = {"schema": "cargos"}

    id_cargo = Column(Integer, primary_key=True)
    nombre_cargo = Column(String(50), nullable=False)
    id_unidad = Column(
        Integer,
        ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"),
        nullable=False,
    )
    unidad = relationship("UnidadOrganizacional")


class Personal(Base):
    __tablename__ = "personal"
    __table_args__ = {"schema": "personal"}

    id_persona = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    id_cargo = Column(Integer, ForeignKey("cargos.cargo.id_cargo"), nullable=False)
    documento = Column(String(20), nullable=False)
    correo = Column(String(150), nullable=False)
    telefono = Column(String(20), nullable=False)
    estado = Column(Boolean, nullable=True)
    supabase_id = Column(UUID(as_uuid=True), nullable=True, unique=True)
    cargo = relationship("Cargo")


class Equipo(Base):
    __tablename__ = "equipos"
    __table_args__ = {"schema": "equipos"}

    id_equipo = Column(Integer, primary_key=True)
    id_unidad = Column(
        Integer,
        ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"),
        nullable=False,
    )
    nombre_equipo = Column(String(50), nullable=False)
    placa = Column(String(40), nullable=True)
    serial = Column(String(50), nullable=True)
    marca = Column(String(50), nullable=True)
    modelo = Column(String(50), nullable=True)
    image_path = Column(String(100), nullable=True)
    manual_operacion = Column(String(100), nullable=True)
    requiere_calibracion = Column(Boolean, nullable=True)
    guia_rapida = Column(String(100), nullable=True)
    instalador = Column(String(100), nullable=True)
    estado = Column(Boolean, nullable=True)
    id_categoria = Column(Integer, nullable=True)
    proxima_fecha_calibracion = Column(Date, nullable=True)
    proxima_fecha_mantenimiento = Column(Date, nullable=True)
    frecuencia_calibracion = Column(Integer, nullable=True)
    frecuencia_mantenimiento = Column(Integer, nullable=True)
    unidad = relationship("UnidadOrganizacional")
