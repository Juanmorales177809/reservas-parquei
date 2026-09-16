from datetime import date, time

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Column, Date, DateTime, ForeignKey, Index, Integer, String, Text, Time, UniqueConstraint, func, text
from sqlalchemy.orm import relationship

from app.db import Base


ESTADOS_RESERVA = ("PENDIENTE", "APROBADA", "RECHAZADA", "CANCELADA")
ESTADOS_BLOQUEANTES = ("PENDIENTE", "APROBADA")


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True)
    id_cuenta = Column(BigInteger, ForeignKey("auth.cuentas.id_cuenta"), nullable=False)
    id_unidad = Column(Integer, ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"), nullable=False)
    espacio_id = Column(Integer, ForeignKey("reservas.espacios.id"), nullable=True)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    asistentes = Column(Integer, nullable=False)
    ubicacion_uso = Column(String(255), nullable=True)
    tipo_uso = Column(String(30), nullable=False)
    tipo_reserva_id = Column(Integer, ForeignKey("reservas.tipos_reserva.id"), nullable=False)
    motivo_solicitud_id = Column(Integer, ForeignKey("reservas.motivos_solicitud.id"), nullable=True)
    estado = Column(String(20), nullable=False, server_default=text("'PENDIENTE'"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cuenta = relationship("Cuenta", back_populates="reservas")
    unidad = relationship("UnidadOrganizacional")
    espacio = relationship("Espacio", back_populates="reservas")
    tipo_reserva = relationship("TipoReserva")
    motivo_solicitud = relationship("MotivoSolicitud")
    equipos = relationship("ReservaEquipo", back_populates="reserva")
    mobiliarios = relationship("ReservaMobiliario", back_populates="reserva")
    otros = relationship("ReservaOtro", back_populates="reserva")
    acompanantes = relationship("ReservaAcompanante", back_populates="reserva")
    notificaciones = relationship("Notificacion", back_populates="reserva")

    # These checks mirror the database model. Cross-row composition remains
    # application work for a later block.
    __table_args__ = (
        CheckConstraint("hora_inicio < hora_fin", name="ck_reservas_horario"),
        CheckConstraint("asistentes >= 0", name="reservas_asistentes_check"),
        CheckConstraint("tipo_uso IN ('ESPACIO_RESERVADO', 'DENTRO_CAMPUS', 'FUERA_CAMPUS')", name="reservas_tipo_uso_check"),
        CheckConstraint("estado IN ('PENDIENTE', 'APROBADA', 'RECHAZADA', 'CANCELADA')", name="reservas_estado_check"),
        CheckConstraint(
            "(tipo_uso = 'ESPACIO_RESERVADO' AND espacio_id IS NOT NULL) "
            "OR (tipo_uso = 'DENTRO_CAMPUS' AND "
            "(espacio_id IS NOT NULL OR NULLIF(btrim(ubicacion_uso), '') IS NOT NULL)) "
            "OR (tipo_uso = 'FUERA_CAMPUS' AND espacio_id IS NULL AND "
            "NULLIF(btrim(ubicacion_uso), '') IS NOT NULL)",
            name="ck_reservas_tipo_uso",
        ),
        Index("ix_reservas_fecha_estado", "fecha", "estado"),
        Index("ix_reservas_unidad_fecha", "id_unidad", "fecha"),
        {"schema": "reservas"},
    )


class TipoReserva(Base):
    __tablename__ = "tipos_reserva"
    __table_args__ = {"schema": "reservas"}
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    habilitado = Column(Boolean, nullable=False, server_default=text("true"))


class MotivoSolicitud(Base):
    __tablename__ = "motivos_solicitud"
    __table_args__ = {"schema": "reservas"}
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    habilitado = Column(Boolean, nullable=False, server_default=text("true"))


class ReservaEquipo(Base):
    __tablename__ = "reserva_equipos"
    __table_args__ = (
        UniqueConstraint("reserva_id", "id_equipo", name="uq_reserva_equipo"),
        {"schema": "reservas"},
    )
    id = Column(Integer, primary_key=True)
    reserva_id = Column(Integer, ForeignKey("reservas.reservas.id", ondelete="CASCADE"), nullable=False)
    id_equipo = Column(Integer, ForeignKey("equipos.equipos.id_equipo"), nullable=False)
    reserva = relationship("Reserva", back_populates="equipos")
    equipo = relationship("Equipo")


class Mobiliario(Base):
    __tablename__ = "mobiliarios"
    __table_args__ = {"schema": "reservas"}
    id = Column(Integer, primary_key=True)
    id_unidad = Column(Integer, ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    habilitado = Column(Boolean, nullable=False, server_default=text("true"))


class Otro(Base):
    __tablename__ = "otros"
    __table_args__ = {"schema": "reservas"}
    id = Column(Integer, primary_key=True)
    id_unidad = Column(Integer, ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    habilitado = Column(Boolean, nullable=False, server_default=text("true"))


class ReservaMobiliario(Base):
    __tablename__ = "reserva_mobiliarios"
    __table_args__ = (
        UniqueConstraint("reserva_id", "mobiliario_id", name="uq_reserva_mobiliario"),
        {"schema": "reservas"},
    )
    id = Column(Integer, primary_key=True)
    reserva_id = Column(Integer, ForeignKey("reservas.reservas.id", ondelete="CASCADE"), nullable=False)
    mobiliario_id = Column(Integer, ForeignKey("reservas.mobiliarios.id"), nullable=False)
    reserva = relationship("Reserva", back_populates="mobiliarios")
    mobiliario = relationship("Mobiliario")


class ReservaOtro(Base):
    __tablename__ = "reserva_otros"
    __table_args__ = (
        UniqueConstraint("reserva_id", "otro_id", name="uq_reserva_otro"),
        {"schema": "reservas"},
    )
    id = Column(Integer, primary_key=True)
    reserva_id = Column(Integer, ForeignKey("reservas.reservas.id", ondelete="CASCADE"), nullable=False)
    otro_id = Column(Integer, ForeignKey("reservas.otros.id"), nullable=False)
    reserva = relationship("Reserva", back_populates="otros")
    otro = relationship("Otro")


class ReservaAcompanante(Base):
    __tablename__ = "reserva_acompanantes"
    __table_args__ = {"schema": "reservas"}
    id = Column(Integer, primary_key=True)
    reserva_id = Column(Integer, ForeignKey("reservas.reservas.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(150), nullable=False)
    correo = Column(String(255), nullable=True)
    reserva = relationship("Reserva", back_populates="acompanantes")
