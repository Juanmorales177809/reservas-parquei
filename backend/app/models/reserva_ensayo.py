from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint

from app.db import Base


class ReservaEnsayo(Base):
    __tablename__ = "reserva_ensayos"

    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id", ondelete="CASCADE"), nullable=False, index=True)
    ensayo_id = Column(Integer, ForeignKey("ensayos.id"), nullable=False, index=True)

    # Un mismo ensayo no se repite dentro de la misma reserva; el mismo
    # ensayo sí puede aparecer en muchas reservas distintas a lo largo del
    # tiempo. A diferencia de ReservaRecurso/ReservaZona, Ensayo no tiene
    # agenda propia ni constraint EXCLUDE — es solo etiqueta descriptiva.
    __table_args__ = (UniqueConstraint("reserva_id", "ensayo_id", name="uq_reserva_ensayos_par"),)
