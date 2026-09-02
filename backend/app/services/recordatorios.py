from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.domain.enums import EstadoReserva
from app.domain.protocols import Reloj
from app.models import Reserva
from app.services.email import encolar_correo, procesar_pendientes
from app.services.email_templates import plantilla_recordatorio_reserva
from app.services.reloj import RelojLocal

# Cada cuánto corre el chequeo y con cuánta antelación avisa -- constantes
# simples, no settings de entorno: no hay ningún caso de uso hoy que
# necesite configurarlos por instalación (ver `main.py`, wiring del
# `BackgroundScheduler`).
INTERVALO_MINUTOS = 15
HORAS_ANTES_DEFAULT = 1


def enviar_recordatorios_pendientes(db: Session, *, horas_antes: int = HORAS_ANTES_DEFAULT, reloj: Reloj | None = None) -> int:
    """Encola el recordatorio de cada reserva `aprobada` que empieza dentro
    de las próximas `horas_antes` horas y todavía no lo recibió
    (`Reserva.recordatorio_enviado_en IS NULL`, marca de idempotencia).

    Función pura de servicio, sin conocimiento del scheduler que la llama
    (`app/main.py`) -- testeable directo con un reloj fijo, mismo patrón
    que `services/reservas.py::validar_anticipacion`.
    """
    ahora = (reloj or RelojLocal()).ahora()
    limite = ahora + timedelta(hours=horas_antes)

    candidatas = (
        db.query(Reserva)
        .filter(
            Reserva.estado == EstadoReserva.APROBADA.value,
            Reserva.recordatorio_enviado_en.is_(None),
            Reserva.fecha >= ahora.date(),
            Reserva.fecha <= limite.date(),
        )
        .all()
    )

    enviados = 0
    for reserva in candidatas:
        inicio = datetime.combine(reserva.fecha, reserva.hora_inicio)
        if not (ahora <= inicio <= limite):
            continue
        actor = reserva.actor
        encolar_correo(
            db,
            destinatario=actor.email,
            asunto="Tu reserva empieza pronto",
            cuerpo=plantilla_recordatorio_reserva(
                nombre_saludo=actor.username,
                reserva_id=reserva.id,
                espacio=reserva.laboratorio.nombre,
                fecha=str(reserva.fecha),
                hora_inicio=str(reserva.hora_inicio),
                hora_fin=str(reserva.hora_fin),
            ),
            es_html=True,
        )
        reserva.recordatorio_enviado_en = ahora
        enviados += 1

    if enviados:
        db.commit()
        procesar_pendientes(db)
    return enviados
