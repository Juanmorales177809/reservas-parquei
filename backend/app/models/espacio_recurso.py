from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base


class EspacioRecurso(Base):
    """Asociacion N:N tecnica Espacio<->Recurso (Fase 12C-3).

    `UniqueConstraint` sobre `recurso_id` solo (no sobre el par
    espacio_id+recurso_id): impone la unicidad funcional aprobada -- un
    recurso pertenece, como maximo, a un espacio -- mismo patron ya usado
    por `UsuarioLaboratorio.uq_usuarios_laboratorios_usuario` para "un
    gestor administra, como maximo, un laboratorio".
    """

    __tablename__ = "espacio_recursos"

    id = Column(Integer, primary_key=True)
    espacio_id = Column(Integer, ForeignKey("espacios.id", ondelete="CASCADE"), nullable=False, index=True)
    recurso_id = Column(Integer, ForeignKey("recursos.id", ondelete="CASCADE"), nullable=False)

    # Relaciones unidireccionales a proposito: esta subfase no modifica
    # app/models/espacio.py ni app/models/recurso.py (fuera de alcance).
    espacio = relationship("Espacio")
    recurso = relationship("Recurso")

    __table_args__ = (
        UniqueConstraint("recurso_id", name="uq_espacio_recursos_recurso"),
    )
