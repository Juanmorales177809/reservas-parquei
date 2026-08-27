# -*- coding: utf-8 -*-
"""Verificación de JWT de Supabase firmados con clave asimétrica (ES256).

Supabase migró sus proyectos nuevos a "JWT Signing Keys" (asimétricas):
firma con una clave privada que nunca sale de sus servidores, y publica la
pública en un endpoint fijo y sin autenticación
(`{SUPABASE_URL}/auth/v1/.well-known/jwks.json`). No hay ningún secreto que
compartir para verificar -- a diferencia del esquema legado (HS256 +
`SUPABASE_JWT_SECRET` compartido), que `deps.py::decode_token` sigue
soportando en paralelo solo para la suite de tests (ver ese archivo).

Cacheado en memoria: `obtener_clave` se ejercita en TODO request
autenticado (vía `deps.py::decode_token`), así que pedir el JWKS de nuevo
en cada uno sería un round-trip de red por request. Se refresca solo
cuando aparece un `kid` que no está en la caché (rotación de clave), nunca
por tiempo -- las claves de firma de Supabase no rotan seguido.
"""

from __future__ import annotations

import httpx
from jose import JWTError

from app.config import settings

_jwks_cache: dict | None = None


def _obtener_jwks(forzar_refresco: bool = False) -> dict:
    global _jwks_cache
    if _jwks_cache is None or forzar_refresco:
        url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
        try:
            resp = httpx.get(url, timeout=10)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise JWTError(f"No se pudo obtener el JWKS de Supabase: {exc}") from exc
        _jwks_cache = resp.json()
    return _jwks_cache


def obtener_clave(kid: str | None) -> dict:
    """Devuelve la clave pública JWK que corresponde a `kid`.

    Si no está en la caché actual, refresca una vez (cubre rotación de
    clave del lado de Supabase) antes de rendirse.
    """
    jwks = _obtener_jwks()
    for clave in jwks.get("keys", []):
        if clave.get("kid") == kid:
            return clave
    jwks = _obtener_jwks(forzar_refresco=True)
    for clave in jwks.get("keys", []):
        if clave.get("kid") == kid:
            return clave
    raise JWTError(f"No se encontró una clave JWKS con kid={kid!r}")


def _reset_cache_para_tests() -> None:
    """Solo para tests: limpia la caché entre pruebas que mockean
    `_obtener_jwks`, para que no quede el JWKS de una prueba anterior
    sirviendo a la siguiente."""
    global _jwks_cache
    _jwks_cache = None
