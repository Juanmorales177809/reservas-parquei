from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base


class UsuarioEspacio(Base):
    """Asigna un espacio a un gestor -- pese al nombre (no se renombra la
    tabla/columna para no ampliar más la superficie de la separación
    personal/usuarios, ver `~/.claude/plans/dazzling-wobbling-zebra.md`),
    `usuario_id` apunta a `personal.id`: solo `Personal` (rol `gestor`)
    tiene un espacio asignado, nunca `Usuario`."""

    __tablename__ = "usuarios_espacios"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("personal.id"), nullable=False)
    espacio_id = Column(Integer, ForeignKey("espacios.id"), nullable=False)

    personal = relationship("Personal", back_populates="espacios_asignados")
    espacio = relationship("Espacio", back_populates="gestores")

    __table_args__ = (
        UniqueConstraint("usuario_id", name="uq_usuarios_espacios_usuario"),
    )
