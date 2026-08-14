# backend/tests/CLAUDE.md

## TDD RED → GREEN → REFACTOR

Para reglas de negocio nuevas o modificadas: escribir primero el test que falla (RED) contra el comportamiento esperado, implementarlo en `app/` hasta que pase (GREEN), y solo entonces refactorizar manteniendo la suite en verde. Esta suite nació como red de regresión (Fase 0) antes de los refactorings de las fases 1–5; cualquier cambio nuevo debe seguir dejándola en verde.

## pytest

Config en [pytest.ini](../pytest.ini): `testpaths = tests`, `pythonpath = .` (permite `import app` desde `backend/`).

## PostgreSQL real

Base `reservas_test` en `localhost:5433` (`docker-compose.test.yml`, raíz del repo). No se usa SQLite: la exclusión `reservas_sin_solapamiento` y la extensión `btree_gist` son específicas de PostgreSQL y no tienen equivalente en SQLite.

## Fixtures

Definidas en `conftest.py`: `preparar_esquema` (crea el esquema una vez por sesión y ejecuta `migrate_resource_reservations()`), `db` (sesión SQLAlchemy), `client` (`TestClient` **sin** context manager, para que el lifespan no se ejecute y no se siembren espacios/admin en cada test).

## Aislamiento

`TRUNCATE ... RESTART IDENTITY CASCADE` de todas las tablas al inicio de cada test. El esquema se crea una sola vez por sesión de pytest, no por test.

## Datos deterministas

Los tests no dependen de datos preexistentes ni del orden de ejecución; cada test crea los datos que necesita dentro de su propio cuerpo o fixture.

## Limpieza

No hay limpieza automática de la base entre sesiones de pytest; la limpieza completa es manual:

```bash
docker compose -f docker-compose.test.yml down -v
```

## Uso de reloj inyectado

La anticipación mínima de reservas se prueba inyectando un reloj fijo (`_RelojFijo`, protocolo `Reloj` de `app/domain/protocols.py`) en vez de `monkeypatch` sobre funciones sueltas de `app.services.reservas`.

## Pruebas de lifespan con `with TestClient`

`test_lifespan_arranque.py` es la excepción a la fixture `client` normal: usa `with TestClient(app)` explícitamente para ejercitar el lifespan (`/health`, idempotencia en dos ciclos de arranque).

## Pruebas de dominio

`test_domain_enums.py`, `test_domain_valor.py`, `test_domain_protocols.py`: valores JSON de enums, invariantes de `FranjaHoraria`/`HorarioAtencion`, contrato estructural de `Reloj`/`RegistroAuditoria`.

## Pruebas de servicios

`test_horarios.py`, `test_reservas_validaciones.py`, `test_reloj.py`, `test_auditoria_dominio.py`: unitarias de `services/horarios.py`, `services/reservas.py`, `services/reloj.py` y el adaptador `AuditoriaSesion`.

## Pruebas de API

`test_api_auth.py`, `test_api_reservas.py`, `test_api_espacios.py` (incluye `TestRN005ListadoPublico`), `test_api_usuarios.py`, `test_api_notificaciones.py`, `test_admin_dashboard_ocupacion.py`, `test_schemas_contrato.py`.

## Pruebas de integración

Los 409 por solapamiento ejercitan la constraint real de la base (`reservas_sin_solapamiento`), no solo la validación del servicio; esto es integración real contra PostgreSQL, no mocks.

## Clasificación de errores

- Si falla una prueba o una migración, la ejecución se detiene y el error se reporta tal cual — no silenciar ni reintentar en bucle.
- Un `ZoneInfoNotFoundError` en Windows indica falta del paquete `tzdata` (dev-only, en `requirements-dev.txt`).
- Un fallo por puerto 5433 ocupado indica que `docker-compose.test.yml` no pudo levantar `reservas_test`; no cambiar el puerto silenciosamente, reportarlo.

## No usar SQLite si el comportamiento depende de PostgreSQL

No introducir SQLite ni ningún mock de base de datos para probar solapamiento, exclusión `btree_gist` o cualquier constraint específica de PostgreSQL.

## No ejecutar contra desarrollo/producción

`DATABASE_URL`/`SECRET_KEY` deben fijarse en las primeras líneas de `conftest.py` antes de cualquier `import app.*`; importar antes de fijarlas apuntaría el engine global a la base de desarrollo. Nunca ejecutar la suite contra una `DATABASE_URL` de desarrollo o producción.

## No incluir secretos

`SECRET_KEY` de pruebas es un valor fijo local sin significado fuera del proceso de test; no sustituirlo por una clave real ni reutilizar la de desarrollo/producción.

## Comandos de ejecución

```bash
docker compose -f docker-compose.test.yml up -d --wait   # desde la raíz del repo
cd backend
pytest -v
docker compose -f docker-compose.test.yml down -v         # limpieza opcional
```

## Criterios de aceptación

- Suite completa en verde contra PostgreSQL 13 real.
- Ningún archivo de `app/` modificado solo para hacer pasar un test (salvo que el test exponga un bug real, y en ese caso se corrige `app/` con aprobación).
- Toda regla de negocio nueva o modificada tiene al menos un test que la cubre antes de considerarse terminada.
