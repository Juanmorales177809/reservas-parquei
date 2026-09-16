from sqlalchemy import BigInteger, Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func, text
from sqlalchemy.orm import relationship

from app.db import Base


class Cuenta(Base):
    __tablename__ = "cuentas"
    __table_args__ = (
        CheckConstraint("tipo_cuenta IN ('USUARIO', 'PERSONAL')", name="ck_auth_cuentas_tipo"),
        CheckConstraint(
            "(tipo_cuenta = 'USUARIO' AND id_usuario IS NOT NULL AND id_persona IS NULL) "
            "OR (tipo_cuenta = 'PERSONAL' AND id_persona IS NOT NULL AND id_usuario IS NULL)",
            name="ck_auth_cuentas_identidad",
        ),
        UniqueConstraint("correo", name="uq_auth_cuentas_correo"),
        UniqueConstraint("id_usuario", name="uq_auth_cuentas_usuario"),
        UniqueConstraint("id_persona", name="uq_auth_cuentas_persona"),
        {"schema": "auth"},
    )

    id_cuenta = Column(BigInteger, primary_key=True)
    correo = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    tipo_cuenta = Column(String(20), nullable=False)
    id_usuario = Column(BigInteger, ForeignKey("usuarios.usuarios.id_usuario"), nullable=True)
    id_persona = Column(Integer, ForeignKey("personal.personal.id_persona"), nullable=True)
    estado = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuario = relationship("UsuarioInstitucional")
    persona = relationship("Personal")
    reservas = relationship("Reserva", back_populates="cuenta")
