"""Lógica de identidades funcionales y perfil propio (API-06).

Dueño de `RN-DAT-01/02` y `RN-PRS-05` (usuarios): valida y persiste
`usuarios.usuarios` y `personal.personal`. Auth delega en este servicio la
creación y resolución de identidades (RN-AUTH-ID-06 de auth); no las duplica.

La unicidad real la garantiza la base con UNIQUE; el servicio anticipa el
código de error exacto y mapea `IntegrityError` por restricción para la
carrera (límite 5 de plan.md).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import ContextoAutenticado
from app.core.errors import (
    Conflicto,
    DocumentoDuplicado,
    NoEncontrado,
    TelefonoDuplicado,
    Validacion,
)
from app.modules.usuarios import repository as repo
from app.modules.usuarios import schemas


def _restriccion_violada(exc: IntegrityError) -> str | None:
    diag = getattr(getattr(exc, "orig", None), "diag", None)
    nombre = getattr(diag, "constraint_name", None)
    if nombre:
        return nombre
    texto = str(exc.orig) if exc.orig else str(exc)
    for candidata in (
        "uq_usuarios_documento",
        "uq_usuarios_telefono",
        "uq_usuarios_correo",
        "uq_personal_documento",
        "uq_personal_correo",
        "uq_personal_telefono",
    ):
        if candidata in texto:
            return candidata
    return None


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


# --- Usuarios (§5) ---------------------------------------------------------------


def crear_identidad(
    db: Session, *, nombre: str, documento: str, telefono: str,
    institucion: str, dependencia: str, correo: str,
):
    """Crea la identidad de Usuario (RN-DAT-01/02 de usuarios). La usa auth y §5.1."""
    if repo.existe_documento_usuario(db, documento):
        raise DocumentoDuplicado()
    if repo.existe_telefono_usuario(db, telefono):
        raise TelefonoDuplicado()
    if repo.existe_correo_usuario(db, correo):
        raise Conflicto("El correo ya corresponde a otra identidad.")
    try:
        with db.begin_nested():
            usuario = repo.crear_usuario(
                db, nombre=nombre, documento=documento, telefono=telefono,
                institucion=institucion, dependencia=dependencia, correo=correo,
            )
    except IntegrityError as exc:
        _traducir_integridad_usuario(exc)
    return usuario


def _traducir_integridad_usuario(exc: IntegrityError) -> None:
    restriccion = _restriccion_violada(exc)
    if restriccion == "uq_usuarios_documento":
        raise DocumentoDuplicado() from exc
    if restriccion == "uq_usuarios_telefono":
        raise TelefonoDuplicado() from exc
    raise Conflicto("La identidad entra en conflicto con un registro existente.") from exc


def identidad_ocupada(db: Session, *, correo: str, documento: str, telefono: str) -> bool:
    """¿El registro/invitación debe responder genérico? (no enumeración, auth)."""
    from app.modules.auth import repository_cuentas as repo_cuentas

    return (
        repo.existe_correo_usuario(db, correo)
        or repo_cuentas.obtener_cuenta_por_correo(db, correo) is not None
        or repo.existe_documento_usuario(db, documento)
        or repo.existe_telefono_usuario(db, telefono)
    )


def crear_usuario_admin(db: Session, datos: schemas.UsuarioCrear) -> dict:
    usuario = crear_identidad(
        db, nombre=datos.nombre, documento=datos.documento, telefono=datos.telefono,
        institucion=datos.institucion, dependencia=datos.dependencia, correo=str(datos.correo),
    )
    db.commit()
    return _usuario_dict(db, usuario)


def actualizar_usuario(db: Session, id_usuario: int, datos: schemas.UsuarioActualizar) -> dict:
    usuario = repo.obtener_usuario(db, id_usuario)
    if usuario is None:
        raise NoEncontrado()
    if datos.correo is not None and str(datos.correo) != usuario.correo:
        if repo.cuenta_de_usuario(db, id_usuario) is not None:
            # RN-AUTH-ID-12 de auth: con cuenta asociada el correo es inmutable.
            raise Conflicto("El correo no puede modificarse porque la identidad ya tiene cuenta asociada.")
        if repo.existe_correo_usuario(db, str(datos.correo), excluir_id=id_usuario):
            raise Conflicto("El correo ya corresponde a otra identidad.")
        usuario.correo = str(datos.correo)
    if datos.documento is not None and datos.documento != usuario.documento:
        if repo.existe_documento_usuario(db, datos.documento, excluir_id=id_usuario):
            raise DocumentoDuplicado()
        usuario.documento = datos.documento
    if datos.telefono is not None and datos.telefono != usuario.telefono:
        if repo.existe_telefono_usuario(db, datos.telefono, excluir_id=id_usuario):
            raise TelefonoDuplicado()
        usuario.telefono = datos.telefono
    if datos.nombre is not None:
        usuario.nombre = datos.nombre
    if datos.institucion is not None:
        usuario.institucion = datos.institucion
    if datos.dependencia is not None:
        usuario.dependencia = datos.dependencia
    usuario.updated_at = _ahora()
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        _traducir_integridad_usuario(exc)
    return _usuario_dict(db, usuario)


def cambiar_estado_usuario(db: Session, id_usuario: int, estado: bool) -> dict:
    usuario = repo.obtener_usuario(db, id_usuario)
    if usuario is None:
        raise NoEncontrado()
    # RN-USR-03 (administration): baja lógica, el historial se conserva.
    usuario.estado = estado
    usuario.updated_at = _ahora()
    db.commit()
    return _usuario_dict(db, usuario)


def _usuario_dict(db: Session, usuario) -> dict:
    db.refresh(usuario)
    return {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "documento": usuario.documento,
        "telefono": usuario.telefono,
        "institucion": usuario.institucion,
        "dependencia": usuario.dependencia,
        "correo": usuario.correo,
        "estado": usuario.estado,
        "perfil_actualizado_at": usuario.perfil_actualizado_at,
    }


def detalle_usuario(db: Session, id_usuario: int) -> dict:
    usuario = repo.obtener_usuario(db, id_usuario)
    if usuario is None:
        raise NoEncontrado()
    return _usuario_dict(db, usuario)


def listar_usuarios(db: Session, *, estado: bool | None, busqueda: str | None, paginacion) -> tuple[list, int]:
    filas, total = repo.listar_usuarios(
        db, estado=estado, busqueda=busqueda,
        limite=paginacion.tamano, desplazamiento=paginacion.offset, orden=paginacion.orden,
    )
    return [_usuario_dict(db, f) for f in filas], total


# --- Personal (§6) -----------------------------------------------------------------


def crear_ficha(db: Session, datos: schemas.PersonalCrear) -> dict:
    """Registra la ficha (RN-PRS-05 de usuarios). Nace activa por DEFAULT."""
    if repo.obtener_cargo(db, datos.id_cargo) is None:
        raise NoEncontrado("El cargo no existe.")
    if repo.existe_documento_personal(db, datos.documento):
        raise Conflicto("El documento ya está registrado en otra ficha.")
    if repo.existe_correo_personal(db, str(datos.correo)):
        raise Conflicto("El correo ya está registrado en otra ficha.")
    if repo.existe_telefono_personal(db, datos.telefono):
        raise Conflicto("El teléfono ya está registrado en otra ficha.")
    try:
        with db.begin_nested():
            persona = repo.crear_personal(
                db, nombre=datos.nombre, documento=datos.documento,
                correo=str(datos.correo), telefono=datos.telefono, id_cargo=datos.id_cargo,
            )
    except IntegrityError as exc:
        raise Conflicto("La ficha entra en conflicto con un registro existente.") from exc
    db.commit()
    return ficha_dict(db, persona)


def actualizar_ficha(db: Session, id_persona: int, datos: schemas.PersonalActualizar) -> dict:
    persona = repo.obtener_personal(db, id_persona)
    if persona is None:
        raise NoEncontrado()
    if datos.correo is not None and str(datos.correo) != persona.correo:
        if repo.cuenta_de_persona(db, id_persona) is not None:
            raise Conflicto("El correo no puede modificarse porque la ficha ya tiene cuenta asociada.")
        if repo.existe_correo_personal(db, str(datos.correo), excluir_id=id_persona):
            raise Conflicto("El correo ya está registrado en otra ficha.")
        persona.correo = str(datos.correo)
    if datos.documento is not None and datos.documento != persona.documento:
        if repo.existe_documento_personal(db, datos.documento, excluir_id=id_persona):
            raise Conflicto("El documento ya está registrado en otra ficha.")
        persona.documento = datos.documento
    if datos.telefono is not None and datos.telefono != persona.telefono:
        if repo.existe_telefono_personal(db, datos.telefono, excluir_id=id_persona):
            raise Conflicto("El teléfono ya está registrado en otra ficha.")
        persona.telefono = datos.telefono
    if datos.nombre is not None:
        persona.nombre = datos.nombre
    if datos.id_cargo is not None:
        if repo.obtener_cargo(db, datos.id_cargo) is None:
            raise NoEncontrado("El cargo no existe.")
        # RN-PRS-02/03 (usuarios): el cargo determina la unidad; el cambio
        # queda trazable en la ficha y lo audita API-08.
        persona.id_cargo = datos.id_cargo
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise Conflicto("La ficha entra en conflicto con un registro existente.") from exc
    return ficha_dict(db, persona)


def cambiar_estado_ficha(db: Session, id_persona: int, estado: bool) -> dict:
    persona = repo.obtener_personal(db, id_persona)
    if persona is None:
        raise NoEncontrado()
    if persona.estado and not estado:
        cuenta = repo.cuenta_de_persona(db, id_persona)
        if cuenta is not None and repo.es_administrador_activo(db, cuenta.id_cuenta):
            if repo.otros_administradores_activos(db, cuenta.id_cuenta) == 0:
                # RN-AUTH-ROL-09 de auth: el sistema no se queda sin administradores.
                raise Conflicto("La operación dejaría al sistema sin ninguna cuenta con permisos de administrador.")
    # RN-PRS-04 (usuarios): la ficha se desactiva, su historial permanece.
    persona.estado = estado
    db.commit()
    return ficha_dict(db, persona)


def ficha_dict(db: Session, persona) -> dict:
    db.refresh(persona)
    cargo = repo.obtener_cargo(db, persona.id_cargo)
    unidad = repo.obtener_unidad(db, cargo.id_unidad) if cargo else None
    return {
        "id_persona": persona.id_persona,
        "nombre": persona.nombre,
        "documento": persona.documento,
        "correo": persona.correo,
        "telefono": persona.telefono,
        "estado": persona.estado,
        "id_cargo": persona.id_cargo,
        "cargo": {"id_cargo": cargo.id_cargo, "nombre_cargo": cargo.nombre_cargo} if cargo else None,
        "unidad": {"id_unidad": unidad.id_unidad, "nombre": unidad.nombre} if unidad else None,
    }


def detalle_ficha(db: Session, id_persona: int) -> dict:
    persona = repo.obtener_personal(db, id_persona)
    if persona is None:
        raise NoEncontrado()
    return ficha_dict(db, persona)


def listar_personal(
    db: Session, *, estado: bool | None, id_unidad: int | None,
    busqueda: str | None, paginacion,
) -> tuple[list, int]:
    filas, total = repo.listar_personal(
        db, estado=estado, id_unidad=id_unidad, busqueda=busqueda,
        limite=paginacion.tamano, desplazamiento=paginacion.offset, orden=paginacion.orden,
    )
    return [ficha_dict(db, f) for f in filas], total


def resolver_persona_activa_por_correo(db: Session, correo: str):
    """Ficha activa para invitar PERSONAL (RN-USR-07 de administration)."""
    persona = repo.obtener_persona_por_correo(db, correo)
    if persona is None or not persona.estado:
        raise Validacion("No existe una ficha activa de personal para ese correo.")
    return persona


# --- Perfil propio (§2) ---------------------------------------------------------------


def obtener_perfil(db: Session, contexto: ContextoAutenticado) -> dict:
    """Perfil consolidado. Solo cuentas USUARIO; PERSONAL → 404 (API-06)."""
    if contexto.tipo_cuenta != "USUARIO" or contexto.id_usuario is None:
        raise NoEncontrado("Esta cuenta no tiene perfil de Usuario.")
    usuario = repo.obtener_usuario(db, contexto.id_usuario)
    if usuario is None:
        raise NoEncontrado()
    return {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "documento": usuario.documento,
        "telefono": usuario.telefono,
        "institucion": usuario.institucion,
        "dependencia": usuario.dependencia,
        "correo": usuario.correo,
        "actualizacion_inicial_pendiente": usuario.perfil_actualizado_at is None,
        "perfil_actualizado_at": usuario.perfil_actualizado_at,
        # Perfiles y vinculaciones los aporta API-11 (researchs).
        "perfiles": [],
        "vinculaciones": {"proyectos": [], "semilleros": [], "pasantias": [], "trabajos_grado": []},
    }


def actualizar_perfil(db: Session, contexto: ContextoAutenticado, datos: schemas.PerfilActualizar) -> dict:
    if contexto.tipo_cuenta != "USUARIO" or contexto.id_usuario is None:
        raise NoEncontrado("Esta cuenta no tiene perfil de Usuario.")
    if datos.correo is not None:
        # UF-USR-04: el correo es solo lectura; enviarlo se rechaza.
        raise Conflicto("El correo es de solo lectura y no puede modificarse por esta vía.")
    usuario = repo.obtener_usuario(db, contexto.id_usuario)
    if usuario is None:
        raise NoEncontrado()
    if datos.documento is not None and datos.documento != usuario.documento:
        if repo.existe_documento_usuario(db, datos.documento, excluir_id=usuario.id_usuario):
            raise DocumentoDuplicado()
        usuario.documento = datos.documento
    if datos.telefono is not None and datos.telefono != usuario.telefono:
        if repo.existe_telefono_usuario(db, datos.telefono, excluir_id=usuario.id_usuario):
            raise TelefonoDuplicado()
        usuario.telefono = datos.telefono
    if datos.nombre is not None:
        usuario.nombre = datos.nombre
    if datos.institucion is not None:
        usuario.institucion = datos.institucion
    if datos.dependencia is not None:
        usuario.dependencia = datos.dependencia
    usuario.updated_at = _ahora()
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        _traducir_integridad_usuario(exc)
    return obtener_perfil(db, contexto)
