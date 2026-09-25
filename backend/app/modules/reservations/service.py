"""Servicio de reservations (API-13): creación, edición, consulta,
disponibilidad y preparación de lista de espera.

Dueño de la transacción y de la selección de estrategia
(`architecture.md`): comprueba acceso, carga datos, selecciona la
`ReservationStrategy` por `tipo_reserva`, construye el `Reserva` Context,
delega la decisión y persiste el resultado con el repositorio. Ni
`Reserva` ni las estrategias ejecutan SQL ni confirman transacciones.

**Fuera de alcance de API-13, a propósito**: aprobación/rechazo manual,
agregar/retirar recursos post-creación, propuestas de periodo, ejecución,
finalización y cancelación (contrato §4 a §6) son API-14. `generar_fgl` de
`PrestamoFisicoPolicy` sí se usa aquí, para la creación autoaprobada, y
queda listo para que API-14 lo reutilice al aprobar manualmente.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

from app.core.deps import ContextoAutenticado
from app.core.authz import exigir_permiso
from app.core.errors import (
    Conflicto,
    EstadoIncompatible,
    NoAutorizado,
    NoEncontrado,
    PerfilInicialPendiente,
    TipoNoAdmitido,
    Validacion,
    VinculacionRequerida,
)
from app.modules.espacios import repository as esp_repo
from app.modules.researchs import repository as inv_repo
from app.modules.reservations import repository as repo
from app.modules.reservations import schemas
from app.modules.reservations.domain.reserva import Reserva
from app.modules.reservations.policies import acceso as acceso_policy
from app.modules.reservations.policies import apoyo as apoyo_policy
from app.modules.reservations.policies import contexto as contexto_policy
from app.modules.reservations.policies import prestamo_fisico as prestamo_policy
from app.modules.reservations import storage
from app.modules.reservations.strategies import selector
from app.modules.resources import repository as rec_repo

_TIPOS_CON_PRESTAMO_FISICO = ("RECURSO_CAMPUS", "RECURSO_EXTERNO")
_ZONA_OPERATIVA = ZoneInfo("America/Bogota")

_CAMPOS_FECHA_DETALLE = ("fecha", "fecha_salida", "fecha_devolucion_estimada")
_CAMPOS_HORA_DETALLE = ("hora_inicio", "hora_fin")


def _normalizar_detalle(detalle: dict) -> dict:
    """`detalle` llega como `dict[str, Any]` sin esquema propio (contrato
    §2.1 depende de `tipo_reserva`): Pydantic nunca convierte sus fechas y
    horas, quedan como texto ISO. Cada estrategia recibe tipos ya nativos."""
    normalizado = dict(detalle)
    for campo in _CAMPOS_FECHA_DETALLE:
        valor = normalizado.get(campo)
        if isinstance(valor, str):
            normalizado[campo] = date.fromisoformat(valor)
    for campo in _CAMPOS_HORA_DETALLE:
        valor = normalizado.get(campo)
        if isinstance(valor, str):
            normalizado[campo] = time.fromisoformat(valor)
    return normalizado


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


# --- Contexto académico: validación y snapshot ---------------------------------------


def _resolver_contexto(db, contexto_datos: dict, contexto: ContextoAutenticado) -> dict:
    snapshot: dict = {
        "proyecto_id": None, "semillero_id": None, "pasantia_id": None, "trabajo_grado_id": None,
        "actividad_institucional_id": None, "proyecto_codigo": None, "proyecto_nombre": None,
        "semillero_codigo": None, "semillero_nombre": None, "actividad_nombre": None,
        "pasantia_universidad": None, "pasantia_docente_nombre": None, "pasantia_docente_correo": None,
        "trabajo_grado_director_nombre": None, "trabajo_grado_director_correo": None,
    }
    id_usuario = contexto.id_usuario if contexto.tipo_cuenta == "USUARIO" else None

    def _validar_vinculacion(tipo: str, entidad_id: int) -> None:
        if contexto.tipo_cuenta != "USUARIO":
            return
        vinculacion = inv_repo.obtener_vinculacion(db, tipo, id_usuario, entidad_id)
        if vinculacion is None or not vinculacion.estado:
            raise NoEncontrado(f"No existe una vinculación activa para el {tipo[:-1]} seleccionado.")

    if contexto_datos.get("proyecto_id") is not None:
        proyecto = inv_repo.obtener_proyecto(db, contexto_datos["proyecto_id"])
        if proyecto is None or not proyecto.estado:
            raise NoEncontrado("El proyecto no existe o está deshabilitado.")
        _validar_vinculacion("proyectos", proyecto.id_proyecto)
        snapshot.update(proyecto_id=proyecto.id_proyecto, proyecto_codigo=proyecto.codigo, proyecto_nombre=proyecto.nombre)

    if contexto_datos.get("semillero_id") is not None:
        semillero = inv_repo.obtener_semillero(db, contexto_datos["semillero_id"])
        if semillero is None or not semillero.estado:
            raise NoEncontrado("El semillero no existe o está deshabilitado.")
        _validar_vinculacion("semilleros", semillero.id_semillero)
        snapshot.update(semillero_id=semillero.id_semillero, semillero_codigo=semillero.codigo, semillero_nombre=semillero.nombre)

    if contexto_datos.get("pasantia_id") is not None:
        pasantia = inv_repo.obtener_entidad(db, "pasantias", contexto_datos["pasantia_id"])
        if pasantia is None or not pasantia.estado:
            raise NoEncontrado("La pasantía no existe o está deshabilitada.")
        _validar_vinculacion("pasantias", pasantia.id_pasantia)
        snapshot.update(
            pasantia_id=pasantia.id_pasantia, pasantia_universidad=pasantia.universidad,
            pasantia_docente_nombre=pasantia.docente_itm_nombre, pasantia_docente_correo=pasantia.docente_itm_correo,
        )

    if contexto_datos.get("trabajo_grado_id") is not None:
        trabajo = inv_repo.obtener_entidad(db, "trabajos_grado", contexto_datos["trabajo_grado_id"])
        if trabajo is None or not trabajo.estado:
            raise NoEncontrado("El trabajo de grado no existe o está deshabilitado.")
        _validar_vinculacion("trabajos_grado", trabajo.id_trabajo_grado)
        snapshot.update(
            trabajo_grado_id=trabajo.id_trabajo_grado, trabajo_grado_director_nombre=trabajo.director_nombre,
            trabajo_grado_director_correo=trabajo.director_correo,
        )

    if contexto_datos.get("actividad_institucional_id") is not None:
        actividad = inv_repo.obtener_actividad(db, contexto_datos["actividad_institucional_id"])
        if actividad is None or not actividad.estado:
            raise NoEncontrado("La actividad institucional no existe o está deshabilitada.")
        snapshot.update(actividad_institucional_id=actividad.id_actividad, actividad_nombre=actividad.nombre)

    return snapshot


def _validar_acompanantes(db, ids_cuentas: list[int], contexto_resuelto: dict) -> None:
    if not ids_cuentas:
        return
    if not contexto_resuelto["proyecto_id"] and not contexto_resuelto["semillero_id"]:
        raise Validacion("Los acompañantes solo aplican cuando la reserva tiene proyecto o semillero como contexto.")
    for id_cuenta in ids_cuentas:
        id_usuario = repo.id_usuario_de_cuenta(db, id_cuenta)
        if id_usuario is None:
            raise NoEncontrado(f"La cuenta {id_cuenta} no existe.")
        vinculado = False
        if contexto_resuelto["proyecto_id"]:
            v = inv_repo.obtener_vinculacion(db, "proyectos", id_usuario, contexto_resuelto["proyecto_id"])
            vinculado = vinculado or (v is not None and v.estado)
        if contexto_resuelto["semillero_id"]:
            v = inv_repo.obtener_vinculacion(db, "semilleros", id_usuario, contexto_resuelto["semillero_id"])
            vinculado = vinculado or (v is not None and v.estado)
        if not vinculado:
            raise NoEncontrado(f"La cuenta {id_cuenta} no tiene vinculación activa con el proyecto o semillero de la reserva.")


# --- §2.1 Crear ------------------------------------------------------------------------


def crear_reserva(db, datos: schemas.ReservaCrear, contexto: ContextoAutenticado) -> dict:
    ahora = _ahora()

    if contexto.tipo_cuenta == "USUARIO":
        if contexto.actualizacion_inicial_pendiente:
            raise PerfilInicialPendiente()
        if not inv_repo.tiene_vinculacion_activa(db, contexto.id_usuario):
            raise VinculacionRequerida()

    unidad_cargo = repo.unidad_del_cargo_de_persona(db, contexto.id_persona) if contexto.tipo_cuenta == "PERSONAL" else None
    acceso_policy.validar_unidad_receptora(contexto, datos.id_unidad, unidad_cargo)

    unidad = rec_repo.obtener_unidad(db, datos.id_unidad)
    if unidad is None or not unidad.estado:
        raise NoEncontrado("La unidad no existe.")

    tipo = repo.obtener_tipo_por_codigo(db, datos.tipo_reserva)
    if tipo is None:
        raise Validacion(f"El tipo {datos.tipo_reserva} no existe o está deshabilitado.")
    config = rec_repo.obtener_config(db, datos.id_unidad)
    if config is None or not config.habilitado_reservas:
        raise Conflicto("La unidad no admite reservas.")
    if datos.tipo_reserva not in rec_repo.obtener_tipos_habilitados(db, datos.id_unidad):
        raise Conflicto(f"El tipo {datos.tipo_reserva} no está habilitado para este laboratorio.")

    contexto_datos = datos.contexto.model_dump()
    contexto_policy.validar_composicion(contexto_datos)
    if contexto.tipo_cuenta == "PERSONAL":
        contexto_policy.validar_para_personal(contexto_datos)
    contexto_resuelto = _resolver_contexto(db, contexto_datos, contexto)

    strategy = selector.seleccionar(datos.tipo_reserva)
    reserva_ctx = Reserva(tipo_codigo=datos.tipo_reserva, strategy=strategy)
    condiciones = {"db": db, "config": config, "ahora": ahora}
    datos_operacion = datos.model_dump()
    datos_operacion["detalle"] = _normalizar_detalle(datos_operacion["detalle"])

    reserva_ctx.validar("crear", datos_operacion, condiciones)
    if datos.acompanantes:
        _validar_acompanantes(db, datos.acompanantes, contexto_resuelto)
    cambios = reserva_ctx.determinar_cambios("crear", datos_operacion, condiciones)

    recurso_ids = [r["recurso_id"] for r in cambios.get("recursos", [])]
    requiere_por_equipo = apoyo_policy.algun_recurso_requiere_apoyo(db, recurso_ids)
    requiere_apoyo_efectivo = apoyo_policy.apoyo_efectivo(datos.requiere_apoyo, requiere_por_equipo)

    if datos.tipo_reserva == "LISTA_ESPERA":
        estado_codigo = "SOLICITADA"
    elif contexto.tipo_cuenta == "USUARIO":
        estado_codigo = "APROBADA" if config.aprobacion_automatica else "SOLICITADA"
    else:
        estado_codigo = "APROBADA"
    estado_id = repo.obtener_estado_id_codigo(db, estado_codigo)

    reserva = repo.crear_reserva(
        db, id_unidad=datos.id_unidad, tipo_reserva_id=tipo.id, id_cuenta=contexto.id_cuenta,
        estado_id=estado_id, observacion=datos.observacion, requiere_apoyo=requiere_apoyo_efectivo,
        created_by=contexto.id_cuenta,
    )
    repo.registrar_historial(db, reserva_id=reserva.id, estado_anterior_id=None, estado_nuevo_id=estado_id, actor_cuenta_id=contexto.id_cuenta, motivo=None)
    repo.crear_contexto(db, reserva.id, **contexto_resuelto)

    if "detalle_espacio" in cambios:
        repo.crear_detalle_espacio(db, reserva.id, **cambios["detalle_espacio"])
    if "detalle_interno" in cambios:
        repo.crear_detalle_interno(db, reserva.id, **cambios["detalle_interno"])
    if "detalle_campus" in cambios:
        repo.crear_detalle_campus(db, reserva.id, **cambios["detalle_campus"])
        repo.crear_datos_salida(db, reserva.id, **cambios["datos_salida"])
    if "detalle_externo" in cambios:
        repo.crear_detalle_externo(db, reserva.id, **cambios["detalle_externo"])
        repo.crear_datos_salida(db, reserva.id, **cambios["datos_salida"])
    if "detalle_lista_espera" in cambios:
        repo.crear_detalle_lista_espera(db, reserva.id, **cambios["detalle_lista_espera"])

    if datos.tipo_reserva in _TIPOS_CON_PRESTAMO_FISICO and recurso_ids:
        prestamo_policy.establecer_compromisos(db, reserva_id=reserva.id, recurso_ids=recurso_ids)
    for r in cambios.get("recursos", []):
        repo.crear_asignacion_recurso(db, reserva_id=reserva.id, recurso_id=r["recurso_id"], rol=r["rol"])

    if datos.acompanantes:
        repo.reemplazar_acompanantes(db, reserva.id, datos.acompanantes)
    if datos.campos_adicionales:
        repo.reemplazar_campos_valores(db, reserva.id, [
            _valor_campo_snapshot(db, c.campo_id, c.valor_texto, c.opcion_id) for c in datos.campos_adicionales
        ])

    if estado_codigo == "APROBADA":
        _al_aprobar(db, reserva, contexto, ahora, datos.tipo_reserva)

    db.commit()
    db.refresh(reserva)
    return {"id": reserva.id, "estado": estado_codigo, "tipo_reserva": datos.tipo_reserva, "id_unidad": reserva.id_unidad, "requiere_apoyo": reserva.requiere_apoyo, "created_at": reserva.created_at}


def _valor_campo_snapshot(db, campo_id: int, valor_texto: str | None, opcion_id: int | None) -> dict:
    campo = esp_repo.obtener_campo(db, campo_id)
    if campo is None:
        raise NoEncontrado(f"El campo {campo_id} no existe.")
    opcion_nombre = None
    if opcion_id is not None:
        opcion = esp_repo.obtener_opcion(db, opcion_id)
        if opcion is None or opcion.campo_id != campo_id:
            raise Validacion(f"La opción {opcion_id} no pertenece al campo {campo_id}.")
        opcion_nombre = opcion.valor
    return {
        "campo_id": campo_id, "campo_nombre_snapshot": campo.nombre, "campo_tipo_snapshot": campo.tipo_campo,
        "obligatorio_snapshot": campo.obligatorio, "valor_texto": valor_texto, "opcion_id": opcion_id,
        "opcion_nombre_snapshot": opcion_nombre,
    }


def _al_aprobar(db, reserva, contexto: ContextoAutenticado, ahora: datetime, tipo_codigo: str) -> None:
    """Efectos de que una reserva nazca `APROBADA` (autoaprobación): fecha de
    aprobación, FGL 030 para préstamos, e inicio inmediato de `ESPACIO` si la
    creación cae dentro de su propia franja (RN-TIP-PE-27, extendido a la
    autoaprobación en creación por la misma razón que se aplica al aprobar)."""
    reserva.fecha_aprobacion = ahora

    if tipo_codigo in _TIPOS_CON_PRESTAMO_FISICO:
        prestamo_policy.generar_fgl(db, reserva=reserva, contexto_actor=contexto)
        return

    if tipo_codigo == "ESPACIO":
        detalle = repo.obtener_detalle_espacio(db, reserva.id)
        ahora_local = ahora.astimezone(_ZONA_OPERATIVA)
        dentro_de_franja = (
            detalle.fecha == ahora_local.date()
            and detalle.hora_inicio <= ahora_local.time() < detalle.hora_fin
        )
        if dentro_de_franja:
            estado_ejecucion = repo.obtener_estado_id_codigo(db, "EN_EJECUCION")
            estado_anterior = reserva.estado_id
            reserva.estado_id = estado_ejecucion
            repo.registrar_historial(db, reserva_id=reserva.id, estado_anterior_id=estado_anterior, estado_nuevo_id=estado_ejecucion, actor_cuenta_id=None, motivo="Inicio inmediato dentro de la franja aprobada")


# --- §2.8 Editar ------------------------------------------------------------------------


def actualizar_reserva(db, id_reserva: int, datos: schemas.ReservaActualizar, contexto: ContextoAutenticado) -> dict:
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None:
        raise NoEncontrado()
    acceso_policy.validar_propietario(contexto, reserva.id_cuenta)
    estado_actual = repo.obtener_estado(db, reserva.estado_id)
    acceso_policy.exigir_solicitada(estado_actual.codigo)

    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    cambios_entrada = datos.model_dump(exclude_unset=True)
    if not cambios_entrada:
        raise Validacion("El cuerpo debe contener al menos un campo editable.")

    # Construye el estado resultante completo: lo no enviado conserva su valor actual.
    detalle_actual = _detalle_por_tipo(db, reserva, tipo.codigo)
    detalle_resultante = dict(detalle_actual)
    if "detalle" in cambios_entrada and cambios_entrada["detalle"]:
        detalle_resultante.update(_normalizar_detalle(cambios_entrada["detalle"]))

    contexto_actual = repo.obtener_contexto(db, id_reserva)
    if "contexto" in cambios_entrada:
        contexto_datos = cambios_entrada["contexto"] or {}
        contexto_policy.validar_composicion(contexto_datos)
        if contexto.tipo_cuenta == "PERSONAL":
            contexto_policy.validar_para_personal(contexto_datos)
        contexto_resuelto = _resolver_contexto(db, contexto_datos, contexto)
    else:
        contexto_resuelto = _contexto_dict(contexto_actual)

    if "recursos" in cambios_entrada:
        recursos_resultantes = [{"recurso_id": r["recurso_id"], "rol": r["rol"]} for r in (cambios_entrada["recursos"] or [])]
    else:
        recursos_resultantes = [{"recurso_id": a.recurso_id, "rol": a.rol} for a in repo.asignaciones_de_reserva(db, id_reserva, solo_vigentes=True)]

    acompanantes_resultantes = cambios_entrada.get("acompanantes", repo.acompanantes_de_reserva(db, id_reserva))
    if acompanantes_resultantes is None:
        acompanantes_resultantes = []

    if "campos_adicionales" in cambios_entrada and cambios_entrada["campos_adicionales"] is not None:
        campos_resultantes = cambios_entrada["campos_adicionales"]
    else:
        # No enviado: conserva los obligatorios ya satisfechos, para que la
        # revalidación (heredada de crear) no exija resenviarlos siempre.
        campos_resultantes = [{"campo_id": c.campo_id} for c in repo.campos_valores_de_reserva(db, id_reserva)]

    config = rec_repo.obtener_config(db, reserva.id_unidad)
    ahora = _ahora()
    strategy = selector.seleccionar(tipo.codigo)
    reserva_ctx = Reserva(tipo_codigo=tipo.codigo, strategy=strategy, cabecera=reserva)
    condiciones = {"db": db, "config": config, "ahora": ahora, "excluir_reserva_id": id_reserva}
    datos_operacion = {
        "id_unidad": reserva.id_unidad, "detalle": detalle_resultante, "recursos": recursos_resultantes,
        "acompanantes": acompanantes_resultantes, "campos_adicionales": campos_resultantes,
    }

    reserva_ctx.validar("editar", datos_operacion, condiciones)
    if datos_operacion["acompanantes"]:
        _validar_acompanantes(db, datos_operacion["acompanantes"], contexto_resuelto)
    resultado = reserva_ctx.determinar_cambios("editar", datos_operacion, condiciones)

    if "observacion" in cambios_entrada:
        reserva.observacion = cambios_entrada["observacion"]
    if "contexto" in cambios_entrada:
        if contexto_actual is not None:
            for campo, valor in contexto_resuelto.items():
                setattr(contexto_actual, campo, valor)
        else:
            repo.crear_contexto(db, id_reserva, **contexto_resuelto)

    if "detalle_espacio" in resultado:
        d = repo.obtener_detalle_espacio(db, id_reserva)
        for campo, valor in resultado["detalle_espacio"].items():
            setattr(d, campo, valor)
    if "detalle_interno" in resultado:
        d = repo.obtener_detalle_interno(db, id_reserva)
        for campo, valor in resultado["detalle_interno"].items():
            setattr(d, campo, valor)
    if "detalle_campus" in resultado:
        d = repo.obtener_detalle_campus(db, id_reserva)
        for campo, valor in resultado["detalle_campus"].items():
            setattr(d, campo, valor)
        salida = repo.obtener_datos_salida(db, id_reserva)
        for campo, valor in resultado["datos_salida"].items():
            setattr(salida, campo, valor)
    if "detalle_externo" in resultado:
        d = repo.obtener_detalle_externo(db, id_reserva)
        for campo, valor in resultado["detalle_externo"].items():
            setattr(d, campo, valor)
        salida = repo.obtener_datos_salida(db, id_reserva)
        for campo, valor in resultado["datos_salida"].items():
            setattr(salida, campo, valor)
    if "detalle_lista_espera" in resultado and resultado["detalle_lista_espera"]:
        d = repo.obtener_detalle_lista_espera(db, id_reserva)
        descripcion_anterior = d.descripcion_necesidad
        for campo, valor in resultado["detalle_lista_espera"].items():
            setattr(d, campo, valor)
        if d.descripcion_necesidad != descripcion_anterior and d.viable is not None:
            # RN-TIP-PLE-09: cambiar efectivamente la descripción invalida viabilidad y revisión.
            d.viable = None
            d.fecha_evaluacion_viabilidad = None
            formulario = repo.obtener_formulario_lista_espera(db, id_reserva)
            if formulario is not None:
                formulario.datos_tecnico = None
                formulario.revisado_por = None
                formulario.revisado_at = None

    if "recursos" in resultado:
        for a in repo.asignaciones_de_reserva(db, id_reserva, solo_vigentes=True):
            db.delete(a)
        db.flush()
        recurso_ids_nuevos = [r["recurso_id"] for r in resultado["recursos"]]
        if tipo.codigo in _TIPOS_CON_PRESTAMO_FISICO and recurso_ids_nuevos:
            prestamo_policy.establecer_compromisos(db, reserva_id=id_reserva, recurso_ids=recurso_ids_nuevos)
        for r in resultado["recursos"]:
            repo.crear_asignacion_recurso(db, reserva_id=id_reserva, recurso_id=r["recurso_id"], rol=r["rol"])
        requiere_por_equipo = apoyo_policy.algun_recurso_requiere_apoyo(db, recurso_ids_nuevos)
        if "requiere_apoyo" in cambios_entrada:
            reserva.requiere_apoyo = apoyo_policy.apoyo_efectivo(cambios_entrada["requiere_apoyo"], requiere_por_equipo)
        else:
            reserva.requiere_apoyo = apoyo_policy.apoyo_efectivo(reserva.requiere_apoyo, requiere_por_equipo)
    elif "requiere_apoyo" in cambios_entrada:
        recurso_ids_actuales = [a.recurso_id for a in repo.asignaciones_de_reserva(db, id_reserva, solo_vigentes=True)]
        requiere_por_equipo = apoyo_policy.algun_recurso_requiere_apoyo(db, recurso_ids_actuales)
        reserva.requiere_apoyo = apoyo_policy.apoyo_efectivo(cambios_entrada["requiere_apoyo"], requiere_por_equipo)

    if "acompanantes" in cambios_entrada:
        repo.reemplazar_acompanantes(db, id_reserva, acompanantes_resultantes)
    if "campos_adicionales" in cambios_entrada and cambios_entrada["campos_adicionales"] is not None:
        repo.reemplazar_campos_valores(db, id_reserva, [
            _valor_campo_snapshot(db, c["campo_id"], c.get("valor_texto"), c.get("opcion_id")) for c in cambios_entrada["campos_adicionales"]
        ])

    reserva.updated_at = ahora
    db.commit()
    return obtener_reserva_detalle(db, id_reserva, contexto)


# --- §2.3 Lista de espera: formulario ---------------------------------------------------


def _exigir_lista_espera_solicitada(db, id_reserva: int):
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None:
        raise NoEncontrado()
    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    if tipo.codigo != "LISTA_ESPERA":
        raise TipoNoAdmitido()
    estado = repo.obtener_estado(db, reserva.estado_id)
    if estado.codigo != "SOLICITADA":
        raise EstadoIncompatible()
    return reserva


def diligenciar_formulario(db, id_reserva: int, cuerpo: schemas.FormularioParteCuerpo, contexto: ContextoAutenticado) -> dict:
    if (cuerpo.datos_usuario is None) == (cuerpo.datos_tecnico is None):
        raise Validacion("Envíe exactamente una de las dos partes: datos_usuario o datos_tecnico.")

    reserva = _exigir_lista_espera_solicitada(db, id_reserva)
    strategy = selector.seleccionar("LISTA_ESPERA")
    reserva_ctx = Reserva(tipo_codigo="LISTA_ESPERA", strategy=strategy)
    detalle = repo.obtener_detalle_lista_espera(db, id_reserva)
    formulario = repo.obtener_formulario_lista_espera(db, id_reserva)

    if cuerpo.datos_usuario is not None:
        acceso_policy.validar_propietario(contexto, reserva.id_cuenta)
        parte, valor = "reservista", cuerpo.datos_usuario
    else:
        exigir_permiso(db, contexto.id_cuenta, "reservas.administrar", id_unidad=reserva.id_unidad)
        parte, valor = "tecnica", cuerpo.datos_tecnico

    condiciones = {"viable": detalle.viable is True, "formulario_reservista_existente": formulario is not None}
    reserva_ctx.validar("lista_espera_formulario", {"parte": parte, "valor": valor}, condiciones)

    if parte == "reservista":
        if formulario is None:
            formulario = repo.crear_formulario_reservista(db, id_reserva, valor)
        else:
            formulario.datos_usuario = valor
            formulario.diligenciado_at = _ahora()
            if formulario.revisado_at is not None:
                # RN-TIP-PLE-04: modificar la parte del reservista tras revisión invalida la técnica.
                formulario.datos_tecnico = None
                formulario.revisado_por = None
                formulario.revisado_at = None
    else:
        formulario.datos_tecnico = valor
        formulario.revisado_por = contexto.id_cuenta
        formulario.revisado_at = _ahora()

    db.commit()
    db.refresh(formulario)
    return {
        "reserva_id": id_reserva, "datos_usuario": formulario.datos_usuario, "datos_tecnico": formulario.datos_tecnico,
        "diligenciado_at": formulario.diligenciado_at, "revisado_por": formulario.revisado_por, "revisado_at": formulario.revisado_at,
    }


# --- §2.4 Lista de espera: viabilidad ----------------------------------------------------


def registrar_viabilidad(db, id_reserva: int, cuerpo: schemas.ViabilidadCrear, contexto: ContextoAutenticado) -> dict:
    reserva = _exigir_lista_espera_solicitada(db, id_reserva)
    exigir_permiso(db, contexto.id_cuenta, "reservas.administrar", id_unidad=reserva.id_unidad)

    strategy = selector.seleccionar("LISTA_ESPERA")
    reserva_ctx = Reserva(tipo_codigo="LISTA_ESPERA", strategy=strategy)
    datos = {"viable": cuerpo.viable, "motivo": cuerpo.motivo}
    reserva_ctx.validar("lista_espera_viabilidad", datos, {})

    detalle = repo.obtener_detalle_lista_espera(db, id_reserva)
    ahora = _ahora()
    detalle.viable = cuerpo.viable
    detalle.fecha_evaluacion_viabilidad = ahora

    if cuerpo.viable is False:
        estado_rechazada = repo.obtener_estado_id_codigo(db, "RECHAZADA")
        estado_anterior = reserva.estado_id
        reserva.estado_id = estado_rechazada
        repo.registrar_historial(db, reserva_id=id_reserva, estado_anterior_id=estado_anterior, estado_nuevo_id=estado_rechazada, actor_cuenta_id=contexto.id_cuenta, motivo=cuerpo.motivo)

    db.commit()
    estado_actual = repo.obtener_estado(db, reserva.estado_id)
    return {"id": id_reserva, "viable": detalle.viable, "fecha_evaluacion_viabilidad": detalle.fecha_evaluacion_viabilidad, "estado": estado_actual.codigo}


# --- §2.5-2.7 Adjuntos -----------------------------------------------------------------

_TIPOS_ADJUNTO_CONTENT_TYPES = {
    "PLANO": {"image/vnd.dwg", "image/vnd.dxf", "model/step", "model/stl"},
    "IMAGEN": {"image/png", "image/jpeg"},
    "DOCUMENTO": {"application/pdf"},
}
_MAX_ADJUNTO_BYTES = 5 * 1024 * 1024


def subir_adjunto(db, id_reserva: int, *, tipo_adjunto: str, nombre_original: str, content_type: str, contenido: bytes, contexto: ContextoAutenticado) -> dict:
    reserva = _exigir_lista_espera_solicitada(db, id_reserva)
    acceso_policy.validar_propietario(contexto, reserva.id_cuenta)

    if not contenido:
        raise Validacion("El archivo está vacío.")
    if len(contenido) > _MAX_ADJUNTO_BYTES:
        raise Validacion("El archivo supera los 5 MB permitidos.")
    admitidos = _TIPOS_ADJUNTO_CONTENT_TYPES.get(tipo_adjunto)
    if admitidos is None:
        raise Validacion("tipo_adjunto debe ser PLANO, IMAGEN o DOCUMENTO.")
    if content_type not in admitidos:
        raise Validacion(f"El archivo declarado como {content_type} no es un formato admitido para {tipo_adjunto}.")
    if not storage.validar_contenido(content_type, contenido):
        raise Validacion("El contenido del archivo no corresponde al tipo declarado.")

    storage_key = storage.guardar(contenido)
    adjunto = repo.crear_adjunto(
        db, reserva_id=id_reserva, tipo_adjunto=tipo_adjunto, nombre_original=nombre_original,
        storage_key=storage_key, content_type=content_type, size_bytes=len(contenido), uploaded_by=contexto.id_cuenta,
    )
    db.commit()
    db.refresh(adjunto)
    return _adjunto_dict(adjunto)


def _adjunto_dict(a) -> dict:
    return {
        "id": a.id, "reserva_id": a.reserva_id, "tipo_adjunto": a.tipo_adjunto, "nombre_original": a.nombre_original,
        "content_type": a.content_type, "size_bytes": a.size_bytes, "uploaded_by": a.uploaded_by, "created_at": a.created_at,
    }


def listar_adjuntos(db, id_reserva: int, pagina: int, tamano: int, contexto: ContextoAutenticado) -> tuple[list[dict], int]:
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None or not acceso_policy.validar_ambito_lectura(contexto, reserva.id_cuenta, reserva.id_unidad):
        raise NoEncontrado()
    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    if tipo.codigo != "LISTA_ESPERA":
        raise TipoNoAdmitido()
    items, total = repo.adjuntos_de_reserva(db, id_reserva, offset=(pagina - 1) * tamano, tamano=tamano)
    return [_adjunto_dict(a) for a in items], total


def descargar_adjunto(db, id_reserva: int, adjunto_id: int, contexto: ContextoAutenticado) -> tuple[bytes, str, str]:
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None or not acceso_policy.validar_ambito_lectura(contexto, reserva.id_cuenta, reserva.id_unidad):
        raise NoEncontrado()
    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    if tipo.codigo != "LISTA_ESPERA":
        raise TipoNoAdmitido()
    adjunto = repo.obtener_adjunto(db, adjunto_id)
    if adjunto is None or adjunto.reserva_id != id_reserva:
        raise NoEncontrado()
    return storage.leer(adjunto.storage_key), adjunto.content_type, adjunto.nombre_original


# --- §2.2 Catálogo de tipos ----------------------------------------------------------------


def tipos_habilitados(db, id_unidad: int) -> list[dict]:
    codigos = rec_repo.obtener_tipos_habilitados(db, id_unidad)
    resultado = []
    for codigo in codigos:
        tipo = repo.obtener_tipo_por_codigo(db, codigo)
        if tipo is not None:
            resultado.append({"codigo": tipo.codigo, "nombre": tipo.nombre})
    return resultado


# --- §3 Consulta ------------------------------------------------------------------------


def _detalle_por_tipo(db, reserva, tipo_codigo: str) -> dict:
    if tipo_codigo == "ESPACIO":
        d = repo.obtener_detalle_espacio(db, reserva.id)
        return {"espacio_id": d.espacio_id, "fecha": d.fecha, "hora_inicio": d.hora_inicio, "hora_fin": d.hora_fin, "asistentes": d.asistentes}
    if tipo_codigo == "RECURSO_INTERNO":
        d = repo.obtener_detalle_interno(db, reserva.id)
        return {"fecha": d.fecha, "hora_inicio": d.hora_inicio, "hora_fin": d.hora_fin}
    if tipo_codigo in ("RECURSO_CAMPUS", "RECURSO_EXTERNO"):
        d = repo.obtener_detalle_campus(db, reserva.id) if tipo_codigo == "RECURSO_CAMPUS" else repo.obtener_detalle_externo(db, reserva.id)
        salida = repo.obtener_datos_salida(db, reserva.id)
        return {
            "fecha_salida": d.fecha_salida, "fecha_devolucion_estimada": d.fecha_devolucion_estimada,
            "razon_solicitud": salida.razon_solicitud, "lugar_nombre": salida.lugar_nombre,
            "lugar_direccion": salida.lugar_direccion, "nombre_actividad_evento": salida.nombre_actividad_evento,
        }
    if tipo_codigo == "LISTA_ESPERA":
        d = repo.obtener_detalle_lista_espera(db, reserva.id)
        return {"descripcion_necesidad": d.descripcion_necesidad}
    return {}


def _contexto_dict(contexto) -> dict:
    if contexto is None:
        return {}
    return {
        "proyecto_id": contexto.proyecto_id, "proyecto_codigo": contexto.proyecto_codigo, "proyecto_nombre": contexto.proyecto_nombre,
        "semillero_id": contexto.semillero_id, "semillero_codigo": contexto.semillero_codigo, "semillero_nombre": contexto.semillero_nombre,
        "pasantia_id": contexto.pasantia_id, "pasantia_universidad": contexto.pasantia_universidad,
        "pasantia_docente_nombre": contexto.pasantia_docente_nombre, "pasantia_docente_correo": contexto.pasantia_docente_correo,
        "trabajo_grado_id": contexto.trabajo_grado_id, "trabajo_grado_director_nombre": contexto.trabajo_grado_director_nombre,
        "trabajo_grado_director_correo": contexto.trabajo_grado_director_correo,
        "actividad_institucional_id": contexto.actividad_institucional_id, "actividad_nombre": contexto.actividad_nombre,
    }


def obtener_reserva_detalle(db, id_reserva: int, contexto: ContextoAutenticado) -> dict:
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None or not acceso_policy.validar_ambito_lectura(contexto, reserva.id_cuenta, reserva.id_unidad):
        raise NoEncontrado()

    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    estado = repo.obtener_estado(db, reserva.estado_id)

    recursos = []
    for a in repo.asignaciones_de_reserva(db, id_reserva):
        reserva_causante_id = None
        if a.reserva_causante_id is not None:
            causante = repo.obtener_reserva(db, a.reserva_causante_id)
            if causante is not None and acceso_policy.validar_ambito_lectura(contexto, causante.id_cuenta, causante.id_unidad):
                reserva_causante_id = a.reserva_causante_id
        recursos.append({
            "reserva_recurso_id": a.id, "recurso_id": a.recurso_id, "rol": a.rol, "estado_asignacion": a.estado_asignacion,
            "incorporado_at": a.incorporado_at, "retirado_at": a.retirado_at, "causa_retiro": a.causa_retiro,
            "reserva_causante_id": reserva_causante_id,
        })

    lista_espera_extra = None
    if tipo.codigo == "LISTA_ESPERA":
        le = repo.obtener_detalle_lista_espera(db, id_reserva)
        formulario = repo.obtener_formulario_lista_espera(db, id_reserva)
        lista_espera_extra = {
            "viable": le.viable, "fecha_evaluacion_viabilidad": le.fecha_evaluacion_viabilidad,
            "fecha_recepcion_material": le.fecha_recepcion_material, "prioridad": le.prioridad,
            "horas_ejecucion": float(le.horas_ejecucion) if le.horas_ejecucion is not None else None,
            "formulario": None if formulario is None else {
                "datos_usuario": formulario.datos_usuario, "datos_tecnico": formulario.datos_tecnico,
                "diligenciado_at": formulario.diligenciado_at, "revisado_por": formulario.revisado_por, "revisado_at": formulario.revisado_at,
            },
        }

    return {
        "id": reserva.id, "estado": estado.codigo, "tipo_reserva": tipo.codigo, "id_unidad": reserva.id_unidad,
        "id_cuenta": reserva.id_cuenta, "observacion": reserva.observacion, "requiere_apoyo": reserva.requiere_apoyo,
        "created_at": reserva.created_at, "updated_at": reserva.updated_at, "fecha_aprobacion": reserva.fecha_aprobacion,
        "fecha_cancelacion": reserva.fecha_cancelacion, "motivo_cancelacion": reserva.motivo_cancelacion,
        "detalle": _detalle_por_tipo(db, reserva, tipo.codigo),
        "contexto": _contexto_dict(repo.obtener_contexto(db, id_reserva)),
        "recursos": recursos,
        "acompanantes": repo.acompanantes_de_reserva(db, id_reserva),
        "campos_adicionales": [
            {"campo_id": c.campo_id, "campo_nombre": c.campo_nombre_snapshot, "valor_texto": c.valor_texto, "opcion_id": c.opcion_id, "opcion_nombre": c.opcion_nombre_snapshot}
            for c in repo.campos_valores_de_reserva(db, id_reserva)
        ],
        "historial": [
            {
                "estado_anterior": (repo.obtener_estado(db, h.estado_anterior_id).codigo if h.estado_anterior_id else None),
                "estado_nuevo": repo.obtener_estado(db, h.estado_nuevo_id).codigo,
                "actor_cuenta_id": h.actor_cuenta_id, "motivo": h.motivo, "created_at": h.created_at,
            }
            for h in repo.historial_de_reserva(db, id_reserva)
        ],
        "propuesta_vigente": None,
        "lista_espera": lista_espera_extra,
    }


def listar_reservas(db, filtros: dict, pagina: int, tamano: int, orden: str | None, contexto: ContextoAutenticado) -> tuple[list[dict], int]:
    id_cuenta = None
    id_unidad = filtros.get("id_unidad")
    if contexto.rol == "USUARIO" or (contexto.rol == "TECNICO" and contexto.unidades_autorizadas == []):
        id_cuenta = contexto.id_cuenta
    elif contexto.rol == "TECNICO":
        id_unidad = id_unidad or (contexto.unidades_autorizadas[0] if contexto.unidades_autorizadas != "GLOBAL" else None)
        if contexto.unidades_autorizadas != "GLOBAL" and id_unidad not in contexto.unidades_autorizadas:
            id_cuenta = contexto.id_cuenta  # fuera de su unidad: solo lo propio

    items, total = repo.listar_reservas(
        db, id_cuenta=id_cuenta, id_unidad=id_unidad, estado_codigo=filtros.get("estado"),
        tipo_codigo=filtros.get("tipo_reserva"), desde=filtros.get("desde"), hasta=filtros.get("hasta"),
        espacio_id=filtros.get("espacio_id"), recurso_id=filtros.get("recurso_id"),
        orden=orden, offset=(pagina - 1) * tamano, tamano=tamano,
    )
    datos = []
    for r in items:
        tipo = repo.obtener_tipo(db, r.tipo_reserva_id)
        estado = repo.obtener_estado(db, r.estado_id)
        datos.append({
            "id": r.id, "estado": estado.codigo, "tipo_reserva": tipo.codigo, "id_unidad": r.id_unidad,
            "id_cuenta": r.id_cuenta, "observacion": r.observacion, "requiere_apoyo": r.requiere_apoyo, "created_at": r.created_at,
        })
    return datos, total


# --- §3.3 Disponibilidad -----------------------------------------------------------------


def consultar_disponibilidad(db, *, id_unidad: int, espacio_id: int | None, recurso_id: int | None, desde: date, hasta: date) -> dict:
    if (espacio_id is None) == (recurso_id is None):
        raise Validacion("Debe indicar exactamente uno de 'espacio_id' o 'recurso_id'.")

    config = rec_repo.obtener_config(db, id_unidad)
    if config is None:
        raise NoEncontrado("La unidad no tiene configuración de laboratorio.")
    horario_unidad = {"dias_atencion": config.dias_atencion, "hora_apertura": config.hora_apertura, "hora_cierre": config.hora_cierre}

    franjas = []
    if espacio_id is not None:
        for fecha, hora_i, hora_f in repo.franjas_ocupadas_espacio(db, espacio_id, desde, hasta):
            franjas.append({"fecha": fecha, "hora_inicio": hora_i, "hora_fin": hora_f, "disponible": False})
    else:
        if repo.tiene_compromiso_fisico_vigente(db, recurso_id):
            franjas.append({"fecha": desde, "hora_inicio": None, "hora_fin": None, "disponible": False})
        else:
            for fecha, hora_i, hora_f in repo.franjas_ocupadas_recurso_interno(db, recurso_id, desde, hasta):
                franjas.append({"fecha": fecha, "hora_inicio": hora_i, "hora_fin": hora_f, "disponible": False})

    return {"horario_unidad": horario_unidad, "franjas": franjas}
