# -*- coding: utf-8 -*-
"""Protocols de la capa de dominio.

Contratos estructurales sin dependencias de infraestructura: no importan
FastAPI, SQLAlchemy, Session, modelos, `app.db` ni servicios concretos.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class Reloj(Protocol):
    """Fuente de la hora actual de negocio.

    Contrato: devuelve un `datetime` NAIVE (sin tzinfo) en la zona horaria
    configurada por `APP_TIMEZONE`. La implementación actual es
    `app.services.reloj.ahora_local`; el adaptador a este protocolo se
    cableará en Fase 3 para poder inyectar relojes falsos en pruebas.
    """

    def ahora(self) -> datetime:
        ...


@runtime_checkable
class RegistroAuditoria(Protocol):
    """Registro de cambios administrativos.

    Usa únicamente tipos primitivos. El adaptador a
    `app.services.auditoria.registrar_cambio` (que hoy recibe `Session` y un
    modelo `Usuario`) se implementará en Fase 3.
    """

    def registrar(
        self,
        *,
        usuario_id: int,
        accion: str,
        entidad: str,
        entidad_id: int | None,
        descripcion: str,
    ) -> None:
        ...
