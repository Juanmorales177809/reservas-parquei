# Repository Agent Instructions

Última revisión: 2026-08-18. Commit de referencia: `f73b9c3e8f17c9d49d2715411ff9021c76b5c12e` (`feature/soV0.1`).

## Scope

Estas instrucciones aplican a todo el repositorio. Las instrucciones anidadas de `backend/AGENTS.md` y `frontend/AGENTS.md` añaden reglas específicas de esa carpeta y tienen prioridad sobre las de aquí cuando el archivo editado vive dentro de esa carpeta — pero ninguna instrucción anidada puede contradecir las reglas de seguridad de esta sección raíz (Security rules, Scope boundaries).

Para contexto y convenciones detalladas por carpeta, ver los `CLAUDE.md` existentes: raíz, `backend/CLAUDE.md`, `backend/tests/CLAUDE.md`, `frontend/CLAUDE.md`, `frontend/e2e/CLAUDE.md`. Este archivo no repite ese contenido — lo complementa con reglas accionables para agentes.

## Repository map

- `backend/` — API FastAPI (`app/`: `api/`, `auth/`, `crud/`, `domain/`, `models/`, `schemas/`, `services/`, `deps.py`, `config.py`, `db.py`, `main.py`, `migrations.py`); suite de pruebas en `backend/tests/` (pytest + PostgreSQL real).
- `frontend/` — Next.js 14 App Router (`src/app`, `src/components`, `src/context`, `src/services`, `src/types`, `src/utils`); pruebas unitarias/componentes con Vitest en `src/`; E2E con Playwright en `frontend/e2e/`.
- `docker-compose.yml` — stack de desarrollo (db, pgadmin, backend, frontend).
- `docker-compose.test.yml` — PostgreSQL exclusivo de pruebas (`reservas_test`, puerto `5433`), independiente del de desarrollo.
- `.github/workflows/ci.yml` — CI en GitHub Actions: tres jobs (`backend` pytest, `frontend` lint/type-check/test/build, `e2e` Playwright), disparado en push a `feature/soV0.1` y en PRs contra `feature/v0.1`/`feature/soV0.1`.
- `README.md` — guía de uso y despliegue. `CHANGELOG.md` — registro cronológico factual de fases, con hashes de commit reales.

## Exact commands

Backend (requiere `reservas_test` levantada, ver abajo):

```bash
cd backend
pytest -v
pytest -v tests/test_openapi_contrato.py
```

Frontend:

```bash
cd frontend
npm run test
npm run type-check
npm run lint
npm run build
```

E2E (Playwright, requiere `reservas_test` levantada):

```bash
cd frontend
npm run test:e2e            # smoke
npm run test:e2e:regresion  # smoke + regresión
npm run test:e2e:all        # suite completa — lo que corre CI también
```

Base de pruebas — levantar antes de correr backend o E2E, limpiar solo de forma manual y explícita, nunca automática ni desde un test:

```bash
docker compose -f docker-compose.test.yml up -d --wait
docker compose -f docker-compose.test.yml down -v   # limpieza manual, cuando ya no se necesite
```

## Workflow

- Inspeccionar `git status` antes de editar cualquier archivo.
- Trabajar con RED → GREEN cuando la tarea introduce o modifica una regla de negocio o comportamiento observable: escribir primero la prueba que falla, implementar hasta que pase.
- Mostrar qué archivos se van a modificar antes de tocarlos, especialmente si la tarea implica varias fases o pasos.
- Hacer cambios mínimos: no refactorizar, renombrar ni "mejorar" código fuera del alcance pedido.
- Ejecutar las pruebas relevantes (no necesariamente toda la suite en cada cambio menor, pero sí antes de dar una tarea por terminada).
- Usar `git diff --check` antes de hacer staging, para detectar errores de espacio en blanco.
- Revisar el diff completo y buscar secretos (`SECRET_KEY`, contraseñas, tokens, cadenas de conexión reales) antes de proponer un commit.
- No hacer `git commit` ni `git push` sin autorización explícita del usuario en el turno actual — la autorización de una tarea no cubre las siguientes.
- No usar `git add .` ni `git add -A`. Hacer staging explícito, archivo por archivo, listando exactamente lo que se autorizó.

## Scope boundaries

No tocar sin aprobación explícita y separada:

- Migraciones (`backend/app/migrations.py`) y cambios de esquema de base de datos.
- Docker (`Dockerfile`, `docker-compose*.yml`) o imágenes base.
- CI (`.github/workflows/ci.yml`).
- Dependencias (`requirements*.txt`, `package.json`/`package-lock.json`) — agregar, quitar o subir de versión.
- El snapshot de OpenAPI (`backend/tests/openapi.snapshot.json`) y, en general, el contrato de la API (rutas, métodos, schemas Pydantic).
- Mecanismo de cookies/JWT (atributos de la cookie, `deps.py`, `auth/auth.py`, `api/auth.py`).
- Rate limiting (`backend/app/services/rate_limit.py`).
- `frontend/` cuando la tarea está delimitada como backend-only.
- `backend/` cuando la tarea está delimitada como frontend-only.
- Secretos, `.env`/`.env.*` (salvo `.env.example`), credenciales, y archivos locales no versionados (p. ej. `handoff-casa.md`).

## Security rules

- Nunca registrar (logs, comentarios, mensajes de commit) passwords, tokens, cookies, el header `Authorization`, cuerpos completos de request/response ni ningún otro secreto.
- No devolver `str(exc)`, traceback ni detalles internos al cliente en respuestas de error; el handler global ya sanitiza esto (`backend/app/main.py`) — no lo debilites.
- No confiar en `X-Forwarded-For` para IP real sin un proxy confiable configurado (no existe uno en este despliegue).
- No reintroducir `localStorage.token` ni ningún almacenamiento de JS-accesible para el JWT en el frontend — la sesión vive en una cookie HttpOnly desde la Fase 9F-B.
- Mantener la compatibilidad dual JWT cookie + header `Authorization` en el backend hasta que exista una decisión explícita de retirarla (ver `CHANGELOG.md`, Fase 9G).
- Documentar riesgos aceptados y cualquier cambio de contrato en el `README.md`/`CHANGELOG.md` correspondiente, siguiendo el patrón ya usado.

## Git

- Commits atómicos: un cambio coherente por commit, no mezclar fases o propósitos distintos.
- Mensaje de commit explícito y descriptivo del cambio real.
- Comprobar los archivos en staging (`git diff --cached --name-only`) antes de commitear.
- No hacer push automático; el push requiere autorización explícita separada de la del commit.
- No alterar `master` ni `main` — no existen en este repo; la rama base es `feature/v0.1` y no debe tocarse sin autorización aparte.
- Tras publicar, verificar el hash (SHA), la rama y, si aplica, el estado de CI antes de darlo por confirmado — no asumir ni inventar un resultado de CI que no se haya consultado realmente.

## Done when

Una tarea está terminada solo cuando:

- Los archivos modificados coinciden exactamente con el alcance acordado.
- Las pruebas relevantes pasan.
- El diff está limpio (`git diff --check` sin errores).
- No hay secretos en el diff.
- Se reportan los riesgos conocidos y el trabajo pendiente, si los hay.
- El commit y/o push solo se realizan con autorización explícita del usuario en ese turno.

## No verificado / pendiente

- No existe un archivo de convenciones de commit unificado a nivel de todo el repo más allá de lo observado en `CHANGELOG.md` (`<tipo>: <resumen>`, p. ej. `security:`, `test:`, `docs:`); no se documenta aquí como regla obligatoria porque no hay una política formalizada que lo exija para todo tipo de cambio.
