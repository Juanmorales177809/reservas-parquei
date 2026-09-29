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
from app.modules.reservations.schemas import (
    AprobacionCuerpo,
    AprobacionRespuesta,
    CancelacionCuerpo,
    EjecucionCuerpo,
    FinalizacionCuerpo,
    PropuestaCrear,
    PropuestaRespuesta,
    RechazoCuerpo,
    RechazoRespuesta,
    RecursosAgregarCuerpo,
    TransicionRespuesta,
)

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


@router.get("/contexto/opciones", response_model=dict)
def opciones_contexto(
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> dict:
    """§2.9. Contextos elegibles según el tipo de cuenta (RN-CTX-05, RN-CTX-08)."""
    return service.opciones_contexto(db, contexto)


@router.get("/acompanantes/opciones", response_model=dict)
def opciones_acompanantes(
    proyecto_id: int | None = None,
    semillero_id: int | None = None,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> dict:
    """§2.10. Cuentas elegibles como acompañantes (RN-ACO-02, RN-ACO-04)."""
    return envolver_catalogo(service.opciones_acompanantes(db, proyecto_id, semillero_id, contexto))


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


@router.get("/exportacion")
def exportar_reservas(
    request: Request,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> Response:
    """§8.2. Antes de `/{id_reserva}`: si no, 'exportacion' caería en el id. Sin paginación."""
    filtros = {
        "estado": request.query_params.get("estado"),
        "tipo_reserva": request.query_params.get("tipo_reserva"),
        "id_unidad": _entero(request, "id_unidad"),
        "desde": request.query_params.get("desde"),
        "hasta": request.query_params.get("hasta"),
        "espacio_id": _entero(request, "espacio_id"),
        "recurso_id": _entero(request, "recurso_id"),
    }
    contenido, media_type, nombre = service.exportar_reservas(
        db, filtros, request.query_params.get("formato", ""), contexto
    )
    return Response(
        content=contenido, media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
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


# --- §4 Gestión por el Técnico (API-14) -------------------------------------------------


@router.post("/{id_reserva}/aprobacion", response_model=AprobacionRespuesta)
def aprobar_reserva(
    id_reserva: int,
    cuerpo: AprobacionCuerpo,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> AprobacionRespuesta:
    """§4.1. Para lista de espera registra también recepción de material."""
    return AprobacionRespuesta(**service.aprobar_reserva(db, id_reserva, cuerpo, contexto))


@router.post("/{id_reserva}/rechazo", response_model=RechazoRespuesta)
def rechazar_reserva(
    id_reserva: int,
    cuerpo: RechazoCuerpo,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> RechazoRespuesta:
    """§4.2."""
    return RechazoRespuesta(**service.rechazar_reserva(db, id_reserva, cuerpo, contexto))


@router.post("/{id_reserva}/recursos", status_code=201, response_model=dict)
def agregar_recursos(
    id_reserva: int,
    cuerpo: RecursosAgregarCuerpo,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> dict:
    """§4.3. Solo ESPACIO y RECURSO_INTERNO."""
    return envolver_catalogo([
        schemas.RecursoAsignadoDetalle(**a).model_dump(mode="json") for a in service.agregar_recursos(db, id_reserva, cuerpo, contexto)
    ])


@router.delete("/{id_reserva}/recursos/{reserva_recurso_id}", status_code=204)
def retirar_recurso(
    id_reserva: int,
    reserva_recurso_id: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> Response:
    """§4.4. Retiro manual sin historial ni metadatos propios."""
    service.retirar_recurso(db, id_reserva, reserva_recurso_id, contexto)
    return Response(status_code=204)


# --- §5 Propuestas de periodo (API-14) ---------------------------------------------------


@router.post("/{id_reserva}/propuestas", status_code=201, response_model=PropuestaRespuesta)
def crear_propuesta(
    id_reserva: int,
    cuerpo: PropuestaCrear,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> PropuestaRespuesta:
    """§5.1. `origen` se deriva del rol del actor, no del cuerpo."""
    return PropuestaRespuesta(**service.crear_propuesta(db, id_reserva, cuerpo, contexto))


@router.post("/{id_reserva}/propuestas/vigente/aceptacion", response_model=schemas.ReservaDetalleRespuesta)
def aceptar_propuesta_vigente(
    id_reserva: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.ReservaDetalleRespuesta:
    """§5.2. Solo la contraparte de quien propuso puede aceptar."""
    return schemas.ReservaDetalleRespuesta(**service.aceptar_propuesta_vigente(db, id_reserva, contexto))


@router.post("/{id_reserva}/propuestas/vigente/rechazo", response_model=PropuestaRespuesta)
def rechazar_propuesta_vigente(
    id_reserva: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> PropuestaRespuesta:
    """§5.3. No revoca una aprobación existente."""
    return PropuestaRespuesta(**service.rechazar_propuesta_vigente(db, id_reserva, contexto))


# --- §6 Ejecución (API-14) -----------------------------------------------------------------


@router.post("/{id_reserva}/ejecucion", response_model=TransicionRespuesta)
def ejecutar_reserva(
    id_reserva: int,
    cuerpo: EjecucionCuerpo,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> TransicionRespuesta:
    """§6.1. No aplica a ESPACIO ni RECURSO_INTERNO (inicio automático)."""
    return TransicionRespuesta(**service.ejecutar_reserva(db, id_reserva, cuerpo, contexto))


@router.post("/{id_reserva}/finalizacion", response_model=TransicionRespuesta)
def finalizar_reserva(
    id_reserva: int,
    cuerpo: FinalizacionCuerpo,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> TransicionRespuesta:
    """§6.2. No aplica a ESPACIO ni RECURSO_INTERNO (cierre automático)."""
    return TransicionRespuesta(**service.finalizar_reserva(db, id_reserva, cuerpo, contexto))


@router.post("/{id_reserva}/cancelacion", response_model=TransicionRespuesta)
def cancelar_reserva(
    id_reserva: int,
    cuerpo: CancelacionCuerpo,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> TransicionRespuesta:
    """§6.3. Admitida mientras la ejecución no haya iniciado."""
    return TransicionRespuesta(**service.cancelar_reserva(db, id_reserva, cuerpo, contexto))


# --- §7 Orden de salida (API-15) ---------------------------------------------------------------


@router.get("/{id_reserva}/orden-salida", response_model=schemas.OrdenSalidaRespuesta)
def orden_salida(
    id_reserva: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> schemas.OrdenSalidaRespuesta:
    """§7.1. Lee snapshots inmutables; no genera ni versiona."""
    return schemas.OrdenSalidaRespuesta(**service.obtener_orden(db, id_reserva, contexto))


@router.get("/{id_reserva}/orden-salida.pdf")
def orden_salida_pdf(
    id_reserva: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> Response:
    """§7.2. PDF listo para imprimir; las firmas van en papel."""
    return Response(
        content=service.generar_orden_pdf(db, id_reserva, contexto),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="orden-{id_reserva}.pdf"'},
    )


# --- §8 Calendario y exportación (API-15) -------------------------------------------------------


@router.get("/{id_reserva}/calendario.ics")
def calendario_ics(
    id_reserva: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> Response:
    """§8.1. Solo ESPACIO/RECURSO_INTERNO aprobadas."""
    return Response(
        content=service.generar_ics(db, id_reserva, contexto),
        media_type="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="reserva-{id_reserva}.ics"'},
    )
