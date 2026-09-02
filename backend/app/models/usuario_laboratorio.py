from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base


class UsuarioLaboratorio(Base):
    """Asigna un laboratorio a un gestor -- pese al nombre (no se renombra
    la columna `usuario_id` para no ampliar más la superficie de la
    separación personal/usuarios, ver `~/.claude/plans/dazzling-wobbling-zebra.md`),
    `usuario_id` apunta a `personal.id`: solo `Personal` (rol `gestor`)
    tiene un laboratorio asignado, nunca `Usuario`."""

    __tablename__ = "usuarios_laboratorios"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("personal.id"), nullable=False)
    laboratorio_id = Column(Integer, ForeignKey("laboratorios.id"), nullable=False)

    personal = relationship("Personal", back_populates="laboratorios_asignados")
    laboratorio = relationship("Laboratorio", back_populates="gestores")

    __table_args__ = (
        UniqueConstraint("usuario_id", name="uq_usuarios_laboratorios_usuario"),
    )
