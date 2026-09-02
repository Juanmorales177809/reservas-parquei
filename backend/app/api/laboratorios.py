from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud.laboratorios import create_laboratorio, get_laboratorio_by_nombre, update_laboratorio
from app.db import get_db
from app.deps import get_current_user, get_current_user_optional, get_managed_laboratory_id, require_admin
from app.domain.enums import EstadoEntidad, Rol
from app.models import Laboratorio, Personal, Recurso, Reserva, UsuarioLaboratorio
from app.models.reserva import ESTADOS_BLOQUEANTES
from app.models.usuario import Usuario
from app.schemas.disponibilidad import DisponibilidadSlot
from app.schemas.laboratorio import (
    ConfiguracionLaboratorioResponse,
    ConfiguracionLaboratorioUpdate,
    LaboratorioCreate,
    LaboratorioResponse,
    LaboratorioUpdate,
)
from app.services.auditoria import registrar_cambio
from app.services.horarios import horas_atencion_dia
from app.services.reloj import ahora_local


router = APIRouter(prefix="/laboratorios", tags=["laboratorios"])


def _configuracion_response(laboratorio: Laboratorio) -> ConfiguracionLaboratorioResponse:
    return ConfiguracionLaboratorioResponse(
        laboratorio_id=laboratorio.id,
        laboratorio_nombre=laboratorio.nombre,
        dias_atencion=laboratorio.dias_atencion,
        hora_apertura=laboratorio.hora_apertura,
        hora_cierre=laboratorio.hora_cierre,
        horario_atencion=laboratorio.horario_atencion,
        horas_antelacion=laboratorio.horas_antelacion,
        aprobacion_automatica=laboratorio.aprobacion_automatica,
    )


@router.get("", response_model=list[LaboratorioResponse])
def listar_laboratorios(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    usuario: Usuario | None = Depends(get_current_user_optional),
):
    """Listar laboratorios públicos. No requiere autenticación."""
    query = db.query(Laboratorio).order_by(Laboratorio.nombre.asc())
    if usuario is None or usuario.rol == Rol.USUARIO.value:
        query = query.filter(Laboratorio.estado == EstadoEntidad.ACTIVO.value)
    return query.offset(skip).limit(limit).all()


@router.get("/gestion/configuracion", response_model=ConfiguracionLaboratorioResponse)
def obtener_configuracion_gestion(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.rol != "gestor":
        raise HTTPException(status_code=403, detail="Solo un gestor puede configurar su laboratorio")
    laboratorio_id = get_managed_laboratory_id(db, current_user)
    laboratorio = db.query(Laboratorio).filter(Laboratorio.id == laboratorio_id).first()
    if laboratorio is None:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")
    return _configuracion_response(laboratorio)


@router.put("/gestion/configuracion", response_model=ConfiguracionLaboratorioResponse)
def actualizar_configuracion_gestion(
    payload: ConfiguracionLaboratorioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.rol != "gestor":
        raise HTTPException(status_code=403, detail="Solo un gestor puede configurar su laboratorio")
    laboratorio_id = get_managed_laboratory_id(db, current_user)
    laboratorio = db.query(Laboratorio).filter(Laboratorio.id == laboratorio_id).first()
    if laboratorio is None:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")

    horario = {str(dia): horas for dia, horas in payload.horario_atencion.items() if horas}
    horas = [hora for horas_dia in horario.values() for hora in horas_dia]
    laboratorio.horario_atencion = horario
    laboratorio.dias_atencion = sorted(int(dia) for dia in horario)
    laboratorio.hora_apertura = time(min(horas), 0)
    laboratorio.hora_cierre = time(max(horas) + 1, 0)
    laboratorio.horas_antelacion = payload.horas_antelacion
    laboratorio.aprobacion_automatica = payload.aprobacion_automatica
    laboratorio.updated_at = datetime.now(timezone.utc)
    laboratorio.updated_by = current_user.id
    registrar_cambio(
        db,
        current_user,
        "configurar",
        "laboratorio",
        laboratorio.id,
        f"Actualizó las reglas de reserva de {laboratorio.nombre}",
    )
    db.commit()
    db.refresh(laboratorio)
    return _configuracion_response(laboratorio)


@router.get("/{laboratorio_id}", response_model=LaboratorioResponse)
def obtener_laboratorio(
    laboratorio_id: int,
    db: Session = Depends(get_db),
):
    """Obtener un laboratorio por ID."""
    laboratorio = db.query(Laboratorio).filter(Laboratorio.id == laboratorio_id).first()
    if not laboratorio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laboratorio no encontrado",
        )
    return laboratorio


@router.get("/{laboratorio_id}/disponibilidad", response_model=list[DisponibilidadSlot])
def obtener_disponibilidad(
    laboratorio_id: int,
    fecha: date = Query(..., description="Fecha en formato YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    """Obtener disponibilidad horaria de un laboratorio para una fecha dada. No requiere autenticación."""
    laboratorio = db.query(Laboratorio).filter(Laboratorio.id == laboratorio_id).first()
    if not laboratorio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laboratorio no encontrado",
        )

    slots: list[DisponibilidadSlot] = []
    fecha_minima = ahora_local() + timedelta(hours=laboratorio.horas_antelacion)

    for hora in horas_atencion_dia(laboratorio, fecha.weekday()):
        cursor = datetime.combine(fecha, time(hora, 0))
        siguiente = cursor + timedelta(hours=1)
        slot_inicio = cursor.time()
        slot_fin = siguiente.time()

        if laboratorio.estado != "activo":
            estado = "mantenimiento"
        elif cursor < fecha_minima:
            continue
        else:
            bloqueantes = db.query(Reserva).filter(
                Reserva.laboratorio_id == laboratorio_id,
                Reserva.fecha == fecha,
                Reserva.estado.in_(ESTADOS_BLOQUEANTES),
                Reserva.hora_inicio < slot_fin,
                Reserva.hora_fin > slot_inicio,
            ).first()
            estado = "ocupado" if bloqueantes else "libre"

        slots.append(
            DisponibilidadSlot(
                hora_inicio=slot_inicio.strftime("%H:%M"),
                hora_fin=slot_fin.strftime("%H:%M"),
                estado=estado,
            )
        )

    return slots


@router.post("", response_model=LaboratorioResponse, status_code=status.HTTP_201_CREATED)
def crear_laboratorio(
    payload: LaboratorioCreate,
    current_user: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Crear un laboratorio. Solo admin."""
    if get_laboratorio_by_nombre(db, payload.nombre) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El nombre del laboratorio ya existe",
        )
    laboratorio = create_laboratorio(db, payload)
    registrar_cambio(db, current_user, "crear", "laboratorio", laboratorio.id, f"Creó el laboratorio {laboratorio.nombre}")
    db.commit()
    return laboratorio


@router.put("/{laboratorio_id}", response_model=LaboratorioResponse)
def actualizar_laboratorio(
    laboratorio_id: int,
    payload: LaboratorioUpdate,
    current_user: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Actualizar un laboratorio. Solo admin."""
    laboratorio = update_laboratorio(db, laboratorio_id, payload)
    if laboratorio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laboratorio no encontrado",
        )
    registrar_cambio(
        db, current_user, "actualizar", "laboratorio", laboratorio.id, f"Actualizó el laboratorio {laboratorio.nombre}"
    )
    db.commit()
    return laboratorio


@router.delete("/{laboratorio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_laboratorio(
    laboratorio_id: int,
    current_user: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Eliminar un laboratorio. Solo admin."""
    laboratorio = db.query(Laboratorio).filter(Laboratorio.id == laboratorio_id).first()
    if not laboratorio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laboratorio no encontrado",
        )
    dependencias = {
        "reservas": db.query(Reserva).filter(Reserva.laboratorio_id == laboratorio_id).count(),
        "recursos": db.query(Recurso).filter(Recurso.laboratorio_id == laboratorio_id).count(),
        "gestores": db.query(UsuarioLaboratorio).filter(UsuarioLaboratorio.laboratorio_id == laboratorio_id).count(),
    }
    if any(dependencias.values()):
        detalle = ", ".join(
            f"{cantidad} {tipo}"
            for tipo, cantidad in dependencias.items()
            if cantidad
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"No se puede eliminar el laboratorio porque tiene {detalle}. "
                "Cambia su estado a inactivo para conservar el historial."
            ),
        )
    descripcion = f"Eliminó el laboratorio {laboratorio.nombre}"
    db.delete(laboratorio)
    registrar_cambio(db, current_user, "eliminar", "laboratorio", laboratorio_id, descripcion)
    db.commit()
    return None
