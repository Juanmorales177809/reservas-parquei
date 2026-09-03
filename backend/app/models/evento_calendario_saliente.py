from sqlalchemy import JSON, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db import Base


class EventoCalendarioSaliente(Base):
    """Outbox de eventos de Outlook Calendar (invitación vía Microsoft
    Graph, 2026-09-03) -- mismo patrón *transactional outbox* que
    `CorreoSaliente` (ver `app/services/email.py`), pero para
    `app/services/calendario.py::procesar_eventos_calendario_pendientes`.

    Deliberadamente diferido, no síncrono dentro de la request que aprueba
    la reserva: a diferencia del `.ics` (bytes en memoria, nunca falla por
    red), crear un evento de Graph es la primera llamada HTTP real en vivo
    de este tipo en el proyecto -- un timeout de Graph no debe alargar ni
    poder tumbar una aprobación.

    Tabla nueva sin datos que migrar -- `Base.metadata.create_all` ya la
    crea sola (mismo criterio que `lista_espera`/`tipos_reserva`), sin
    entrada en `migrations.py`.
    """

    __tablename__ = "evento_calendario_saliente"

    id = Column(Integer, primary_key=True)
    # Nullable a propósito (no solo por prolijidad): al eliminar una reserva
    # con evento ya creado (`services/reservas.py::eliminar_reserva`), la
    # fila `cancelar` que avisa a Graph tiene que SOBREVIVIR al `DELETE` de
    # la reserva que la originó -- si llevara el `reserva_id` real, el
    # `ondelete="CASCADE"` de abajo se la llevaría puesta en la misma
    # transacción (el cascade actúa sobre el estado referencial en el
    # momento del DELETE, no importa si la fila se insertó antes). Por eso
    # ese único caso encola con `reserva_id=None` -- el resto (crear/
    # actualizar/cancelar por cambio de estado, sin DELETE de por medio)
    # sigue mandando el id real, y si esa reserva se borrara más tarde con
    # la fila todavía pendiente, el cascade sí debe limpiarla (ya no hay
    # nada que crear/actualizar/cancelar para una reserva que no existe).
    reserva_id = Column(Integer, ForeignKey("reservas.id", ondelete="CASCADE"), nullable=True, index=True)
    accion = Column(String(20), nullable=False)
    estado = Column(String(20), nullable=False, default="pendiente")
    intentos = Column(Integer, nullable=False, default=0)
    # Ya conocido al encolar `actualizar`/`cancelar` (viene de
    # `Reserva.graph_event_id`); se completa acá para `crear` recién cuando
    # el procesador tiene éxito -- ahí también se copia a
    # `Reserva.graph_event_id`.
    graph_event_id = Column(String(255), nullable=True)
    # Datos para reconstruir el payload de Graph -- todos nullable porque
    # `actualizar`/`cancelar` no necesitan todos (ver
    # `services/calendario.py::encolar_evento_calendario`).
    asunto = Column(String(255), nullable=True)
    cuerpo = Column(Text, nullable=True)
    ubicacion = Column(String(255), nullable=True)
    inicio = Column(DateTime(timezone=True), nullable=True)
    fin = Column(DateTime(timezone=True), nullable=True)
    # Lista de pares [email, nombre] -- mismo criterio que el resto del
    # proyecto para listas chicas sin tabla propia (ver `dias_atencion`).
    asistentes = Column(JSON, nullable=True)
    comentario = Column(Text, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    procesado_en = Column(DateTime(timezone=True), nullable=True)

    reserva = relationship("Reserva", overlaps="eventos_calendario")

    __table_args__ = (
        CheckConstraint(
            "accion IN ('crear', 'actualizar', 'cancelar')",
            name="ck_evento_calendario_saliente_accion",
        ),
        CheckConstraint(
            "estado IN ('pendiente', 'enviado', 'fallido')",
            name="ck_evento_calendario_saliente_estado",
        ),
    )
