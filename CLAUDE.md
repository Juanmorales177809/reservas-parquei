# CLAUDE.md — reservas-parquei

## Propósito

Sistema de gestión de reservas de espacios institucionales: autenticación JWT, roles, disponibilidad horaria, aprobación de solicitudes, notificaciones, auditoría y paneles de gestión. Monorepo `backend/` (FastAPI) + `app_flutter/` (Flutter — única UI, Móvil/Escritorio nativos + Web). Todo el código, mensajes y documentación están en español; mantener ese idioma.

## Migración a Flutter — completada (Fase 7 del plan ejecutada)

`app_flutter/` reemplazó al frontend Next.js, que **ya se retiró del repo** (`frontend/` fue eliminado — commit `chore: retira frontend Next.js y promueve Flutter como única UI`). Flutter es la única UI, para Móvil (Android/iOS) y Escritorio (Windows/macOS/Linux) nativos + Web. No modificar `backend/` sin aprobación explícita separada — sigue vigente la misma regla que antes aplicaba con `frontend/`. Detalle completo del estado de la migración, decisiones de diseño y deuda técnica propia de Flutter en [app_flutter/CLAUDE.md](app_flutter/CLAUDE.md) — no duplicado aquí.

## Estado de referencia

- Rama de trabajo: `feature/soV0.1`.
- Commit de referencia: `914cf36e749e44f425c32fb50b63c9946d67866c`.
- Rama base para PR: `feature/v0.1`.

## Arquitectura general

```
Navegador → flutter_proxy (nginx) :8091 → (proxy /api, /docs, /openapi.json) → FastAPI :8000 → PostgreSQL :5432
Escritorio/Móvil nativo (Windows/macOS/Linux/Android/iOS) → FastAPI :8000 directo (sin proxy — usa cookie_jar propio, no navegador)
```

El navegador (Web) solo habla con `flutter_proxy`, igual que antes hablaba solo con Next.js — mismo patrón same-origin, mismo motivo (la cookie de sesión `HttpOnly`/`SameSite=Lax` exige mismo origen). Los clientes nativos no pasan por ningún proxy: no están sujetos a CORS/SameSite del navegador, hablan directo con el backend. PostgreSQL no se expone al host (red interna en Docker). Detalle completo en [README.md](README.md) y en `docker-compose.yml`.

**`http://localhost:8091` corre contra `reservas_db` (base de desarrollo), no contra `reservas_test`** — ver la advertencia en [app_flutter/CLAUDE.md](app_flutter/CLAUDE.md) antes de usarlo para cualquier verificación o E2E.

## Separación backend/app_flutter

- `backend/app/`: capas `api/` (rutas), `services/` (reglas de negocio), `crud/` (SQLAlchemy), `schemas/` (Pydantic), `models/`, `domain/` (enums y value objects tipados), `auth/` (JWT + bcrypt), `deps.py` (autorización), `main.py` (lifespan), `migrations.py` (SQL idempotente, sin Alembic).
- `app_flutter/lib/`: `core/` (config, red, router, tema, widgets compartidos), `features/<dominio>/` (`data/domain/application/presentation`, uno por recurso del backend), `shell/` (navegación adaptativa: bottom nav en móvil/tablet angosta, rail lateral en tablet/ventana media, top nav en escritorio/Web ancho).
- Ver [backend/CLAUDE.md](backend/CLAUDE.md), [backend/tests/CLAUDE.md](backend/tests/CLAUDE.md), [app_flutter/CLAUDE.md](app_flutter/CLAUDE.md) para detalle por área.

## Comandos principales

```bash
docker compose up -d --build      # levantar todo el stack (desarrollo): db + backend + flutter_proxy
docker compose logs -f backend    # logs backend
docker compose logs -f flutter_proxy   # logs del proxy Web (nginx)
docker compose down               # detener sin borrar datos
```

`flutter_proxy` sirve el build estático de `app_flutter/build/web` — hay que generarlo antes (`flutter build web --dart-define-from-file=env/web.json` desde `app_flutter/`) o el proxy no tiene qué servir. **Si ese directorio falta, nginx responde 403, no 404.**

## Despliegue continuo (CD)

El servidor **no se actualiza a mano**: un agente propio (`deploy/`) consulta cada 3 minutos la última corrida **verde** de CI en `feature/soV0.1`, descarga el bundle web que esa corrida publicó como artefacto, deja el checkout en ese commit exacto y converge el stack, con health check y rollback automático.

Es un modelo *pull* (el servidor consulta a GitHub, GitHub nunca entra) porque el servidor tiene IP privada y quien lo opera no es admin del repo. El ciclo completo es: `git push` → ~7 min de CI → hasta 3 min de poll. Nadie compila Flutter en el servidor.

Detalle completo, instalación y las decisiones no obvias en [deploy/README.md](deploy/README.md) — incluido que **el agente no se autoactualiza**: cambiar `deploy/reservas-deploy.sh` exige reinstalarlo a mano.

Backend local (sin Docker): `cd backend && python -m venv .venv && pip install -r requirements.txt && uvicorn app.main:app --reload` (requiere `DATABASE_URL` y `SECRET_KEY` exportadas; `config.py` no llama `load_dotenv()`).
Flutter local: ver "Comandos" en [app_flutter/CLAUDE.md](app_flutter/CLAUDE.md) (`flutter analyze`, `flutter test`, `flutter run -d chrome|windows|...`).

## Comandos de tests

```bash
# Backend (PostgreSQL real de pruebas)
docker compose -f docker-compose.test.yml up -d --wait
cd backend && pytest -v

# Flutter — unitarios/widget
cd app_flutter && flutter analyze && flutter test

# Flutter — E2E (integration_test; ver bloqueos de entorno vigentes en app_flutter/CLAUDE.md antes de intentarlo)
cd app_flutter
flutter drive --driver=test_driver/integration_test.dart --target=integration_test/reserva_flujo_test.dart -d chrome
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

`.env` / `.env.*` (excepto `.env.example`), `__pycache__/`, `.venv/`, `coverage/` (backend); `app_flutter/build/`, `app_flutter/.dart_tool/` (Flutter) — ver [.gitignore](.gitignore) y `app_flutter/.gitignore`.

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

`POST /auth/login` está excluido del interceptor global de 401 (`AuthInterceptor` en `app_flutter/lib/core/network/auth_interceptor.dart`, equivalente al viejo `apiFetch` de Next.js). Un 401 aquí son credenciales inválidas y el error llega al formulario de login (`LoginScreen`) vía `apiErrorMessage`, sin redirigir.

## Comportamiento ante 401 en endpoints protegidos

`AuthInterceptor` dispara `handleSessionExpired()` (`authProvider`), que limpia el estado de sesión en memoria y deja que el `redirect` de `go_router` (`app_router.dart`) mande a `/login`. No hay `localStorage` que limpiar: Flutter nunca guardó el JWT ahí — la sesión vive únicamente en la cookie `HttpOnly` que fija el backend (nativo: `cookie_jar` propio; Web: cookie del navegador, `withCredentials: true`). Ver "Sesión: cookie HttpOnly, nunca un token en el cliente" en `app_flutter/CLAUDE.md`.

## Comportamiento ante 403

El backend lo lanza por rol insuficiente (`require_admin`, `require_resource_manager`) o por gestor sin espacio asignado (`get_managed_space_id`, en `backend/app/deps.py`). No hay manejo global de 403 en `app_flutter/` (solo de 401 vía `AuthInterceptor`); cada pantalla trata el error según su contexto con `apiErrorMessage`/`apiErrorStatusCode`.

## Riesgos conocidos

- Cookie `HttpOnly`/`SameSite=Lax` como única fuente de sesión (riesgo XSS reducido, no eliminado — ver `app_flutter/CLAUDE.md`): evitar scripts de terceros. El JWT nunca se decodifica ni se guarda en `localStorage`/`shared_preferences`.
- FKs redundantes generadas por `migrations.py` junto a las de `create_all` en una base limpia (hallazgo no bloqueante).
- Falta prueba determinista de la carrera del advisory lock en `proteger_administradores` (cobertura actual indirecta).
- E2E (`app_flutter/integration_test/`) escrito pero sin correr de punta a punta todavía — dos gaps de entorno reales (Visual Studio no instalado para nativo, `flutter drive` sin soporte de `--use-existing-app` para Web + política de CORS del backend). Detalle completo en `app_flutter/CLAUDE.md`, sección "E2E".
- Builds nativos (Windows/Android) sin verificar en ejecución real por el mismo motivo (toolchain no instalado).

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

Un cambio se considera terminado cuando: pasa `pytest -v` en backend contra `reservas_test`; en `app_flutter/` pasan `flutter analyze` ("No issues found!") y `flutter test`, y si el cambio es de UI se verificó manualmente contra un backend real (análisis estático limpio no garantiza que el flujo funcione — ver los bugs reales documentados en `app_flutter/CLAUDE.md`); no se modificó ningún contrato de API sin aprobación; y los cambios quedan documentados (README de la carpeta afectada en `backend/`, o `app_flutter/CLAUDE.md` para Flutter, siguiendo el patrón ya establecido ahí).
