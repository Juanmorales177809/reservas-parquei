from sqlalchemy import Column, Date, ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base


class ReservaEspacio(Base):
    """Asociación Reserva<->Espacio (Fase 12C-4a).

    Mismo criterio que `ReservaRecurso`: columnas de fecha/hora/estado
    desnormalizadas para el futuro `EXCLUDE USING gist` (Fase 12C-4c);
    tabla aislada en esta subfase, sin integración todavía con `Reserva`.

    `espacio_id` tampoco lleva `ondelete="CASCADE"` — un espacio
    referenciado en una reserva no debe poder eliminarse silenciosamente.
    """

    __tablename__ = "reserva_espacios"

    id = Column(Integer, primary_key=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id", ondelete="CASCADE"), nullable=False, index=True)
    espacio_id = Column(Integer, ForeignKey("espacios.id"), nullable=False, index=True)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    estado = Column(String(20), nullable=False)

    # Relaciones unidireccionales a propósito: esta subfase no modifica
    # app/models/reserva.py ni app/models/espacio.py.
    reserva = relationship("Reserva")
    espacio = relationship("Espacio")

    __table_args__ = (
        UniqueConstraint("reserva_id", "espacio_id", name="uq_reserva_espacios_reserva_espacio"),
    )
