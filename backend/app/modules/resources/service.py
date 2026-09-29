"""Lógica de recursos y configuración del laboratorio (API-09).

Dueño de `RN-REC`, `RN-EQP`, `RN-MOB`, `RN-OTR`, `RN-ROL`, `RN-DES`, `RN-LAB`
(resources). Al deshabilitar un recurso `PRINCIPAL`, aplica el efecto mínimo
de `RN-CAN-04`/`RN-CAN-05` de reservations —cancelar o retirar la
asignación— porque hoy no existe un servicio de reservations al que
delegarlo (`API-13`/`API-14` no están construidos). **No reimplementa** la
exclusión de `RN-CAN-06` por estado de ejecución u orden de salida
generada: ninguna reserva puede alcanzar esos estados todavía, porque nada
puede crearlas. Cuando exista el servicio de reservations, este efecto se
delega ahí y se retira de aquí.

Cada escritura audita en la misma transacción (patrón de `AUTH-C1`).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core import audit
from app.core.authz import exigir_permiso
from app.core.deps import ContextoAutenticado
from app.core.errors import Conflicto, NoAutorizado, NoEncontrado, SolicitudInvalida, UnidadIncompatible, Validacion
from app.db.models.reservas import LaboratoriosConfig, Reservas
from app.modules.resources import repository as repo
from app.modules.resources import schemas

MOTIVO_DESHABILITACION = "Deshabilitación del recurso"

# Campos editables de la especialización por tipo (contrato §2.4).
_CAMPOS_MOBILIARIO_OTRO = {"nombre", "descripcion"}
_CAMPOS_EQUIPO = {
    "nombre_equipo", "placa", "serial", "marca", "modelo", "image_path", "manual_operacion",
    "requiere_calibracion", "guia_rapida", "instalador", "estado", "requiere_apoyo", "acreditado",
    "id_categoria", "proxima_fecha_calibracion", "proxima_fecha_mantenimiento",
    "frecuencia_calibracion", "frecuencia_mantenimiento",
}


def _permiso_escritura(db: Session, contexto: ContextoAutenticado, tipo: str, id_unidad: int) -> None:
    """Permiso administrativo por tipo (contrato §1). Para equipos, el
    Técnico exige ámbito en la unidad del equipo; el Administrador, alcance
    global. Para mobiliario/otro, `recursos.administrar` en su unidad."""
    if tipo == "EQUIPO":
        try:
            exigir_permiso(db, contexto.id_cuenta, "recursos.editar_equipos", id_unidad=id_unidad)
        except NoAutorizado:
            exigir_permiso(db, contexto.id_cuenta, "recursos.administrar_equipos", id_unidad=None)
    else:
        exigir_permiso(db, contexto.id_cuenta, "recursos.administrar", id_unidad=id_unidad)


def _especializacion_dict(tipo: str, fila) -> dict:
    if tipo == "EQUIPO":
        return {c: getattr(fila, c) for c in _CAMPOS_EQUIPO} | {
            "bodega": fila.bodega, "centro_costo": fila.centro_costo, "fecha_compra": fila.fecha_compra,
        }
    return {"nombre": fila.nombre, "descripcion": fila.descripcion}


def _recurso_detalle(recurso, especializacion) -> dict:
    return {
        "id": recurso.id, "tipo": recurso.tipo, "id_unidad": recurso.id_unidad,
        "habilitado": recurso.habilitado, "created_at": recurso.created_at, "updated_at": recurso.updated_at,
        "especializacion": _especializacion_dict(recurso.tipo, especializacion),
    }


# --- §2.1 Crear -----------------------------------------------------------------


def crear_recurso(db: Session, datos: schemas.RecursoCrear, contexto: ContextoAutenticado) -> dict:
    if repo.obtener_unidad(db, datos.id_unidad) is None:
        raise NoEncontrado("La unidad no existe.")

    if datos.tipo == "EQUIPO":
        exigir_permiso(db, contexto.id_cuenta, "recursos.administrar_equipos", id_unidad=None)
    else:
        exigir_permiso(db, contexto.id_cuenta, "recursos.administrar", id_unidad=datos.id_unidad)

    esp = datos.especializacion
    campos_admitidos = _CAMPOS_EQUIPO if datos.tipo == "EQUIPO" else _CAMPOS_MOBILIARIO_OTRO
    desconocidos = set(esp.keys()) - campos_admitidos
    if desconocidos:
        raise SolicitudInvalida(f"Campos no admitidos para {datos.tipo}: {', '.join(sorted(desconocidos))}.")

    if datos.tipo == "EQUIPO":
        if not esp.get("nombre_equipo", "").strip():
            raise Validacion("nombre_equipo es obligatorio.")
        placa = esp.get("placa")
        if placa and repo.existe_placa(db, placa):
            raise Conflicto("Ya existe un equipo con esa placa.")
        serial = esp.get("serial")
        if serial and repo.existe_serial(db, serial):
            raise Conflicto("Ya existe un equipo con ese serial.")
        id_categoria = esp.get("id_categoria")
        if id_categoria is not None and not repo.existe_categoria(db, id_categoria):
            raise NoEncontrado("La categoría no existe.")
    else:
        if not esp.get("nombre", "").strip():
            raise Validacion("nombre es obligatorio.")

    recurso = repo.crear_recurso(db, datos.id_unidad, datos.tipo)
    if datos.tipo == "EQUIPO":
        especializacion = repo.crear_equipo(db, recurso.id, **esp)
    else:
        especializacion = repo.crear_mobiliario_u_otro(
            db, datos.tipo, recurso.id, datos.id_unidad, esp["nombre"], esp.get("descripcion")
        )

    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="recursos.recursos", entidad_id=recurso.id,
        accion="CREAR_RECURSO", datos_nuevos={"tipo": datos.tipo, "id_unidad": datos.id_unidad},
    )
    db.commit()
    db.refresh(recurso)
    return {"id": recurso.id, "tipo": recurso.tipo, "id_unidad": recurso.id_unidad, "habilitado": recurso.habilitado}


# --- §2.2/§2.3 Consultar ---------------------------------------------------------


def obtener_recurso(db: Session, id_recurso: int) -> dict:
    recurso = repo.obtener_recurso(db, id_recurso)
    if recurso is None:
        raise NoEncontrado()
    especializacion = repo.obtener_especializacion(db, recurso.tipo, id_recurso)
    return _recurso_detalle(recurso, especializacion)


def listar_recursos(db: Session, filtros: dict, pagina: int, tamano: int, orden: str | None) -> tuple[list[dict], int]:
    items, total = repo.listar_recursos(
        db, id_unidad=filtros.get("id_unidad"), tipo=filtros.get("tipo"), habilitado=filtros.get("habilitado"),
        busqueda=filtros.get("busqueda"), reservable=filtros.get("reservable", False),
        orden=orden, offset=(pagina - 1) * tamano, tamano=tamano,
    )
    nombres = repo.nombres_de_recursos(db, [r.id for r in items])
    datos = [
        {"id": r.id, "tipo": r.tipo, "nombre": nombres.get(r.id), "id_unidad": r.id_unidad, "habilitado": r.habilitado}
        for r in items
    ]
    return datos, total


# --- §2.4 Editar especialización --------------------------------------------------


def actualizar_recurso(db: Session, id_recurso: int, datos: schemas.RecursoActualizar, contexto: ContextoAutenticado) -> dict:
    recurso = repo.obtener_recurso(db, id_recurso)
    if recurso is None:
        raise NoEncontrado()
    _permiso_escritura(db, contexto, recurso.tipo, recurso.id_unidad)

    especializacion = repo.obtener_especializacion(db, recurso.tipo, id_recurso)
    campos_admitidos = _CAMPOS_EQUIPO if recurso.tipo == "EQUIPO" else _CAMPOS_MOBILIARIO_OTRO
    cambios = datos.especializacion
    desconocidos = set(cambios.keys()) - campos_admitidos
    if desconocidos:
        raise SolicitudInvalida(f"Campos no admitidos para {recurso.tipo}: {', '.join(sorted(desconocidos))}.")

    if recurso.tipo == "EQUIPO":
        if "placa" in cambios and cambios["placa"] and repo.existe_placa(db, cambios["placa"], excluir_id=id_recurso):
            raise Conflicto("Ya existe un equipo con esa placa.")
        if "serial" in cambios and cambios["serial"] and repo.existe_serial(db, cambios["serial"], excluir_id=id_recurso):
            raise Conflicto("Ya existe un equipo con ese serial.")

    datos_anteriores = _especializacion_dict(recurso.tipo, especializacion)
    for campo, valor in cambios.items():
        setattr(especializacion, campo, valor)

    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad=f"recursos.{recurso.tipo.lower()}", entidad_id=id_recurso,
        accion="EDITAR_RECURSO", datos_anteriores=datos_anteriores, datos_nuevos=cambios,
    )
    db.commit()
    db.refresh(recurso)
    db.refresh(especializacion)
    return _recurso_detalle(recurso, especializacion)


# --- §2.5/§2.6 Habilitación -------------------------------------------------------


def impacto_deshabilitacion(db: Session, id_recurso: int, contexto: ContextoAutenticado) -> dict:
    recurso = repo.obtener_recurso(db, id_recurso)
    if recurso is None:
        raise NoEncontrado()
    _permiso_escritura(db, contexto, recurso.tipo, recurso.id_unidad)
    a_cancelar, a_retirar = repo.contar_impacto(db, id_recurso)
    return {"reservas_a_cancelar": a_cancelar, "reservas_a_retirar": a_retirar}


def cambiar_estado(db: Session, id_recurso: int, datos: schemas.EstadoActualizar, contexto: ContextoAutenticado) -> dict:
    recurso = repo.obtener_recurso(db, id_recurso)
    if recurso is None:
        raise NoEncontrado()
    _permiso_escritura(db, contexto, recurso.tipo, recurso.id_unidad)

    if datos.habilitado or not recurso.habilitado:
        # Reactivar, o deshabilitar algo ya deshabilitado: sin efecto sobre reservas.
        repo.cambiar_habilitado(db, recurso, datos.habilitado)
        audit.registrar(
            db, actor_cuenta_id=contexto.id_cuenta, entidad="recursos.recursos", entidad_id=id_recurso,
            accion="CAMBIAR_ESTADO_RECURSO", datos_nuevos={"habilitado": datos.habilitado},
        )
        db.commit()
        return {"id": id_recurso, "habilitado": datos.habilitado, "reservas_canceladas": 0, "reservas_afectadas": 0}

    # Deshabilitar un recurso habilitado: RN-DES-06/07.
    asignaciones = repo.asignaciones_vigentes(db, id_recurso)
    principales = [a for a in asignaciones if a.rol == "PRINCIPAL"]
    adicionales = [a for a in asignaciones if a.rol == "ADICIONAL"]

    if principales and not datos.confirmado:
        raise Conflicto(
            "Deshabilitar este recurso cancelará reservas futuras; confirme para continuar.",
            detalles=[{"reservas_a_cancelar": len(principales), "reservas_a_retirar": len(adicionales)}],
        )

    for asignacion in principales:
        reserva = db.get(Reservas, asignacion.reserva_id)
        repo.cancelar_reserva(db, reserva, MOTIVO_DESHABILITACION, contexto.id_cuenta)
        repo.retirar_asignacion(db, asignacion)
    for asignacion in adicionales:
        repo.retirar_asignacion(db, asignacion)

    repo.cambiar_habilitado(db, recurso, False)
    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="recursos.recursos", entidad_id=id_recurso,
        accion="CAMBIAR_ESTADO_RECURSO",
        datos_nuevos={"habilitado": False, "reservas_canceladas": len(principales), "reservas_afectadas": len(asignaciones)},
    )
    db.commit()
    from app.modules.notifications import productor as notificador

    for asignacion in principales:
        notificador.notificar_reserva(
            db, asignacion.reserva_id, "RESERVA_AFECTADA_DESHABILITACION",
            f"RESERVA_AFECTADA_DESHABILITACION-{asignacion.reserva_id}",
        )
    return {
        "id": id_recurso, "habilitado": False,
        "reservas_canceladas": len(principales), "reservas_afectadas": len(asignaciones),
    }


# --- §2.7 Reasignar unidad --------------------------------------------------------


def cambiar_unidad(db: Session, id_recurso: int, datos: schemas.UnidadActualizar, contexto: ContextoAutenticado) -> dict:
    exigir_permiso(db, contexto.id_cuenta, "recursos.reasignar_unidad", id_unidad=None)
    recurso = repo.obtener_recurso(db, id_recurso)
    if recurso is None:
        raise NoEncontrado()
    if repo.obtener_unidad(db, datos.id_unidad) is None:
        raise NoEncontrado("La unidad destino no existe.")
    unidad_espacio = repo.unidad_espacio_vinculado(db, id_recurso)
    if unidad_espacio is not None and unidad_espacio != datos.id_unidad:
        raise UnidadIncompatible("El recurso está asociado a un espacio de otra unidad.")

    especializacion = repo.obtener_especializacion(db, recurso.tipo, id_recurso)
    unidad_anterior = recurso.id_unidad
    repo.cambiar_unidad(db, recurso, datos.id_unidad, especializacion)

    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="recursos.recursos", entidad_id=id_recurso,
        accion="REASIGNAR_UNIDAD_RECURSO",
        datos_anteriores={"id_unidad": unidad_anterior}, datos_nuevos={"id_unidad": datos.id_unidad},
    )
    db.commit()
    db.refresh(recurso)
    return {"id": recurso.id, "tipo": recurso.tipo, "id_unidad": recurso.id_unidad, "habilitado": recurso.habilitado}


# --- §3 Configuración del laboratorio -----------------------------------------
# `hora_apertura`/`hora_cierre` no tienen valor por defecto: son NOT NULL sin
# DEFAULT en el modelo (parte de ck_laboratorios_config_horario), así que la
# primera vez que se configura una unidad son obligatorios.
_DEFAULTS_CONFIG = {
    "habilitado_reservas": True, "dias_atencion": [0, 1, 2, 3, 4, 5], "horario_atencion": {},
    "horas_antelacion": 0, "aprobacion_automatica": False, "notificar_por_correo": False,
    "mostrar_estado_reserva": False, "mostrar_reservista": False, "recordatorio_horas_antes": 24,
}


def _config_dict(db: Session, config) -> dict:
    return {
        "id_unidad": config.id_unidad, "habilitado_reservas": config.habilitado_reservas,
        "dias_atencion": config.dias_atencion, "hora_apertura": config.hora_apertura,
        "hora_cierre": config.hora_cierre, "horas_antelacion": config.horas_antelacion,
        "aprobacion_automatica": config.aprobacion_automatica,
        "recordatorio_horas_antes": config.recordatorio_horas_antes,
        "mostrar_estado_reserva": config.mostrar_estado_reserva,
        "mostrar_reservista": config.mostrar_reservista,
        "notificar_por_correo": config.notificar_por_correo,
        "tipos_reserva": repo.obtener_tipos_habilitados(db, config.id_unidad),
    }


def listar_laboratorios(db: Session) -> list[dict]:
    """§3.0. Catálogo de laboratorios, legible por cualquier cuenta autenticada."""
    return [
        {"id_unidad": id_unidad, "nombre": nombre, "habilitado_reservas": habilitado}
        for id_unidad, nombre, habilitado in repo.listar_laboratorios(db)
    ]


def obtener_configuracion(db: Session, id_unidad: int) -> dict:
    """§3.1. Lectura pública para cualquier cuenta autenticada (RN-DIS-07);
    el router solo exige sesión, no permiso."""
    if repo.obtener_unidad(db, id_unidad) is None:
        raise NoEncontrado("La unidad no existe.")
    config = repo.obtener_config(db, id_unidad)
    if config is None:
        raise NoEncontrado("La unidad todavía no tiene configuración de laboratorio.")
    return _config_dict(db, config)


def actualizar_configuracion(db: Session, id_unidad: int, datos: schemas.ConfiguracionActualizar, contexto: ContextoAutenticado) -> dict:
    exigir_permiso(db, contexto.id_cuenta, "laboratorios.configurar", id_unidad=id_unidad)
    if repo.obtener_unidad(db, id_unidad) is None:
        raise NoEncontrado("La unidad no existe.")

    config = repo.obtener_config(db, id_unidad)
    ahora = datetime.now(timezone.utc)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)

    if config is None:
        hora_apertura = cambios.get("hora_apertura")
        hora_cierre = cambios.get("hora_cierre")
        if hora_apertura is None or hora_cierre is None:
            raise Validacion("hora_apertura y hora_cierre son obligatorias al configurar la unidad por primera vez.")
        if hora_apertura >= hora_cierre:
            raise Validacion("hora_apertura debe ser anterior a hora_cierre.")
        valores = {**_DEFAULTS_CONFIG, **cambios}
        config = LaboratoriosConfig(id_unidad=id_unidad, **valores)
        db.add(config)
        db.flush()
        horario_cambio = True
        datos_anteriores = None
    else:
        datos_anteriores = {
            "dias_atencion": config.dias_atencion, "hora_apertura": str(config.hora_apertura),
            "hora_cierre": str(config.hora_cierre),
        }
        hora_apertura = cambios.get("hora_apertura", config.hora_apertura)
        hora_cierre = cambios.get("hora_cierre", config.hora_cierre)
        if hora_apertura >= hora_cierre:
            raise Validacion("hora_apertura debe ser anterior a hora_cierre.")
        horario_cambio = any(k in cambios for k in ("dias_atencion", "hora_apertura", "hora_cierre"))
        for campo, valor in cambios.items():
            setattr(config, campo, valor)

    if horario_cambio:
        # RN-LAB-08: cada versión del horario, incluida la primera, queda en
        # el histórico con su intervalo de vigencia, sin solapar la anterior.
        repo.cerrar_version_vigente(db, id_unidad, ahora)
        db.flush()
        repo.abrir_version_historico(db, config, ahora)

    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="reservas.laboratorios_config", entidad_id=id_unidad,
        accion="ACTUALIZAR_CONFIGURACION_LABORATORIO", datos_anteriores=datos_anteriores, datos_nuevos=cambios,
    )
    db.commit()
    db.refresh(config)
    return _config_dict(db, config)


def actualizar_tipos_reserva(db: Session, id_unidad: int, datos: schemas.TiposReservaActualizar, contexto: ContextoAutenticado) -> dict:
    exigir_permiso(db, contexto.id_cuenta, "laboratorios.configurar", id_unidad=id_unidad)
    if repo.obtener_unidad(db, id_unidad) is None:
        raise NoEncontrado("La unidad no existe.")

    catalogo = repo.catalogo_tipos_reserva(db)
    desconocidos = set(datos.tipos) - set(catalogo.keys())
    if desconocidos:
        raise Validacion(f"Tipos de reserva desconocidos: {', '.join(sorted(desconocidos))}.")

    repo.actualizar_tipos_reserva(db, id_unidad, set(datos.tipos), catalogo)
    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="reservas.laboratorio_tipos_reserva", entidad_id=id_unidad,
        accion="ACTUALIZAR_TIPOS_RESERVA_LABORATORIO", datos_nuevos={"tipos": datos.tipos},
    )
    db.commit()
    return {"id_unidad": id_unidad, "tipos_reserva": repo.obtener_tipos_habilitados(db, id_unidad)}


def actualizar_visibilidad(db: Session, id_unidad: int, datos: schemas.VisibilidadActualizar, contexto: ContextoAutenticado) -> dict:
    exigir_permiso(db, contexto.id_cuenta, "laboratorios.configurar", id_unidad=id_unidad)
    config = repo.obtener_config(db, id_unidad)
    if config is None:
        raise NoEncontrado("La unidad todavía no tiene configuración de laboratorio.")

    config.mostrar_estado_reserva = datos.mostrar_estado_reserva
    config.mostrar_reservista = datos.mostrar_reservista
    audit.registrar(
        db, actor_cuenta_id=contexto.id_cuenta, entidad="reservas.laboratorios_config", entidad_id=id_unidad,
        accion="ACTUALIZAR_VISIBILIDAD_LABORATORIO",
        datos_nuevos={"mostrar_estado_reserva": datos.mostrar_estado_reserva, "mostrar_reservista": datos.mostrar_reservista},
    )
    db.commit()
    return {"id_unidad": id_unidad, **_config_dict(db, config)}
