from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    rol = Column(String(20), nullable=False, default="usuario")
    # True cuando la contraseña la generó el backend (alta de usuario o
    # recuperación) en vez de elegirla la propia persona -- fuerza el
    # cambio en el primer login. Ver app/api/usuarios.py y
    # app/api/auth.py::cambiar_password.
    debe_cambiar_password = Column(Boolean, nullable=False, default=False)
    # Puente Supabase Auth hybrid: UUID de auth.users (nullable para que
    # SUPABASE_ENABLED=false no rompa el flujo clásico; único cuando no nulo).
    supabase_id = Column(UUID(as_uuid=True), unique=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    reservas = relationship("Reserva", back_populates="usuario", cascade="all, delete-orphan")
    espacios_asignados = relationship("UsuarioEspacio", back_populates="usuario", cascade="all, delete-orphan")
    recursos_creados = relationship("Recurso", foreign_keys="Recurso.created_by")
    recursos_actualizados = relationship("Recurso", foreign_keys="Recurso.update_by")
    notificaciones = relationship("Notificacion", back_populates="usuario", cascade="all, delete-orphan")
    control_cambios = relationship("ControlCambio", back_populates="usuario")

    @property
    def espacio(self):
        return self.espacios_asignados[0].espacio if self.espacios_asignados else None
