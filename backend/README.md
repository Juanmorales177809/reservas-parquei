# backend

## Propósito

API FastAPI del sistema de reservas. Esta carpeta contiene la aplicación (`app/`), los requisitos de runtime (`requirements.txt`), las dependencias de desarrollo (`requirements-dev.txt`), la configuración de pytest (`pytest.ini`) y la suite automatizada (`tests/`).

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| requirements-dev.txt | Creado | `pytest==8.3.5`, `httpx==0.27.2` y `tzdata==2025.2` (zonas horarias en Windows) pinnados para la suite |
| pytest.ini | Creado | `testpaths = tests`, `pythonpath = .` (permite importar `app` desde esta carpeta) |
| tests/ | Creado | Suite de regresión de Fase 0 (ver `tests/README.md`) |

## Reglas de negocio relacionadas

- RN-017: confirmación de reserva por aprobación o creación directa del gestor.
- RN-019: reservas de usuarios requieren aprobación.
- RN-020: reservas entre espacios (gestor ajeno) requieren aprobación.
- RN-021: reservas del propio espacio del gestor no requieren aprobación.
- RN-029: integridad de relaciones entre entidades.
- Reglas adicionales del código: bloques de hora completa, anticipación mínima, solapamiento (exclusión `btree_gist`), máquina de transiciones de estado, autorización por rol.

## Decisiones técnicas

- PostgreSQL real para integración (`docker-compose.test.yml`, base `reservas_test` en `localhost:5433`): SQLite no representa la extensión `btree_gist` ni la exclusión `reservas_sin_solapamiento`.
- Orden obligatorio en pruebas: fijar `DATABASE_URL`/`SECRET_KEY` → importar `app` → `create_all` → `migrate_resource_reservations()` → ejecutar.
- `TestClient` sin context manager para no ejecutar el startup (evita sembrar espacios y admin inicial).
- `bcrypt==3.2.2` (pin de `requirements.txt`) instaló correctamente sobre Python 3.14.

## Pruebas

```powershell
docker compose -f docker-compose.test.yml up -d --wait   # desde la raíz del repo
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -v
```

Resultado esperado: suite en verde contra PostgreSQL 13 (ver detalle por regla en `tests/README.md`).

## Impacto y compatibilidad

- Ningún archivo de `app/` fue modificado: sin cambios de contrato, de OpenAPI ni de base de datos de desarrollo.
- La base de pruebas es exclusiva y descartable (`docker compose -f docker-compose.test.yml down -v`).

## Riesgos

- Importar cualquier módulo de `app` antes de fijar las variables de entorno apuntaría el engine global a la base de desarrollo; la suite lo evita fijándolas en las primeras líneas de `tests/conftest.py`.
- En Windows, `zoneinfo` requiere el paquete `tzdata` (añadido a `requirements-dev.txt`). El backend local en Windows sin `tzdata` falla en `services/reloj.py`; en Docker funciona porque la imagen Debian lo incluye. Pendiente: decidir si se agrega a `requirements.txt` para desarrollo local en Windows.
- Hallazgo documentado (no bloqueante): en una base limpia, el bloque de FKs de `app/migrations.py` añade FKs redundantes junto a las auto-generadas por `create_all`.

## Pendientes

- La rama de carrera del advisory lock de `proteger_administradores` no tiene prueba determinista en Fase 0; se cubre indirectamente (auto-eliminación de admin).

## Fase de implementación

Fase 0 (red de regresión).
