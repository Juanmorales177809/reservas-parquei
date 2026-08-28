from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer, String, Text, func

from app.db import Base


class CorreoSaliente(Base):
    """Outbox de correo saliente (patrón *transactional outbox*).

    Una fila se escribe en la MISMA transacción que la operación de negocio
    que la origina (reserva, alta de usuario, recuperación de contraseña),
    así que nunca queda un correo "prometido" sin la operación real ni al
    revés. El envío efectivo (`app/services/email.py::procesar_pendientes`)
    ocurre DESPUÉS de ese commit y nunca propaga una excepción: un SMTP
    lento o caído no debe bloquear ni revertir la operación que generó el
    correo, solo deja la fila en `pendiente` para el próximo intento.
    """

    __tablename__ = "correo_saliente"

    id = Column(Integer, primary_key=True)
    destinatario = Column(String(255), nullable=False)
    asunto = Column(String(255), nullable=False)
    cuerpo = Column(Text, nullable=False)
    # Plantillas institucionales (ej. invitación de usuario, app/services/
    # email_templates.py) mandan HTML; el resto de las notificaciones
    # (aprobada/rechazada/etc.) siguen en texto plano -- default false
    # conserva ese comportamiento para todas las filas existentes.
    es_html = Column(Boolean, nullable=False, default=False)
    estado = Column(String(20), nullable=False, default="pendiente")
    intentos = Column(Integer, nullable=False, default=0)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    enviado_en = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "estado IN ('pendiente', 'enviado', 'fallido')",
            name="correo_saliente_estado_check",
        ),
    )
