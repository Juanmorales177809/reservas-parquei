"""Lógica de alta, recuperación, invitaciones y administración
(carril B: AUTH-B1 a AUTH-B5)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.authz import resolver_rol
from app.core.config import get_settings
from app.core.deps import ContextoAutenticado
from app.core.errors import Conflicto, CredencialesInvalidas, NoAutorizado, NoEncontrado, TokenNoVigente, Validacion
from app.core.rate_limit import limitar
from app.core.security import emitir_token_acceso, generar_token, hash_contrasena, hashear_token, verificar_contrasena
from app.db.models.auth import Cuentas
from app.db.models.identidad import Personal, Usuarios
from app.modules.auth import repository as repo
from app.modules.auth import repository_cuentas as repo_cuentas
from app.modules.auth import schemas
from app.modules.auth.service import VIGENCIA_REFRESH_SEGUNDOS, _actualizacion_inicial_pendiente


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _vigente(expira_at: datetime, usado_o_revocado: bool) -> bool:
    return not usado_o_revocado and _aware(expira_at) > datetime.now(timezone.utc)


# --- AUTH-B1: Autorregistro --------------------------------------------------


def limitar_registro(clave: str) -> None:
    limitar(f"registro:{clave}", maximo=5, ventana_segundos=15 * 60)


def registrar(db: Session, datos: schemas.RegistroSolicitud) -> None:
    """`202` idéntico en todos los casos (SEC-ABU-02): el llamador nunca
    distingue éxito de rechazo por duplicado desde esta función."""
    correo_en_usuarios = repo_cuentas.obtener_usuario_por_correo(db, datos.correo) is not None
    correo_en_cuentas = repo_cuentas.obtener_cuenta_por_correo(db, datos.correo) is not None
    duplicado = repo_cuentas.documento_o_telefono_duplicado(db, datos.documento, datos.telefono)

    if correo_en_usuarios or correo_en_cuentas or duplicado:
        return

    usuario = repo_cuentas.crear_identidad_usuario(
        db,
        nombre=datos.nombre,
        documento=datos.documento,
        telefono=datos.telefono,
        institucion=datos.institucion,
        dependencia=datos.dependencia,
        correo=datos.correo,
    )
    repo_cuentas.crear_cuenta(
        db,
        correo=datos.correo,
        password_hash=hash_contrasena(datos.contrasena),
        tipo_cuenta="USUARIO",
        id_usuario=usuario.id_usuario,
    )
    db.commit()


# --- AUTH-B2: Recuperación de contraseña ------------------------------------


def limitar_recuperacion(clave: str) -> None:
    limitar(f"recuperacion:{clave}", maximo=5, ventana_segundos=15 * 60)


def solicitar_recuperacion(db: Session, correo: str) -> None:
    """Misma respuesta exista o no la cuenta (SEC-REC-01): el llamador no
    distingue los dos casos."""
    cuenta = repo_cuentas.obtener_cuenta_por_correo(db, correo)
    if cuenta is not None and cuenta.estado:
        _, token_hash = generar_token()
        repo_cuentas.crear_token_recuperacion(db, cuenta.id_cuenta, token_hash)
        db.commit()
        # La entrega del enlace por correo es de notifications (API-18);
        # aquí solo se origina el token. No es responsabilidad de auth
        # enviarlo, conforme al contrato.


def validar_token_recuperacion(db: Session, token: str) -> bool:
    fila = repo_cuentas.obtener_token_recuperacion(db, hashear_token(token))
    if fila is None or not _vigente(fila.expira_at, fila.usado_at is not None):
        raise TokenNoVigente()
    return True


def restablecer_contrasena(db: Session, token: str, nueva_contrasena: str) -> None:
    fila = repo_cuentas.obtener_token_recuperacion(db, hashear_token(token))
    if fila is None or not _vigente(fila.expira_at, fila.usado_at is not None):
        raise TokenNoVigente()

    cuenta = repo_cuentas.obtener_cuenta(db, fila.id_cuenta)
    if cuenta is None:
        raise TokenNoVigente()

    repo_cuentas.actualizar_password(db, cuenta, hash_contrasena(nueva_contrasena))
    repo_cuentas.marcar_token_recuperacion_usado(db, fila)
    repo_cuentas.revocar_todas_las_sesiones(db, cuenta.id_cuenta)
    db.commit()
    # Notificar el cambio (SEC-REC-04) es de notifications; no implementado aquí.


# --- AUTH-B3: Invitaciones ---------------------------------------------------


def _dentro_del_ambito(contexto: ContextoAutenticado, id_unidad: int) -> bool:
    return contexto.unidades_autorizadas == "GLOBAL" or id_unidad in contexto.unidades_autorizadas


def emitir_invitacion(
    db: Session, emisor: ContextoAutenticado, correo: str, tipo_cuenta: str, id_unidad: int | None
) -> dict:
    cuenta_existente = repo_cuentas.obtener_cuenta_por_correo(db, correo)
    if cuenta_existente is not None and cuenta_existente.estado:
        raise Conflicto("El correo ya corresponde a una cuenta activa.")

    if tipo_cuenta == "PERSONAL":
        if id_unidad is None:
            raise Validacion("id_unidad es obligatorio para tipo_cuenta PERSONAL.")
        if not _dentro_del_ambito(emisor, id_unidad):
            raise NoAutorizado("La unidad está fuera del ámbito del emisor.")
        persona = repo_cuentas.obtener_personal_por_correo(db, correo)
        if persona is None or not persona.estado:
            raise Validacion("No existe una ficha activa de personal para ese correo.")
        if repo_cuentas.obtener_unidad_del_cargo(db, persona.id_cargo) != id_unidad:
            raise Validacion("La unidad del cargo de la ficha no coincide con id_unidad.")
        id_persona, id_usuario = persona.id_persona, None
    else:  # USUARIO
        usuario = repo_cuentas.obtener_usuario_por_correo(db, correo)
        if usuario is None:
            raise Validacion("No existe una identidad de Usuario para ese correo.")
        id_persona, id_usuario = None, usuario.id_usuario

    anterior = repo_cuentas.invitacion_utilizable_por_correo(db, correo)
    if anterior is not None:
        repo_cuentas.revocar_invitacion(db, anterior)  # SEC-INV-03

    _, token_hash = generar_token()
    inv = repo_cuentas.crear_invitacion(
        db, correo=correo, tipo_cuenta=tipo_cuenta, token_hash=token_hash,
        creada_por=emisor.id_cuenta, id_usuario=id_usuario, id_persona=id_persona,
    )
    db.commit()
    return {"id": inv.id, "correo": inv.correo, "tipo_cuenta": inv.tipo_cuenta, "expira_en": inv.expira_at, "estado": "PENDIENTE"}


def reenviar_invitacion(db: Session, id_invitacion: int) -> dict:
    inv = repo_cuentas.obtener_invitacion(db, id_invitacion)
    if inv is None:
        raise NoEncontrado()
    if inv.usada_at is not None:
        raise Conflicto("La invitación ya fue utilizada.")
    _, token_hash = generar_token()
    repo_cuentas.renovar_token_invitacion(db, inv, token_hash)
    db.commit()
    return {"id": inv.id, "expira_en": inv.expira_at, "estado": "PENDIENTE"}


def validar_invitacion(db: Session, token: str) -> dict:
    inv = repo_cuentas.obtener_invitacion_por_token_hash(db, hashear_token(token))
    usado_o_revocado = inv is not None and (inv.usada_at is not None or inv.revocada_at is not None)
    if inv is None or not _vigente(inv.expira_at, usado_o_revocado):
        raise TokenNoVigente()
    return {"vigente": True, "correo": inv.correo}


def activar_invitacion(db: Session, token: str, contrasena: str) -> tuple[dict, str, str]:
    inv = repo_cuentas.obtener_invitacion_por_token_hash(db, hashear_token(token))
    usado_o_revocado = inv is not None and (inv.usada_at is not None or inv.revocada_at is not None)
    if inv is None or not _vigente(inv.expira_at, usado_o_revocado):
        raise TokenNoVigente()

    # El tipo y la identidad son los ALMACENADOS, nunca los que enviaría el
    # cliente (SEC-AUTZ-03): no se leen del cuerpo de la solicitud.
    if inv.tipo_cuenta == "PERSONAL":
        persona = db.get(Personal, inv.id_persona)
        if persona is None or not persona.estado or persona.correo != inv.correo:
            raise TokenNoVigente()
        id_persona, id_usuario = persona.id_persona, None
    else:
        usuario = db.get(Usuarios, inv.id_usuario)
        if usuario is None:
            raise TokenNoVigente()
        id_persona, id_usuario = None, usuario.id_usuario

    cuenta = repo_cuentas.obtener_cuenta_por_correo(db, inv.correo)
    hash_pw = hash_contrasena(contrasena)
    if cuenta is not None:
        # Reactiva la cuenta existente en vez de duplicar el correo único
        # (RN-AUTH-ID-02); no crea una identidad nueva (RN-HAB-04).
        cuenta.estado = True
        cuenta.tipo_cuenta = inv.tipo_cuenta
        cuenta.id_persona = id_persona
        cuenta.id_usuario = id_usuario
        repo_cuentas.actualizar_password(db, cuenta, hash_pw)
    else:
        cuenta = repo_cuentas.crear_cuenta(
            db, correo=inv.correo, password_hash=hash_pw, tipo_cuenta=inv.tipo_cuenta,
            id_usuario=id_usuario, id_persona=id_persona,
        )

    repo_cuentas.marcar_invitacion_usada(db, inv)

    refresh_token, refresh_hash = generar_token()
    sesion = repo.crear_sesion(db, cuenta.id_cuenta, refresh_hash, VIGENCIA_REFRESH_SEGUNDOS)
    db.commit()

    token_acceso = emitir_token_acceso(sub=str(cuenta.id_cuenta), sid=str(sesion.id_sesion))
    rol = resolver_rol(db, cuenta.id_cuenta).rol
    datos = {
        "id_cuenta": cuenta.id_cuenta,
        "tipo_cuenta": cuenta.tipo_cuenta,
        "rol": rol,
        "correo": cuenta.correo,
        "actualizacion_inicial_pendiente": _actualizacion_inicial_pendiente(db, cuenta),
        "id_sesion": str(sesion.id_sesion),
        "expira_en": sesion.expires_at,
    }
    return datos, token_acceso, refresh_token


# --- AUTH-B4: Administración de cuentas -------------------------------------


def cambiar_estado(db: Session, id_cuenta: int, nuevo_estado: bool) -> dict:
    cuenta = repo_cuentas.obtener_cuenta(db, id_cuenta)
    if cuenta is None:
        raise NoEncontrado()

    if cuenta.estado and not nuevo_estado and repo_cuentas.es_administrador_activo(db, id_cuenta):
        if repo_cuentas.contar_administradores_activos(db, excluir_id_cuenta=id_cuenta) == 0:
            raise Conflicto("La operación dejaría al sistema sin ninguna cuenta con permisos de administrador.")

    cuenta.estado = nuevo_estado
    revocadas = repo_cuentas.revocar_todas_las_sesiones(db, id_cuenta) if not nuevo_estado else 0
    db.commit()
    return {"id_cuenta": id_cuenta, "estado": nuevo_estado, "sesiones_revocadas": revocadas}


def cambiar_identidad(
    db: Session, id_cuenta: int, tipo_cuenta: str, id_persona: int | None, id_usuario: int | None
) -> dict:
    cuenta = repo_cuentas.obtener_cuenta(db, id_cuenta)
    if cuenta is None:
        raise NoEncontrado()

    if tipo_cuenta == "PERSONAL":
        if id_persona is None or id_usuario is not None:
            raise Validacion("Enviar exactamente id_persona para tipo_cuenta PERSONAL.")
        destino = db.get(Personal, id_persona)
        if destino is None:
            raise NoEncontrado()
        if not destino.estado:
            raise Conflicto("La identidad destino está inactiva.")
        if destino.correo != cuenta.correo:
            raise Validacion("El correo de la identidad no coincide con el de la cuenta.")
        ya_asignada = db.scalar(
            select(Cuentas.id_cuenta).where(Cuentas.id_persona == id_persona, Cuentas.id_cuenta != id_cuenta)
        )
        if ya_asignada is not None:
            raise Conflicto("La identidad ya pertenece a otra cuenta.")
        cuenta.tipo_cuenta, cuenta.id_persona, cuenta.id_usuario = "PERSONAL", id_persona, None
    else:
        if id_usuario is None or id_persona is not None:
            raise Validacion("Enviar exactamente id_usuario para tipo_cuenta USUARIO.")
        destino = db.get(Usuarios, id_usuario)
        if destino is None:
            raise NoEncontrado()
        if not destino.estado:
            raise Conflicto("La identidad destino está inactiva.")
        if destino.correo != cuenta.correo:
            raise Validacion("El correo de la identidad no coincide con el de la cuenta.")
        ya_asignada = db.scalar(
            select(Cuentas.id_cuenta).where(Cuentas.id_usuario == id_usuario, Cuentas.id_cuenta != id_cuenta)
        )
        if ya_asignada is not None:
            raise Conflicto("La identidad ya pertenece a otra cuenta.")
        # Una cuenta USUARIO nunca tiene permisos administrativos: degradar
        # el último administrador se rechaza.
        if repo_cuentas.es_administrador_activo(db, id_cuenta):
            if repo_cuentas.contar_administradores_activos(db, excluir_id_cuenta=id_cuenta) == 0:
                raise Conflicto("El cambio dejaría al sistema sin administradores.")
        cuenta.tipo_cuenta, cuenta.id_usuario, cuenta.id_persona = "USUARIO", id_usuario, None

    db.commit()
    return {
        "id_cuenta": cuenta.id_cuenta, "tipo_cuenta": cuenta.tipo_cuenta,
        "id_persona": cuenta.id_persona, "id_usuario": cuenta.id_usuario,
    }


# --- AUTH-B5: Reautenticación y cambio de contraseña ------------------------


def limitar_reautenticacion(clave: str) -> None:
    limitar(f"reautenticacion:{clave}", maximo=5, ventana_segundos=15 * 60)


def reautenticar(db: Session, contexto: ContextoAutenticado, contrasena: str) -> tuple[dict, str, str]:
    """Regenera el identificador de sesión (SEC-REAUTH-04, SEC-SES-13): la
    sesión vieja se revoca y se crea una nueva marcada como reautenticada."""
    cuenta = repo_cuentas.obtener_cuenta(db, contexto.id_cuenta)
    if cuenta is None or not verificar_contrasena(contrasena, cuenta.password_hash):
        raise CredencialesInvalidas()

    sesion_vieja = repo.obtener_sesion(db, contexto.id_sesion)
    if sesion_vieja is not None:
        repo.revocar_sesion(db, sesion_vieja)

    refresh_token, refresh_hash = generar_token()
    nueva_sesion = repo.crear_sesion(db, cuenta.id_cuenta, refresh_hash, VIGENCIA_REFRESH_SEGUNDOS)
    ahora = datetime.now(timezone.utc)
    nueva_sesion.reautenticado_at = ahora
    db.commit()

    nuevo_acceso = emitir_token_acceso(sub=str(cuenta.id_cuenta), sid=str(nueva_sesion.id_sesion))
    hasta = ahora + timedelta(seconds=get_settings().reautenticacion_ventana_segundos)
    return {"autenticacion_reciente_hasta": hasta}, nuevo_acceso, refresh_token


def cambiar_contrasena_propia(db: Session, contexto: ContextoAutenticado, nueva_contrasena: str) -> None:
    cuenta = repo_cuentas.obtener_cuenta(db, contexto.id_cuenta)
    if cuenta is None:
        raise NoEncontrado()
    repo_cuentas.actualizar_password(db, cuenta, hash_contrasena(nueva_contrasena))
    repo_cuentas.revocar_todas_las_sesiones(db, cuenta.id_cuenta)
    db.commit()
    # Notificar el cambio (SEC-REC-04) es de notifications; no implementado aquí.
