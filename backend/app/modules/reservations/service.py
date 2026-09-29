"""Servicio de reservations (API-13/API-14): creación, edición, consulta,
disponibilidad, preparación de lista de espera, gestión por el Técnico,
propuestas de periodo y ejecución.

Dueño de la transacción y de la selección de estrategia
(`architecture.md`): comprueba acceso, carga datos, selecciona la
`ReservationStrategy` por `tipo_reserva`, construye el `Reserva` Context,
delega la decisión y persiste el resultado con el repositorio. Ni
`Reserva` ni las estrategias ejecutan SQL ni confirman transacciones.

**Fuera de alcance de API-14, a propósito**: consulta y exportación de la
FGL 030 ya generada (§7, orden-salida/orden-salida.pdf), calendario `.ics` y
exportación de reservas (§8) son API-15. El proceso automático de horario
que hace avanzar espacio/interno por el mero paso del tiempo sin ninguna
petición HTTP (RN-TIP-PE-25/27, RN-TIP-RI-08/09) exige un planificador que
no forma parte de ningún endpoint de este contrato; solo se implementa aquí
el caso ya cubierto por creación y aprobación (`_al_aprobar`), cuando la
franja ya está vigente en el instante de la operación.
"""

from __future__ import annotations

import io
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
    SolicitudInvalida,
    TipoNoAdmitido,
    Validacion,
    VinculacionRequerida,
)
from app.modules.espacios import repository as esp_repo
from app.modules.notifications import productor as notificador
from app.modules.researchs import repository as inv_repo
from app.modules.reservations import repository as repo
from app.modules.reservations import schemas
from app.modules.reservations.domain.reserva import Reserva
from app.modules.reservations.policies import acceso as acceso_policy
from app.modules.reservations.policies import apoyo as apoyo_policy
from app.modules.reservations.policies import contexto as contexto_policy
from app.modules.reservations.policies import prestamo_fisico as prestamo_policy
from app.modules.reservations.policies import propuestas as propuestas_policy
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


def opciones_contexto(db, contexto: ContextoAutenticado) -> dict:
    """§2.9. Qué contextos puede elegir la cuenta al reservar (RN-CTX-05, RN-CTX-08).

    `USUARIO`: solo sus vinculaciones activas y vigentes, más las actividades institucionales
    activas. `PERSONAL`: proyectos y semilleros activos del catálogo general, sin pasantías,
    trabajos de grado ni actividades (no se le consulta vinculación propia).
    """
    respuesta: dict = {
        "tipo_cuenta": contexto.tipo_cuenta,
        "proyectos": [], "semilleros": [], "pasantias": [], "trabajos_grado": [], "actividades": [],
    }

    if contexto.tipo_cuenta != "USUARIO":
        proyectos, _ = inv_repo.listar_proyectos(db, estado=True, busqueda=None, orden="nombre", offset=0, tamano=500)
        semilleros, _ = inv_repo.listar_semilleros(db, estado=True, busqueda=None, orden="nombre", offset=0, tamano=500)
        respuesta["proyectos"] = [{"id": p.id_proyecto, "codigo": p.codigo, "nombre": p.nombre} for p in proyectos]
        respuesta["semilleros"] = [{"id": s.id_semillero, "codigo": s.codigo, "nombre": s.nombre} for s in semilleros]
        return respuesta

    def entidades_vigentes(tipo: str):
        campo = inv_repo.campo_fk_vinculacion(tipo)
        for vinculo in inv_repo.vinculaciones_usuario(db, tipo, contexto.id_usuario):
            if not vinculo.estado:
                continue
            entidad = inv_repo.obtener_entidad(db, tipo, getattr(vinculo, campo))
            if entidad is not None and entidad.estado:
                yield entidad

    respuesta["proyectos"] = [
        {"id": e.id_proyecto, "codigo": e.codigo, "nombre": e.nombre} for e in entidades_vigentes("proyectos")
    ]
    respuesta["semilleros"] = [
        {"id": e.id_semillero, "codigo": e.codigo, "nombre": e.nombre} for e in entidades_vigentes("semilleros")
    ]
    respuesta["pasantias"] = [
        {"id": e.id_pasantia, "universidad": e.universidad, "docente_nombre": e.docente_itm_nombre}
        for e in entidades_vigentes("pasantias")
    ]
    respuesta["trabajos_grado"] = [
        {"id": e.id_trabajo_grado, "director_nombre": e.director_nombre} for e in entidades_vigentes("trabajos_grado")
    ]
    actividades, _ = inv_repo.listar_actividades(db, estado=True, dependencia=None, busqueda=None, offset=0, tamano=500)
    respuesta["actividades"] = [
        {"id": a.id_actividad, "nombre": a.nombre, "dependencia": a.dependencia} for a in actividades
    ]
    return respuesta


def opciones_acompanantes(db, proyecto_id: int | None, semillero_id: int | None, contexto: ContextoAutenticado) -> list[dict]:
    """§2.10. Cuentas que pueden acompañar: vinculación activa con el proyecto o el semillero (RN-ACO-02, RN-ACO-04)."""
    if proyecto_id is None and semillero_id is None:
        raise Validacion("Indica un proyecto o un semillero.")
    ids_usuario: set[int] = set()
    if proyecto_id is not None:
        proyecto = inv_repo.obtener_proyecto(db, proyecto_id)
        if proyecto is None or not proyecto.estado:
            raise NoEncontrado("El proyecto no existe o está deshabilitado.")
        ids_usuario.update(inv_repo.usuarios_vinculados(db, "proyectos", proyecto_id))
    if semillero_id is not None:
        semillero = inv_repo.obtener_semillero(db, semillero_id)
        if semillero is None or not semillero.estado:
            raise NoEncontrado("El semillero no existe o está deshabilitado.")
        ids_usuario.update(inv_repo.usuarios_vinculados(db, "semilleros", semillero_id))
    return [
        {"id_cuenta": id_cuenta, "nombre": nombre}
        for id_cuenta, nombre in repo.cuentas_activas_de_usuarios(db, sorted(ids_usuario))
        if id_cuenta != contexto.id_cuenta
    ]


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
    if datos.tipo_reserva == "LISTA_ESPERA":
        notificador.notificar_reserva(
            db, reserva.id, "LISTA_ESPERA_CAMBIO_ESTADO",
            f"LISTA_ESPERA_CAMBIO_ESTADO-{reserva.id}-{estado_codigo}",
            datos={"estado": estado_codigo},
        )
    else:
        notificador.notificar_reserva(db, reserva.id, "SOLICITUD_REGISTRADA", f"SOLICITUD_REGISTRADA-{reserva.id}")
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
    if tipo.codigo == "LISTA_ESPERA":
        no_aplicables = sorted({"recursos", "acompanantes", "campos_adicionales", "requiere_apoyo"} & cambios_entrada.keys())
        if no_aplicables:
            raise Validacion(f"LISTA_ESPERA no admite editar: {', '.join(no_aplicables)}.")

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


def _resumen_legible(db, reserva, tipo_codigo: str) -> dict:
    """Lo que una persona necesita ver en un listado sin abrir cada reserva: cuándo, qué, dónde y quién."""
    detalle = _detalle_por_tipo(db, reserva, tipo_codigo)
    asignaciones = repo.asignaciones_de_reserva(db, reserva.id, solo_vigentes=True)
    nombres = rec_repo.nombres_de_recursos(db, [a.recurso_id for a in asignaciones])

    if tipo_codigo in ("ESPACIO", "RECURSO_INTERNO"):
        periodo = {"fecha": detalle["fecha"], "hora_inicio": detalle["hora_inicio"], "hora_fin": detalle["hora_fin"]}
    elif tipo_codigo in ("RECURSO_CAMPUS", "RECURSO_EXTERNO"):
        periodo = {"fecha_salida": detalle["fecha_salida"], "fecha_devolucion_estimada": detalle["fecha_devolucion_estimada"]}
    else:
        periodo = None

    if tipo_codigo == "ESPACIO":
        objeto = repo.nombre_de_espacio(db, detalle["espacio_id"])
    elif tipo_codigo == "LISTA_ESPERA":
        texto = detalle.get("descripcion_necesidad") or ""
        objeto = texto if len(texto) <= 80 else texto[:77] + "..."
    else:
        principal = next((a for a in asignaciones if a.rol == "PRINCIPAL"), None)
        extras = len(asignaciones) - (1 if principal else 0)
        objeto = nombres.get(principal.recurso_id) if principal else None
        if objeto and extras > 0:
            objeto = f"{objeto} y {extras} más"

    unidad = rec_repo.obtener_unidad(db, reserva.id_unidad)
    return {
        "periodo": periodo,
        "objeto": objeto,
        "unidad_nombre": unidad.nombre if unidad else None,
        "solicitante_nombre": repo.nombre_de_cuenta(db, reserva.id_cuenta),
    }


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
    asignaciones = repo.asignaciones_de_reserva(db, id_reserva)
    nombres_recursos = rec_repo.nombres_de_recursos(db, [a.recurso_id for a in asignaciones])
    for a in asignaciones:
        reserva_causante_id = None
        if a.reserva_causante_id is not None:
            causante = repo.obtener_reserva(db, a.reserva_causante_id)
            if causante is not None and acceso_policy.validar_ambito_lectura(contexto, causante.id_cuenta, causante.id_unidad):
                reserva_causante_id = a.reserva_causante_id
        recursos.append({
            "reserva_recurso_id": a.id, "recurso_id": a.recurso_id, "nombre": nombres_recursos.get(a.recurso_id),
            "rol": a.rol, "estado_asignacion": a.estado_asignacion,
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

    propuesta = repo.obtener_propuesta_vigente(db, id_reserva)
    propuesta_vigente = None if propuesta is None else {
        "id": propuesta.id, "origen": propuesta.origen, "fecha_inicio_propuesta": propuesta.fecha_inicio_propuesta,
        "fecha_fin_propuesta": propuesta.fecha_fin_propuesta, "hora_inicio": propuesta.hora_inicio,
        "hora_fin": propuesta.hora_fin, "motivo": propuesta.motivo, "created_at": propuesta.created_at,
    }

    return {
        "id": reserva.id, "estado": estado.codigo, "tipo_reserva": tipo.codigo, "id_unidad": reserva.id_unidad,
        "id_cuenta": reserva.id_cuenta, "observacion": reserva.observacion, "requiere_apoyo": reserva.requiere_apoyo,
        "created_at": reserva.created_at, "updated_at": reserva.updated_at, "fecha_aprobacion": reserva.fecha_aprobacion,
        "fecha_cancelacion": reserva.fecha_cancelacion, "motivo_cancelacion": reserva.motivo_cancelacion,
        "detalle": {**_detalle_por_tipo(db, reserva, tipo.codigo), **(
            {"espacio_nombre": repo.nombre_de_espacio(db, _detalle_por_tipo(db, reserva, tipo.codigo)["espacio_id"])}
            if tipo.codigo == "ESPACIO" else {}
        )},
        "unidad_nombre": (lambda u: u.nombre if u else None)(rec_repo.obtener_unidad(db, reserva.id_unidad)),
        "solicitante_nombre": repo.nombre_de_cuenta(db, reserva.id_cuenta),
        "contexto": _contexto_dict(repo.obtener_contexto(db, id_reserva)),
        "recursos": recursos,
        "acompanantes": repo.acompanantes_de_reserva(db, id_reserva),
        "acompanantes_detalle": [
            {"id_cuenta": c, "nombre": repo.nombre_de_cuenta(db, c)} for c in repo.acompanantes_de_reserva(db, id_reserva)
        ],
        "campos_adicionales": [
            {"campo_id": c.campo_id, "campo_nombre": c.campo_nombre_snapshot, "valor_texto": c.valor_texto, "opcion_id": c.opcion_id, "opcion_nombre": c.opcion_nombre_snapshot}
            for c in repo.campos_valores_de_reserva(db, id_reserva)
        ],
        "historial": [
            {
                "estado_anterior": (repo.obtener_estado(db, h.estado_anterior_id).codigo if h.estado_anterior_id else None),
                "estado_nuevo": repo.obtener_estado(db, h.estado_nuevo_id).codigo,
                "actor_cuenta_id": h.actor_cuenta_id, "actor_nombre": repo.nombre_de_cuenta(db, h.actor_cuenta_id),
                "motivo": h.motivo, "created_at": h.created_at,
            }
            for h in repo.historial_de_reserva(db, id_reserva)
        ],
        "propuesta_vigente": propuesta_vigente,
        "lista_espera": lista_espera_extra,
    }


def _fecha_de_filtro(valor, nombre: str) -> date | None:
    if valor in (None, ""):
        return None
    if isinstance(valor, date):
        return valor
    try:
        return date.fromisoformat(str(valor))
    except ValueError:
        raise Validacion(f"'{nombre}' debe ser una fecha AAAA-MM-DD.") from None


def listar_reservas(db, filtros: dict, pagina: int, tamano: int, orden: str | None, contexto: ContextoAutenticado) -> tuple[list[dict], int]:
    id_cuenta = None
    id_unidad = filtros.get("id_unidad")
    if contexto.rol == "USUARIO" or (contexto.rol == "TECNICO" and contexto.unidades_autorizadas == []):
        id_cuenta = contexto.id_cuenta
    elif contexto.rol == "TECNICO":
        id_unidad = id_unidad or (contexto.unidades_autorizadas[0] if contexto.unidades_autorizadas != "GLOBAL" else None)
        if contexto.unidades_autorizadas != "GLOBAL" and id_unidad not in contexto.unidades_autorizadas:
            id_cuenta = contexto.id_cuenta  # fuera de su unidad: solo lo propio

    desde = _fecha_de_filtro(filtros.get("desde"), "desde")
    hasta = _fecha_de_filtro(filtros.get("hasta"), "hasta")
    if desde is not None and hasta is not None and desde > hasta:
        raise Validacion("'desde' no puede ser posterior a 'hasta'.")
    items, total = repo.listar_reservas(
        db, id_cuenta=id_cuenta, id_unidad=id_unidad, estado_codigo=filtros.get("estado"),
        tipo_codigo=filtros.get("tipo_reserva"), desde=desde, hasta=hasta,
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
            **_resumen_legible(db, r, tipo.codigo),
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


# --- §4.1 Aprobación --------------------------------------------------------------------


def _asignacion_dict(a) -> dict:
    return {
        "reserva_recurso_id": a.id, "recurso_id": a.recurso_id, "rol": a.rol, "estado_asignacion": a.estado_asignacion,
        "incorporado_at": a.incorporado_at, "retirado_at": a.retirado_at, "causa_retiro": a.causa_retiro,
        "reserva_causante_id": a.reserva_causante_id,
    }


def aprobar_reserva(db, id_reserva: int, cuerpo: schemas.AprobacionCuerpo, contexto: ContextoAutenticado) -> dict:
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None:
        raise NoEncontrado()
    exigir_permiso(db, contexto.id_cuenta, "reservas.administrar", id_unidad=reserva.id_unidad)
    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    estado_actual = repo.obtener_estado(db, reserva.estado_id)
    if estado_actual.codigo != "SOLICITADA":
        raise EstadoIncompatible()
    if tipo.codigo != "LISTA_ESPERA" and cuerpo.material_recibido is not None:
        raise Validacion("material_recibido no se admite para este tipo de reserva.")

    ahora = _ahora()
    strategy = selector.seleccionar(tipo.codigo)
    reserva_ctx = Reserva(tipo_codigo=tipo.codigo, strategy=strategy, cabecera=reserva)

    if tipo.codigo == "LISTA_ESPERA":
        detalle_le = repo.obtener_detalle_lista_espera(db, id_reserva)
        formulario = repo.obtener_formulario_lista_espera(db, id_reserva)
        datos_op = {"material_recibido": cuerpo.material_recibido}
        condiciones = {"viable": detalle_le.viable, "formulario": formulario}
    else:
        config = rec_repo.obtener_config(db, reserva.id_unidad)
        detalle = _detalle_por_tipo(db, reserva, tipo.codigo)
        recursos = [{"recurso_id": a.recurso_id, "rol": a.rol} for a in repo.asignaciones_de_reserva(db, id_reserva, solo_vigentes=True)]
        datos_op = {"detalle": detalle, "recursos": recursos}
        condiciones = {"db": db, "config": config, "ahora": ahora, "excluir_reserva_id": id_reserva}

    reserva_ctx.validar("aprobar", datos_op, condiciones)

    estado_aprobada_id = repo.obtener_estado_id_codigo(db, "APROBADA")
    estado_anterior_id = reserva.estado_id
    reserva.estado_id = estado_aprobada_id
    repo.registrar_historial(db, reserva_id=id_reserva, estado_anterior_id=estado_anterior_id, estado_nuevo_id=estado_aprobada_id, actor_cuenta_id=contexto.id_cuenta, motivo=cuerpo.observacion)

    detalle_extra = None
    if tipo.codigo == "LISTA_ESPERA":
        reserva.fecha_aprobacion = ahora
        detalle_le.fecha_recepcion_material = ahora
        detalle_extra = {"fecha_recepcion_material": ahora}
    else:
        _al_aprobar(db, reserva, contexto, ahora, tipo.codigo)

    db.commit()
    db.refresh(reserva)
    estado_final = repo.obtener_estado(db, reserva.estado_id)
    if tipo.codigo == "LISTA_ESPERA":
        notificador.notificar_reserva(
            db, reserva.id, "LISTA_ESPERA_CAMBIO_ESTADO",
            f"LISTA_ESPERA_CAMBIO_ESTADO-{reserva.id}-APROBADA",
            datos={"estado": "APROBADA"},
        )
    else:
        notificador.notificar_reserva(db, reserva.id, "RESERVA_APROBADA", f"RESERVA_APROBADA-{reserva.id}")
    return {"id": reserva.id, "estado": estado_final.codigo, "fecha_aprobacion": reserva.fecha_aprobacion, "detalle": detalle_extra}


# --- §4.2 Rechazo ------------------------------------------------------------------------


def rechazar_reserva(db, id_reserva: int, cuerpo: schemas.RechazoCuerpo, contexto: ContextoAutenticado) -> dict:
    """Sin dispatch por estrategia: la precondición de estado y el motivo
    son comunes a los cinco tipos; una vez fuera de SOLICITADA/APROBADA
    EN_EJECUCION ya implica entrega física (campus/externo) o inicio
    automático (espacio/interno), así que RN-DIS-06 queda cubierto por el
    propio chequeo de estado, sin una condición adicional por tipo."""
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None:
        raise NoEncontrado()
    exigir_permiso(db, contexto.id_cuenta, "reservas.administrar", id_unidad=reserva.id_unidad)
    estado_actual = repo.obtener_estado(db, reserva.estado_id)
    if estado_actual.codigo not in ("SOLICITADA", "APROBADA"):
        raise EstadoIncompatible()
    if not (cuerpo.motivo or "").strip():
        raise Validacion("motivo es obligatorio.")

    estado_rechazada_id = repo.obtener_estado_id_codigo(db, "RECHAZADA")
    estado_anterior_id = reserva.estado_id
    reserva.estado_id = estado_rechazada_id
    repo.registrar_historial(db, reserva_id=id_reserva, estado_anterior_id=estado_anterior_id, estado_nuevo_id=estado_rechazada_id, actor_cuenta_id=contexto.id_cuenta, motivo=cuerpo.motivo)
    db.commit()
    notificador.notificar_reserva(
        db, id_reserva, "RESERVA_RECHAZADA", f"RESERVA_RECHAZADA-{id_reserva}",
        datos={"motivo": cuerpo.motivo},
    )
    return {"id": id_reserva, "estado": "RECHAZADA", "motivo": cuerpo.motivo}


# --- §4.3/§4.4 Recursos genéricos ---------------------------------------------------------

_TIPOS_CON_RECURSOS_GENERICOS = ("ESPACIO", "RECURSO_INTERNO")
_ESTADOS_RECURSOS_GENERICOS = ("SOLICITADA", "APROBADA", "EN_EJECUCION")


def agregar_recursos(db, id_reserva: int, cuerpo: schemas.RecursosAgregarCuerpo, contexto: ContextoAutenticado) -> list[dict]:
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None:
        raise NoEncontrado()
    exigir_permiso(db, contexto.id_cuenta, "reservas.administrar", id_unidad=reserva.id_unidad)
    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    if tipo.codigo not in _TIPOS_CON_RECURSOS_GENERICOS:
        raise TipoNoAdmitido()
    estado_actual = repo.obtener_estado(db, reserva.estado_id)
    if estado_actual.codigo not in _ESTADOS_RECURSOS_GENERICOS:
        raise EstadoIncompatible()

    ahora = _ahora()
    incorporado_at = ahora if estado_actual.codigo == "EN_EJECUCION" else None
    detalle = _detalle_por_tipo(db, reserva, tipo.codigo)
    strategy = selector.seleccionar(tipo.codigo)
    reserva_ctx = Reserva(tipo_codigo=tipo.codigo, strategy=strategy, cabecera=reserva)
    datos_op = {"detalle": detalle, "recursos": [{"recurso_id": r.recurso_id, "rol": r.rol} for r in cuerpo.recursos]}
    condiciones = {"db": db, "incorporado_at": incorporado_at}

    reserva_ctx.validar("agregar_recursos", datos_op, condiciones)
    resultado = reserva_ctx.determinar_cambios("agregar_recursos", datos_op, condiciones)

    creados = [
        repo.crear_asignacion_recurso(db, reserva_id=id_reserva, recurso_id=r["recurso_id"], rol=r["rol"], incorporado_at=incorporado_at)
        for r in resultado["recursos"]
    ]
    db.commit()
    if estado_actual.codigo == "APROBADA":
        notificador.notificar_reserva(
            db, id_reserva, "RECURSO_ADICIONAL_INCORPORADO",
            f"RECURSO_ADICIONAL_INCORPORADO-{id_reserva}-{creados[0].id}",
        )
    return [_asignacion_dict(a) for a in creados]


def retirar_recurso(db, id_reserva: int, reserva_recurso_id: int, contexto: ContextoAutenticado) -> None:
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None:
        raise NoEncontrado()
    exigir_permiso(db, contexto.id_cuenta, "reservas.administrar", id_unidad=reserva.id_unidad)
    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    if tipo.codigo not in _TIPOS_CON_RECURSOS_GENERICOS:
        raise TipoNoAdmitido()
    estado_actual = repo.obtener_estado(db, reserva.estado_id)
    if estado_actual.codigo not in _ESTADOS_RECURSOS_GENERICOS:
        raise EstadoIncompatible()

    asignacion = repo.obtener_asignacion(db, reserva_recurso_id)
    if asignacion is None or asignacion.reserva_id != id_reserva or asignacion.estado_asignacion != "ASIGNADO":
        raise NoEncontrado()

    strategy = selector.seleccionar(tipo.codigo)
    reserva_ctx = Reserva(tipo_codigo=tipo.codigo, strategy=strategy, cabecera=reserva)
    reserva_ctx.validar("retirar_recurso", {"asignacion": asignacion}, {})

    db.delete(asignacion)
    db.commit()


# --- §5 Propuestas de periodo --------------------------------------------------------------


def _propuesta_dict(p) -> dict:
    return {
        "id": p.id, "reserva_id": p.reserva_id, "origen": p.origen, "fecha_inicio_propuesta": p.fecha_inicio_propuesta,
        "fecha_fin_propuesta": p.fecha_fin_propuesta, "hora_inicio": p.hora_inicio, "hora_fin": p.hora_fin,
        "motivo": p.motivo, "estado": p.estado, "creada_por": p.creada_por, "resuelta_por": p.resuelta_por,
        "created_at": p.created_at, "resuelta_at": p.resuelta_at,
    }


def crear_propuesta(db, id_reserva: int, cuerpo: schemas.PropuestaCrear, contexto: ContextoAutenticado) -> dict:
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None or not acceso_policy.validar_ambito_lectura(contexto, reserva.id_cuenta, reserva.id_unidad):
        raise NoEncontrado()
    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    propuestas_policy.validar_tipo_admite_propuesta(tipo.codigo)
    estado_actual = repo.obtener_estado(db, reserva.estado_id)
    propuestas_policy.validar_estado_negociable(estado_actual.codigo)

    if contexto.id_cuenta == reserva.id_cuenta:
        origen = "USUARIO"
    else:
        exigir_permiso(db, contexto.id_cuenta, "reservas.administrar", id_unidad=reserva.id_unidad)
        origen = "TECNICO"

    if cuerpo.fecha_fin_propuesta < cuerpo.fecha_inicio_propuesta:
        raise Validacion("fecha_fin_propuesta debe ser posterior o igual a fecha_inicio_propuesta.")

    if tipo.codigo in ("RECURSO_CAMPUS", "RECURSO_EXTERNO"):
        orden_existente = repo.obtener_orden_por_reserva(db, id_reserva) is not None
        propuestas_policy.validar_sin_fgl(tipo.codigo, orden_existente)
        if cuerpo.hora_inicio is not None or cuerpo.hora_fin is not None:
            raise Validacion("hora_inicio/hora_fin no aplican a RECURSO_CAMPUS/RECURSO_EXTERNO.")
    else:
        if cuerpo.fecha_inicio_propuesta != cuerpo.fecha_fin_propuesta:
            raise Validacion("Para ESPACIO/RECURSO_INTERNO, fecha_inicio_propuesta debe ser igual a fecha_fin_propuesta.")
        if cuerpo.hora_inicio is None or cuerpo.hora_fin is None:
            raise Validacion("hora_inicio y hora_fin son obligatorias para ESPACIO/RECURSO_INTERNO.")
        if cuerpo.hora_inicio >= cuerpo.hora_fin:
            raise Validacion("hora_inicio debe ser anterior a hora_fin.")

    vigente = repo.obtener_propuesta_vigente(db, id_reserva)
    if vigente is not None:
        repo.resolver_propuesta(db, vigente, estado="SUSTITUIDA", resuelta_por=contexto.id_cuenta, resuelta_at=_ahora())

    nueva = repo.crear_propuesta(
        db, reserva_id=id_reserva, origen=origen, fecha_inicio_propuesta=cuerpo.fecha_inicio_propuesta,
        fecha_fin_propuesta=cuerpo.fecha_fin_propuesta, hora_inicio=cuerpo.hora_inicio, hora_fin=cuerpo.hora_fin,
        motivo=cuerpo.motivo, creada_por=contexto.id_cuenta,
    )
    db.commit()
    db.refresh(nueva)
    notificador.notificar_reserva(
        db, id_reserva, "PROPUESTA_PERIODO_REGISTRADA",
        f"PROPUESTA_PERIODO_REGISTRADA-{nueva.id}",
        datos={"motivo": nueva.motivo}, tecnicos=(origen == "USUARIO"),
    )
    return _propuesta_dict(nueva)


def aceptar_propuesta_vigente(db, id_reserva: int, contexto: ContextoAutenticado) -> dict:
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None or not acceso_policy.validar_ambito_lectura(contexto, reserva.id_cuenta, reserva.id_unidad):
        raise NoEncontrado()
    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    propuestas_policy.validar_tipo_admite_propuesta(tipo.codigo)
    estado_actual = repo.obtener_estado(db, reserva.estado_id)
    propuestas_policy.validar_estado_negociable(estado_actual.codigo)

    propuesta = repo.obtener_propuesta_vigente(db, id_reserva)
    if propuesta is None:
        raise NoEncontrado("No hay una propuesta vigente.")
    if propuesta.origen == "TECNICO":
        acceso_policy.validar_propietario(contexto, reserva.id_cuenta)
    else:
        exigir_permiso(db, contexto.id_cuenta, "reservas.administrar", id_unidad=reserva.id_unidad)

    if tipo.codigo in ("RECURSO_CAMPUS", "RECURSO_EXTERNO"):
        orden_existente = repo.obtener_orden_por_reserva(db, id_reserva) is not None
        propuestas_policy.validar_sin_fgl(tipo.codigo, orden_existente)

    ahora = _ahora()
    config = rec_repo.obtener_config(db, reserva.id_unidad)
    strategy = selector.seleccionar(tipo.codigo)
    reserva_ctx = Reserva(tipo_codigo=tipo.codigo, strategy=strategy, cabecera=reserva)

    detalle_propuesto = dict(_detalle_por_tipo(db, reserva, tipo.codigo))
    if tipo.codigo in ("ESPACIO", "RECURSO_INTERNO"):
        detalle_propuesto["fecha"] = propuesta.fecha_inicio_propuesta
        detalle_propuesto["hora_inicio"] = propuesta.hora_inicio
        detalle_propuesto["hora_fin"] = propuesta.hora_fin
    else:
        detalle_propuesto["fecha_salida"] = propuesta.fecha_inicio_propuesta
        detalle_propuesto["fecha_devolucion_estimada"] = propuesta.fecha_fin_propuesta

    datos_op = {
        "id_unidad": reserva.id_unidad,
        "detalle": detalle_propuesto,
        "recursos": [{"recurso_id": a.recurso_id, "rol": a.rol} for a in repo.asignaciones_de_reserva(db, id_reserva, solo_vigentes=True)],
        "acompanantes": repo.acompanantes_de_reserva(db, id_reserva),
        "campos_adicionales": [{"campo_id": c.campo_id} for c in repo.campos_valores_de_reserva(db, id_reserva)],
    }
    condiciones = {"db": db, "config": config, "ahora": ahora, "excluir_reserva_id": id_reserva}

    reserva_ctx.validar("editar", datos_op, condiciones)
    resultado = reserva_ctx.determinar_cambios("editar", datos_op, condiciones)

    if "detalle_espacio" in resultado:
        d = repo.obtener_detalle_espacio(db, id_reserva)
        d.fecha, d.hora_inicio, d.hora_fin = detalle_propuesto["fecha"], detalle_propuesto["hora_inicio"], detalle_propuesto["hora_fin"]
    elif "detalle_interno" in resultado:
        d = repo.obtener_detalle_interno(db, id_reserva)
        d.fecha, d.hora_inicio, d.hora_fin = detalle_propuesto["fecha"], detalle_propuesto["hora_inicio"], detalle_propuesto["hora_fin"]
    elif "detalle_campus" in resultado:
        d = repo.obtener_detalle_campus(db, id_reserva)
        d.fecha_salida, d.fecha_devolucion_estimada = detalle_propuesto["fecha_salida"], detalle_propuesto["fecha_devolucion_estimada"]
    elif "detalle_externo" in resultado:
        d = repo.obtener_detalle_externo(db, id_reserva)
        d.fecha_salida, d.fecha_devolucion_estimada = detalle_propuesto["fecha_salida"], detalle_propuesto["fecha_devolucion_estimada"]

    repo.resolver_propuesta(db, propuesta, estado="ACEPTADA", resuelta_por=contexto.id_cuenta, resuelta_at=ahora)
    reserva.updated_at = ahora
    db.commit()
    notificador.anular_por_cambio(db, id_reserva, "Reprogramación por propuesta aceptada.")
    return obtener_reserva_detalle(db, id_reserva, contexto)


def rechazar_propuesta_vigente(db, id_reserva: int, contexto: ContextoAutenticado) -> dict:
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None or not acceso_policy.validar_ambito_lectura(contexto, reserva.id_cuenta, reserva.id_unidad):
        raise NoEncontrado()
    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    propuestas_policy.validar_tipo_admite_propuesta(tipo.codigo)
    estado_actual = repo.obtener_estado(db, reserva.estado_id)
    propuestas_policy.validar_estado_negociable(estado_actual.codigo)

    propuesta = repo.obtener_propuesta_vigente(db, id_reserva)
    if propuesta is None:
        raise NoEncontrado("No hay una propuesta vigente.")
    if propuesta.origen == "TECNICO":
        acceso_policy.validar_propietario(contexto, reserva.id_cuenta)
    else:
        exigir_permiso(db, contexto.id_cuenta, "reservas.administrar", id_unidad=reserva.id_unidad)

    repo.resolver_propuesta(db, propuesta, estado="RECHAZADA", resuelta_por=contexto.id_cuenta, resuelta_at=_ahora())
    db.commit()
    return _propuesta_dict(propuesta)


# --- §6.1 Ejecución ------------------------------------------------------------------------


def ejecutar_reserva(db, id_reserva: int, cuerpo: schemas.EjecucionCuerpo, contexto: ContextoAutenticado) -> dict:
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None:
        raise NoEncontrado()
    exigir_permiso(db, contexto.id_cuenta, "reservas.administrar", id_unidad=reserva.id_unidad)
    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    estado_actual = repo.obtener_estado(db, reserva.estado_id)
    strategy = selector.seleccionar(tipo.codigo)
    reserva_ctx = Reserva(tipo_codigo=tipo.codigo, strategy=strategy, cabecera=reserva)

    if tipo.codigo == "LISTA_ESPERA":
        if cuerpo.recursos is not None:
            raise Validacion("LISTA_ESPERA no admite recursos en esta operación.")
        datos_op, condiciones = {}, {"estado_actual": estado_actual.codigo}
    else:
        recursos_entrega = cuerpo.recursos or []
        datos_op = {"recursos": [{"reserva_recurso_id": r.reserva_recurso_id, "observacion_entrega": r.observacion_entrega} for r in recursos_entrega]}
        condiciones = {"db": db, "estado_actual": estado_actual.codigo}

    reserva_ctx.validar("ejecutar", datos_op, condiciones)
    resultado = reserva_ctx.determinar_cambios("ejecutar", datos_op, condiciones)

    ahora = _ahora()
    estado_ejecucion_id = repo.obtener_estado_id_codigo(db, "EN_EJECUCION")
    estado_anterior_id = reserva.estado_id
    reserva.estado_id = estado_ejecucion_id
    repo.registrar_historial(db, reserva_id=id_reserva, estado_anterior_id=estado_anterior_id, estado_nuevo_id=estado_ejecucion_id, actor_cuenta_id=contexto.id_cuenta, motivo=None)

    for entrega in resultado.get("entregas") or []:
        repo.crear_ejecucion_recurso(
            db, reserva_recurso_id=entrega["reserva_recurso_id"], entregado_por=contexto.id_cuenta,
            entregado_at=ahora, observacion_entrega=entrega.get("observacion_entrega"),
        )

    db.commit()
    if tipo.codigo == "LISTA_ESPERA":
        notificador.notificar_reserva(
            db, id_reserva, "LISTA_ESPERA_CAMBIO_ESTADO",
            f"LISTA_ESPERA_CAMBIO_ESTADO-{id_reserva}-EN_EJECUCION",
            datos={"estado": "EN_EJECUCION"},
        )
    return {"id": id_reserva, "estado": "EN_EJECUCION", "detalle": None}


# --- §6.2 Finalización ---------------------------------------------------------------------


def finalizar_reserva(db, id_reserva: int, cuerpo: schemas.FinalizacionCuerpo, contexto: ContextoAutenticado) -> dict:
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None:
        raise NoEncontrado()
    exigir_permiso(db, contexto.id_cuenta, "reservas.administrar", id_unidad=reserva.id_unidad)
    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    estado_actual = repo.obtener_estado(db, reserva.estado_id)
    strategy = selector.seleccionar(tipo.codigo)
    reserva_ctx = Reserva(tipo_codigo=tipo.codigo, strategy=strategy, cabecera=reserva)

    if tipo.codigo == "LISTA_ESPERA":
        if cuerpo.recursos is not None:
            raise Validacion("LISTA_ESPERA no admite recursos en esta operación.")
        datos_op = {"horas_ejecucion": cuerpo.horas_ejecucion}
        condiciones = {"estado_actual": estado_actual.codigo}
    else:
        if cuerpo.horas_ejecucion is not None:
            raise Validacion("horas_ejecucion no aplica a este tipo de reserva.")
        recursos_devolucion = cuerpo.recursos or []
        datos_op = {"recursos": [{"reserva_recurso_id": r.reserva_recurso_id, "observacion_devolucion": r.observacion_devolucion} for r in recursos_devolucion]}
        condiciones = {"db": db, "estado_actual": estado_actual.codigo}

    reserva_ctx.validar("finalizar", datos_op, condiciones)
    resultado = reserva_ctx.determinar_cambios("finalizar", datos_op, condiciones)

    ahora = _ahora()
    estado_finalizada_id = repo.obtener_estado_id_codigo(db, "FINALIZADA")
    estado_anterior_id = reserva.estado_id
    reserva.estado_id = estado_finalizada_id
    repo.registrar_historial(db, reserva_id=id_reserva, estado_anterior_id=estado_anterior_id, estado_nuevo_id=estado_finalizada_id, actor_cuenta_id=contexto.id_cuenta, motivo=None)

    detalle_extra = None
    if tipo.codigo == "LISTA_ESPERA":
        detalle_le = repo.obtener_detalle_lista_espera(db, id_reserva)
        detalle_le.horas_ejecucion = cuerpo.horas_ejecucion
        detalle_extra = {"horas_ejecucion": cuerpo.horas_ejecucion}
    else:
        for devolucion in resultado.get("devoluciones") or []:
            ejecucion = repo.entrega_abierta_de_asignacion(db, devolucion["reserva_recurso_id"])
            ejecucion.recibido_por = contexto.id_cuenta
            ejecucion.devuelto_at = ahora
            ejecucion.observacion_devolucion = devolucion.get("observacion_devolucion")

    db.commit()
    if tipo.codigo == "LISTA_ESPERA":
        notificador.notificar_reserva(
            db, id_reserva, "LISTA_ESPERA_CAMBIO_ESTADO",
            f"LISTA_ESPERA_CAMBIO_ESTADO-{id_reserva}-FINALIZADA",
            datos={"estado": "FINALIZADA"},
        )
    return {"id": id_reserva, "estado": "FINALIZADA", "detalle": detalle_extra}


# --- §6.3 Cancelación ----------------------------------------------------------------------


def cancelar_reserva(db, id_reserva: int, cuerpo: schemas.CancelacionCuerpo, contexto: ContextoAutenticado) -> dict:
    """Sin dispatch por estrategia: RN-CAN-02 se resuelve uniformemente por
    estado en los cinco tipos, porque `EN_EJECUCION` siempre significa que
    la ejecución ya inició (automática en espacio/interno, entrega física en
    campus/externo, inicio de fabricación/prestación en lista de espera)."""
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None:
        raise NoEncontrado()
    if contexto.id_cuenta != reserva.id_cuenta:
        exigir_permiso(db, contexto.id_cuenta, "reservas.administrar", id_unidad=reserva.id_unidad)

    estado_actual = repo.obtener_estado(db, reserva.estado_id)
    if estado_actual.codigo not in ("SOLICITADA", "APROBADA"):
        raise EstadoIncompatible("La reserva ya inició su ejecución o está en un estado terminal.")

    ahora = _ahora()
    estado_cancelada_id = repo.obtener_estado_id_codigo(db, "CANCELADA")
    estado_anterior_id = reserva.estado_id
    reserva.estado_id = estado_cancelada_id
    reserva.fecha_cancelacion = ahora
    reserva.motivo_cancelacion = cuerpo.motivo
    repo.registrar_historial(db, reserva_id=id_reserva, estado_anterior_id=estado_anterior_id, estado_nuevo_id=estado_cancelada_id, actor_cuenta_id=contexto.id_cuenta, motivo=cuerpo.motivo)
    db.commit()
    notificador.anular_por_cambio(db, id_reserva, "Cancelación de la reserva.")
    notificador.notificar_reserva(db, id_reserva, "RESERVA_CANCELADA", f"RESERVA_CANCELADA-{id_reserva}")
    return {"id": id_reserva, "estado": "CANCELADA", "detalle": None}


# --- §7 Orden de salida (API-15) ---------------------------------------------------------
#
# Solo lectura de snapshots inmutables: nada aquí genera, modifica ni
# versiona la orden. La FGL se generó al aprobar (API-13/API-14).


_TIPOS_CON_ORDEN = ("RECURSO_CAMPUS", "RECURSO_EXTERNO")


def _orden_dict(db, orden) -> dict:
    return {
        "id": orden.id,
        "reserva_id": orden.reserva_id,
        "fecha_generacion": orden.fecha_generacion,
        "razon_solicitud": orden.razon_solicitud,
        "nombre_actividad_evento": orden.nombre_actividad_evento,
        "lugar_nombre": orden.lugar_nombre,
        "lugar_direccion": orden.lugar_direccion,
        "dependencia_solicitante_snapshot": orden.dependencia_solicitante_snapshot,
        "fecha_retiro_snapshot": orden.fecha_retiro_snapshot,
        "fecha_regreso_snapshot": orden.fecha_regreso_snapshot,
        "proyecto_codigo_snapshot": orden.proyecto_codigo_snapshot,
        "responsable_nombre_snapshot": orden.responsable_nombre_snapshot,
        "responsable_cedula_snapshot": orden.responsable_cedula_snapshot,
        "responsable_correo_snapshot": orden.responsable_correo_snapshot,
        "responsable_telefono_snapshot": orden.responsable_telefono_snapshot,
        "observaciones": orden.observaciones,
        "actividades": repo.actividades_de_orden(db, orden.id),
        "items": [
            {
                "reserva_recurso_id": i.reserva_recurso_id,
                "placa_snapshot": i.placa_snapshot,
                "descripcion_snapshot": i.descripcion_snapshot,
                "bodega_snapshot": i.bodega_snapshot,
                "cc_snapshot": i.cc_snapshot,
                "fecha_compra_snapshot": i.fecha_compra_snapshot,
            }
            for i in repo.items_de_orden(db, orden.id)
        ],
    }


def obtener_orden(db, id_reserva: int, contexto: ContextoAutenticado) -> dict:
    """§7.1. Cabecera con snapshots, actividades e ítems. Sin firmas."""
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None or not acceso_policy.validar_ambito_lectura(contexto, reserva.id_cuenta, reserva.id_unidad):
        raise NoEncontrado()
    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    if tipo.codigo not in _TIPOS_CON_ORDEN:
        raise TipoNoAdmitido("Este tipo de reserva no genera orden de salida.")
    orden = repo.obtener_orden_por_reserva(db, id_reserva)
    if orden is None:
        raise NoEncontrado("La orden aún no se ha generado.")
    return _orden_dict(db, orden)


def generar_orden_pdf(db, id_reserva: int, contexto: ContextoAutenticado) -> bytes:
    """§7.2. Renderiza los snapshots a PDF listo para imprimir. Las firmas
    y recibidos se diligencian a mano sobre el papel (RN-TIP-RC-14)."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet

    orden = _orden_dict(db, _orden_exigida(db, id_reserva, contexto))
    estilos = getSampleStyleSheet()
    normal = estilos["Normal"]
    titulo = estilos["Heading1"]
    seccion = estilos["Heading2"]

    celdas = lambda etiqueta, valor: [Paragraph(f"<b>{etiqueta}</b>", normal), Paragraph(str(valor or "—"), normal)]  # noqa: E731

    historia = [
        Paragraph("FGL 030 — Orden de salida de equipos y herramientas", titulo),
        Paragraph(f"Reserva {orden['reserva_id']} · Generada {orden['fecha_generacion']}", normal),
        Spacer(1, 0.4 * cm),
        Paragraph("1. Información general", seccion),
        Table([
            celdas("Razón de la solicitud", orden["razon_solicitud"]),
            celdas("Actividad / evento", orden["nombre_actividad_evento"]),
            celdas("Lugar", f"{orden['lugar_nombre']} — {orden['lugar_direccion']}"),
            celdas("Dependencia solicitante", orden["dependencia_solicitante_snapshot"]),
            celdas("Retiro", orden["fecha_retiro_snapshot"]),
            celdas("Regreso", orden["fecha_regreso_snapshot"]),
            celdas("Proyecto", orden["proyecto_codigo_snapshot"]),
            celdas(
                "Responsable",
                f"{orden['responsable_nombre_snapshot']} · {orden['responsable_cedula_snapshot']} · "
                f"{orden['responsable_correo_snapshot']} · {orden['responsable_telefono_snapshot']}",
            ),
        ], colWidths=[5 * cm, 11 * cm]),
        Spacer(1, 0.4 * cm),
        Paragraph("Actividades asociadas", seccion),
        Paragraph(", ".join(orden["actividades"]) or "—", normal),
        Spacer(1, 0.4 * cm),
        Paragraph("2. Información técnica", seccion),
        Table(
            [["Descripción", "Placa", "Bodega", "C. costos", "Compra"]]
            + [
                [i["descripcion_snapshot"], i["placa_snapshot"], i["bodega_snapshot"], i["cc_snapshot"], i["fecha_compra_snapshot"]]
                for i in orden["items"]
            ],
            colWidths=[6 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm],
        ),
        Spacer(1, 0.6 * cm),
        Paragraph("3. Autorizaciones (firmas en papel)", seccion),
        Table([
            ["Jefe de laboratorio", "V.o.B.o. Parque I", "Bienes muebles"],
            ["", "", ""],
            ["Firma y fecha", "Firma y fecha", "Firma y fecha"],
        ], colWidths=[5.3 * cm, 5.3 * cm, 5.3 * cm]),
        Spacer(1, 0.4 * cm),
        Paragraph("4. Entrega y 5. Devolución (firmas en papel)", seccion),
        Table([
            ["Entrega: quien entrega / quien retira", "Devolución: quien regresa / quien recibe"],
            ["", ""],
            ["Firmas y fechas", "Firmas y fechas"],
        ], colWidths=[8 * cm, 8 * cm]),
    ]
    for flowable in historia:
        if isinstance(flowable, Table):
            flowable.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, "grey"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))

    buffer = io.BytesIO()
    SimpleDocTemplate(buffer, pagesize=letter, title=f"FGL-030 reserva {orden['reserva_id']}").build(historia)
    return buffer.getvalue()


def _orden_exigida(db, id_reserva: int, contexto: ContextoAutenticado):
    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None or not acceso_policy.validar_ambito_lectura(contexto, reserva.id_cuenta, reserva.id_unidad):
        raise NoEncontrado()
    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    if tipo.codigo not in _TIPOS_CON_ORDEN:
        raise TipoNoAdmitido("Este tipo de reserva no genera orden de salida.")
    orden = repo.obtener_orden_por_reserva(db, id_reserva)
    if orden is None:
        raise NoEncontrado("La orden aún no se ha generado.")
    return orden


# --- §8.1 Calendario (API-15) -------------------------------------------------------------


def generar_ics(db, id_reserva: int, contexto: ContextoAutenticado) -> str:
    """Archivo iCalendar de una reserva APROBADA de ESPACIO o RECURSO_INTERNO."""
    import io as _io

    reserva = repo.obtener_reserva(db, id_reserva)
    if reserva is None or not acceso_policy.validar_ambito_lectura(contexto, reserva.id_cuenta, reserva.id_unidad):
        raise NoEncontrado()
    tipo = repo.obtener_tipo(db, reserva.tipo_reserva_id)
    estado = repo.obtener_estado(db, reserva.estado_id)
    if tipo.codigo not in ("ESPACIO", "RECURSO_INTERNO"):
        raise TipoNoAdmitido("El calendario solo aplica a espacio y recurso interno.")
    if estado.codigo != "APROBADA":
        raise EstadoIncompatible("El calendario requiere una reserva aprobada.")

    ubicacion = ""
    if tipo.codigo == "ESPACIO":
        detalle = repo.obtener_detalle_espacio(db, id_reserva)
        espacio = esp_repo.obtener_espacio(db, detalle.espacio_id)
        inicio = datetime.combine(detalle.fecha, detalle.hora_inicio, tzinfo=_ZONA_OPERATIVA)
        fin = datetime.combine(detalle.fecha, detalle.hora_fin, tzinfo=_ZONA_OPERATIVA)
        resumen = f"Reserva {id_reserva} — {espacio.nombre}"
        if espacio.ubicacion:
            ubicacion = f"LOCATION:{_ics_texto(espacio.ubicacion)}\r\n"
    else:
        detalle = repo.obtener_detalle_interno(db, id_reserva)
        inicio = datetime.combine(detalle.fecha, detalle.hora_inicio, tzinfo=_ZONA_OPERATIVA)
        fin = datetime.combine(detalle.fecha, detalle.hora_fin, tzinfo=_ZONA_OPERATIVA)
        resumen = f"Reserva {id_reserva} — Recurso interno"

    lineas = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//ParqueI//Reservas//ES", "BEGIN:VEVENT",
        f"UID:reserva-{id_reserva}@reservas.itm.edu.co",
        f"DTSTART;TZID=America/Bogota:{inicio.strftime('%Y%m%dT%H%M%S')}",
        f"DTEND;TZID=America/Bogota:{fin.strftime('%Y%m%dT%H%M%S')}",
        f"SUMMARY:{_ics_texto(resumen)}",
        ubicacion.rstrip("\r\n"),
        "END:VEVENT", "END:VCALENDAR", "",
    ]
    return _io.StringIO("\r\n".join(l for l in lineas if l)).getvalue() + "\r\n"


def _ics_texto(valor: str) -> str:
    return valor.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


# --- §8.2 Exportación (API-15) ------------------------------------------------------------


_COLUMNAS_EXPORTACION = ("id", "estado", "tipo_reserva", "id_unidad", "id_cuenta", "observacion", "requiere_apoyo", "created_at")


def exportar_reservas(db, filtros: dict, formato: str, contexto: ContextoAutenticado) -> tuple[bytes, str, str]:
    """Exporta lo visible según filtro y ámbito (RN-REP-03). Permiso `reservas.exportar`."""
    import csv as _csv
    import io as _io

    if formato not in ("csv", "excel"):
        raise SolicitudInvalida("formato debe ser 'csv' o 'excel'.")
    exigir_permiso(db, contexto.id_cuenta, "reservas.exportar", id_unidad=filtros.get("id_unidad"))

    _, total = listar_reservas(db, dict(filtros), 1, 1, None, contexto)
    datos, _ = listar_reservas(db, dict(filtros), 1, total or 1, None, contexto)
    filas = [[d[c] for c in _COLUMNAS_EXPORTACION] for d in datos]

    if formato == "csv":
        buffer = _io.StringIO()
        escritor = _csv.writer(buffer)
        escritor.writerow(_COLUMNAS_EXPORTACION)
        escritor.writerows(filas)
        return buffer.getvalue().encode("utf-8"), "text/csv", "reservas.csv"

    import openpyxl

    libro = openpyxl.Workbook()
    hoja = libro.active
    hoja.append(list(_COLUMNAS_EXPORTACION))
    for fila in filas:
        hoja.append([str(v) if v is not None else "" for v in fila])
    buffer = _io.BytesIO()
    libro.save(buffer)
    return buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "reservas.xlsx"
