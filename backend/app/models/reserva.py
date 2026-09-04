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
    # `usuario` O `personal` (un gestor reserva su propio laboratorio) --
    # exactamente una de las dos debe estar llena, nunca las dos ni
    # ninguna (`ck_reservas_actor_unico`). Ver `actor` más abajo y
    # `app/services/actores.py::columnas_actor`.
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    personal_id = Column(Integer, ForeignKey("personal.id"), nullable=True, index=True)
    laboratorio_id = Column(Integer, ForeignKey("laboratorios.id"), nullable=False, index=True)
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
    # Fase 7: reemplaza `tipo` como catálogo real por laboratorio (ver
    # app/models/tipo_reserva.py) -- `tipo` se deja intacto, sin backfill ni
    # lectura/escritura de código nuevo (dato histórico inerte, mismo
    # criterio de cautela que `serie_id`/`ensayos` de fases anteriores).
    tipo_reserva_id = Column(Integer, ForeignKey("tipos_reserva.id"), nullable=True)
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
    # backfill de la migración). Distinto de `tipo` (académico) -- ver el
    # docstring de `TipoSolicitud`.
    tipo_solicitud = Column(String(30), nullable=False, default="reserva_en_laboratorio")
    # Fase 2 (motivos en tabla): FK a motivos_solicitud, reemplaza progresivamente
    # el varchar tipo_solicitud hacia adelante. Nullable para filas históricas
    # y para reservas que no declaran motivo.
    motivo_solicitud_id = Column(Integer, ForeignKey("motivos_solicitud.id"), nullable=True)
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
    # Fase C (contrapropuesta): el técnico propone horarios alternativos en
    # vez de rechazar; la reserva queda `esperando` con la propuesta visible
    # y es el usuario quien acepta o contrapropone. Todo nullable: sin
    # propuesta no hay dato que migrar para filas históricas.
    propuesta_motivo = Column(Text, nullable=True)
    propuesta_horarios = Column(Text, nullable=True)
    propuesta_por = Column(String(20), nullable=True)
    propuesta_en = Column(DateTime(timezone=True), nullable=True)
    # Reservas multi-día agrupadas (2026-09-03): correlación neutra de "N
    # reservas creadas juntas en una misma solicitud" -- deliberadamente
    # llamada `grupo_id`, no `serie_id` (ese campo existió y se revirtió a
    # pedido explícito del usuario: repetía la misma franja horaria cada
    # semana, un concepto distinto de este). Nullable: la inmensa mayoría de
    # las reservas no pertenecen a ningún grupo. Sin CheckConstraint -- la
    # coherencia del grupo (mismo actor, mismos recursos/espacios) la
    # garantiza el servicio, no el esquema.
    grupo_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    # Invitación de Outlook Calendar (2026-09-03, rediseño): NO es un id de
    # Microsoft Graph (el plan original -- API de eventos -- quedó
    # bloqueado por política de admin del tenant del ITM, ver
    # `backend/CLAUDE.md`). Es el `UID` (RFC 5545) del `.ics` de invitación
    # que ya se mandó por correo (`services/calendario.py`) -- se completa
    # sincrónicamente al encolar la primera invitación (mandar un correo no
    # puede fallar por causas externas como sí podía una llamada HTTP a
    # Graph, no hace falta esperar a que se procese). `null` mientras la
    # reserva nunca se aprobó. El nombre de la columna quedó igual que en
    # el diseño original a propósito -- no tiene datos reales en ningún
    # entorno todavía, pero renombrarla exigiría una migración sin
    # beneficio funcional.
    graph_event_id = Column(String(255), nullable=True)
    # Contador de revisiones de esa invitación (`SEQUENCE` de RFC 5545) --
    # se incrementa cada vez que se reprograma o cancela, para que el
    # cliente de correo del destinatario reconozca una actualización del
    # mismo evento (mismo UID) en vez de confundirlo con uno nuevo.
    calendario_secuencia = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    usuario = relationship("Usuario", back_populates="reservas")
    personal = relationship("Personal", back_populates="reservas")
    laboratorio = relationship("Laboratorio", back_populates="reservas")
    recurso = relationship("Recurso", back_populates="reservas")
    tipo_reserva = relationship("TipoReserva")
    motivo_solicitud = relationship("MotivoSolicitud")
    notificaciones = relationship("Notificacion", back_populates="reserva", cascade="all, delete-orphan")

    # Fase 12C-6: relaciones aditivas de lectura hacia las tablas de
    # asociación (sin cambio de esquema). `reserva_recursos`/`reserva_espacios`
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
    # una reserva con recursos/espacios asociados. La FK real ya tenía
    # `ondelete="CASCADE"` desde siempre (ver `ReservaRecurso`/
    # `ReservaEspacio`); esto solo alinea el cascade de la ORM con lo que la
    # base de datos ya hacía.
    recursos_asociados = relationship(
        "ReservaRecurso",
        foreign_keys="ReservaRecurso.reserva_id",
        uselist=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="reserva",
    )
    espacios_asociados = relationship(
        "ReservaEspacio",
        foreign_keys="ReservaEspacio.reserva_id",
        uselist=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="reserva",
    )
    espacios = relationship(
        "Espacio",
        secondary="reserva_espacios",
        primaryjoin="Reserva.id == ReservaEspacio.reserva_id",
        secondaryjoin="ReservaEspacio.espacio_id == Espacio.id",
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
        CheckConstraint("propuesta_por IS NULL OR propuesta_por IN ('tecnico', 'usuario')", name="ck_reservas_propuesta_por"),
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
