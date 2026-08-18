from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base


class ZonaRecurso(Base):
    """Asociacion N:N tecnica Zona<->Recurso (Fase 12C-3).

    `UniqueConstraint` sobre `recurso_id` solo (no sobre el par
    zona_id+recurso_id): impone la unicidad funcional aprobada -- un
    recurso pertenece, como maximo, a una zona -- mismo patron ya usado
    por `UsuarioEspacio.uq_usuarios_espacios_usuario` para "un gestor
    administra, como maximo, un espacio".
    """

    __tablename__ = "zona_recursos"

    id = Column(Integer, primary_key=True)
    zona_id = Column(Integer, ForeignKey("zonas.id", ondelete="CASCADE"), nullable=False, index=True)
    recurso_id = Column(Integer, ForeignKey("recursos.id", ondelete="CASCADE"), nullable=False)

    # Relaciones unidireccionales a proposito: esta subfase no modifica
    # app/models/zona.py ni app/models/recurso.py (fuera de alcance).
    zona = relationship("Zona")
    recurso = relationship("Recurso")

    __table_args__ = (
        UniqueConstraint("recurso_id", name="uq_zona_recursos_recurso"),
    )
