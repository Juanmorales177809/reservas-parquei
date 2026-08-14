# app

## Propósito

Paquete raíz de la aplicación FastAPI: punto de entrada (`main.py`), configuración (`config.py`), acceso a datos (`db.py`), dependencias de autorización (`deps.py`) y migraciones idempotentes (`migrations.py`).

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| main.py | Modificado | `@app.on_event("startup"/"shutdown")` (deprecado) migrado a `lifespan` con `asynccontextmanager`; orden conservado: `create_all` → `migrate_resource_reservations()` → `seed_admin_user()`; `engine.dispose()` al cierre |

## Reglas de negocio relacionadas

- Arranque idempotente: creación de esquema, instalación de `btree_gist` y exclusión `reservas_sin_solapamiento`, seed de espacios iniciales y creación opcional del primer admin (`INITIAL_ADMIN_*`).

## Decisiones técnicas

- **Lifespan**: patrón actual de FastAPI (verificado en docs oficiales vía Context7). Los warnings de deprecación de `on_event` desaparecieron; el único warning restante de la suite es el shim de `httpx` (externo al proyecto).
- **`engine.dispose()` seguro**: solo cierra conexiones ociosas del pool; el engine global de `app.db` sigue siendo utilizable después (se reabren conexiones al usarlo). Verificado: el fixture `db` y otros tests abren conexiones nuevas sin problema tras el lifespan.
- **Tests**: el fixture `client` de `tests/conftest.py` usa `TestClient` SIN context manager, por lo que el lifespan NO se ejecuta en la suite normal (sin seeding). `tests/test_lifespan_arranque.py` lo ejercita explícitamente con `with TestClient(app)` y comprueba idempotencia con dos ciclos.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_lifespan_arranque.py -v
```

Resultado esperado: 3 tests verdes (lifespan definido, `/health` 200, idempotencia).

## Impacto y compatibilidad

- Rutas y comportamiento de startup sin cambios salvo el mecanismo de ciclo de vida. OpenAPI byte-idéntico (verificado en Fase 3).

## Riesgos

- Ninguno identificado para el arranque en Docker (healthcheck de compose usa `/health`, que no depende del orden del lifespan).

## Pendientes

- N/A para esta fase.

## Fase de implementación

Fase 3 (integración de la capa de dominio).
