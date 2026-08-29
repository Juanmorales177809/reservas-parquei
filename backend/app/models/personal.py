from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class Personal(Base):
    """Personal institucional (`admin`/`gestor`) -- separado de `Usuario`
    (rol `usuario`, quien reserva) a pedido explícito del usuario del
    proyecto (2026-08-28, ver `~/.claude/plans/dazzling-wobbling-zebra.md`).

    Mismas columnas de perfil que `Usuario`, sin las columnas vestigiales
    de la migración a Supabase (`hashed_password`, `debe_cambiar_password`)
    -- es una tabla nueva, no hace falta arrastrar ese vestigio.
    """

    __tablename__ = "personal"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    supabase_id = Column(UUID(as_uuid=True), unique=True, nullable=True, index=True)
    rol = Column(String(20), nullable=False)
    documento_identificacion = Column(String(30), nullable=True)
    telefono = Column(String(30), nullable=True)
    institucion = Column(String(120), nullable=True)
    vinculacion = Column(String(30), nullable=True)
    dependencia = Column(String(150), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    espacios_asignados = relationship("UsuarioEspacio", back_populates="personal", cascade="all, delete-orphan")
    recursos_creados = relationship("Recurso", foreign_keys="Recurso.created_by")
    recursos_actualizados = relationship("Recurso", foreign_keys="Recurso.update_by")
    notificaciones = relationship("Notificacion", back_populates="personal")
    control_cambios = relationship("ControlCambio", back_populates="personal")
    reservas = relationship("Reserva", back_populates="personal")

    __table_args__ = (
        CheckConstraint("rol IN ('admin', 'gestor')", name="ck_personal_rol"),
        CheckConstraint(
            "vinculacion IS NULL OR vinculacion IN "
            "('docente', 'estudiante', 'contratista_empleado', 'extension', 'otra')",
            name="ck_personal_vinculacion",
        ),
    )

    @property
    def espacio(self):
        return self.espacios_asignados[0].espacio if self.espacios_asignados else None
