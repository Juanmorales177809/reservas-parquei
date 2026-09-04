# Gestión de Reservas

Aplicación web para administrar espacios institucionales, sus recursos y las reservas realizadas por usuarios. Incluye autenticación JWT, roles, disponibilidad horaria, aprobación de solicitudes, notificaciones, auditoría y paneles de gestión.

## Funcionalidades

- Consulta pública de laboratorios, espacios y recursos con disponibilidad horaria.
- **Forma única de reserva**: `LaboratorioReservaSheet` con dropdowns de `TipoReserva` y `MotivoSolicitud` (catálogos por laboratorio, FK `tipo_reserva_id`/`motivo_solicitud_id`), sin página inicial separada de motivos.
- Reservas multi-recurso y multi-espacio: al elegir un `Espacio` se pre-seleccionan sus `Recursos` pero son editables (quitar/poner) al reservar.
- Propuesta/contrapropuesta sin pasar a `rechazada`: el técnico propone horarios alternativos (`propuesta_motivo/horarios/por/en` en `reservas`, queda `esperando` con bloque activo), el usuario acepta (re-agenda), rechaza o contrapropone; correos con botón `Ver reserva` (`FRONTEND_URL`).
- Tipos y motivos en tabla por laboratorio (`tipos_reserva`, `motivos_solicitud` con `UNIQUE(laboratorio_id,nombre)`), no enums fijos.
- Recursos que exigen acompañamiento del auxiliar del laboratorio (`Recurso.requiere_apoyo_auxiliar`): al reservarlos, el campo `requiere_apoyo_auxiliar` de la reserva se fuerza a `true` sin que el usuario pueda destildarlo.
- Acompañantes nombrados (nombre y correo) por reserva.
- Validación de capacidad efectiva (min laboratorio/espacios/recursos), anticipación, estado y horario de atención.
- Prevención transaccional de reservas superpuestas en PostgreSQL (`btree_gist` `EXCLUDE` en `reservas`, `reserva_recursos` y `reserva_espacios`).
- Aprobación automática por flag de laboratorio o por gestor en su laboratorio.
- Gestión de solicitudes por administradores y gestores, incluido registro de asistencia y auditoría.
- Notificaciones in-app + correo saliente con link a `FRONTEND_URL/reservas/mis-reservas`.
- Dashboard, control de cambios y administración de usuarios/laboratorios/espacios/recursos/tipos/motivos.
- `Mi perfil` centrado dentro del `ShellRoute` con navbar visible (fix 2026-09-02).
- Correo opcional: toggle por laboratorio (`notificar_por_correo`) y preferencia por persona (`recibir_correos`), independientes entre sí.
- Reservas multi-día agrupadas (`POST /reservas/grupo`): un grupo con horario distinto por día, "mejor esfuerzo" por ocurrencia, cada día cancelable solo o el grupo entero de una.
- Invitación de Outlook Calendar al aprobar una reserva: adjunto `.ics` de invitación real (`METHOD:REQUEST`/`CANCEL`, técnico + usuario como asistentes) vía el mismo correo saliente ya existente — sin depender de ningún permiso de Microsoft Graph que requiera aprobación de un admin del tenant.

## Tecnologías

| Capa | Tecnología |
| --- | --- |
| Frontend | Flutter 3.47.1 (Web, Windows, Android/iOS) — única UI, Riverpod + Freezed + go_router |
| Backend | FastAPI, SQLAlchemy, Pydantic y Uvicorn |
| Autenticación | Supabase Auth (JWT `supabase_id` + cookie `access_token` HttpOnly) |
| Base de datos | PostgreSQL 17 (`reservas_test`) / 13 (`reservas_db` prod) + `btree_gist` |
| Contenedores | Docker y Docker Compose (nginx `flutter_proxy :8091` same-origin) |

## Imágenes base y runtimes

| Imagen | Uso | Versión fijada |
| --- | --- | --- |
| `node:24.19.0-alpine` | `frontend/Dockerfile` (builder y runner) | Tag versionado exacto |
| `python:3.12-slim-bookworm` | `backend/Dockerfile` | Tag versionado (minor + variante) |
| `postgres:13` | `docker-compose.yml` (desarrollo) | Sin cambios |
| `postgres:17` | `docker-compose.test.yml` (`reservas_test`) | Sin cambios |
| `dpage/pgadmin4:9.17` | `docker-compose.yml` (pgAdmin) | Tag versionado exacto |

Detalle de cada cambio, verificación, digest y riesgos aceptados en [`CHANGELOG.md`](CHANGELOG.md) (Fase 10).

## Arquitectura

```text
Navegador → flutter_proxy (nginx) :8091 → (proxy /api, /docs, /openapi.json) → FastAPI :8000 → PostgreSQL :5432
Móvil/Escritorio nativo (Windows/Android/iOS) → FastAPI :8000 directo (cookie_jar, sin proxy)
```

El navegador habla solo con `flutter_proxy` (same-origin, cookie `HttpOnly` `SameSite=Lax`); clientes nativos hablan directo. PostgreSQL y pgAdmin como antes (`:8085`). Ver `docker-compose.yml` y `CLAUDE.md`.

## Roles y permisos

| Rol | Capacidades principales |
| --- | --- |
| `usuario` | Consultar disponibilidad, crear reservas, consultar y editar solicitudes pendientes, cancelar reservas aprobadas y leer notificaciones. |
| `gestor` | Gestionar recursos, zonas, ensayos, configuración y reservas únicamente del espacio asignado. |
| `admin` | Gestión global de usuarios, espacios, recursos, reservas, dashboard y control de cambios. |

Un gestor solo puede estar asignado a un espacio. La aplicación impide eliminar o degradar la propia cuenta administrativa y garantiza que permanezca al menos un administrador.

## Reglas de reserva

Para crear o modificar una reserva:

- El espacio debe estar activo, y también cada recurso o zona incluido (`recurso_ids`/`zona_ids`). Debe indicarse al menos uno de los dos.
- El número de asistentes no puede superar la capacidad mínima entre los recursos y zonas seleccionados (si ninguno tiene capacidad definida, no se aplica el límite).
- El intervalo debe estar contenido completamente en el horario configurado.
- Las horas deben ser bloques completos; por ejemplo, `08:00–10:00`.
- Debe cumplirse la anticipación mínima configurada para el espacio.
- No puede existir otra reserva `esperando` o `aprobada` que se solape para el mismo recurso o zona y fecha.
- Los intervalos contiguos sí están permitidos: `08:00–10:00` y `10:00–11:00`.

PostgreSQL aplica la restricción de solapamiento mediante la extensión `btree_gist`. La validación del backend ofrece un mensaje inmediato y la base de datos protege también frente a solicitudes concurrentes.

### Zonas, ensayos, tipo y acompañantes

- Cada espacio tiene una modalidad de reserva (`equipos`, `zonas` o `mixto`) que determina si expone recursos individuales, zonas, o ambos.
- Una zona pertenece a un único espacio y puede tener recursos asociados (un recurso pertenece, como máximo, a una zona); es reservable aunque no tenga recursos propios.
- Los ensayos pertenecen a una zona y pueden seleccionarse opcionalmente al reservar; cada ensayo elegido debe corresponder a una de las zonas efectivamente reservadas.
- El tipo de reserva (`trabajo_investigacion`, `trabajo_grado`, `servicio_de_ensayo`) es opcional, salvo para los recursos marcados como prestación de servicios (PS): no están disponibles para el rol `usuario`, y `gestor`/`admin` solo pueden reservarlos con `tipo=servicio_de_ensayo`.
- Los acompañantes son opcionales: nombre y correo por cada persona adicional registrada en la reserva.

### Estados

```text
esperando ──► aprobada ──► cancelada
    │
    ├────────► rechazada
    └────────► cancelada
```

`rechazada` y `cancelada` son estados terminales. Una reserva rechazada no puede aprobarse posteriormente.

## Requisitos

- Docker Engine 24 o posterior.
- Docker Compose 2.20 o posterior.
- OpenSSL para generar la clave JWT.

No es necesario instalar Node.js, Python ni PostgreSQL en el equipo si se utiliza Docker Compose.

## Configuración inicial

1. Copiar el archivo de ejemplo:

   ```bash
   cp .env.example .env
   ```

2. Generar una clave JWT segura:

   ```bash
   openssl rand -hex 32
   ```

3. Guardar el resultado en `SECRET_KEY` y configurar las demás variables necesarias:

   ```env
   SECRET_KEY=<clave-generada-de-64-caracteres>

   POSTGRES_DB=reservas_db
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=<contraseña-segura>
   DATABASE_URL=postgresql://postgres:<contraseña-segura>@db:5432/reservas_db

   PGADMIN_DEFAULT_EMAIL=admin@example.com
   PGADMIN_DEFAULT_PASSWORD=<contraseña-segura>
   ```

   Si la contraseña de PostgreSQL contiene caracteres reservados para una URL, debe codificarse en `DATABASE_URL`.

4. Para crear el primer administrador, configurar temporalmente las tres variables siguientes:

   ```env
   INITIAL_ADMIN_USERNAME=administrador
   INITIAL_ADMIN_EMAIL=administrador@example.com
   INITIAL_ADMIN_PASSWORD=<contraseña-de-al-menos-12-caracteres>
   ```

Las tres variables `INITIAL_ADMIN_*` deben definirse juntas. El administrador solo se crea si todavía no existe ninguna cuenta con rol `admin`. Después de comprobar el acceso, pueden retirarse del entorno y recrearse el backend.

`SECRET_KEY` es obligatoria y debe contener al menos 32 caracteres. Cambiarla invalida todas las sesiones JWT existentes.

## Variables de entorno

| Variable | Predeterminado | Descripción |
| --- | --- | --- |
| `DATABASE_URL` | PostgreSQL interno | Cadena de conexión utilizada por FastAPI. |
| `POSTGRES_DB` | `reservas_db` | Nombre de la base de datos. |
| `POSTGRES_USER` | `postgres` | Usuario de PostgreSQL. |
| `POSTGRES_PASSWORD` | `postgres` | Contraseña de PostgreSQL; debe cambiarse fuera de desarrollo. |
| `SECRET_KEY` | Sin valor | Clave de firma JWT; obligatoria, mínimo 32 caracteres. |
| `ALGORITHM` | `HS256` | Algoritmo de firma JWT. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Duración de la sesión. |
| `APP_TIMEZONE` | `America/Bogota` | Zona horaria usada por las reglas de anticipación. |
| `BACKEND_CORS_ORIGINS` | `http://localhost:3000` | Orígenes permitidos, separados por comas. |
| `BACKEND_URL` | `http://backend:8000` | Destino interno del proxy de Next.js. |
| `INITIAL_ADMIN_USERNAME` | Vacío | Usuario opcional del primer administrador. |
| `INITIAL_ADMIN_EMAIL` | Vacío | Correo opcional del primer administrador. |
| `INITIAL_ADMIN_PASSWORD` | Vacío | Contraseña inicial, mínimo 12 caracteres. |
| `FRONTEND_PORT` | `3000` | Puerto público de la aplicación. |
| `PGADMIN_HOST_PORT` | `8085` | Puerto público de pgAdmin. |
| `PGADMIN_DEFAULT_EMAIL` | Sin valor | Usuario inicial de pgAdmin. |
| `PGADMIN_DEFAULT_PASSWORD` | Sin valor | Contraseña inicial de pgAdmin. |

## Ejecución con Docker Compose

Construir e iniciar todos los servicios:

```bash
docker compose up -d --build
```

Comprobar su estado:

```bash
docker compose ps
```

Ver los logs:

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

Detener los contenedores sin borrar datos:

```bash
docker compose down
```

Accesos predeterminados:

| Servicio | URL |
| --- | --- |
| Aplicación | http://localhost:3000 |
| Swagger UI | http://localhost:3000/docs |
| OpenAPI JSON | http://localhost:3000/openapi.json |
| pgAdmin | http://localhost:8085 |

Para conectar pgAdmin a PostgreSQL desde Docker, utilizar `db` como host, `5432` como puerto y las credenciales `POSTGRES_*` del archivo `.env`.

## API principal

Los endpoints protegidos se autentican únicamente con la cookie de sesión `access_token` (`HttpOnly`, `SameSite=Lax`, `Secure` solo en producción, fijada automáticamente por el navegador tras `POST /auth/login`). Desde la Fase 9G el backend **ya no acepta** el header `Authorization: Bearer <token>`, y `POST /auth/login` **ya no devuelve** `access_token` en el body (`LoginResponse` contiene solo `user`). Detalle del corte en [`CHANGELOG.md`](CHANGELOG.md) (Fase 9G).

| Método y ruta | Acceso | Propósito |
| --- | --- | --- |
| `POST /auth/login` | Público | Iniciar sesión: fija la cookie de sesión y devuelve el usuario (`LoginResponse`). |
| `POST /auth/logout` | Público | Cierra la sesión de cookie. Idempotente, no exige autenticación. |
| `GET /usuarios/me` | Autenticado | Consultar la cuenta actual. |
| `GET/POST/PUT/DELETE /usuarios` | Admin | Administrar usuarios. |
| `GET /espacios` | Público | Listar espacios. |
| `GET /espacios/{id}/disponibilidad` | Público | Consultar franjas de un espacio. |
| `POST/PUT/DELETE /espacios` | Admin | Administrar espacios. |
| `GET /espacios/gestion/configuracion` | Gestor | Consultar reglas del espacio asignado. |
| `PUT /espacios/gestion/configuracion` | Gestor | Modificar horarios, anticipación y aprobación automática. |
| `GET /recursos` | Público | Listar o filtrar recursos. |
| `GET /recursos/{id}/disponibilidad` | Público | Consultar disponibilidad de un recurso. |
| `POST/PUT/DELETE /recursos` | Admin o gestor | Administrar recursos dentro del alcance permitido. |
| `GET /zonas` | Público | Listar zonas de un espacio. |
| `POST/PUT/DELETE /zonas` | Admin o gestor | Administrar zonas dentro del alcance permitido. |
| `PUT /zonas/{id}/recursos` | Admin o gestor | Reemplazar por completo los recursos asociados a una zona. |
| `GET /ensayos` | Público | Listar ensayos de una zona. |
| `POST/PUT/DELETE /ensayos` | Admin o gestor | Administrar ensayos dentro del alcance permitido. |
| `POST /reservas` | Autenticado | Crear una reserva (recursos y/o espacios, `tipo_reserva_id`/`motivo_solicitud_id` opcionales). |
| `GET /reservas/mis-reservas` | Autenticado | Consultar reservas propias. |
| `PATCH /reservas/{id}` | Autenticado | Editar una reserva dentro de los permisos aplicables. |
| `PUT /reservas/{id}/cancelar` | Propietario | Cancelar una reserva aprobada propia. |
| `PUT /reservas/{id}/proponer-horarios` | Gestor/Admin | Proponer horarios alternativos (queda `esperando` + correo con link). |
| `PUT /reservas/{id}/contraproponer` | Propietario | Contraproponer horarios al técnico. |
| `PUT /reservas/{id}/aceptar-propuesta` | Según `propuesta_por` | Aceptar y re-agendar (revalida solapamiento). |
| `PUT /reservas/{id}/rechazar-propuesta` | Según `propuesta_por` | Rechazar propuesta (limpia, sigue `esperando`). |
| `GET /reservas` | Admin o gestor | Listar reservas gestionables. |
| `PUT /reservas/{id}/estado` | Admin o gestor | Aprobar, rechazar o cancelar (rechazada histórico). |
| `PUT /reservas/{id}/asistio` | Admin o gestor | Registrar si el reservante asistió. |
| `GET /tipos-reserva` `GET /motivos-solicitud` | Autenticado | Catálogos por laboratorio (`laboratorio_id`). |
| `GET/PATCH /notificaciones` | Autenticado | Consultar y marcar notificaciones. |
| `GET /admin/dashboard/summary` | Admin | Estadísticas globales. |
| `GET /gestion/dashboard/summary` | Admin o gestor | Estadísticas dentro del alcance gestionado. |
| `GET /admin/control-cambios` | Admin | Consultar la auditoría. |

La especificación completa y los esquemas de solicitud y respuesta están disponibles en Swagger UI.

## Estructura del proyecto

```text
gestionReservas/
├── .github/workflows/    # CI (GitHub Actions)
├── backend/
│   ├── app/
│   │   ├── api/          # Endpoints FastAPI
│   │   ├── auth/         # Hash de contraseñas y JWT
│   │   ├── crud/         # Consultas de persistencia
│   │   ├── domain/       # Enums y value objects tipados (horarios, roles, estados)
│   │   ├── middleware/   # Middleware ASGI (trazabilidad por request id)
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── schemas/      # Contratos Pydantic
│   │   ├── services/     # Reglas de negocio
│   │   ├── migrations.py # Ajustes incrementales de PostgreSQL
│   │   ├── deps.py       # Dependencias de autorización
│   │   └── main.py       # Inicialización de la API
│   ├── tests/            # Suite automatizada (pytest + PostgreSQL de prueba)
│   ├── pytest.ini
│   ├── requirements-dev.txt
│   └── Dockerfile
├── app_flutter/        # Única UI (Flutter Web + Windows/Android/iOS)
│   ├── lib/core/         # Config, red (dio+cookie), router (go_router), tema, widgets
│   ├── lib/features/     # laboratorios, espacios, recursos, reservas, tipos_reserva, motivos_solicitud, usuarios, auditoría
│   ├── lib/shell/        # AppShell adaptativo (bottom/rail/top nav)
│   ├── integration_test/ # E2E Flutter (Windows nativo)
│   └── test/             # Unitarios/widget
├── frontend/ (retirado, ver `app_flutter/CLAUDE.md` Fase 7)
├── .env.example
├── docker-compose.yml
└── docker-compose.test.yml
```

## Base de datos y migraciones

Durante el arranque, el backend:

1. Crea las tablas que todavía no existan.
2. Ejecuta las migraciones incrementales incluidas en `backend/app/migrations.py`.
3. Instala `btree_gist` y crea la restricción contra solapamientos.
4. Carga los espacios iniciales si corresponde.
5. Crea opcionalmente el primer administrador.

El usuario de `DATABASE_URL` necesita permisos para crear la extensión `btree_gist`, tablas, índices y restricciones. Si ya existen reservas solapadas, la instalación de la restricción se detendrá hasta corregir esos registros.

Los espacios con reservas, recursos o gestores no pueden eliminarse. Deben marcarse como `inactivo` para preservar el historial. Del mismo modo, un recurso con reservas no puede trasladarse a otro espacio.

## Persistencia, respaldo y restauración

Los datos se conservan en los volúmenes `reservas_postgres_data` y `reservas_pgadmin_data` de forma predeterminada.

Crear un respaldo:

```bash
docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" > reservas.sql
```

Si las variables no están exportadas en la terminal, sustituirlas por los valores de `.env`.

Restaurar un respaldo en una base vacía:

```bash
docker compose exec -T db psql -U postgres -d reservas_db < reservas.sql
```

> `docker compose down -v` elimina los volúmenes y todos los datos. No debe utilizarse salvo que se quiera reiniciar completamente el sistema y exista un respaldo válido.

## Desarrollo local

Frontend:

```bash
cd frontend
npm ci
npm run dev
```

Verificaciones disponibles:

```bash
npm run type-check
npm run lint
npm run build
```

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Para ejecutar el backend fuera de Docker, `DATABASE_URL` debe apuntar a un PostgreSQL accesible y `SECRET_KEY` debe estar exportada en el entorno.

### Pruebas automatizadas

La suite del backend (Fase 0) se ejecuta contra una base PostgreSQL exclusiva de pruebas (`reservas_test` en `localhost:5433`), sin SQLite y sin datos de producción:

```bash
docker compose -f docker-compose.test.yml up -d --wait
cd backend
python -m venv .venv
pip install -r requirements.txt -r requirements-dev.txt
pytest -v
```

Para limpiar la base de pruebas: `docker compose -f docker-compose.test.yml down -v`. Detalles de la suite y de las reglas cubiertas en `backend/tests/README.md`.

## Pruebas E2E con Playwright

Cubren el flujo real del frontend (`:3000`) contra el backend (`:8000`) y la misma base exclusiva de pruebas usada por el backend: `reservas_test` en `localhost:5433`. **Nunca se usa la base de desarrollo ni producción.**

Requisitos: Node.js y npm (versión indicada en `frontend/e2e/README.md`).

```bash
cd frontend
npm ci
npx playwright install chromium
```

Preparación manual de la base de pruebas (desde la raíz del repo):

```bash
docker compose -f docker-compose.test.yml up -d --wait
```

Ejecución:

```bash
cd frontend
npm run test:e2e            # smoke
npm run test:e2e:regresion  # smoke + regresión
npm run test:e2e:all        # conjunto completo configurado
```

Para conocer el conteo real vigente de escenarios, sin depender de cifras desactualizadas en la documentación:

```bash
npx playwright test --list
```

Reporte HTML de la última ejecución:

```bash
npm run test:e2e:report
```

Limpieza de la base de pruebas, siempre manual y explícita — Playwright **no** ejecuta `down -v` automáticamente en ningún momento:

```bash
docker compose -f docker-compose.test.yml down -v
```

No deben rastrearse en git los artefactos de esta suite: `frontend/e2e/.auth/` (sesiones guardadas), `frontend/test-results/`, `frontend/playwright-report/`, ni ningún secreto o credencial real (las credenciales usadas en `playwright.config.ts` son ficticias y exclusivas del proceso E2E local). Detalle completo en `frontend/e2e/README.md`.

## Integración continua (CI)

`.github/workflows/ci.yml` corre en cada push a `feature/soV0.1` y en cada pull request contra `feature/v0.1` o `feature/soV0.1`, con tres jobs independientes:

| Job | Contenido |
| --- | --- |
| `backend` | `pytest -v` (incluye el contrato de OpenAPI) contra un Postgres 13 de servicio, propio del job. |
| `frontend` | `npm run lint`, `type-check`, `test` (Vitest) y `build`; auditoría de dependencias (`npm audit`) informativa, no bloqueante. |
| `e2e` | Levanta backend y frontend en el runner y corre la suite completa de Playwright (`npm run test:e2e:all`) contra su propio Postgres de servicio. Depende de que `backend` y `frontend` hayan pasado. |

Ninguna credencial usada en el workflow es real: son los mismos valores ficticios ya presentes en `backend/tests/conftest.py` y `frontend/playwright.config.ts`. No hay despliegue automático — el alcance de CI es solo verificación.

## Solución de problemas

### El backend aparece como `unhealthy`

Consultar primero:

```bash
docker compose logs --tail=200 backend
```

Si aparece `SECRET_KEY es obligatoria y debe tener al menos 32 caracteres`, generar una clave con `openssl rand -hex 32`, actualizar `.env` y recrear el servicio:

```bash
docker compose up -d --build --force-recreate backend
```

### El frontend no inicia

El frontend espera que el backend esté saludable. Revisar `docker compose ps` y los logs del backend antes de diagnosticar Next.js.

### Error de conexión a PostgreSQL

- Dentro de Docker, el host debe ser `db`, no `localhost`.
- `DATABASE_URL` debe coincidir con `POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB`.
- Si se cambia la contraseña después de haber creado el volumen, PostgreSQL no actualiza automáticamente la contraseña almacenada.

### Conflicto al crear una reserva

Una respuesta HTTP `409` indica que otro usuario reservó el mismo recurso y horario o que la transición de estado solicitada no está permitida. Debe actualizarse la disponibilidad antes de volver a intentar.

## Seguridad operativa

- No versionar `.env`, respaldos ni claves reales.
- Utilizar contraseñas diferentes para PostgreSQL, pgAdmin y la cuenta administrativa.
- Retirar `INITIAL_ADMIN_*` después del aprovisionamiento inicial.
- No usar credenciales predeterminadas en producción.
- Servir la aplicación detrás de HTTPS en entornos públicos.
- El JWT viaja en una cookie de sesión `access_token` (`HttpOnly`, `SameSite=Lax`, `Secure` solo en producción) fijada por el backend; JavaScript de página no puede leerla ni escribirla, lo que reduce el riesgo de robo de token por XSS frente al modelo anterior (JWT en `localStorage`, retirado del frontend en la Fase 9F-B). Desde la Fase 9G el backend **solo** acepta la cookie: el header `Authorization: Bearer` y el `access_token` del body de login fueron retirados del contrato. Sigue habiendo riesgo de **CSRF, mitigado pero no eliminado** por `SameSite=Lax` + cookie host-only + proxy same-origin de Next.js (todo el tráfico del navegador al backend pasa por `/api`); **no existe token CSRF ni validación de Origin/Referer** (decisión del análisis 9H: diferida, no implementada). **No se aceptan clientes cross-origin con cookies** (CORS sin credenciales + SameSite=Lax + proxy mismo-origen). Los clientes no navegador se autentican con el mecanismo cookie-only y **no se consideran un vector CSRF**. La fase 9H debe reabrirse antes de: `SameSite=None`, Domain compartido, CORS con credentials, subdominios autenticados, un cliente web cross-origin o mutaciones accesibles desde otros orígenes (detalle en [`CHANGELOG.md`](CHANGELOG.md), Fase 9H). Evitar scripts de terceros y revisar con cuidado cualquier cambio de frontend que pueda introducir XSS sigue siendo válido.
- Cabeceras de seguridad (CSP, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`) en todas las respuestas de backend y frontend. `Strict-Transport-Security` y `Cross-Origin-Opener-Policy` requieren fijar `ENVIRONMENT=production` explícitamente — no se activan solo por desplegar con Docker Compose.
- `POST /auth/login` aplica límite de intentos (5 fallos por ventana deslizante de 15 minutos, por IP + username) para mitigar fuerza bruta. Es una mitigación en memoria del proceso, no distribuida: si el backend llega a correr con varios workers o réplicas, cada uno cuenta por separado.
- Cualquier excepción no controlada del backend responde siempre `500` con un mensaje genérico; el detalle (traceback, tipo de excepción) solo se registra en el log del servidor, nunca en la respuesta al cliente.
- Detalle completo de estas decisiones, valores y riesgos aceptados en [`CHANGELOG.md`](CHANGELOG.md).

