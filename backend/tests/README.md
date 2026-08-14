# tests

## Propósito

Suite automatizada de regresión del backend. Captura el comportamiento actual de las reglas de negocio de reservas, usuarios, espacios y notificaciones antes de los refactorings de las fases 1 a 5.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| __init__.py | Creado | Marca `tests` como paquete |
| conftest.py | Creado | Entorno de prueba, fixtures (`preparar_esquema`, `db`, `client`) y helpers |
| test_horarios.py | Creado | Unitarias de `services/horarios.py` |
| test_reservas_validaciones.py | Creado | Unitarias de validaciones de `services/reservas.py` |
| test_api_auth.py | Creado | Integración del endpoint `/auth/login` |
| test_api_reservas.py | Creado | Integración de creación, solapamiento y transiciones |
| test_api_espacios.py | Creado | Integración de espacios y disponibilidad |
| test_api_usuarios.py | Creado | Integración de administración de usuarios |
| test_api_notificaciones.py | Creado | Integración de notificaciones |
| test_domain_enums.py | Creado | Unitarias de enums y constantes de `app/domain` (Fase 1) |
| test_domain_valor.py | Creado | Unitarias de `FranjaHoraria` y `HorarioAtencion` (Fase 1) |
| test_domain_protocols.py | Creado | Contrato estructural de `Reloj` y `RegistroAuditoria` (Fase 1) |
| test_schemas_contrato.py | Creado | Contrato de los schemas alineados con enums del dominio (Fase 2) |
| test_reloj.py | Creado | `RelojLocal` (protocolo, naive, wrapper) (Fase 3) |
| test_auditoria_dominio.py | Creado | Adaptador `AuditoriaSesion` y wrapper `registrar_cambio` (Fase 3) |
| test_lifespan_arranque.py | Creado | Lifespan con `with TestClient`, `/health` e idempotencia (Fase 3) |
| test_admin_dashboard_ocupacion.py | Creado | Ocupación real con `horario_atencion` (Fase 4) |

## Reglas de negocio relacionadas

- RN-017, RN-019, RN-020, RN-021: ciclo de vida de la reserva y aprobación.
- RN-002 (análogo) y RN-003/RN-004: administración de usuarios y roles.
- RN-029: integridad relacional y consistencia.
- Reglas adicionales del código: bloques de hora completa, anticipación mínima, solapamiento con exclusión `btree_gist` (409), estados terminales, autorización por rol, notificaciones internas.
- Fase 1 (dominio): valores JSON de enums, transiciones de estado, invariantes de `FranjaHoraria`/`HorarioAtencion` y contrato de `Reloj`/`RegistroAuditoria` (detalle en `app/domain/README.md`).
- Fase 2 (schemas): contrato JSON conservado (incluida la opción A de horario: días vacíos con `[]`), campos tipados con enums y valores rechazados (detalle en `app/schemas/README.md`).
- Fase 3 (services/models/crud/lifespan): `Reloj` inyectable (los tests de anticipación usan `_RelojFijo` en lugar de `monkeypatch`), guard de horario vacío, adaptador de auditoría y arranque con lifespan (detalle en los READMEs de `app/services/`, `app/`, `app/models/` y `app/crud/`).
- Fase 4 (RN-005 y ocupación): `TestRN005ListadoPublico` en `test_api_espacios.py` (8 tests) y `test_admin_dashboard_ocupacion.py` (7 tests, fechas fijas y reservas legacy insertadas directamente en la DB; detalle en `app/api/README.md`).

## Decisiones técnicas

- **Base de datos**: PostgreSQL 13 real (`docker-compose.test.yml`, `reservas_test` en `localhost:5433`). No se usa SQLite: la exclusión `reservas_sin_solapamiento` y las constraints son específicas de PostgreSQL.
- **Orden crítico de inicialización** (ver `conftest.py`): fijar `DATABASE_URL`/`SECRET_KEY` → importar `app` → `Base.metadata.create_all` → `migrate_resource_reservations()` (instala `btree_gist` y la exclusión) → ejecutar pruebas. Cualquier import de `app.*` antes de fijar el entorno apuntaría a la base de desarrollo.
- **Aislamiento entre pruebas**: `TRUNCATE ... RESTART IDENTITY CASCADE` de todas las tablas al inicio de cada prueba; el esquema se crea una vez por sesión.
- **Sin seeding de startup**: `TestClient` sin context manager evita `init_espacios` y `seed_admin_user`.
- **Reloj**: la anticipación se prueba con `monkeypatch` sobre `app.services.reservas.ahora_local` (en Fase 3 pasará a un protocolo `Reloj` inyectable).
- **Migración sobre base limpia**: verificación de idempotencia realizada (README de `backend/`). Hallazgo no bloqueante: bloque de FKs de `app/migrations.py` genera FKs redundantes junto a las de `create_all`.

## Pruebas

```powershell
docker compose -f docker-compose.test.yml up -d --wait   # desde la raíz del repo
cd backend
.\.venv\Scripts\python.exe -m pytest -v
docker compose -f docker-compose.test.yml down -v        # limpieza opcional
```

Resultado esperado: todos los tests en verde. Los 409 por solapamiento ejercitan la constraint de la base, no solo la validación del servicio.

## Impacto y compatibilidad

- Sin impacto sobre la aplicación: no se modifican archivos de `app/`, contratos ni datos de desarrollo.
- Solo se usa la base exclusiva de pruebas; nunca datos de producción.

## Riesgos

- Requiere Docker y el puerto 5433 libre; si el puerto está ocupado, la ejecución se detiene y se reporta (no se cambia silenciosamente).
- En Windows, `zoneinfo` exige el paquete `tzdata` (añadido a `requirements-dev.txt`); sin él, las pruebas que invocan `ahora_local()` fallan con `ZoneInfoNotFoundError`.
- Si falla una prueba o la migración, la fase se detiene y se reporta el error tal cual.

## Pendientes

- Test determinista de la carrera del advisory lock de `proteger_administradores` (cobertura actual indirecta).
- El conteo de slots de disponibilidad asume el horario por defecto 07:00–19:00 de lunes a sábado.

## Fase de implementación

Fase 0 (red de regresión).
