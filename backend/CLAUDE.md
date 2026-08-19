# backend/CLAUDE.md

## Stack

FastAPI + SQLAlchemy + Pydantic v2 + Uvicorn ([requirements.txt](requirements.txt)). `bcrypt==3.2.2` está pineado a propósito: passlib no funciona con bcrypt≥4; no subir esa versión.

## Lifespan

`app/main.py` usa `lifespan` (`asynccontextmanager`), no `on_event`. Orden obligatorio en el arranque:

1. `Base.metadata.create_all`
2. `migrate_resource_reservations()` (instala `btree_gist` y la exclusión `reservas_sin_solapamiento`)
3–4. `seed_admin_user()` — una única llamada desde `main.py`. Internamente:
   - ejecuta `init_espacios(db)` para sembrar los espacios iniciales;
   - si no existe un usuario con rol admin y están configuradas las variables `INITIAL_ADMIN_*`, crea el administrador inicial (las tres variables deben definirse juntas, password ≥ 12 caracteres).
5. `engine.dispose()` al cierre

Orden real: `create_all` → migraciones → `seed_admin_user()`. No describir `init_espacios()` como una segunda llamada independiente del lifespan.

## PostgreSQL real para tests

La suite usa PostgreSQL 13 real, nunca SQLite: la exclusión `reservas_sin_solapamiento` y `btree_gist` son específicas de PostgreSQL. Base `reservas_test` en `localhost:5433` vía `docker-compose.test.yml` (raíz del repo).

```bash
docker compose -f docker-compose.test.yml up -d --wait   # desde la raíz del repo
cd backend
pytest -v
docker compose -f docker-compose.test.yml down -v         # limpieza manual, opcional
```

## Estructura por capas

- `api/`: routers FastAPI (`auth.py`, `espacios.py`, `recursos.py`, `reservas.py`, `usuarios.py`, `notificaciones.py`, `admin_dashboard.py`, `control_cambios.py`).
- `domain/`: capa tipada — `enums.py` (`EstadoReserva`, `EstadoEntidad`, `EstadoSlot`, `Rol`), `valor.py` (`FranjaHoraria`, `HorarioAtencion`), `protocols.py` (`Reloj`, `RegistroAuditoria`).
- `services/`: reglas de negocio — `reservas.py`, `horarios.py`, `reloj.py`, `auditoria.py`.
- `crud/`: acceso SQLAlchemy (`espacios.py`, `reservas.py`, `usuarios.py`).
- `models/`: modelos SQLAlchemy (`espacio.py`, `recurso.py`, `reserva.py`, `usuario.py`, `usuario_espacio.py`, `notificacion.py`, `control_cambio.py`).
- `schemas/`: contratos Pydantic, uno por entidad + `admin_dashboard.py`, `disponibilidad.py`.
- `auth/auth.py`: hash de contraseñas y JWT. `deps.py`: dependencias de autorización.
- `config.py`, `db.py`, `main.py`, `migrations.py` en la raíz de `app/`.

## Enums de dominio

`EstadoReserva`: `ESPERANDO`, `APROBADA`, `RECHAZADA`, `CANCELADA` (`app/domain/enums.py`). `RECHAZADA` y `CANCELADA` son terminales. Transiciones válidas: `esperando → aprobada | rechazada | cancelada`, `aprobada → cancelada`.

## HorarioAtencion y FranjaHoraria

Value objects tipados en `app/domain/valor.py` que envuelven la columna JSONB `horario_atencion` de `Espacio` (día → horas). Validados por `app/services/horarios.py` (`horas_atencion_dia`, `horario_cubre_reserva`). Las horas deben ser bloques completos (`minute == 0`).

## RelojLocal y reloj inyectable

`app/services/reloj.py` define el protocolo `Reloj` y `RelojLocal`; devuelve `datetime` naive a propósito, en `APP_TIMEZONE` (por defecto `America/Bogota`). No "arreglar" añadiendo `tzinfo`. Los tests inyectan un reloj fijo (`_RelojFijo`) en vez de usar `monkeypatch` sobre funciones sueltas.

## AuditoriaSesion

Adaptador de auditoría en `app/services/auditoria.py` que implementa el protocolo `RegistroAuditoria` de `app/domain/protocols.py`; registra cambios administrativos consultables vía `GET /admin/control-cambios`.

## Roles y dependencias de autorización

Definidas en `app/deps.py`:

- `get_current_user`: decodifica el JWT de la cookie `access_token` (`sub`=user_id, Fase 9G cookie-only), 401 si no hay cookie, el token es inválido o el usuario no existe.
- `require_admin`: 403 si `rol != admin`.
- `require_resource_manager`: 403 si `rol not in {admin, gestor}`.
- `get_managed_space_id`: para gestores, resuelve su único espacio en `usuarios_espacios`; 403 si no tiene espacio asignado. Para admin devuelve `None` (sin restricción).
- `get_current_user_optional`: lee la cookie `access_token` manualmente vía `Request` (sin `Depends(cookie_auth)`) para no exigir esquema de seguridad en endpoints públicos como `GET /espacios` (RN-005); un token inválido se trata como acceso anónimo, nunca como error. Fase 9G: ya no acepta `Authorization`.

## Reglas de autorización

Un gestor solo puede estar asignado a un espacio. No se puede eliminar ni degradar la propia cuenta administrativa, y siempre debe quedar al menos un `admin` en el sistema (protegido con advisory lock en `proteger_administradores`).

## Migraciones SQL idempotentes sin Alembic

No hay Alembic. El esquema evoluciona en `app/migrations.py` mediante SQL idempotente (`ADD COLUMN IF NOT EXISTS`, bloques `DO $$`), ejecutado en cada arranque después de `Base.metadata.create_all`. Cualquier cambio de esquema nuevo debe seguir ese mismo patrón.

## Compatibilidad de constraints

La exclusión `reservas_sin_solapamiento` (extensión `btree_gist`, estados `esperando`/`aprobada`) la aplica PostgreSQL. El servicio valida antes de escribir; un `IntegrityError` de esa constraint se traduce a HTTP 409 (`_traducir_error_integridad`), nunca debe propagarse crudo al cliente.

## Comandos pytest

```bash
cd backend
pytest -v                              # suite completa
pytest tests/test_lifespan_arranque.py -v   # solo lifespan
```

Orden crítico si se ejecuta manualmente fuera de la suite: fijar `DATABASE_URL`/`SECRET_KEY` → importar `app` → `create_all` → `migrate_resource_reservations()` → ejecutar. Importar `app.*` antes de fijar el entorno apuntaría al motor de la base de desarrollo.

## No modificar schemas/OpenAPI sin aprobación

Ningún cambio en `app/schemas/`, en los routers de `app/api/` ni en el OpenAPI generado debe hacerse sin aprobación explícita del usuario, dado que el frontend y los E2E dependen del contrato actual.

## No cambiar endpoints sin pruebas de contrato

Todo cambio de comportamiento en un endpoint debe ir acompañado de la actualización o creación del test correspondiente en `backend/tests/` (ver [backend/tests/CLAUDE.md](tests/CLAUDE.md)) antes de darse por terminado.
