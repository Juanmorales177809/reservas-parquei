from collections import Counter
from math import ceil

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_managed_space_id, require_admin, require_resource_manager
from app.domain.valor import HorarioAtencion
from app.models import Espacio, Recurso, Reserva, ReservaRecurso, Usuario
from app.models.reserva import ESTADOS_BLOQUEANTES
from app.schemas.admin_dashboard import AdminDashboardSummary
from app.services.horarios import horas_atencion_dia


router = APIRouter(prefix="/admin/dashboard", tags=["admin-dashboard"])
gestion_router = APIRouter(prefix="/gestion/dashboard", tags=["gestion-dashboard"])

DIAS = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo")


def _construir_resumen(db: Session, espacio_id: int | None) -> dict:
    reservas_query = db.query(Reserva)
    recursos_query = db.query(Recurso)
    if espacio_id is not None:
        reservas_query = reservas_query.filter(Reserva.espacio_id == espacio_id)
        recursos_query = recursos_query.filter(Recurso.espacio_id == espacio_id)

    estados = dict(
        reservas_query.with_entities(Reserva.estado, func.count(Reserva.id))
        .group_by(Reserva.estado)
        .all()
    )

    reservas_por_fecha = [
        {"fecha": fecha, "cantidad": cantidad}
        for fecha, cantidad in (
            reservas_query.with_entities(Reserva.fecha, func.count(Reserva.id))
            .group_by(Reserva.fecha)
            .order_by(Reserva.fecha.asc())
            .all()
        )
    ]

    reservas_por_espacio_query = (
        db.query(Espacio.id, Espacio.nombre, func.count(Reserva.id).label("cantidad"))
        .join(Reserva, Reserva.espacio_id == Espacio.id)
    )
    if espacio_id is not None:
        reservas_por_espacio_query = reservas_por_espacio_query.filter(Espacio.id == espacio_id)
    reservas_por_espacio = [
        {"espacio_id": item_id, "nombre": nombre, "cantidad": cantidad}
        for item_id, nombre, cantidad in (
            reservas_por_espacio_query
            .group_by(Espacio.id, Espacio.nombre)
            .order_by(func.count(Reserva.id).desc(), Espacio.nombre.asc())
            .all()
        )
    ]

    # Fase 12C-6: "el dashboard cuenta por recurso" -> JOIN contra
    # `reserva_recursos` (los recursos efectivos materializados), no contra la
    # columna histórica `Reserva.recurso_id`. Una reserva de zona con N
    # recursos efectivos cuenta N veces (cada fila reclamada).
    recursos_mas_reservados_query = (
        db.query(Recurso.id, Recurso.nombre, func.count(ReservaRecurso.id).label("cantidad"))
        .join(ReservaRecurso, ReservaRecurso.recurso_id == Recurso.id)
    )
    if espacio_id is not None:
        recursos_mas_reservados_query = recursos_mas_reservados_query.filter(Recurso.espacio_id == espacio_id)
    recursos_mas_reservados = [
        {"recurso_id": recurso_id, "nombre": nombre, "cantidad": cantidad}
        for recurso_id, nombre, cantidad in (
            recursos_mas_reservados_query
            .group_by(Recurso.id, Recurso.nombre)
            .order_by(func.count(ReservaRecurso.id).desc(), Recurso.nombre.asc())
            .limit(5)
            .all()
        )
    ]

    ocupacion = Counter()
    reservas_bloqueantes = (
        reservas_query.with_entities(
            Reserva.espacio_id, Reserva.fecha, Reserva.hora_inicio, Reserva.hora_fin
        )
        .filter(Reserva.estado.in_(ESTADOS_BLOQUEANTES))
        .all()
    )

    # Horario real por espacio (fuente única del dominio). Un horario vacío o
    # inválido no aporta horas habilitadas (dato legacy, no error funcional).
    horarios_por_espacio: dict[int, HorarioAtencion | None] = {}
    for espacio_id, horario in db.query(Espacio.id, Espacio.horario_atencion).all():
        try:
            horarios_por_espacio[espacio_id] = HorarioAtencion(horario or {})
        except ValueError:
            horarios_por_espacio[espacio_id] = None

    for espacio_id, fecha, hora_inicio, hora_fin in reservas_bloqueantes:
        horario = horarios_por_espacio.get(espacio_id)
        habilitadas = (
            set(horario.horas_del_dia(fecha.weekday())) if horario is not None else set()
        )
        # El grid del heatmap conserva el rango 7..19 del contrato del gráfico;
        # las horas atendidas fuera de ese rango se cuentan igualmente en
        # ocupacion_global aunque el gráfico no las muestre.
        inicio = max(7, hora_inicio.hour)
        fin = min(20, ceil(hora_fin.hour + hora_fin.minute / 60))
        for hora in range(inicio, fin):
            if hora in habilitadas:
                ocupacion[(fecha.weekday(), hora)] += 1

    ocupacion_por_dia_hora = [
        {
            "dia": DIAS[dia],
            "dia_orden": dia,
            "hora": hora,
            "cantidad": ocupacion[(dia, hora)],
        }
        for dia in range(7)
        for hora in range(7, 20)
    ]

    recursos_activos = (
        recursos_query
        .filter(Recurso.estado == "activo")
        .all()
    )
    fechas_con_ocupacion = {fecha for _, fecha, _, _ in reservas_bloqueantes}

    # Horas ocupadas según el horario real de cada espacio (no un rango fijo).
    horas_ocupadas = 0.0
    for espacio_id, fecha, hora_inicio, hora_fin in reservas_bloqueantes:
        horario = horarios_por_espacio.get(espacio_id)
        habilitadas = (
            set(horario.horas_del_dia(fecha.weekday())) if horario is not None else set()
        )
        horas_ocupadas += sum(
            1
            for hora in range(hora_inicio.hour, ceil(hora_fin.hour + hora_fin.minute / 60))
            if hora in habilitadas
        )
    horas_disponibles = 0.0
    for fecha in fechas_con_ocupacion:
        for recurso in recursos_activos:
            espacio_recurso = recurso.espacio
            if espacio_recurso.estado == "activo":
                horas_disponibles += len(horas_atencion_dia(espacio_recurso, fecha.weekday()))
    porcentaje_ocupacion = (
        round((horas_ocupadas / horas_disponibles) * 100, 2)
        if horas_disponibles > 0
        else 0
    )

    total_reservas = sum(estados.values())
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first() if espacio_id is not None else None
    return {
        "total_reservas": total_reservas,
        "reservas_pendientes": estados.get("esperando", 0),
        "recursos_activos": len(recursos_activos),
        "usuarios": db.query(Usuario).count(),
        "espacio_nombre": espacio.nombre if espacio else None,
        "reservas_por_estado": {
            "pendientes": estados.get("esperando", 0),
            "aprobadas": estados.get("aprobada", 0),
            "rechazadas": estados.get("rechazada", 0),
            "canceladas": estados.get("cancelada", 0),
        },
        "reservas_por_fecha": reservas_por_fecha,
        "reservas_por_espacio": reservas_por_espacio,
        "recursos_mas_reservados": recursos_mas_reservados,
        "ocupacion_por_dia_hora": ocupacion_por_dia_hora,
        "ocupacion_global": {
            "horas_ocupadas": round(horas_ocupadas, 2),
            "horas_disponibles": round(horas_disponibles, 2),
            "porcentaje": porcentaje_ocupacion,
        },
    }


@router.get("/summary", response_model=AdminDashboardSummary)
def obtener_resumen_dashboard_admin(
    _: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Resumen global de reservas de recursos para todos los espacios."""
    return _construir_resumen(db, espacio_id=None)


@gestion_router.get("/summary", response_model=AdminDashboardSummary)
def obtener_resumen_dashboard_gestor(
    current_user: Usuario = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    espacio_id = get_managed_space_id(db, current_user)
    return _construir_resumen(db, espacio_id=espacio_id)
