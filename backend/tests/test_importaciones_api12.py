"""Pruebas de API-12: importaciones masivas en dos pasos.

Se generan .xlsx reales con openpyxl: validación con fila buena y fila en
error (confirmable false + 409 al confirmar), confirmación que escribe, y
EQUIPOS sin unidad (400).
"""

from __future__ import annotations

from io import BytesIO

import openpyxl
from sqlalchemy import text

from .conftest import (
    crear_admin,
    headers_autenticados,
    iniciar_sesion,
    otorgar_permiso_global,
)


def _login_admin(client, db, tag):
    cuenta = crear_admin(db, tag)
    otorgar_permiso_global(db, cuenta, "importacion.ejecutar")
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso admin")
    return headers_autenticados(jar), cuenta


def _xlsx(filas: list[list]) -> bytes:
    libro = openpyxl.Workbook()
    hoja = libro.active
    for fila in filas:
        hoja.append(fila)
    buffer = BytesIO()
    libro.save(buffer)
    return buffer.getvalue()


def _validar(client, headers, catalogo, contenido, id_unidad=None):
    archivos = {"archivo": ("carga.xlsx", contenido,
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    datos = {"catalogo": catalogo}
    if id_unidad is not None:
        datos["id_unidad"] = str(id_unidad)
    return client.post("/api/importaciones", files=archivos, data=datos, headers=headers)


def _limpiar_importacion(db, iid: int) -> None:
    db.execute(
        text("DELETE FROM administration.importacion_resultados WHERE importacion_id = :i"),
        {"i": iid})
    db.execute(
        text("DELETE FROM administration.importaciones WHERE id = :i"), {"i": iid})
    db.commit()


def test_proyectos_valida_y_confirma(client, db, tag):
    """Fila válida se confirma y crea; el detalle conserva resultados."""
    h, _ = _login_admin(client, db, f"a{tag}")
    iid = None
    codigo = f"PRY-{tag}"
    try:
        contenido = _xlsx([["codigo", "nombre", "estado"],
                           [codigo, f"Proyecto {tag}", "ACTIVO"]])
        v = _validar(client, h, "PROYECTOS", contenido)
        assert v.status_code == 201, v.text
        assert v.json()["confirmable"] is True
        iid = v.json()["id"]
        c = client.post(f"/api/importaciones/{iid}/confirmacion", headers=h)
        assert c.status_code == 200, c.text
        existe = db.scalar(
            text("SELECT count(*) FROM investigacion.proyectos WHERE codigo = :c"),
            {"c": codigo.upper()})
        assert existe == 1
    finally:
        if iid:
            _limpiar_importacion(db, iid)
        db.execute(
            text("DELETE FROM investigacion.proyectos WHERE codigo = :c"),
            {"c": codigo.upper()})
        db.commit()


def test_fila_en_error_no_confirmable(client, db, tag):
    """Una fila en error → confirmable false y confirmar da 409."""
    h, _ = _login_admin(client, db, f"a{tag}")
    iid = None
    try:
        contenido = _xlsx([["codigo", "nombre", "estado"],
                           [f"PRY-{tag}", f"Proyecto {tag}", "ACTIVO"],
                           ["", "Sin codigo", "ACTIVO"]])
        v = _validar(client, h, "PROYECTOS", contenido)
        assert v.status_code == 201, v.text
        assert v.json()["confirmable"] is False
        iid = v.json()["id"]
        c = client.post(f"/api/importaciones/{iid}/confirmacion", headers=h)
        assert c.status_code == 409, c.text
    finally:
        if iid:
            _limpiar_importacion(db, iid)
        db.execute(
            text("DELETE FROM investigacion.proyectos WHERE codigo = :c"),
            {"c": f"PRY-{tag}"})
        db.commit()


def test_equipos_sin_unidad_400(client, db, tag):
    """EQUIPOS sin id_unidad → 400 SOLICITUD_INVALIDA."""
    h, _ = _login_admin(client, db, f"a{tag}")
    contenido = _xlsx([["PLACA", "DESCRIPCIÓN", "CODIGO BODEGA",
                        "CENTRO DE COSTOS", "FECHA INICIO"],
                       ["PL-1", "Equipo uno", "B1", "CC1", "2024-01-15"]])
    r = _validar(client, h, "EQUIPOS", contenido)
    assert r.status_code == 400, r.text
