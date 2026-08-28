# -*- coding: utf-8 -*-
"""Cliente mínimo de la API de administración de Supabase Auth (REST directo,
sin el SDK oficial -- son dos endpoints, no vale la pena la dependencia
completa por eso).

Ambas funciones usan `SUPABASE_SERVICE_ROLE_KEY`, que **nunca** debe llegar
al cliente Flutter (a diferencia de la `publishableKey`/`anonKey`, que sí es
pública por diseño de Supabase) -- vive únicamente en el backend, vía
variable de entorno.

Este módulo es el ÚNICO lugar del sistema que puede crear una identidad de
Supabase para un usuario. `POST /auth/supabase/sesion` (app/api/auth.py)
solo BUSCA por `supabase_id` ya existente, nunca crea ni vincula nada por su
cuenta -- así se cierra el hueco de seguridad de la versión anterior
(auto-alta / auto-vínculo por email desde un request anónimo).
"""

from __future__ import annotations

import uuid

import httpx

from app.config import settings


class SupabaseAdminError(Exception):
    """Fallo al hablar con la API de administración de Supabase (red, 4xx/5xx,
    o una respuesta sin el campo esperado). Quien llama decide cómo
    traducirlo a HTTP -- este módulo no conoce FastAPI."""


def _headers() -> dict[str, str]:
    return {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
    }


def invitar_usuario(email: str) -> uuid.UUID:
    """Crea el usuario en Supabase y dispara SU PROPIO correo de invitación
    -- la persona fija su contraseña con el link que manda Supabase. Acá no
    se genera ninguna contraseña temporal ni se encola ningún correo propio.
    """
    url = f"{settings.supabase_url}/auth/v1/invite"
    try:
        resp = httpx.post(url, headers=_headers(), json={"email": email}, timeout=10)
    except httpx.HTTPError as exc:
        raise SupabaseAdminError(f"No se pudo contactar a Supabase: {exc}") from exc
    if resp.status_code >= 400:
        raise SupabaseAdminError(f"Supabase rechazó la invitación ({resp.status_code}): {resp.text}")
    data = resp.json()
    user_id = data.get("id") or data.get("user", {}).get("id")
    if not user_id:
        raise SupabaseAdminError(f"Respuesta de Supabase sin id de usuario: {data}")
    return uuid.UUID(user_id)


def eliminar_usuario(supabase_id: uuid.UUID) -> None:
    """Borra la identidad de Supabase de un usuario.

    SIEMPRE se llama antes de borrar la fila local
    (`api/usuarios.py::delete_usuario_endpoint`) -- en el orden inverso,
    un fallo a mitad de camino deja una identidad huérfana en Supabase
    (con el email todavía "registrado" ahí) que bloquea reinvitar ese
    mismo email más adelante. Encontrado en producción el 2026-08-27:
    borrar un usuario solo tocaba `reservas_db`, nunca Supabase, y
    reinvitar el mismo email fallaba con 422 `email_exists` contra una
    cuenta que ya no existía en nuestro lado.

    Un 404 se trata como éxito, no como error: la identidad ya no existe,
    que es exactamente el estado buscado -- idempotente, por si alguien
    la borró antes a mano desde el dashboard de Supabase.
    """
    url = f"{settings.supabase_url}/auth/v1/admin/users/{supabase_id}"
    try:
        resp = httpx.delete(url, headers=_headers(), timeout=10)
    except httpx.HTTPError as exc:
        raise SupabaseAdminError(f"No se pudo contactar a Supabase: {exc}") from exc
    if resp.status_code >= 400 and resp.status_code != 404:
        raise SupabaseAdminError(f"Supabase rechazó el borrado ({resp.status_code}): {resp.text}")


def generar_link_invitacion(email: str) -> str:
    """Genera un link de invitación fresco para un usuario que YA existe en
    Supabase (a diferencia de [invitar_usuario], que crea uno nuevo y
    falla con 422 `email_exists` si el email ya está registrado -- probado
    contra el proyecto real el 2026-08-27, `/auth/v1/invite` rechaza
    reinvitar aunque la invitación original nunca se haya confirmado).

    A diferencia de `invitar_usuario`, este endpoint de Supabase **no manda
    ningún correo por su cuenta** -- solo genera y devuelve el link
    (`action_link`); entregarlo es responsabilidad de quien llama (ver
    `reenviar_invitacion_endpoint` en `app/api/usuarios.py`, que lo encola
    en el outbox propio, `app/services/email.py`).
    """
    url = f"{settings.supabase_url}/auth/v1/admin/generate_link"
    try:
        resp = httpx.post(url, headers=_headers(), json={"type": "invite", "email": email}, timeout=10)
    except httpx.HTTPError as exc:
        raise SupabaseAdminError(f"No se pudo contactar a Supabase: {exc}") from exc
    if resp.status_code >= 400:
        raise SupabaseAdminError(f"Supabase rechazó la generación del link ({resp.status_code}): {resp.text}")
    data = resp.json()
    link = data.get("action_link")
    if not link:
        raise SupabaseAdminError(f"Respuesta de Supabase sin action_link: {data}")
    return link


def crear_usuario_y_generar_link(email: str) -> tuple[uuid.UUID, str]:
    """Crea la identidad en Supabase para un email NUEVO y devuelve el link
    de invitación, sin que Supabase mande su propio correo -- a diferencia
    de `invitar_usuario`, que crea la identidad Y manda el correo en un
    solo paso (2026-08-28: se dejó de usar en `POST /usuarios` para que la
    invitación salga por nuestro propio outbox/Graph en vez de depender de
    un SMTP de terceros configurado en Supabase).

    Usa el mismo endpoint que `generar_link_invitacion`
    (`/auth/v1/admin/generate_link`, `type=invite`) -- documentado por
    Supabase como el mismo mecanismo interno que `/auth/v1/invite` pero sin
    el envío de correo, así que también crea el usuario si no existe. Si
    la respuesta no trae `id` de usuario (o sea, si ese supuesto resultara
    falso contra el proyecto real), esta función falla fuerte
    (`SupabaseAdminError`) en vez de guardar una fila local sin
    `supabase_id` -- el fallo es ruidoso, no silencioso.
    """
    url = f"{settings.supabase_url}/auth/v1/admin/generate_link"
    try:
        resp = httpx.post(url, headers=_headers(), json={"type": "invite", "email": email}, timeout=10)
    except httpx.HTTPError as exc:
        raise SupabaseAdminError(f"No se pudo contactar a Supabase: {exc}") from exc
    if resp.status_code >= 400:
        raise SupabaseAdminError(f"Supabase rechazó la generación del link ({resp.status_code}): {resp.text}")
    data = resp.json()
    link = data.get("action_link")
    user_id = data.get("id") or data.get("user", {}).get("id")
    if not link or not user_id:
        raise SupabaseAdminError(f"Respuesta de Supabase sin action_link o id de usuario: {data}")
    return uuid.UUID(user_id), link


def generar_link_recuperacion(email: str) -> str | None:
    """Genera un link de recuperación de contraseña (`type=recovery`) para
    un email que YA existe en Supabase -- sin mandar ningún correo por su
    cuenta, igual que `generar_link_invitacion`.

    A diferencia de `type=invite`, Supabase rechaza `type=recovery` para un
    email que no tiene cuenta -- acá esa condición se traduce a `None`, NO
    a una excepción: el endpoint que llama (`POST /auth/recuperar`, ver
    `app/api/auth.py`) tiene que devolver siempre la misma respuesta
    exista o no la cuenta, para no filtrar qué emails están registrados
    (mismo invariante de privacidad que ya tenía el flujo 100%
    client-side contra Supabase que este endpoint reemplaza -- ver
    `backend/CLAUDE.md`, "Correo por Microsoft Graph").
    """
    url = f"{settings.supabase_url}/auth/v1/admin/generate_link"
    try:
        resp = httpx.post(url, headers=_headers(), json={"type": "recovery", "email": email}, timeout=10)
    except httpx.HTTPError:
        return None
    if resp.status_code >= 400:
        return None
    data = resp.json()
    return data.get("action_link")


def crear_usuario_confirmado(email: str, password: str) -> uuid.UUID:
    """Crea el usuario con una contraseña YA puesta, sin enviar ningún
    correo. Solo la usa el bootstrap del primer admin
    (`app/main.py::seed_admin_user`): ahí la contraseña ya la fijó
    `INITIAL_ADMIN_PASSWORD` y no tiene sentido un flujo de invitación.
    """
    url = f"{settings.supabase_url}/auth/v1/admin/users"
    try:
        resp = httpx.post(
            url,
            headers=_headers(),
            json={"email": email, "password": password, "email_confirm": True},
            timeout=10,
        )
    except httpx.HTTPError as exc:
        raise SupabaseAdminError(f"No se pudo contactar a Supabase: {exc}") from exc
    if resp.status_code >= 400:
        raise SupabaseAdminError(f"Supabase rechazó la creación ({resp.status_code}): {resp.text}")
    data = resp.json()
    user_id = data.get("id")
    if not user_id:
        raise SupabaseAdminError(f"Respuesta de Supabase sin id de usuario: {data}")
    return uuid.UUID(user_id)
