# -*- coding: utf-8 -*-
"""Códigos de recuperación de contraseña.

En memoria del proceso, NUNCA en la base de datos -- mismo patrón y misma
limitación aceptada que `app/services/rate_limit.py`: un solo worker
Uvicorn, sin réplicas (ver docker-compose.yml/backend/Dockerfile). Si el
proceso se reinicia, los códigos pendientes se pierden y quien lo pidió
simplemente solicita uno nuevo -- un correo más, sin ningún dato
inconsistente. Decisión explícita: no se suma Redis solo para esto.

El código se hashea con el mismo mecanismo que las contraseñas
(`hash_password`/`verify_password`, bcrypt vía passlib) -- nunca se guarda
en texto plano ni siquiera en memoria. El hash por sí solo no basta contra
fuerza bruta (6 dígitos = 1.000.000 de combinaciones): la defensa real es
`app.services.rate_limit.limitador_recuperacion`, aplicada por quien llama
a `verificar_codigo` (ver `POST /auth/restablecer` en `app/api/auth.py`).
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import NamedTuple

from app.auth.auth import hash_password, verify_password
from app.domain.protocols import Reloj
from app.services.reloj import RelojLocal

VENTANA_CODIGO = timedelta(minutes=15)


class _CodigoRecuperacion(NamedTuple):
    hash_codigo: str
    vencimiento: datetime


class RecuperacionPassword:
    """Un código pendiente como máximo por usuario -- pedir uno nuevo
    invalida el anterior (mismo criterio que "el último código es el
    válido", evita confusión sobre cuál correo usar)."""

    def __init__(self, reloj: Reloj | None = None, ventana: timedelta = VENTANA_CODIGO) -> None:
        self._reloj = reloj or RelojLocal()
        self._ventana = ventana
        self._codigos: dict[int, _CodigoRecuperacion] = {}

    def generar_codigo(self, usuario_id: int) -> str:
        codigo = f"{secrets.randbelow(1_000_000):06d}"
        vencimiento = self._reloj.ahora() + self._ventana
        self._codigos[usuario_id] = _CodigoRecuperacion(hash_password(codigo), vencimiento)
        return codigo

    def verificar_codigo(self, usuario_id: int, codigo: str) -> bool:
        """Un intento fallido NO quema el código -- solo lo hace un acierto
        o el vencimiento. Que un tipeo equivocado no obligue a pedir un
        correo nuevo es justamente lo que existe el límite de intentos de
        `limitador_recuperacion`: es la defensa contra fuerza bruta, no
        esto."""
        entrada = self._codigos.get(usuario_id)
        if entrada is None:
            return False
        if self._reloj.ahora() >= entrada.vencimiento:
            del self._codigos[usuario_id]
            return False
        if not verify_password(codigo, entrada.hash_codigo):
            return False
        del self._codigos[usuario_id]
        return True


recuperacion_password = RecuperacionPassword()
