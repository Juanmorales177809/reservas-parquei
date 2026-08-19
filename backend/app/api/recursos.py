from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.crud.reservas import get_reservas_bloqueantes
from app.db import get_db
from app.deps import get_current_user_optional, get_managed_space_id, require_resource_manager
from app.domain.enums import Rol
from app.models import Espacio, Recurso, TipoRecurso, Usuario
from app.models.reserva_recurso import ReservaRecurso
from app.schemas.disponibilidad import DisponibilidadSlot
from app.schemas.recurso import RecursoCreate, RecursoResponse, RecursoUpdate, TipoRecursoResponse
from app.services.auditoria import registrar_cambio
from app.services.horarios import horas_atencion_dia
from app.services.reloj import ahora_local


router = APIRouter(prefix="/recursos", tags=["recursos"])


def _query_recursos(db: Session):
    return db.query(Recurso).options(joinedload(Recurso.espacio), joinedload(Recurso.tipo))


def _puede_ver_ps(usuario: Usuario | None) -> bool:
    """RN-009: solo gestor (laboratorista) y admin (administrador técnico)
    pueden ver/gestionar recursos PS; usuario (investigador) y anónimos,
    no."""
    return usuario is not None and usuario.rol in {Rol.GESTOR.value, Rol.ADMIN.value}


@router.get("", response_model=list[RecursoResponse])
def listar_recursos(
    espacio_id: int | None = None,
    solo_activos: bool = False,
    db: Session = Depends(get_db),
    usuario: Usuario | None = Depends(get_current_user_optional),
):
    query = _query_recursos(db)
    if espacio_id is not None:
        query = query.filter(Recurso.espacio_id == espacio_id)
    if solo_activos:
        query = query.filter(Recurso.estado == "activo")
    if not _puede_ver_ps(usuario):
        query = query.filter(Recurso.es_prestacion_servicio.is_(False))
    return query.order_by(Recurso.nombre.asc()).all()


@router.get("/tipos", response_model=list[TipoRecursoResponse])
def listar_tipos_recursos(db: Session = Depends(get_db)):
    return db.query(TipoRecurso).filter(TipoRecurso.activo == "activo").order_by(TipoRecurso.nombre).all()


@router.get("/gestion", response_model=list[RecursoResponse])
def listar_recursos_gestion(
    current_user: Usuario = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    espacio_id = get_managed_space_id(db, current_user)
    query = _query_recursos(db)
    if espacio_id is not None:
        query = query.filter(Recurso.espacio_id == espacio_id)
    return query.order_by(Recurso.nombre.asc()).all()


@router.get("/{recurso_id}/disponibilidad", response_model=list[DisponibilidadSlot])
def obtener_disponibilidad_recurso(
    recurso_id: int,
    fecha: date = Query(...),
    db: Session = Depends(get_db),
    usuario: Usuario | None = Depends(get_current_user_optional),
):
    recurso = _query_recursos(db).filter(Recurso.id == recurso_id).first()
    if recurso is None:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    if recurso.es_prestacion_servicio and not _puede_ver_ps(usuario):
        raise HTTPException(status_code=403, detail="No tienes permisos para consultar este recurso")

    espacio = recurso.espacio
    slots = []
    fecha_minima = ahora_local() + timedelta(hours=espacio.horas_antelacion)

    for hora in horas_atencion_dia(espacio, fecha.weekday()):
        cursor = datetime.combine(fecha, time(hora, 0))
        siguiente = cursor + timedelta(hours=1)
        inicio, fin = cursor.time(), siguiente.time()
        if recurso.estado != "activo" or espacio.estado != "activo":
            estado_slot = "mantenimiento"
        elif cursor < fecha_minima:
            continue
        else:
            bloqueantes = get_reservas_bloqueantes(db, recurso.id, fecha, inicio, fin)
            estado_slot = "ocupado" if bloqueantes else "libre"
        slots.append(DisponibilidadSlot(
            hora_inicio=inicio.strftime("%H:%M"),
            hora_fin=fin.strftime("%H:%M"),
            estado=estado_slot,
        ))
    return slots


@router.post("", response_model=RecursoResponse, status_code=status.HTTP_201_CREATED)
def crear_recurso(
    payload: RecursoCreate,
    current_user: Usuario = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    espacio_gestionado = get_managed_space_id(db, current_user)
    espacio_id = espacio_gestionado if espacio_gestionado is not None else payload.espacio_id
    if espacio_id is None:
        raise HTTPException(status_code=400, detail="Debes indicar el espacio del recurso")
    if db.query(Espacio).filter(Espacio.id == espacio_id).first() is None:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    if db.query(TipoRecurso).filter(TipoRecurso.id == payload.tipo_recurso_id).first() is None:
        raise HTTPException(status_code=404, detail="Tipo de recurso no encontrado")

    recurso = Recurso(
        nombre=payload.nombre,
        espacio_id=espacio_id,
        tipo_recurso_id=payload.tipo_recurso_id,
        descripcion=payload.descripcion,
        capacidad=payload.capacidad,
        estado=payload.estado,
        created_by=current_user.id,
        update_by=current_user.id,
        es_prestacion_servicio=payload.es_prestacion_servicio,
    )
    db.add(recurso)
    db.flush()
    registrar_cambio(db, current_user, "crear", "recurso", recurso.id, f"Creó el recurso {recurso.nombre}")
    db.commit()
    return _query_recursos(db).filter(Recurso.id == recurso.id).one()


def _recurso_tiene_reservas(db: Session, recurso_id: int) -> bool:
    """Fase 12C-4e-lectores: un recurso no puede moverse/eliminarse si tiene
    reservas. Consulta únicamente `reserva_recursos` (fuente de verdad de los
    conjuntos: incluye recursos reclamados por reservas de zona que no son el
    ancla) -- ya no cae de vuelta a la columna histórica `Reserva.recurso_id`.

    Caso límite: el recurso "ancla" de una reserva de zona SIN recursos
    asociados no tiene fila en `reserva_recursos` y este guard no lo detecta;
    `reservas.recurso_id` sigue siendo NOT NULL con FK real (sin retirar en
    esta subfase), así que ese caso lo sigue bloqueando la base de datos
    misma -- ver el `except IntegrityError` en `eliminar_recurso`."""
    return db.query(ReservaRecurso).filter(ReservaRecurso.recurso_id == recurso_id).first() is not None


@router.put("/{recurso_id}", response_model=RecursoResponse)
def actualizar_recurso(
    recurso_id: int,
    payload: RecursoUpdate,
    current_user: Usuario = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    recurso = db.query(Recurso).filter(Recurso.id == recurso_id).first()
    if recurso is None:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    espacio_gestionado = get_managed_space_id(db, current_user)
    if espacio_gestionado is not None and recurso.espacio_id != espacio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar recursos de tu espacio")

    cambios = payload.model_dump(exclude_unset=True)
    if espacio_gestionado is not None:
        cambios.pop("espacio_id", None)
    nuevo_espacio_id = cambios.get("espacio_id", recurso.espacio_id)
    nuevo_tipo_id = cambios.get("tipo_recurso_id", recurso.tipo_recurso_id)
    if db.query(Espacio).filter(Espacio.id == nuevo_espacio_id).first() is None:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    if db.query(TipoRecurso).filter(TipoRecurso.id == nuevo_tipo_id).first() is None:
        raise HTTPException(status_code=404, detail="Tipo de recurso no encontrado")
    if nuevo_espacio_id != recurso.espacio_id and _recurso_tiene_reservas(db, recurso.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede mover un recurso con reservas a otro espacio",
        )
    for campo, valor in cambios.items():
        setattr(recurso, campo, valor)
    recurso.update_by = current_user.id
    registrar_cambio(db, current_user, "actualizar", "recurso", recurso.id, f"Actualizó el recurso {recurso.nombre}")
    db.commit()
    return _query_recursos(db).filter(Recurso.id == recurso.id).one()


@router.delete("/{recurso_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_recurso(
    recurso_id: int,
    current_user: Usuario = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    recurso = db.query(Recurso).filter(Recurso.id == recurso_id).first()
    if recurso is None:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    espacio_gestionado = get_managed_space_id(db, current_user)
    if espacio_gestionado is not None and recurso.espacio_id != espacio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar recursos de tu espacio")
    if _recurso_tiene_reservas(db, recurso.id):
        raise HTTPException(status_code=409, detail="No se puede eliminar un recurso con reservas")
    descripcion = f"Eliminó el recurso {recurso.nombre}"
    db.delete(recurso)
    registrar_cambio(db, current_user, "eliminar", "recurso", recurso_id, descripcion)
    try:
        db.commit()
    except IntegrityError:
        # Fase 12C-4e-lectores: el guard de arriba ya no detecta el recurso
        # "ancla" de una zona sin recursos (ver `_recurso_tiene_reservas`);
        # para ese caso límite, `reservas.recurso_id` (FK real, NOT NULL, sin
        # retirar en esta subfase) sigue rechazando el borrado a nivel de
        # base de datos. Se traduce a 409 en vez de dejarlo escapar como 500.
        db.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar un recurso con reservas")
    return None
