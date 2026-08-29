from sqlalchemy import CheckConstraint, Column, Date, DateTime, ForeignKey, Integer, String, Time, func
from sqlalchemy.orm import relationship

from app.db import Base


class ListaEspera(Base):
    """Cola de espera para un recurso/horario ya ocupado (2026-08-29). Solo
    a nivel de `recurso_id` -- mismo nivel que la constraint de solapamiento
    principal de `reservas` (`reservas_sin_solapamiento`), donde "se liberó
    un cupo" tiene un significado inequívoco. Ver
    `app/services/lista_espera.py::notificar_primero_en_espera`."""

    __tablename__ = "lista_espera"

    id = Column(Integer, primary_key=True)
    # Polimórfico, mismo patrón que Reserva.usuario_id/personal_id: un
    # gestor también puede anotarse a la lista de espera de un recurso que
    # no gestiona.
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True)
    personal_id = Column(Integer, ForeignKey("personal.id", ondelete="CASCADE"), nullable=True)
    recurso_id = Column(Integer, ForeignKey("recursos.id", ondelete="CASCADE"), nullable=False, index=True)
    fecha = Column(Date, nullable=False, index=True)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    estado = Column(String(20), nullable=False, default="activa")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuario = relationship("Usuario")
    personal = relationship("Personal")
    recurso = relationship("Recurso")

    __table_args__ = (
        CheckConstraint("estado IN ('activa', 'notificada', 'cancelada')", name="ck_lista_espera_estado"),
        CheckConstraint("hora_inicio < hora_fin", name="ck_lista_espera_horario_valido"),
        CheckConstraint(
            "(usuario_id IS NOT NULL) != (personal_id IS NOT NULL)",
            name="ck_lista_espera_actor_unico",
        ),
    )

    @property
    def actor(self):
        return self.usuario or self.personal
