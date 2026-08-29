from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db import Base


class ControlCambio(Base):
    __tablename__ = "control_cambios"

    id = Column(Integer, primary_key=True)
    # Polimórfico, mismo patrón que Reserva/Notificacion -- a diferencia de
    # esas dos, acá SÍ pueden estar las dos columnas en NULL a la vez (el
    # actor pudo haber sido borrado, `ondelete="SET NULL"` ya contemplaba
    # ese caso antes de esta separación).
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    personal_id = Column(Integer, ForeignKey("personal.id", ondelete="SET NULL"), nullable=True, index=True)
    accion = Column(String(20), nullable=False)
    entidad = Column(String(40), nullable=False, index=True)
    entidad_id = Column(Integer, nullable=True)
    descripcion = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    usuario = relationship("Usuario", back_populates="control_cambios")
    personal = relationship("Personal", back_populates="control_cambios")

    __table_args__ = (
        CheckConstraint(
            "usuario_id IS NULL OR personal_id IS NULL",
            name="ck_control_cambios_actor_unico",
        ),
    )

    @property
    def actor(self):
        return self.usuario or self.personal
