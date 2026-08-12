from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud.espacios import create_espacio, get_espacio_by_nombre, update_espacio
from app.db import get_db
from app.deps import get_current_user, get_managed_space_id, require_admin
from app.models import Espacio, Recurso, Reserva, UsuarioEspacio
from app.models.reserva import ESTADOS_BLOQUEANTES
from app.models.usuario import Usuario
from app.schemas.disponibilidad import DisponibilidadSlot
from app.schemas.espacio import (
    ConfiguracionEspacioResponse,
    ConfiguracionEspacioUpdate,
    EspacioCreate,
    EspacioResponse,
    EspacioUpdate,
)
from app.services.auditoria import registrar_cambio
from app.services.horarios import horas_atencion_dia
from app.services.reloj import ahora_local


router = APIRouter(prefix="/espacios", tags=["espacios"])


def _configuracion_response(espacio: Espacio) -> ConfiguracionEspacioResponse:
    return ConfiguracionEspacioResponse(
        espacio_id=espacio.id,
        espacio_nombre=espacio.nombre,
        dias_atencion=espacio.dias_atencion,
        hora_apertura=espacio.hora_apertura,
        hora_cierre=espacio.hora_cierre,
        horario_atencion=espacio.horario_atencion,
        horas_antelacion=espacio.horas_antelacion,
        aprobacion_automatica=espacio.aprobacion_automatica,
    )


@router.get("", response_model=list[EspacioResponse])
def listar_espacios(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """Listar espacios públicos. No requiere autenticación."""
    return db.query(Espacio).order_by(Espacio.nombre.asc()).offset(skip).limit(limit).all()


@router.get("/gestion/configuracion", response_model=ConfiguracionEspacioResponse)
def obtener_configuracion_gestion(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.rol != "gestor":
        raise HTTPException(status_code=403, detail="Solo un gestor puede configurar su espacio")
    espacio_id = get_managed_space_id(db, current_user)
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if espacio is None:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    return _configuracion_response(espacio)


@router.put("/gestion/configuracion", response_model=ConfiguracionEspacioResponse)
def actualizar_configuracion_gestion(
    payload: ConfiguracionEspacioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.rol != "gestor":
        raise HTTPException(status_code=403, detail="Solo un gestor puede configurar su espacio")
    espacio_id = get_managed_space_id(db, current_user)
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if espacio is None:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")

    horario = {str(dia): horas for dia, horas in payload.horario_atencion.items() if horas}
    horas = [hora for horas_dia in horario.values() for hora in horas_dia]
    espacio.horario_atencion = horario
    espacio.dias_atencion = sorted(int(dia) for dia in horario)
    espacio.hora_apertura = time(min(horas), 0)
    espacio.hora_cierre = time(max(horas) + 1, 0)
    espacio.horas_antelacion = payload.horas_antelacion
    espacio.aprobacion_automatica = payload.aprobacion_automatica
    espacio.updated_at = datetime.now(timezone.utc)
    espacio.updated_by = current_user.id
    registrar_cambio(
        db,
        current_user,
        "configurar",
        "espacio",
        espacio.id,
        f"Actualizó las reglas de reserva de {espacio.nombre}",
    )
    db.commit()
    db.refresh(espacio)
    return _configuracion_response(espacio)


@router.get("/{espacio_id}", response_model=EspacioResponse)
def obtener_espacio(
    espacio_id: int,
    db: Session = Depends(get_db),
):
    """Obtener un espacio por ID."""
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if not espacio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Espacio no encontrado",
        )
    return espacio


@router.get("/{espacio_id}/disponibilidad", response_model=list[DisponibilidadSlot])
def obtener_disponibilidad(
    espacio_id: int,
    fecha: date = Query(..., description="Fecha en formato YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    """Obtener disponibilidad horaria de un espacio para una fecha dada. No requiere autenticación."""
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if not espacio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Espacio no encontrado",
        )

    slots: list[DisponibilidadSlot] = []
    fecha_minima = ahora_local() + timedelta(hours=espacio.horas_antelacion)

    for hora in horas_atencion_dia(espacio, fecha.weekday()):
        cursor = datetime.combine(fecha, time(hora, 0))
        siguiente = cursor + timedelta(hours=1)
        slot_inicio = cursor.time()
        slot_fin = siguiente.time()

        if espacio.estado != "activo":
            estado = "mantenimiento"
        elif cursor < fecha_minima:
            continue
        else:
            bloqueantes = db.query(Reserva).filter(
                Reserva.espacio_id == espacio_id,
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


@router.post("", response_model=EspacioResponse, status_code=status.HTTP_201_CREATED)
def crear_espacio(
    payload: EspacioCreate,
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Crear un espacio. Solo admin."""
    if get_espacio_by_nombre(db, payload.nombre) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El nombre del espacio ya existe",
        )
    espacio = create_espacio(db, payload)
    registrar_cambio(db, current_user, "crear", "espacio", espacio.id, f"Creó el espacio {espacio.nombre}")
    db.commit()
    return espacio


@router.put("/{espacio_id}", response_model=EspacioResponse)
def actualizar_espacio(
    espacio_id: int,
    payload: EspacioUpdate,
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Actualizar un espacio. Solo admin."""
    espacio = update_espacio(db, espacio_id, payload)
    if espacio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Espacio no encontrado",
        )
    registrar_cambio(db, current_user, "actualizar", "espacio", espacio.id, f"Actualizó el espacio {espacio.nombre}")
    db.commit()
    return espacio


@router.delete("/{espacio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_espacio(
    espacio_id: int,
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Eliminar un espacio. Solo admin."""
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if not espacio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Espacio no encontrado",
        )
    dependencias = {
        "reservas": db.query(Reserva).filter(Reserva.espacio_id == espacio_id).count(),
        "recursos": db.query(Recurso).filter(Recurso.espacio_id == espacio_id).count(),
        "gestores": db.query(UsuarioEspacio).filter(UsuarioEspacio.espacio_id == espacio_id).count(),
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
                f"No se puede eliminar el espacio porque tiene {detalle}. "
                "Cambia su estado a inactivo para conservar el historial."
            ),
        )
    descripcion = f"Eliminó el espacio {espacio.nombre}"
    db.delete(espacio)
    registrar_cambio(db, current_user, "eliminar", "espacio", espacio_id, descripcion)
    db.commit()
    return None
