from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, func, text

from app.db import Base


class UsuarioInstitucional(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "usuarios"}

    id_usuario = Column(BigInteger, primary_key=True)
    nombre = Column(String(150), nullable=False)
    correo = Column(String(255), nullable=False, unique=True)
    estado = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
