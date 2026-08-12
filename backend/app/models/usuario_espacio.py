from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base


class UsuarioEspacio(Base):
    __tablename__ = "usuarios_espacios"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    espacio_id = Column(Integer, ForeignKey("espacios.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="espacios_asignados")
    espacio = relationship("Espacio", back_populates="gestores")

    __table_args__ = (
        UniqueConstraint("usuario_id", name="uq_usuarios_espacios_usuario"),
    )
