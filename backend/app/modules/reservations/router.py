"""Router de reservations (API-13): `/api/reservas` §2 y §3.

Crear y consultar reservas propias no exige permiso administrativo
(contrato §1): el router solo exige sesión. El ámbito de lectura/edición lo
resuelve el servicio con `policies.acceso`, no `exigir_permiso_dep`.
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, File, Form, Request, Response, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import ContextoAutenticado, obtener_contexto
from app.core.errors import SolicitudInvalida
from app.core.pagination import envolver_catalogo, envolver_listado, paginacion_para
from app.core.security import exigir_csrf
from app.db.session import get_db
from app.modules.reservations import schemas, service

router = APIRouter(prefix="/api/reservas", tags=["reservas"])

_FILTROS_LISTADO = frozenset({"estado", "tipo_reserva", "id_unidad", "desde", "hasta", "espacio_id", "recurso_id"})
_ORDENES_LISTADO = frozenset({"created_at", "fecha", "estado"})


def _entero(request: Request, nombre: str) -> int | None:
    v = request.query_params.get(nombre)
    if v is None:
        return None
    try:
        return int(v)
    except ValueError:
        raise SolicitudInvalida(f"'{nombre}' debe ser un entero.")


@router.post("", status_code=201, response_model=schemas.ReservaResumen)
def crear_reserva(
    cuerpo: schemas.ReservaCrear,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.ReservaResumen:
    """§2.1. Cabecera, detalle, asignaciones, contexto y campos en una sola transacción."""
    return schemas.ReservaResumen(**service.crear_reserva(db, cuerpo, contexto))


@router.get("/tipos", response_model=dict)
def tipos_habilitados(
    id_unidad: int,
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> dict:
    """§2.2. Catálogo cerrado, sin paginación."""
    return envolver_catalogo(service.tipos_habilitados(db, id_unidad))


@router.get("", response_model=dict)
def listar_reservas(
    request: Request,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    pag=Depends(paginacion_para(filtros_admitidos=_FILTROS_LISTADO, ordenes_admitidos=_ORDENES_LISTADO)),
) -> dict:
    """§3.1. El ámbito lo determina el rol: Usuario ve lo suyo, Técnico su unidad, Administrador cualquiera."""
    filtros = {
        "estado": request.query_params.get("estado"),
        "tipo_reserva": request.query_params.get("tipo_reserva"),
        "id_unidad": _entero(request, "id_unidad"),
        "desde": request.query_params.get("desde"),
        "hasta": request.query_params.get("hasta"),
        "espacio_id": _entero(request, "espacio_id"),
        "recurso_id": _entero(request, "recurso_id"),
    }
    datos, total = service.listar_reservas(db, filtros, pag.pagina, pag.tamano, pag.orden, contexto)
    return envolver_listado(
        [schemas.ReservaListItem(**d).model_dump(mode="json") for d in datos],
        pagina=pag.pagina, tamano=pag.tamano, total=total,
    )


@router.get("/disponibilidad", response_model=schemas.DisponibilidadRespuesta)
def consultar_disponibilidad(
    request: Request,
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> schemas.DisponibilidadRespuesta:
    """§3.3. Solo consulta: no reserva ni garantiza nada."""
    id_unidad = _entero(request, "id_unidad")
    if id_unidad is None:
        raise SolicitudInvalida("id_unidad es obligatorio.")
    desde = request.query_params.get("desde")
    hasta = request.query_params.get("hasta")
    if not desde or not hasta:
        raise SolicitudInvalida("desde y hasta son obligatorios.")
    return schemas.DisponibilidadRespuesta(**service.consultar_disponibilidad(
        db, id_unidad=id_unidad, espacio_id=_entero(request, "espacio_id"), recurso_id=_entero(request, "recurso_id"),
        desde=date.fromisoformat(desde), hasta=date.fromisoformat(hasta),
    ))


@router.get("/{id_reserva}", response_model=schemas.ReservaDetalleRespuesta)
def detalle_reserva(
    id_reserva: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> schemas.ReservaDetalleRespuesta:
    """§3.2. Fuera del ámbito del actor: `404`, sin revelar existencia."""
    return schemas.ReservaDetalleRespuesta(**service.obtener_reserva_detalle(db, id_reserva, contexto))


@router.put("/{id_reserva}/lista-espera/formulario", response_model=schemas.FormularioRespuesta)
def diligenciar_formulario(
    id_reserva: int,
    cuerpo: schemas.FormularioParteCuerpo,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.FormularioRespuesta:
    """§2.3. Exactamente una parte por petición; la reserva permanece SOLICITADA."""
    return schemas.FormularioRespuesta(**service.diligenciar_formulario(db, id_reserva, cuerpo, contexto))


@router.post("/{id_reserva}/lista-espera/viabilidad", response_model=schemas.ViabilidadRespuesta)
def registrar_viabilidad(
    id_reserva: int,
    cuerpo: schemas.ViabilidadCrear,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.ViabilidadRespuesta:
    """§2.4. Una evaluación negativa exige motivo y pasa a RECHAZADA en la misma transacción."""
    return schemas.ViabilidadRespuesta(**service.registrar_viabilidad(db, id_reserva, cuerpo, contexto))


@router.post("/{id_reserva}/lista-espera/adjuntos", status_code=201, response_model=schemas.AdjuntoRespuesta)
async def subir_adjunto(
    id_reserva: int,
    archivo: UploadFile = File(...),
    tipo_adjunto: str = Form(...),
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.AdjuntoRespuesta:
    """§2.5. Excepción explícita al JSON: `multipart/form-data`."""
    contenido = await archivo.read()
    return schemas.AdjuntoRespuesta(**service.subir_adjunto(
        db, id_reserva, tipo_adjunto=tipo_adjunto, nombre_original=archivo.filename or "archivo",
        content_type=archivo.content_type or "", contenido=contenido, contexto=contexto,
    ))


@router.get("/{id_reserva}/lista-espera/adjuntos", response_model=dict)
def listar_adjuntos(
    id_reserva: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    pag=Depends(paginacion_para()),
) -> dict:
    """§2.6."""
    datos, total = service.listar_adjuntos(db, id_reserva, pag.pagina, pag.tamano, contexto)
    return envolver_listado(
        [schemas.AdjuntoRespuesta(**d).model_dump(mode="json") for d in datos],
        pagina=pag.pagina, tamano=pag.tamano, total=total,
    )


@router.get("/{id_reserva}/lista-espera/adjuntos/{adjunto_id}")
def descargar_adjunto(
    id_reserva: int,
    adjunto_id: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> Response:
    """§2.7. Descarga autenticada; no expone rutas internas ni URL pública."""
    contenido, content_type, nombre = service.descargar_adjunto(db, id_reserva, adjunto_id, contexto)
    return Response(
        content=contenido, media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{_nombre_seguro(nombre)}"'},
    )


def _nombre_seguro(nombre: str) -> str:
    """Sin caracteres de control ni comillas: evita inyección en la
    cabecera Content-Disposition a partir de un nombre cargado por el Usuario."""
    limpio = "".join(c for c in nombre if c.isprintable() and c not in '"\\').strip()
    return limpio or "adjunto"


@router.patch("/{id_reserva}", response_model=schemas.ReservaDetalleRespuesta)
def actualizar_reserva(
    id_reserva: int,
    cuerpo: schemas.ReservaActualizar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.ReservaDetalleRespuesta:
    """§2.8. Solo el reservista propietario, solo en SOLICITADA."""
    return schemas.ReservaDetalleRespuesta(**service.actualizar_reserva(db, id_reserva, cuerpo, contexto))
