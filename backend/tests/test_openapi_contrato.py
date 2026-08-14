# -*- coding: utf-8 -*-
"""Contrato de OpenAPI: detecta cambios no aprobados en rutas/schemas/seguridad.

Regla cubierta: el OpenAPI generado por `app.openapi()` debe permanecer
byte-idéntico (tras serialización canónica) a `openapi.snapshot.json` salvo
aprobación explícita.

Decisiones de diseño y alcance real (Fase 8, CI/CD):
- Por su propia lógica, este test NO ejecuta ninguna query ni requiere
  PostgreSQL: `from app.main import app` es una importación en frío que no
  dispara el lifespan (a diferencia de `with TestClient(app)`, ver
  test_lifespan_arranque.py), y `create_engine()` en `app/db.py` es
  perezoso — no conecta hasta la primera query. `app.openapi()` es
  evaluado en frío y no ejecuta ninguna consulta a la base de datos.
- Sin embargo, al ejecutarse dentro de la suite normal de `pytest` en esta
  carpeta, este test hereda el fixture `preparar_esquema` de
  `conftest.py` (`scope="session", autouse=True`), que sí crea el esquema
  contra PostgreSQL para toda la sesión. Por eso, si se corre
  `pytest tests/test_openapi_contrato.py` de forma aislada sin
  `reservas_test` levantada, falla por esa dependencia heredada — no por
  nada que haga este archivo. Verificado explícitamente en la Fase 8:
  con la base detenida, el test falla con `OperationalError`; con la base
  arriba, pasa. En el job `backend` de CI esto no es un problema: el
  service container de PostgreSQL ya está disponible para los demás 185
  tests, y este test corre "como parte de pytest" con la base accesible.
  No se modifica `conftest.py` para desacoplar este caso (decisión
  explícita: no tocar infraestructura compartida de tests).
- El entorno mínimo (`DATABASE_URL`, `SECRET_KEY`) ya lo fija `conftest.py`
  antes de que pytest importe cualquier módulo de `app`, con valores
  ficticios (`clave-de-prueba-fase0-minimo-32-caracteres`, 39 caracteres,
  cumple el mínimo de 32 exigido por `config.py`). No se duplica aquí.

Cómo regenerar el snapshot (solo de forma explícita, tras revisión del
diff y aprobación del cambio de contrato — nunca automático ni en CI):

    cd backend
    .venv\\Scripts\\python.exe -c "
    import json
    from app.main import app
    schema = app.openapi()
    raw = json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False)
    with open('tests/openapi.snapshot.json', 'w', encoding='utf-8', newline='\n') as f:
        f.write(raw)
        f.write('\n')
    "

Si este test falla, el diff de pytest sobre las dos cadenas ya indica qué
rutas, schemas, descripciones o esquemas de seguridad cambiaron. CI nunca
debe regenerar ni sobrescribir `openapi.snapshot.json`: un fallo aquí exige
revisión humana, no autocorrección.
"""

import json
from pathlib import Path

from app.main import app

RUTA_SNAPSHOT = Path(__file__).parent / "openapi.snapshot.json"


def _openapi_canonico() -> str:
    return json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False)


def test_openapi_coincide_con_snapshot_versionado():
    actual = _openapi_canonico()
    esperado = RUTA_SNAPSHOT.read_text(encoding="utf-8").rstrip("\n")
    assert actual == esperado, (
        "El OpenAPI generado difiere de tests/openapi.snapshot.json. "
        "Si el cambio de contrato fue aprobado explícitamente, regenera el "
        "snapshot siguiendo las instrucciones en el docstring de este "
        "archivo y revisa el diff antes de commitear. No se regenera "
        "automáticamente."
    )


def test_snapshot_es_json_valido_y_no_esta_vacio():
    contenido = json.loads(RUTA_SNAPSHOT.read_text(encoding="utf-8"))
    assert contenido.get("paths"), "El snapshot no debe quedar vacío de rutas"
