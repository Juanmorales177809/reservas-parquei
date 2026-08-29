from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, ForeignKey, Index, Integer, String, Text, Time, func
from sqlalchemy.dialects.postgresql import UUID
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
    # Polimórfico a propósito: quien crea una reserva puede ser rol
    # `usuario` O `personal` (un gestor reserva su propio espacio) --
    # exactamente una de las dos debe estar llena, nunca las dos ni
    # ninguna (`ck_reservas_actor_unico`). Ver `actor` más abajo y
    # `app/services/actores.py::columnas_actor`.
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    personal_id = Column(Integer, ForeignKey("personal.id"), nullable=True, index=True)
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
    # Fase A3: texto libre opcional donde quien reserva describe la
    # actividad ("Actividad a realizar" del formulario real de solicitud
    # de laboratorios) -- sin CheckConstraint, es puramente descriptivo.
    descripcion = Column(Text, nullable=True)
    # Fase B: motivo de la solicitud (TipoSolicitud) -- NOT NULL con
    # default, a diferencia de `tipo` (académico, nullable): toda reserva
    # SÍ tiene un motivo, aunque no lo declare explícitamente al crearla
    # (las reservas de antes de la Fase B quedan en el default vía
    # backfill de la migración). Distinto de `tipo`/`modalidad_reserva` de
    # `Espacio` -- ver el docstring de `TipoSolicitud`.
    tipo_solicitud = Column(String(30), nullable=False, default="reserva_en_laboratorio")
    # Fase B: solo tiene sentido cuando tipo_solicitud == reserva_fuera_laboratorio
    # (validado en el servicio, no acá) -- el resto de las ramas lo dejan null.
    ubicacion_uso = Column(String(200), nullable=True)
    # Fase B: pregunta 18 del formulario real, aplica a las dos ramas que
    # viven en esta tabla.
    requiere_apoyo_auxiliar = Column(Boolean, nullable=False, default=False)
    # Fase 2026-08-29: marca de idempotencia del recordatorio de reserva
    # próxima (`services/recordatorios.py`) -- nullable, sin backfill (ver
    # `migrations.py`). NULL = todavía no se le mandó el recordatorio.
    recordatorio_enviado_en = Column(DateTime(timezone=True), nullable=True)
    # Fase 2026-08-29: reservas recurrentes -- vincula las N filas creadas
    # en una misma solicitud con `repetir_semanas` (mismo valor para todas
    # las ocurrencias de una serie). NULL para cualquier reserva no
    # recurrente (la inmensa mayoría). A propósito NO hay tabla ni UI de
    # gestión de "la serie completa" en esta primera versión -- cada
    # ocurrencia se edita/cancela individualmente como cualquier otra
    # reserva; esta columna solo deja la correlación guardada para el
    # futuro (`~/.claude/plans/dazzling-wobbling-zebra.md`).
    serie_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    usuario = relationship("Usuario", back_populates="reservas")
    personal = relationship("Personal", back_populates="reservas")
    espacio = relationship("Espacio", back_populates="reservas")
    recurso = relationship("Recurso", back_populates="reservas")
    notificaciones = relationship("Notificacion", back_populates="reserva", cascade="all, delete-orphan")

    # Fase 12C-6: relaciones aditivas de lectura hacia las tablas de
    # asociación (sin cambio de esquema). `reserva_recursos`/`reserva_zonas`
    # son la fuente de verdad de los conjuntos de la reserva; la columna
    # histórica `recurso_id` se conserva como ancla temporal (12C-4e).
    # `foreign_keys` es necesario porque ambas asociaciones tienen dos FK.
    # `cascade="all, delete-orphan"` + `passive_deletes=True`: mismo patrón
    # que `acompanantes` más abajo. Bug real encontrado y corregido
    # (2026-08-29): sin el `cascade`, `passive_deletes=True` solo no
    # alcanza para evitar que SQLAlchemy intente poner `reserva_id=NULL`
    # en las filas asociadas al borrar una `Reserva` -- revienta con
    # `NotNullViolation` porque esa columna es NOT NULL. Nunca se detectó
    # antes porque ningún test ejercitaba `DELETE /reservas/{id}` sobre
    # una reserva con recursos/zonas asociados. La FK real ya tenía
    # `ondelete="CASCADE"` desde siempre (ver `ReservaRecurso`/
    # `ReservaZona`); esto solo alinea el cascade de la ORM con lo que la
    # base de datos ya hacía.
    recursos_asociados = relationship(
        "ReservaRecurso",
        foreign_keys="ReservaRecurso.reserva_id",
        uselist=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="reserva",
    )
    zonas_asociadas = relationship(
        "ReservaZona",
        foreign_keys="ReservaZona.reserva_id",
        uselist=True,
        cascade="all, delete-orphan",
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
        # Fase B: solo los 2 valores que de verdad llegan por ReservaCreate.
        # ORDEN_SALIDA está en el enum TipoSolicitud pero NO en este CHECK
        # todavía -- se agrega en la Fase C, cuando el servicio empiece a
        # materializar filas reales con ese valor. Sin esto, un bug de
        # ruteo en la Fase C que intentara crear una reserva normal con
        # tipo_solicitud='orden_salida' fallaría en silencio en vez de
        # romper la base de datos.
        CheckConstraint(
            "tipo_solicitud IN ('reserva_en_laboratorio', 'reserva_fuera_laboratorio')",
            name="ck_reservas_tipo_solicitud",
        ),
        Index("ix_reservas_recurso_fecha_estado", "recurso_id", "fecha", "estado"),
        CheckConstraint(
            "(usuario_id IS NOT NULL) != (personal_id IS NOT NULL)",
            name="ck_reservas_actor_unico",
        ),
    )

    @property
    def actor(self):
        """El responsable de la reserva, sea `Usuario` o `Personal` --
        exactamente uno de los dos existe (`ck_reservas_actor_unico`)."""
        return self.usuario or self.personal
