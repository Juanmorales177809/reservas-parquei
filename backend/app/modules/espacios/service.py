"""Lógica de espacios, sus recursos asociados y campos adicionales (API-10).

Dueño de `RN-ESP`, `RN-ESP-REC`, `RN-ESP-CAM`, `RN-ESP-DIS`, `RN-ESP-HAB`
(espacios). Al deshabilitar un espacio con reservas futuras, aplica el
efecto mínimo de `RN-CAN-04` de reservations —cancelar la reserva, porque el
objeto de una reserva por espacio desaparece con él— por la misma razón que
`resources` lo hace para recursos (`API-09`): el servicio de escritura de
reservations (`API-13`/`API-14`) todavía no existe. Cuando exista, este
efecto se delega ahí y se retira de aquí.

Un espacio no tiene horario propio (`RN-ESP-DIS-02`): el horario que expone
el detalle es una lectura de `reservas.laboratorios_config`, administrada
por `resources`; este módulo no la escribe.

Cada escritura audita en la misma transacción (patrón de `AUTH-C1`).
"""

from __future__ import annotations

from app.core import audit
from app.core.authz import exigir_permiso
from app.core.deps import ContextoAutenticado
from app.core.errors import (
    CampoSinOpciones,
    Conflicto,
    NoEncontrado,
    NombreDuplicado,
    UnidadIncompatible,
    Validacion,
)
from app.db.models.reservas import Espacios
from app.modules.espacios import repository as repo
from app.modules.espacios import schemas

MOTIVO_DESHABILITACION = "Deshabilitación del espacio"


def _permiso(db, contexto: ContextoAutenticado, id_unidad: int) -> None:
    exigir_permiso(db, contexto.id_cuenta, "espacios.administrar", id_unidad=id_unidad)


def _recurso_asociado_dict(db, asociacion) -> dict:
    recurso = repo.obtener_recurso(db, asociacion.recurso_id)
    nombre = repo.nombre_recurso(db, recurso) if recurso is not None else None
    return {"recurso_id": asociacion.recurso_id, "nombre": nombre, "habilitado": asociacion.habilitado}


def _campo_dict(db, campo) -> dict:
    opciones = repo.opciones_del_campo(db, campo.id)
    return {
        "id": campo.id, "nombre": campo.nombre, "tipo": campo.tipo_campo, "obligatorio": campo.obligatorio,
        "orden": campo.orden, "habilitado": campo.habilitado,
        "opciones": [{"id": o.id, "valor": o.valor, "orden": o.orden, "habilitado": o.habilitado} for o in opciones],
    }


def _resumen(espacio: Espacios) -> dict:
    return {"id": espacio.id, "id_unidad": espacio.id_unidad, "nombre": espacio.nombre,
            "capacidad": espacio.capacidad, "habilitado": espacio.habilitado}


def _detalle(db, espacio: Espacios) -> dict:
    horario = repo.obtener_horario_unidad(db, espacio.id_unidad)
    horario_unidad = None
    if horario is not None:
        horario_unidad = {
            "dias_atencion": horario.dias_atencion, "hora_apertura": horario.hora_apertura,
            "hora_cierre": horario.hora_cierre,
        }
    recursos = [_recurso_asociado_dict(db, a) for a in repo.recursos_asociados(db, espacio.id)]
    campos = [_campo_dict(db, c) for c in repo.campos_del_espacio(db, espacio.id)]
    return {
        "id": espacio.id, "id_unidad": espacio.id_unidad, "nombre": espacio.nombre, "ubicacion": espacio.ubicacion,
        "capacidad": espacio.capacidad, "descripcion": espacio.descripcion, "habilitado": espacio.habilitado,
        "horario_unidad": horario_unidad, "recursos": recursos, "campos": campos,
    }


# --- §2.1/§2.2 Crear y actualizar --------------------------------------------------


def crear_espacio(db, datos: schemas.EspacioCrear, contexto: ContextoAutenticado) -> dict:
    if repo.obtener_unidad(db, datos.id_unidad) is None:
        raise NoEncontrado("La unidad no existe.")
    _permiso(db, contexto, datos.id_unidad)

    nombre = datos.nombre.strip()
    if not nombre:
        raise Validacion("nombre es obligatorio.")
    if datos.capacidad <= 0:
        raise Validacion("capacidad debe ser mayor que cero.")
    if repo.existe_nombre(db, datos.id_unidad, nombre):
        raise NombreDuplicado()

    for recurso_id in datos.recursos:
        recurso = repo.obtener_recurso(db, recurso_id)
        if recurso is None:
            raise NoEncontrado(f"El recurso {recurso_id} no existe.")
        if recurso.id_unidad != datos.id_unidad:
            raise UnidadIncompatible(f"El recurso {recurso_id} pertenece a otra unidad.")
        if repo.tiene_asociacion_activa(db, recurso_id):
            raise Conflicto(f"El recurso {recurso_id} ya está asociado activamente a otro espacio.")

    for campo in datos.campos:
        opciones_habilitadas = len(campo.opciones) > 0
        if campo.tipo == "SELECCION" and not opciones_habilitadas:
            raise CampoSinOpciones(f"El campo '{campo.nombre}' es de selección y no tiene opciones.")

    espacio = repo.crear_espacio(db, datos.id_unidad, nombre, datos.ubicacion, datos.capacidad, datos.descripcion)

    for recurso_id in datos.recursos:
        repo.asociar_recurso(db, espacio.id, recurso_id)

    for campo_datos in datos.campos:
        campo = repo.crear_campo(db, espacio.id, campo_datos.nombre, campo_datos.tipo, campo_datos.obligatorio, campo_datos.orden)
        for opcion in campo_datos.opciones:
            repo.crear_opcion(db, campo.id, opcion.valor, opcion.orden)

    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="reservas.espacios", entidad_id=espacio.id,
        accion="CREAR_ESPACIO",
        datos_nuevos={"id_unidad": datos.id_unidad, "nombre": nombre, "capacidad": datos.capacidad},
    )
    db.commit()
    db.refresh(espacio)
    return _detalle(db, espacio)


def actualizar_espacio(db, id_espacio: int, datos: schemas.EspacioActualizar, contexto: ContextoAutenticado) -> dict:
    espacio = repo.obtener_espacio(db, id_espacio)
    if espacio is None:
        raise NoEncontrado()
    _permiso(db, contexto, espacio.id_unidad)

    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "nombre" in cambios:
        nombre = cambios["nombre"].strip()
        if not nombre:
            raise Validacion("nombre no puede quedar vacío.")
        if repo.existe_nombre(db, espacio.id_unidad, nombre, excluir_id=id_espacio):
            raise NombreDuplicado()
        cambios["nombre"] = nombre
    if "capacidad" in cambios and cambios["capacidad"] <= 0:
        raise Validacion("capacidad debe ser mayor que cero.")

    for campo, valor in cambios.items():
        setattr(espacio, campo, valor)

    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="reservas.espacios", entidad_id=id_espacio,
        accion="ACTUALIZAR_ESPACIO", datos_nuevos=cambios,
    )
    db.commit()
    db.refresh(espacio)
    return _detalle(db, espacio)


# --- §2.3/§2.4 Consultar -----------------------------------------------------------


def _clausula_visibilidad(contexto: ContextoAutenticado):
    if contexto.rol == "ADMINISTRADOR":
        return None
    if contexto.rol == "TECNICO":
        unidad_propia = contexto.unidades_autorizadas[0]
        return (Espacios.habilitado.is_(True)) | (Espacios.id_unidad == unidad_propia)
    return Espacios.habilitado.is_(True)


def listar_espacios(db, filtros: dict, pagina: int, tamano: int, orden: str | None, contexto: ContextoAutenticado) -> tuple[list[dict], int]:
    items, total = repo.listar_espacios(
        db, id_unidad=filtros.get("id_unidad"), habilitado=filtros.get("habilitado"),
        capacidad_minima=filtros.get("capacidad_minima"), clausula_visibilidad=_clausula_visibilidad(contexto),
        orden=orden, offset=(pagina - 1) * tamano, tamano=tamano,
    )
    return [_resumen(e) for e in items], total


def obtener_espacio(db, id_espacio: int) -> dict:
    espacio = repo.obtener_espacio(db, id_espacio)
    if espacio is None:
        raise NoEncontrado()
    return _detalle(db, espacio)


# --- §2.5/§2.6 Habilitación ---------------------------------------------------------


def impacto_deshabilitacion(db, id_espacio: int, contexto: ContextoAutenticado) -> dict:
    espacio = repo.obtener_espacio(db, id_espacio)
    if espacio is None:
        raise NoEncontrado()
    _permiso(db, contexto, espacio.id_unidad)
    return {"reservas_a_cancelar": repo.contar_impacto(db, id_espacio)}


def cambiar_estado(db, id_espacio: int, datos: schemas.EstadoActualizar, contexto: ContextoAutenticado) -> dict:
    espacio = repo.obtener_espacio(db, id_espacio)
    if espacio is None:
        raise NoEncontrado()
    _permiso(db, contexto, espacio.id_unidad)

    if datos.habilitado or not espacio.habilitado:
        repo.cambiar_habilitado(db, espacio, datos.habilitado)
        audit.registrar(
            db, actor_cuenta_id=contexto.id_cuenta, entidad="reservas.espacios", entidad_id=id_espacio,
            accion="CAMBIAR_ESTADO_ESPACIO", datos_nuevos={"habilitado": datos.habilitado},
        )
        db.commit()
        return {"id": id_espacio, "habilitado": datos.habilitado, "reservas_canceladas": 0}

    # Deshabilitar un espacio habilitado: RN-ESP-HAB-05.
    reservas = repo.reservas_vigentes(db, id_espacio)
    if reservas and not datos.confirmado:
        raise Conflicto(
            "Deshabilitar este espacio cancelará reservas futuras; confirme para continuar.",
            detalles=[{"reservas_a_cancelar": len(reservas)}],
        )

    for reserva in reservas:
        repo.cancelar_reserva(db, reserva, MOTIVO_DESHABILITACION, contexto.id_cuenta)

    repo.cambiar_habilitado(db, espacio, False)
    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="reservas.espacios", entidad_id=id_espacio,
        accion="CAMBIAR_ESTADO_ESPACIO",
        datos_nuevos={"habilitado": False, "reservas_canceladas": len(reservas)},
    )
    db.commit()
    return {"id": id_espacio, "habilitado": False, "reservas_canceladas": len(reservas)}


# --- §3 Recursos asociados --------------------------------------------------------


def asociar_recursos(db, id_espacio: int, datos: schemas.RecursosAsociar, contexto: ContextoAutenticado) -> dict:
    espacio = repo.obtener_espacio(db, id_espacio)
    if espacio is None:
        raise NoEncontrado()
    _permiso(db, contexto, espacio.id_unidad)

    for recurso_id in datos.recursos:
        recurso = repo.obtener_recurso(db, recurso_id)
        if recurso is None:
            raise NoEncontrado(f"El recurso {recurso_id} no existe.")
        if recurso.id_unidad != espacio.id_unidad:
            raise UnidadIncompatible(f"El recurso {recurso_id} pertenece a otra unidad.")
        existente = repo.obtener_asociacion(db, id_espacio, recurso_id)
        if existente is not None and existente.habilitado:
            raise Conflicto(f"El recurso {recurso_id} ya está asociado a este espacio.")
        if repo.asociacion_activa_en_otro_espacio(db, recurso_id, id_espacio):
            raise Conflicto(f"El recurso {recurso_id} ya está asociado activamente a otro espacio.")

    for recurso_id in datos.recursos:
        repo.asociar_recurso(db, id_espacio, recurso_id)

    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="reservas.espacio_recursos", entidad_id=id_espacio,
        accion="ASOCIAR_RECURSOS_ESPACIO", datos_nuevos={"recursos": datos.recursos},
    )
    db.commit()
    return {"espacio_id": id_espacio, "recursos": [_recurso_asociado_dict(db, repo.obtener_asociacion(db, id_espacio, r)) for r in datos.recursos]}


def retirar_recurso(db, id_espacio: int, recurso_id: int, contexto: ContextoAutenticado) -> None:
    espacio = repo.obtener_espacio(db, id_espacio)
    if espacio is None:
        raise NoEncontrado()
    _permiso(db, contexto, espacio.id_unidad)

    asociacion = repo.obtener_asociacion(db, id_espacio, recurso_id)
    if asociacion is None or not asociacion.habilitado:
        raise NoEncontrado("La asociación no existe o ya está retirada.")

    repo.retirar_recurso(db, asociacion)
    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="reservas.espacio_recursos", entidad_id=id_espacio,
        accion="RETIRAR_RECURSO_ESPACIO", datos_nuevos={"recurso_id": recurso_id},
    )
    db.commit()


# --- §4 Campos adicionales ----------------------------------------------------------


def crear_campo(db, id_espacio: int, datos: schemas.EspacioCampoCrear, contexto: ContextoAutenticado) -> dict:
    espacio = repo.obtener_espacio(db, id_espacio)
    if espacio is None:
        raise NoEncontrado()
    _permiso(db, contexto, espacio.id_unidad)

    nombre = datos.nombre.strip()
    if not nombre:
        raise Validacion("nombre es obligatorio.")
    if repo.existe_nombre_campo(db, id_espacio, nombre):
        raise Conflicto("Ya existe un campo con ese nombre en este espacio.")
    if datos.tipo == "SELECCION" and not datos.opciones:
        raise CampoSinOpciones()

    campo = repo.crear_campo(db, id_espacio, nombre, datos.tipo, datos.obligatorio, datos.orden)
    for opcion in datos.opciones:
        repo.crear_opcion(db, campo.id, opcion.valor, opcion.orden)

    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="reservas.espacio_campos", entidad_id=campo.id,
        accion="CREAR_CAMPO_ESPACIO", datos_nuevos={"espacio_id": id_espacio, "nombre": nombre, "tipo": datos.tipo},
    )
    db.commit()
    db.refresh(campo)
    return _campo_dict(db, campo)


def actualizar_campo(db, id_espacio: int, campo_id: int, datos: schemas.CampoActualizar, contexto: ContextoAutenticado) -> dict:
    espacio = repo.obtener_espacio(db, id_espacio)
    if espacio is None:
        raise NoEncontrado()
    campo = repo.obtener_campo(db, campo_id)
    if campo is None or campo.espacio_id != id_espacio:
        raise NoEncontrado()
    _permiso(db, contexto, espacio.id_unidad)

    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "nombre" in cambios:
        nombre = cambios["nombre"].strip()
        if not nombre:
            raise Validacion("nombre no puede quedar vacío.")
        if repo.existe_nombre_campo(db, id_espacio, nombre, excluir_id=campo_id):
            raise Conflicto("Ya existe un campo con ese nombre en este espacio.")
        cambios["nombre"] = nombre

    for campo_attr, valor in cambios.items():
        setattr(campo, campo_attr, valor)

    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="reservas.espacio_campos", entidad_id=campo_id,
        accion="EDITAR_CAMPO_ESPACIO", datos_nuevos=cambios,
    )
    db.commit()
    db.refresh(campo)
    return _campo_dict(db, campo)


def cambiar_estado_campo(db, id_espacio: int, campo_id: int, datos: schemas.CampoEstadoActualizar, contexto: ContextoAutenticado) -> dict:
    espacio = repo.obtener_espacio(db, id_espacio)
    if espacio is None:
        raise NoEncontrado()
    campo = repo.obtener_campo(db, campo_id)
    if campo is None or campo.espacio_id != id_espacio:
        raise NoEncontrado()
    _permiso(db, contexto, espacio.id_unidad)

    if datos.habilitado and campo.tipo_campo == "SELECCION" and repo.contar_opciones_habilitadas(db, campo_id) == 0:
        raise CampoSinOpciones()

    campo.habilitado = datos.habilitado
    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="reservas.espacio_campos", entidad_id=campo_id,
        accion="CAMBIAR_ESTADO_CAMPO_ESPACIO", datos_nuevos={"habilitado": datos.habilitado},
    )
    db.commit()
    db.refresh(campo)
    return _campo_dict(db, campo)


def reordenar_campos(db, id_espacio: int, datos: schemas.OrdenActualizar, contexto: ContextoAutenticado) -> list[dict]:
    espacio = repo.obtener_espacio(db, id_espacio)
    if espacio is None:
        raise NoEncontrado()
    _permiso(db, contexto, espacio.id_unidad)

    campos = {c.id: c for c in repo.campos_del_espacio(db, id_espacio)}
    for item in datos.orden:
        if item.campo_id not in campos:
            raise NoEncontrado(f"El campo {item.campo_id} no pertenece a este espacio.")

    for item in datos.orden:
        campos[item.campo_id].orden = item.orden

    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="reservas.espacio_campos", entidad_id=id_espacio,
        accion="REORDENAR_CAMPOS_ESPACIO",
        datos_nuevos={"orden": [{"campo_id": i.campo_id, "orden": i.orden} for i in datos.orden]},
    )
    db.commit()
    return [_campo_dict(db, c) for c in repo.campos_del_espacio(db, id_espacio)]


def crear_opciones(db, id_espacio: int, campo_id: int, datos: schemas.OpcionesCrear, contexto: ContextoAutenticado) -> dict:
    espacio = repo.obtener_espacio(db, id_espacio)
    if espacio is None:
        raise NoEncontrado()
    campo = repo.obtener_campo(db, campo_id)
    if campo is None or campo.espacio_id != id_espacio:
        raise NoEncontrado()
    _permiso(db, contexto, espacio.id_unidad)

    if campo.tipo_campo != "SELECCION":
        raise Validacion("Solo un campo de tipo SELECCION admite opciones.")

    for opcion in datos.opciones:
        if repo.existe_valor_opcion(db, campo_id, opcion.valor):
            raise Conflicto(f"Ya existe la opción '{opcion.valor}' en este campo.")

    for opcion in datos.opciones:
        repo.crear_opcion(db, campo_id, opcion.valor, opcion.orden)

    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="reservas.espacio_campo_opciones", entidad_id=campo_id,
        accion="CREAR_OPCIONES_CAMPO", datos_nuevos={"opciones": [o.valor for o in datos.opciones]},
    )
    db.commit()
    return _campo_dict(db, campo)


def actualizar_opcion(db, id_espacio: int, campo_id: int, opcion_id: int, datos: schemas.OpcionActualizar, contexto: ContextoAutenticado) -> dict:
    espacio = repo.obtener_espacio(db, id_espacio)
    if espacio is None:
        raise NoEncontrado()
    campo = repo.obtener_campo(db, campo_id)
    if campo is None or campo.espacio_id != id_espacio:
        raise NoEncontrado()
    opcion = repo.obtener_opcion(db, opcion_id)
    if opcion is None or opcion.campo_id != campo_id:
        raise NoEncontrado()
    _permiso(db, contexto, espacio.id_unidad)

    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "valor" in cambios:
        valor = cambios["valor"].strip()
        if not valor:
            raise Validacion("valor no puede quedar vacío.")
        if repo.existe_valor_opcion(db, campo_id, valor, excluir_id=opcion_id):
            raise Conflicto(f"Ya existe la opción '{valor}' en este campo.")
        cambios["valor"] = valor

    if cambios.get("habilitado") is False and campo.habilitado:
        if repo.contar_opciones_habilitadas(db, campo_id, excluir_id=opcion_id) == 0:
            raise CampoSinOpciones("No se puede deshabilitar la última opción de un campo habilitado.")

    for campo_attr, valor in cambios.items():
        setattr(opcion, campo_attr, valor)

    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="reservas.espacio_campo_opciones", entidad_id=opcion_id,
        accion="EDITAR_OPCION_CAMPO", datos_nuevos=cambios,
    )
    db.commit()
    db.refresh(opcion)
    return {"id": opcion.id, "valor": opcion.valor, "orden": opcion.orden, "habilitado": opcion.habilitado}
