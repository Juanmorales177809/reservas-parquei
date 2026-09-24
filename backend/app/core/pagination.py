"""Paginación, filtros y orden comunes a todo listado (BK-05, API-02).

Conforme a `specs/contratos/README.md` §4: un listado paginado devuelve
`{"datos": [...], "paginacion": {...}}`; un catálogo cerrado devuelve solo
`{"datos": [...]}` y no admite `pagina`, `tamano` ni `orden`.

Cada endpoint declara sus propios filtros y campos de orden admitidos con
`paginacion_para(...)` o `catalogo_cerrado_para(...)`; cualquier parámetro de
consulta fuera de esa lista responde `400 SOLICITUD_INVALIDA` en lugar de
ignorarse en silencio.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, FrozenSet

from fastapi import Request

from app.core.errors import SolicitudInvalida

TAMANO_POR_DEFECTO = 20
TAMANO_MAXIMO = 100

_PARAMETROS_DE_PAGINACION = frozenset({"pagina", "tamano", "orden"})


@dataclass
class Paginacion:
    pagina: int
    tamano: int
    orden: str | None

    @property
    def offset(self) -> int:
        return (self.pagina - 1) * self.tamano


def _parametros_desconocidos(request: Request, admitidos: FrozenSet[str]) -> set[str]:
    return set(request.query_params.keys()) - admitidos


def paginacion_para(
    filtros_admitidos: FrozenSet[str] = frozenset(),
    ordenes_admitidos: FrozenSet[str] = frozenset(),
) -> Callable[[Request], Paginacion]:
    """Fábrica de la dependencia de paginación para un listado concreto."""

    admitidos = _PARAMETROS_DE_PAGINACION | frozenset(filtros_admitidos)

    def _dependencia(request: Request) -> Paginacion:
        desconocidos = _parametros_desconocidos(request, admitidos)
        if desconocidos:
            raise SolicitudInvalida(
                f"Parámetro desconocido: {', '.join(sorted(desconocidos))}."
            )

        pagina_raw = request.query_params.get("pagina", "1")
        tamano_raw = request.query_params.get("tamano", str(TAMANO_POR_DEFECTO))
        orden = request.query_params.get("orden")

        try:
            pagina = int(pagina_raw)
            tamano = int(tamano_raw)
        except ValueError:
            raise SolicitudInvalida("'pagina' y 'tamano' deben ser enteros.")

        if pagina < 1:
            raise SolicitudInvalida("'pagina' debe ser mayor o igual a 1.")
        if not (1 <= tamano <= TAMANO_MAXIMO):
            raise SolicitudInvalida(f"'tamano' debe estar entre 1 y {TAMANO_MAXIMO}.")

        if orden is not None and ordenes_admitidos:
            campo = orden.removeprefix("-")
            if campo not in ordenes_admitidos:
                raise SolicitudInvalida(f"'orden' no admite el campo '{campo}'.")

        return Paginacion(pagina=pagina, tamano=tamano, orden=orden)

    return _dependencia


def envolver_listado(datos: list, *, pagina: int, tamano: int, total: int) -> dict:
    """Construye `{"datos", "paginacion"}` para un listado paginado."""
    paginas = -(-total // tamano) if tamano else 0  # división entera hacia arriba
    return {
        "datos": datos,
        "paginacion": {
            "pagina": pagina,
            "tamano": tamano,
            "total": total,
            "paginas": max(paginas, 1) if total or pagina == 1 else paginas,
        },
    }


def catalogo_cerrado_para(
    filtros_admitidos: FrozenSet[str] = frozenset(),
) -> Callable[[Request], None]:
    """Fábrica de la dependencia para un catálogo cerrado: sin paginación."""

    def _dependencia(request: Request) -> None:
        presentes = _PARAMETROS_DE_PAGINACION & set(request.query_params.keys())
        if presentes:
            raise SolicitudInvalida(
                "Este catálogo no admite paginación: "
                f"{', '.join(sorted(presentes))}."
            )
        desconocidos = _parametros_desconocidos(request, frozenset(filtros_admitidos))
        if desconocidos:
            raise SolicitudInvalida(
                f"Parámetro desconocido: {', '.join(sorted(desconocidos))}."
            )
        return None

    return _dependencia


def envolver_catalogo(datos: list) -> dict:
    """Construye `{"datos"}` para un catálogo cerrado, sin `paginacion`."""
    return {"datos": datos}
