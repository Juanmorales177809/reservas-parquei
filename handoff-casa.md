# Handoff — continuar en otra máquina

> Archivo **local**, no versionado. No debe commitearse ni pushearse.
> Generado para retomar el desarrollo de `reservas-parquei` en otra máquina,
> con la misma cuenta.

## 1. Estado de rama y commit

- Repositorio: `reservas-parquei` — `https://github.com/Juanmorales177809/reservas-parquei.git`
- Rama de trabajo: `feature/soV0.1`
- Rama base para PR: `feature/v0.1` (no existe `master`/`main` en este repo)
- HEAD local y remoto sincronizados en: `90ee75b2d3edd09aa479a957fb877c38f39ad041`
- Último commit: `ci: add GitHub Actions gates and OpenAPI contract snapshot`
- `git status -sb` en el momento de este handoff:
  ```
  ## feature/soV0.1...origin/feature/soV0.1
  ?? AGENTS.md
  ?? CLAUDE.md
  ?? Documentacion/
  ?? backend/CLAUDE.md
  ?? backend/tests/CLAUDE.md
  ?? frontend/CLAUDE.md
  ?? frontend/e2e/CLAUDE.md
  ```
  Sin cambios pendientes en archivos trackeados; los 7 untracked de arriba son preexistentes (ver sección 13).

## 2. Resultado de la última ejecución de CI (commit `90ee75b`)

Run de GitHub Actions `31846776949` (workflow `.github/workflows/ci.yml`), disparado por el push de este commit — **completado, en verde, sin intervención**:

| Job | Estado final |
|---|---|
| `Backend (pytest)` | ✅ success (1m9s) |
| `Frontend (lint, type-check, test, build)` | ✅ success (2m15s) |
| `E2E (Playwright)` | ✅ success (3m7s) |

Run completo: ✅ success. Fue la primera ejecución real del workflow creado en la Fase 8; no se reinició, no se modificó código para "corregir" nada, no hubo push adicional. Hay tres anotaciones informativas y no bloqueantes sobre deprecación de Node.js 20 en las acciones internas de GitHub (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-node@v4`, `actions/cache@v4`) — son sobre el runtime interno con el que GitHub ejecuta las Actions, no sobre el Node 24.19.0 del proyecto; no requieren ninguna acción.

Detalle: `https://github.com/Juanmorales177809/reservas-parquei/actions/runs/31846776949`.

**Siguiente paso exacto al retomar**: no queda nada pendiente de este run — está cerrado y verde. Decidir la siguiente fase (ver sección 14).

## 3. Fases completadas

- **Fase 0–4**: dominio tipado del backend, servicios, auditoría, reloj inyectable, horarios, lifespan, RN-005, ocupación con horario real.
- **Fase 5A–5C**: frontend Next.js 14 con tipos/guards/accesibilidad, Vitest + RTL (45 tests), Playwright E2E (26 escenarios, 78 skips esperados por diseño de proyectos-rol), corrección del 401 en login.
- **Fase 6**: creación de los 5 `CLAUDE.md` de contexto (untracked, ver sección 13), con una ronda de revisión y correcciones aplicadas.
- **Fase 7**: pinning de `backend/requirements.txt` verificado en Python 3.14 local y `python:3.10-slim` (Docker real), `tzdata` condicionado a Windows, sección de E2E agregada a `README.md`. Commit `f24ae18`, publicado.
- **Fase 8**: snapshot de contrato OpenAPI (`backend/tests/openapi.snapshot.json` + `backend/tests/test_openapi_contrato.py`), `frontend/playwright.config.ts` hecho compatible con CI (arranque condicional del backend), workflow `.github/workflows/ci.yml` (jobs backend/frontend/E2E, Postgres 13 como service container, sin Docker Compose, sin secretos reales, artefactos solo en fallo con retención de 7 días). Commit `90ee75b`, publicado. Primera ejecución de CI: ver sección 2.

## 4. Siguiente paso exacto

Fase 8 cerrada: el run `31846776949` terminó completo en verde (backend, frontend y E2E, ver sección 2). No queda ningún job pendiente de revisión.

Siguiente paso: decidir con el usuario qué fase se arranca a continuación — Fase 9 (hardening de seguridad, sin cambiar contratos), Fase 10 (imágenes base EOL de Docker), deuda técnica de frontend, o backlog de negocio (RN-006 en adelante). Ninguna de esas fases está aprobada todavía; no empezar ninguna sin autorización explícita del turno correspondiente.

## 5. Comandos para preparar una máquina nueva

```bash
git clone https://github.com/Juanmorales177809/reservas-parquei.git
cd reservas-parquei
git checkout feature/soV0.1
git pull origin feature/soV0.1
```

Después, copiar manualmente a la máquina nueva los archivos locales no versionados listados en la sección 13 (no viajan con `git clone`).

Backend:

```bash
cd backend
python -m venv .venv
# Windows:
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
# macOS/Linux:
# .venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
```

Frontend:

```bash
cd frontend
npm ci
npx playwright install chromium
```

## 6. Variables de entorno necesarias (placeholders, sin valores reales)

Para levantar el stack completo con Docker Compose (`.env` en la raíz, copiado de `.env.example`, **nunca versionado**):

```env
SECRET_KEY=<SECRET_KEY>                      # mínimo 32 caracteres
POSTGRES_DB=reservas_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<POSTGRES_PASSWORD>
DATABASE_URL=postgresql://postgres:<POSTGRES_PASSWORD>@db:5432/reservas_db
PGADMIN_DEFAULT_EMAIL=<PGADMIN_DEFAULT_EMAIL>
PGADMIN_DEFAULT_PASSWORD=<PGADMIN_DEFAULT_PASSWORD>
# Opcionales, solo para crear el primer admin (retirar tras el primer arranque):
INITIAL_ADMIN_USERNAME=<INITIAL_ADMIN_USERNAME>
INITIAL_ADMIN_EMAIL=<INITIAL_ADMIN_EMAIL>
INITIAL_ADMIN_PASSWORD=<INITIAL_ADMIN_PASSWORD>  # mínimo 12 caracteres
```

Para backend local sin Docker (`config.py` no llama `load_dotenv()`, hay que exportarlas en el shell):

```bash
DATABASE_URL=<DATABASE_URL>
SECRET_KEY=<TEST_SECRET_KEY>
```

Para pruebas backend (`backend/tests/conftest.py` ya trae defaults ficticios si no se exportan estas dos):

```bash
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5433/reservas_test
TEST_SECRET_KEY=<TEST_SECRET_KEY>   # cualquier valor ficticio ≥32 caracteres
```

Para E2E (`frontend/playwright.config.ts`, valores ficticios ya hardcodeados ahí mismo, no son secretos reales — no hace falta exportarlas a mano salvo que se quieran cambiar):

```bash
BACKEND_URL=<BACKEND_URL>                    # http://localhost:8000 en local
INITIAL_ADMIN_PASSWORD=<INITIAL_ADMIN_PASSWORD>
```

## 7. Puertos

| Servicio | Puerto |
|---|---|
| Frontend (Next.js) | `3000` |
| Backend (FastAPI) | `8000` |
| PostgreSQL desarrollo (Docker interno, no expuesto al host) | `5432` |
| PostgreSQL de pruebas (`reservas_test`) | `5433` (host) → `5432` (contenedor) |
| pgAdmin (opcional) | `8085` (host) → `5050` (contenedor) |

## 8. Base de datos de pruebas

- **Única base válida para pruebas/inspección**: `reservas_test`, `localhost:5433`, vía `docker-compose.test.yml` en la raíz del repo.
- **Nunca** `reservas_db` (desarrollo) ni ninguna base de producción.
- Arranque:
  ```bash
  docker compose -f docker-compose.test.yml up -d --wait
  ```
- El lifespan del backend siembra el esquema, migraciones idempotentes, `btree_gist`, 6 espacios (horario 07:00–19:00 lun–sáb) y, si se configuran `INITIAL_ADMIN_*`, el admin de pruebas.

## 9. Comandos backend

```bash
cd backend
pytest -v                                   # suite completa (187 tests: 185 + 2 de contrato OpenAPI)
pytest -v tests/test_openapi_contrato.py    # solo el contrato de OpenAPI (requiere reservas_test arriba, hereda el fixture autouse de conftest.py)
```

## 10. Comandos frontend

```bash
cd frontend
npm run type-check
npm run lint
npm run test           # Vitest, 45 tests
npm run build           # standalone
```

## 11. Comandos E2E

```bash
cd frontend
npm run test:e2e            # smoke
npm run test:e2e:regresion  # smoke + regresión
npm run test:e2e:all        # completo — 26 passed / 78 skipped esperado (4 proyectos por rol)
npx playwright test --list  # conteo real vigente de escenarios, no confiar en cifras fijas viejas
npm run test:e2e:report     # reporte HTML de la última corrida
```

## 12. Limpieza manual

```bash
docker compose -f docker-compose.test.yml down -v
```

**Siempre manual y explícita.** Nunca automática, nunca desde un test, nunca desde CI (el workflow usa un service container efímero de GitHub Actions, no `docker compose`, así que esto no aplica a CI — solo a la base local levantada a mano).

## 13. Archivos locales no versionados (no viajan con `git clone`)

Copiar manualmente desde esta máquina si se quieren conservar en la nueva:

- `AGENTS.md` (raíz) — desactualizado, no modificar sin autorización aparte (afirma que no hay suite de pruebas y que la rama es `feature/v0.1`; ambas cosas ya no son ciertas).
- `Documentacion/Documentacion_AppReserva_Solucion (2).docx` — binario, no se documenta su contenido aquí.
- `CLAUDE.md` (raíz)
- `backend/CLAUDE.md`
- `backend/tests/CLAUDE.md`
- `frontend/CLAUDE.md`
- `frontend/e2e/CLAUDE.md`
- Este mismo archivo, `handoff-casa.md`.

Tampoco viajan (no son archivos de git, son estado de entorno): `backend/.venv`, `frontend/node_modules`, `frontend/.next`, contenedores/imágenes Docker locales (`reservas_test_db`, etc.), `.pytest_cache`, `frontend/coverage`, `frontend/test-results`, `frontend/playwright-report`, `frontend/e2e/.auth/`.

## 14. Decisiones pendientes

- Definir la siguiente fase a implementar: Fase 9 (hardening de seguridad, sin cambiar contratos), Fase 10 (imágenes base EOL de Docker), deuda técnica de frontend, o backlog de negocio (reglas RN-006 en adelante) — todas discutidas en el roadmap pero ninguna aprobada todavía.
- Decidir si se trackea y actualiza `AGENTS.md`, o se reemplaza por los `CLAUDE.md` ya creados.
- Decidir si Node 20 (el de `frontend/Dockerfile`, producción) se valida en algún punto contra lo que hoy corre en CI/local con Node 24.19.0 — nunca se verificó el build de Docker con Node 20 en esta serie de sesiones.

## 15. Riesgos conocidos

- JWT y usuario en `localStorage` (riesgo XSS) — deuda aceptada, documentada.
- `websockets` transitivo difiere entre Python 3.14 (entorno local de pruebas) y `python:3.10-slim` (Docker real): `17.0.1` vs `16.1.1`. Sin impacto observado, no pinneado (fuera de alcance de la Fase 7).
- FKs redundantes en `backend/app/migrations.py` sobre una base limpia (hallazgo no bloqueante).
- Falta test determinista de la carrera del advisory lock en `proteger_administradores`.
- "Reserva fuera de horario no cuenta en ocupación" solo cubierta por tests de integración del backend con inserción directa en la base, no por E2E ni por la API pública.
- `tzdata` en `requirements.txt` está condicionado a `sys_platform == "win32"`: en Linux/Docker se omite a propósito, no es un bug.
- El workflow de CI (`.github/workflows/ci.yml`) tuvo su primera ejecución real con el commit `90ee75b` y quedó en verde (sección 2) — riesgo ya despejado, se deja la nota por trazabilidad.

## 16. Reglas de no tocar producción

- Ninguna tarea de desarrollo o de este asistente debe leer, escribir ni migrar `reservas_db` (desarrollo) ni ninguna base de producción.
- Solo `reservas_test` (puerto `5433`) es válida para pruebas e inspección.
- No usar credenciales reales en ningún archivo de este repo, ni en este handoff.
- No modificar `feature/v0.1` (rama base) sin autorización aparte — y mucho menos ninguna rama de producción si llegara a existir.

## 17. Reglas de no hacer commit/push sin autorización

- No hacer `git commit` ni `git push` sin autorización explícita del usuario en el turno actual — la autorización de una fase no cubre las siguientes.
- No usar `git reset --hard`, `git clean -fd`, ni sobrescribir cambios sin confirmar antes con `git status`.
- Este archivo (`handoff-casa.md`) es local a propósito: no debe agregarse al índice ni commitearse salvo que el usuario lo pida explícitamente más adelante.
