# Backend Agent Instructions

Scope: `backend/` (FastAPI). Las reglas de `AGENTS.md` (raíz) aplican también aquí; en caso de conflicto sobre seguridad, la raíz tiene precedencia. Para contexto y convenciones detalladas ver `backend/CLAUDE.md` y `backend/tests/CLAUDE.md` — este archivo no repite ese contenido.

Última revisión: 2026-08-18. Commit de referencia: `f73b9c3e8f17c9d49d2715411ff9021c76b5c12e`.

## Exact commands

```bash
cd backend
pytest -v
pytest -v tests/test_openapi_contrato.py
```

Requiere `reservas_test` levantada primero (desde la raíz del repo):

```bash
docker compose -f docker-compose.test.yml up -d --wait
```

En Windows con `.venv` local: `.\.venv\Scripts\python.exe -m pytest -v`.

## Structure

- `app/api/` — routers FastAPI (`auth.py`, `espacios.py`, `recursos.py`, `reservas.py`, `usuarios.py`, `notificaciones.py`, `admin_dashboard.py`, `control_cambios.py`). Solo orquesta validación (schemas) y autorización (deps); sin reglas de negocio propias.
- `app/auth/` — `auth.py`: hash/verificación de contraseñas, `create_access_token`, y helpers de la cookie de sesión (`NOMBRE_COOKIE_ACCESO`, `atributos_cookie_acceso()`, `max_age_cookie_acceso()`).
- `app/deps.py` — dependencias de autenticación/autorización: `get_current_user`, `get_current_user_optional`, `require_admin`, `require_resource_manager`, `get_managed_space_id`.
- `app/schemas/` — contratos Pydantic (uno por entidad).
- `app/services/` — reglas de negocio (`reservas.py`, `horarios.py`, `reloj.py`, `auditoria.py`, `rate_limit.py`).
- `backend/tests/` — suite pytest contra PostgreSQL real (`reservas_test`, nunca SQLite). Convención RED → GREEN para reglas nuevas o modificadas.

## pytest como validación principal

`pytest -v` es el gate principal de corrección backend. Al commit de referencia, la suite completa está en 289/289 — cualquier cambio debe dejarla en verde antes de considerarse terminado.

## OpenAPI

- Regenerar `backend/tests/openapi.snapshot.json` **únicamente** con el mecanismo documentado en el docstring de `backend/tests/test_openapi_contrato.py` (`app.openapi()` + `json.dumps(..., indent=2, sort_keys=True, ensure_ascii=False)`).
- **Nunca editar el snapshot a mano.**
- **No cambiar schemas, rutas, métodos ni el OpenAPI generado sin aprobación explícita** — el frontend y los E2E dependen del contrato actual.

## Rate limiting (estado actual, confirmado en código)

`app/services/rate_limit.py`: **5 intentos fallidos por ventana deslizante de 15 minutos**, clave `IP + username` (sin normalizar), en memoria del proceso (no distribuido). No modificar sin aprobación explícita — cambiarlo afecta directamente la seguridad de `POST /auth/login`.

## JWT dual (estado actual, confirmado en código — Fase 9F-A/9F-B)

- Cookie `access_token`, `HttpOnly=true`.
- `SameSite=Lax`.
- `Path=/`.
- `Secure=true` solo cuando `ENVIRONMENT=production` está confirmado explícitamente.
- `Domain` no fijado.
- `Max-Age` = `ACCESS_TOKEN_EXPIRE_MINUTES * 60`.
- El header `Authorization: Bearer <token>` tiene **prioridad** sobre la cookie cuando ambos están presentes (`app/deps.py`).
- `access_token` **todavía presente** en el body de `TokenResponse` (compatibilidad temporal, no retirar sin aprobación — ver Fase 9G en `CHANGELOG.md`).
- `POST /auth/logout` disponible: `204 No Content`, idempotente, no exige autenticación.

## Handler global de excepciones

`app/main.py`: cualquier excepción no controlada responde siempre `500` con mensaje genérico y estable al cliente (nunca `str(exc)`, traceback, ni detalles internos). El traceback completo y el contexto (método, ruta, tipo de excepción) se registran solo en el log del servidor. **No registrar `Authorization`, passwords ni cuerpos de request/response en ningún log.**

## Migraciones e infraestructura

`app/migrations.py`: SQL idempotente, sin Alembic. Cualquier cambio de esquema debe seguir ese mismo patrón y **requiere aprobación explícita antes de implementarse**. Cambios a `Dockerfile`, `docker-compose*.yml` o CI también requieren aprobación separada (ver `AGENTS.md` raíz).

## Criterios de validación

- `pytest -v` en verde.
- `pytest -v tests/test_openapi_contrato.py` en verde, o snapshot regenerado con el mecanismo documentado y diff revisado explícitamente si el cambio de contrato fue aprobado.
- Ningún secreto, token ni credencial nuevo en logs.
- `README.md` de la carpeta tocada actualizado siguiendo el patrón ya usado (`app/*/README.md`).

## No verificado / pendiente

- No hay una versión mínima de Python declarada como única fuente de verdad: CI (`.github/workflows/ci.yml`) fija `3.10`, mientras que desarrollo local se ha verificado contra `3.12`/`3.14` según distintos `README.md`. No asumir una sola versión canónica sin revisar el contexto de la tarea.
