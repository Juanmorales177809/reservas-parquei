from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer, String, func
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
    # Vestigial desde la migración completa a Supabase Auth: existía para
    # forzar el cambio de una contraseña temporal propia, que ya no existe
    # (Supabase resuelve el primer cambio con su propio link de invitación).
    # La columna se queda (este proyecto nunca hace DROP COLUMN, ver
    # backend/CLAUDE.md) pero ya no se lee ni se expone en la API.
    debe_cambiar_password = Column(Boolean, nullable=False, default=False)
    # Puente hacia Supabase Auth: UUID de `auth.users`, único mecanismo de
    # identidad de autenticación desde la migración completa (ver
    # app/api/auth.py::supabase_sesion). Nullable en el esquema por
    # compatibilidad con filas viejas, pero toda cuenta nueva lo trae desde
    # el momento en que se crea (app/services/supabase_admin.py) -- nunca
    # queda en null para una cuenta que pueda loguearse.
    supabase_id = Column(UUID(as_uuid=True), unique=True, nullable=True, index=True)
    # Fase A2 (perfil de usuario): datos del formulario real de solicitud
    # de laboratorios del ITM que hoy no existían en ningún lado del
    # sistema. Se completan una vez, en el perfil propio (PUT /usuarios/me),
    # no en cada reserva -- por eso todos son nullable, sin backfill
    # posible para las cuentas ya existentes.
    documento_identificacion = Column(String(30), nullable=True)
    telefono = Column(String(30), nullable=True)
    # Texto libre a propósito, sin CHECK: la lista de facultades/dependencias
    # del ITM puede reestructurarse administrativamente, y un CHECK en base
    # de datos convertiría un simple renombre en una migración.
    institucion = Column(String(120), nullable=True)
    vinculacion = Column(String(30), nullable=True)
    dependencia = Column(String(150), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    reservas = relationship("Reserva", back_populates="usuario", cascade="all, delete-orphan")
    espacios_asignados = relationship("UsuarioEspacio", back_populates="usuario", cascade="all, delete-orphan")
    recursos_creados = relationship("Recurso", foreign_keys="Recurso.created_by")
    recursos_actualizados = relationship("Recurso", foreign_keys="Recurso.update_by")
    notificaciones = relationship("Notificacion", back_populates="usuario", cascade="all, delete-orphan")
    control_cambios = relationship("ControlCambio", back_populates="usuario")

    __table_args__ = (
        CheckConstraint(
            "vinculacion IS NULL OR vinculacion IN "
            "('docente', 'estudiante', 'contratista_empleado', 'extension', 'otra')",
            name="ck_usuarios_vinculacion",
        ),
    )

    @property
    def espacio(self):
        return self.espacios_asignados[0].espacio if self.espacios_asignados else None
