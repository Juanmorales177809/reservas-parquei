"""Almacenamiento local de adjuntos de reservations (API-13 §2.5-2.7).

Sin proveedor de almacenamiento externo en el proyecto: guarda en disco
bajo `ADJUNTOS_STORAGE_DIR` (`core/config.py`), montado como volumen con
nombre por `docker-compose.yml`, no en el filesystem efímero del
contenedor. Limitación documentada, igual que `core/rate_limit.py`: un solo
host/proceso; no hay balanceo entre varios backends todavía.
"""

from __future__ import annotations

import os
import uuid

from app.core.config import get_settings

_FIRMAS = {
    "image/png": b"\x89PNG\r\n\x1a\n",
    "image/jpeg": b"\xff\xd8\xff",
    "application/pdf": b"%PDF-",
}
_FIRMAS_DWG = (b"AC10", b"AC12", b"AC13", b"AC14", b"AC15", b"AC18", b"AC21", b"AC24", b"AC32")


def validar_contenido(content_type: str, contenido: bytes) -> bool:
    """Verifica la firma binaria cuando existe una firma confiable para el
    tipo declarado (PNG, JPEG, PDF, DWG, STEP). DXF es texto libre y STL
    binario no tiene una marca universal reconocible —solo el STL en modo
    texto empieza con "solid"—, así que para esos dos se acepta el
    `content_type` declarado sin poder verificar el contenido: es un límite
    real y documentado, no una validación omitida por descuido."""
    firma = _FIRMAS.get(content_type)
    if firma is not None:
        return contenido.startswith(firma)
    if content_type == "model/step":
        return contenido.lstrip()[:9] == b"ISO-10303"
    if content_type == "image/vnd.dwg":
        return contenido[:4] in _FIRMAS_DWG
    return True


def guardar(contenido: bytes) -> str:
    storage_key = uuid.uuid4().hex
    directorio = get_settings().adjuntos_storage_dir
    os.makedirs(directorio, exist_ok=True)
    with open(os.path.join(directorio, storage_key), "wb") as f:
        f.write(contenido)
    return storage_key


def leer(storage_key: str) -> bytes:
    with open(os.path.join(get_settings().adjuntos_storage_dir, storage_key), "rb") as f:
        return f.read()
