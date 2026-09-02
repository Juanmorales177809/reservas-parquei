from sqlalchemy import Column, Date, ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base


class ReservaRecurso(Base):
    """Asociación Reserva<->Recurso (Fase 12C-4a).

    `fecha`/`hora_inicio`/`hora_fin`/`estado` se desnormalizan desde
    `Reserva` a propósito: un `EXCLUDE USING gist` de PostgreSQL (Fase
    12C-4c) no puede indexar a través de un JOIN — mismo motivo
    estructural por el que `reservas_sin_solapamiento` vive hoy sobre
    `reservas` y no sobre una tabla separada.

    Esta subfase deja la tabla aislada: creable y consultable, sin
    backfill, sin escritura desde `services/reservas.py` y sin ningún
    cambio en `Reserva.recurso_id` (que sigue siendo la única fuente de
    verdad hasta 12C-4b en adelante).

    `recurso_id` no lleva `ondelete="CASCADE"` (a diferencia de
    `espacio_id`/`recurso_id` en `EspacioRecurso`, Fase 12C-3): un recurso ya
    referenciado en una reserva no debe poder eliminarse silenciosamente
    a nivel de base de datos — mismo criterio de fondo que ya aplica
    `eliminar_recurso` con su guard de "no se puede eliminar un recurso
    con reservas", aquí reforzado por la propia FK.
    """

    __tablename__ = "reserva_recursos"

    id = Column(Integer, primary_key=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id", ondelete="CASCADE"), nullable=False, index=True)
    recurso_id = Column(Integer, ForeignKey("recursos.id"), nullable=False, index=True)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    estado = Column(String(20), nullable=False)

    # Relaciones unidireccionales a propósito: esta subfase no modifica
    # app/models/reserva.py ni app/models/recurso.py (fuera de alcance).
    reserva = relationship("Reserva")
    recurso = relationship("Recurso")

    __table_args__ = (
        UniqueConstraint("reserva_id", "recurso_id", name="uq_reserva_recursos_reserva_recurso"),
    )
