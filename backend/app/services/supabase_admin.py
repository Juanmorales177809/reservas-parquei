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
