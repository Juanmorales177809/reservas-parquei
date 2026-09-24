"""Limitación de intentos contra abuso automatizado (AUTH-A4, SEC-ABU-01).

`architecture.md` §3 no incluye Redis ni ningún almacén compartido: el stack
fijado es FastAPI, SQLAlchemy, Pydantic, Uvicorn, PostgreSQL 13, JWT y
bcrypt. Sin eso, el mecanismo vive en memoria del proceso.

**Limitación explícita**: esto solo funciona correctamente con un único
proceso de Uvicorn (el `Dockerfile` no pasa `--workers`, así que hoy lo es).
Con más de un worker o una réplica, cada proceso cuenta por separado y el
límite efectivo se multiplica. Si el despliegue crece a varios procesos,
esto necesita un almacén compartido (Postgres o, si se incorpora, Redis);
no se resuelve aquí.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict

from app.core.errors import DemasiadosIntentos

_lock = threading.Lock()
_intentos: dict[str, list[float]] = defaultdict(list)


def limitar(clave: str, maximo: int, ventana_segundos: int) -> None:
    """Registra un intento bajo `clave` y deniega si supera `maximo` en la ventana.

    Superar el límite nunca concede acceso (SEC-ABU-03): esta función solo
    lanza `429`, nunca decide que una operación sea válida.
    """
    ahora = time.monotonic()
    limite_inferior = ahora - ventana_segundos
    with _lock:
        intentos = _intentos[clave]
        # Purga los intentos fuera de la ventana antes de contar.
        vigentes = [t for t in intentos if t > limite_inferior]
        if len(vigentes) >= maximo:
            mas_antiguo = min(vigentes)
            retry_after = max(1, int(mas_antiguo + ventana_segundos - ahora))
            _intentos[clave] = vigentes
            raise DemasiadosIntentos(retry_after=retry_after)
        vigentes.append(ahora)
        _intentos[clave] = vigentes


def limpiar_para_pruebas() -> None:
    """Vacía el estado en memoria. Solo para pruebas."""
    with _lock:
        _intentos.clear()
