from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, ForeignKey, Index, Integer, String, Text, Time, func
from sqlalchemy.orm import relationship

from app.db import Base
from app.domain.enums import ESTADOS_RESERVA_BLOQUEANTES, EstadoReserva


# Alias derivados de los enums del dominio: misma tupla de strings que antes,
# sin duplicar los literales. Sin cambios de esquema ni migraciones.
ESTADOS_RESERVA = tuple(estado.value for estado in EstadoReserva)
ESTADOS_BLOQUEANTES = tuple(estado.value for estado in ESTADOS_RESERVA_BLOQUEANTES)


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    espacio_id = Column(Integer, ForeignKey("espacios.id"), nullable=False, index=True)
    recurso_id = Column(Integer, ForeignKey("recursos.id"), nullable=False, index=True)
    fecha = Column(Date, nullable=False, index=True)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    estado = Column(String(20), nullable=False, default="esperando", index=True)
    asistentes = Column(Integer, nullable=False)
    # Fase 12D (parcial): tipo de reserva académica (RN-012/RN-015).
    # Nullable por diseño: las reservas existentes y las que no especifican
    # tipo lo dejan sin valor. El CheckConstraint (en `__table_args__`) fija
    # los tres valores admitidos del enum TipoReserva.
    tipo = Column(String(30), nullable=True)
    # Fase 12D-bis: asistencia real, separada de estado/aprobación. Nullable
    # por diseño (sin backfill): las reservas existentes lo dejan sin valor.
    # Solo gestor/admin pueden escribirlo vía endpoint dedicado.
    asistio = Column(Boolean, nullable=True)
    # Fase 6: motivo de rechazo (solo cuando estado == rechazada). Nullable
    # para histórico; se limpia al cambiar de rechazada a otro estado
    # (aunque hoy rechazada es terminal, ver TRANSICIONES_ESTADO_RESERVA).
    motivo_rechazo = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    usuario = relationship("Usuario", back_populates="reservas")
    espacio = relationship("Espacio", back_populates="reservas")
    recurso = relationship("Recurso", back_populates="reservas")
    notificaciones = relationship("Notificacion", back_populates="reserva", cascade="all, delete-orphan")

    # Fase 12C-6: relaciones aditivas de lectura hacia las tablas de
    # asociación (sin cambio de esquema). `reserva_recursos`/`reserva_zonas`
    # son la fuente de verdad de los conjuntos de la reserva; la columna
    # histórica `recurso_id` se conserva como ancla temporal (12C-4e).
    # `foreign_keys` es necesario porque ambas asociaciones tienen dos FK.
    recursos_asociados = relationship(
        "ReservaRecurso",
        foreign_keys="ReservaRecurso.reserva_id",
        uselist=True,
        passive_deletes=True,
        overlaps="reserva",
    )
    zonas_asociadas = relationship(
        "ReservaZona",
        foreign_keys="ReservaZona.reserva_id",
        uselist=True,
        passive_deletes=True,
        overlaps="reserva",
    )
    zonas = relationship(
        "Zona",
        secondary="reserva_zonas",
        primaryjoin="Reserva.id == ReservaZona.reserva_id",
        secondaryjoin="ReservaZona.zona_id == Zona.id",
        uselist=True,
        viewonly=True,
    )
    ensayos = relationship(
        "Ensayo",
        secondary="reserva_ensayos",
        primaryjoin="Reserva.id == ReservaEnsayo.reserva_id",
        secondaryjoin="ReservaEnsayo.ensayo_id == Ensayo.id",
        uselist=True,
        viewonly=True,
    )
    acompanantes = relationship(
        "ReservaAcompanante",
        foreign_keys="ReservaAcompanante.reserva_id",
        uselist=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="reserva",
    )

    __table_args__ = (
        CheckConstraint("estado IN ('esperando', 'aprobada', 'rechazada', 'cancelada')", name="ck_reservas_estado"),
        CheckConstraint("hora_inicio < hora_fin", name="ck_reservas_horario_valido"),
        CheckConstraint("asistentes > 0", name="ck_reservas_asistentes_positivos"),
        CheckConstraint(
            "tipo IN ('trabajo_investigacion', 'trabajo_grado', 'servicio_de_ensayo')",
            name="ck_reservas_tipo",
        ),
        Index("ix_reservas_recurso_fecha_estado", "recurso_id", "fecha", "estado"),
    )
