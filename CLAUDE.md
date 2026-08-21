# CLAUDE.md — reservas-parquei

## Propósito

Sistema de gestión de reservas de espacios institucionales: autenticación JWT, roles, disponibilidad horaria, aprobación de solicitudes, notificaciones, auditoría y paneles de gestión. Monorepo `backend/` (FastAPI) + `frontend/` (Next.js 14, App Router) + `app_flutter/` (Flutter, en migración — ver plan de migración). Todo el código, mensajes y documentación están en español; mantener ese idioma.

## Migración a Flutter (en curso)

`app_flutter/` es el reemplazo en curso del frontend, para Móvil (Android/iOS) y Escritorio (Windows/macOS/Linux) nativos + Web vía un proxy same-origin propio (ver `app_flutter/CLAUDE.md`). `frontend/` (Next.js) sigue siendo la app en producción hasta que se confirme paridad funcional completa y se apruebe explícitamente su retiro (Fase 7 del plan). No modificar `backend/` como parte de este trabajo (mismas reglas que ya aplican a `frontend/`).

## Estado de referencia

- Rama de trabajo: `feature/soV0.1`.
- Commit de referencia: `914cf36e749e44f425c32fb50b63c9946d67866c`.
- Rama base para PR: `feature/v0.1`.

## Arquitectura general

```
Navegador → Next.js :3000 → (rewrites /api, /docs, /openapi.json) → FastAPI :8000 → PostgreSQL :5432
```

El navegador solo habla con Next.js. PostgreSQL no se expone al host (red `database_network` interna en Docker). Detalle completo en [README.md](README.md).

## Separación backend/frontend

- `backend/app/`: capas `api/` (rutas), `services/` (reglas de negocio), `crud/` (SQLAlchemy), `schemas/` (Pydantic), `models/`, `domain/` (enums y value objects tipados), `auth/` (JWT + bcrypt), `deps.py` (autorización), `main.py` (lifespan), `migrations.py` (SQL idempotente, sin Alembic).
- `frontend/src/`: `app/` (páginas), `components/`, `context/` (`AuthContext`, `NotificationContext`), `services/` (cliente API), `types/`, `utils/`, `test/` (infra Vitest).
- `app_flutter/lib/`: `core/` (config, red, router, tema, widgets compartidos), `features/<dominio>/` (`data/domain/application/presentation`, uno por recurso del backend), `shell/` (navegación adaptativa: bottom nav en móvil, top nav en escritorio/Web).
- Ver [backend/CLAUDE.md](backend/CLAUDE.md), [frontend/CLAUDE.md](frontend/CLAUDE.md), [frontend/e2e/CLAUDE.md](frontend/e2e/CLAUDE.md), [backend/tests/CLAUDE.md](backend/tests/CLAUDE.md), [app_flutter/CLAUDE.md](app_flutter/CLAUDE.md) para detalle por área.

## Comandos principales

```bash
docker compose up -d --build      # levantar todo el stack (desarrollo)
docker compose logs -f backend    # logs backend
docker compose logs -f frontend   # logs frontend
docker compose down               # detener sin borrar datos
```

Frontend local: `cd frontend && npm ci && npm run dev` (además: `npm run type-check`, `npm run lint`, `npm run build`).
Backend local: `cd backend && python -m venv .venv && pip install -r requirements.txt && uvicorn app.main:app --reload` (requiere `DATABASE_URL` y `SECRET_KEY` exportadas; `config.py` no llama `load_dotenv()`).

## Comandos de tests

```bash
# Backend (PostgreSQL real de pruebas)
docker compose -f docker-compose.test.yml up -d --wait
cd backend && pytest -v

# Frontend unitario/componentes
cd frontend && npm run test

# E2E (requiere frontend :3000, backend :8000 y reservas_test :5433)
cd frontend
npm run test:e2e            # smoke
npm run test:e2e:regresion  # smoke + regresión
npm run test:e2e:all        # suite completa
```

## Preparación de PostgreSQL de pruebas

`docker-compose.test.yml` levanta `reservas_test` en `localhost:5433`, exclusiva y descartable. Limpieza manual y explícita cuando ya no se necesite:

```bash
docker compose -f docker-compose.test.yml down -v
```

Nunca ejecutar `down -v` de forma automática ni desde un test.

## Reglas de no usar desarrollo/producción

- Ninguna prueba, exploración ni tarea de este asistente debe leer, escribir ni migrar la base de desarrollo (`reservas_db`) ni ninguna base de producción.
- Solo `reservas_test` (puerto 5433) es válida para pruebas e inspección durante el trabajo asistido.

## Reglas de commit/push

- No hacer `git commit` ni `git push` sin autorización explícita del usuario en el mensaje actual.
- No usar `git reset --hard`, `git clean -fd`, ni sobrescribir cambios sin confirmar antes con `git status`.
- No hacer merge ni tocar `feature/v0.1` (rama base) sin autorización aparte.

## Archivos que nunca deben commitearse

`.env` / `.env.*` (excepto `.env.example`), `**/.auth/` (storageState de Playwright), `test-results/`, `playwright-report/`, `node_modules/`, `.next/`, `__pycache__/`, `.venv/`, `coverage/`, `*.tsbuildinfo` — ver [.gitignore](.gitignore).

## Política de cambios de API/OpenAPI

No modificar contratos de endpoints, schemas Pydantic ni el OpenAPI generado sin aprobación explícita. Cambios de esquema de base de datos deben seguir el patrón idempotente de `backend/app/migrations.py` (no introducir Alembic).

## Roles del sistema

| Rol | Capacidades |
| --- | --- |
| `usuario` | Consultar disponibilidad, crear reservas, editar/cancelar las propias, leer notificaciones. |
| `gestor` | Gestiona recursos, configuración y reservas únicamente del espacio asignado (un gestor tiene un único espacio). |
| `admin` | Gestión global de usuarios, espacios, recursos, reservas, dashboard y control de cambios. |

## RN-005

`GET /espacios` (público, autenticación opcional): usuarios anónimos y rol `usuario` solo ven espacios `estado=activo`; `admin` y `gestor` ven todos los estados. No hay forma de eludir el filtro vía `skip`/`limit` u otro parámetro. Implementado en [backend/app/api/espacios.py](backend/app/api/espacios.py); ver `backend/app/api/README.md`.

## Fuente de verdad del horario

Columna JSONB `horario_atencion` en el modelo `Espacio` ([backend/app/models/espacio.py](backend/app/models/espacio.py)), validada por `backend/app/services/horarios.py`. Las franjas se representan como value objects tipados (`FranjaHoraria`, `HorarioAtencion`) en `backend/app/domain/valor.py`.

## `ocupacion_global` vs `ocupacion_por_dia_hora`

- `ocupacion_por_dia_hora`: grid fijo de 7 días × horas 07–19 usado por el heatmap del dashboard.
- `ocupacion_global`: agrega también las horas atendidas fuera de ese rango (si un espacio abre antes de las 7 o después de las 19); esas horas no aparecen en el gráfico. Limitación documentada, no bloqueante — ver `backend/app/api/README.md` y `backend/tests/test_admin_dashboard_ocupacion.py`.

## Comportamiento ante 401 durante login

`POST /auth/login` está excluido del interceptor global de 401 en `frontend/src/services/api.ts`. Un 401 aquí son credenciales inválidas y el error llega al formulario de login sin limpiar `localStorage` ni redirigir.

## Comportamiento ante 401 en endpoints protegidos

`apiFetch` limpia `token` y `user` de `localStorage` y redirige a `/login` con el mensaje "Sesión expirada. Por favor, inicia sesión nuevamente."

## Comportamiento ante 403

El backend lo lanza por rol insuficiente (`require_admin`, `require_resource_manager`) o por gestor sin espacio asignado (`get_managed_space_id`, en `backend/app/deps.py`). El frontend no tiene un manejo global de 403 (solo de 401); cada vista debe tratar el error según su contexto.

## Riesgos conocidos

- JWT y usuario en `localStorage` (riesgo XSS): evitar scripts de terceros en el frontend.
- FKs redundantes generadas por `migrations.py` junto a las de `create_all` en una base limpia (hallazgo no bloqueante).
- Falta prueba determinista de la carrera del advisory lock en `proteger_administradores` (cobertura actual indirecta).
- E2E cubre solo Chromium; Firefox/WebKit y CI (GitHub Actions) son trabajo futuro.

## Deuda técnica

- No hay Alembic; el esquema evoluciona por SQL idempotente en `migrations.py`.
- `tzdata` solo está en `requirements-dev.txt`; el backend local en Windows sin Docker puede fallar en `services/reloj.py` si falta.
- "Reserva fuera de horario no cuenta en ocupación" solo está cubierta por tests de integración del backend con inserción directa en la base, no por E2E ni por la API pública.

## Reglas de parada

- Detenerse y pedir confirmación antes de instalar dependencias, modificar Docker/`.env`, ejecutar migraciones o tocar código funcional.
- No usar bases de datos de desarrollo o producción bajo ninguna circunstancia.
- No commitear ni hacer push sin autorización explícita en el turno actual.
- `AGENTS.md` (raíz) está desactualizado (afirma que no existe suite de pruebas y que la rama de trabajo es `feature/v0.1`); no modificarlo sin autorización explícita separada.

## Definición de terminado

Un cambio se considera terminado cuando: el código compila/type-checks (`npm run type-check`), pasa lint (`npm run lint`) y build (`npm run build`) en frontend; pasa `pytest -v` en backend contra `reservas_test`; pasan los tests Vitest afectados y, si aplica, el smoke E2E; no se modificó ningún contrato de API sin aprobación; y los cambios quedan documentados en el README de la carpeta afectada, siguiendo el patrón ya usado en `backend/app/*/README.md`.
