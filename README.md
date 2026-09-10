# Gestión de Reservas

Aplicación web para administrar espacios institucionales, sus recursos y las reservas realizadas por usuarios. Incluye autenticación JWT, roles, disponibilidad horaria, aprobación de solicitudes, notificaciones, auditoría y paneles de gestión.

## Funcionalidades

- Consulta pública de espacios, recursos activos y disponibilidad.
- Reservas de uno o varios bloques horarios consecutivos.
- Validación de capacidad, anticipación, estado y horario de atención.
- Prevención transaccional de reservas superpuestas en PostgreSQL.
- Aprobación automática configurable por espacio.
- Gestión de solicitudes por administradores y gestores.
- Notificaciones de solicitudes pendientes, aprobaciones, rechazos y cancelaciones.
- Dashboard con estadísticas de reservas y ocupación.
- Registro administrativo de cambios.
- Administración de usuarios, espacios y recursos.

## Tecnologías

| Capa | Tecnología |
| --- | --- |
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS y Recharts |
| Backend | FastAPI, SQLAlchemy, Pydantic y Uvicorn |
| Autenticación | JWT, Passlib y bcrypt |
| Base de datos | PostgreSQL 13 |
| Contenedores | Docker y Docker Compose |

## Arquitectura

```text
Navegador
   │
   ▼
Next.js :3000
   │  proxy /api, /docs y /openapi.json
   ▼
FastAPI :8000 (red interna)
   │
   ▼
PostgreSQL :5432 (red interna)
```

El navegador siempre se comunica con Next.js. Las solicitudes a `/api/*` son reenviadas internamente al backend. PostgreSQL no publica su puerto al host. pgAdmin es opcional y se expone en el puerto `8085` de forma predeterminada.

## Roles y permisos

| Rol | Capacidades principales |
| --- | --- |
| `usuario` | Consultar disponibilidad, crear reservas, consultar y editar solicitudes pendientes, cancelar reservas aprobadas y leer notificaciones. |
| `gestor` | Gestionar recursos, configuración y reservas únicamente del espacio asignado. |
| `admin` | Gestión global de usuarios, espacios, recursos, reservas, dashboard y control de cambios. |

Un gestor solo puede estar asignado a un espacio. La aplicación impide eliminar o degradar la propia cuenta administrativa y garantiza que permanezca al menos un administrador.

## Reglas de reserva

Para crear o modificar una reserva:

- El espacio y el recurso deben estar activos.
- El número de asistentes no puede superar la capacidad del recurso.
- El intervalo debe estar contenido completamente en el horario configurado.
- Las horas deben ser bloques completos; por ejemplo, `08:00–10:00`.
- Debe cumplirse la anticipación mínima configurada para el espacio.
- No puede existir otra reserva `esperando` o `aprobada` que se solape para el mismo recurso y fecha.
- Los intervalos contiguos sí están permitidos: `08:00–10:00` y `10:00–11:00`.

PostgreSQL aplica la restricción de solapamiento mediante la extensión `btree_gist`. La validación del backend ofrece un mensaje inmediato y la base de datos protege también frente a solicitudes concurrentes.

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

Todos los endpoints protegidos esperan:

```http
Authorization: Bearer <token>
```

| Método y ruta | Acceso | Propósito |
| --- | --- | --- |
| `POST /auth/login` | Público | Iniciar sesión y obtener el JWT. |
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
| `POST /reservas` | Autenticado | Crear una reserva. |
| `GET /reservas/mis-reservas` | Autenticado | Consultar reservas propias. |
| `PATCH /reservas/{id}` | Autenticado | Editar una reserva dentro de los permisos aplicables. |
| `PUT /reservas/{id}/cancelar` | Propietario | Cancelar una reserva aprobada propia. |
| `GET /reservas` | Admin o gestor | Listar reservas gestionables. |
| `PUT /reservas/{id}/estado` | Admin o gestor | Aprobar, rechazar o cancelar. |
| `GET/PATCH /notificaciones` | Autenticado | Consultar y marcar notificaciones. |
| `GET /admin/dashboard/summary` | Admin | Estadísticas globales. |
| `GET /gestion/dashboard/summary` | Admin o gestor | Estadísticas dentro del alcance gestionado. |
| `GET /admin/control-cambios` | Admin | Consultar la auditoría. |

La especificación completa y los esquemas de solicitud y respuesta están disponibles en Swagger UI.

## Estructura del proyecto

```text
gestionReservas/
├── backend/
│   ├── app/
│   │   ├── api/          # Endpoints FastAPI
│   │   ├── auth/         # Hash de contraseñas y JWT
│   │   ├── crud/         # Consultas de persistencia
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── schemas/      # Contratos Pydantic
│   │   ├── services/     # Reglas de negocio
│   │   ├── migrations.py # Ajustes incrementales de PostgreSQL
│   │   └── main.py       # Inicialización de la API
│   └── Dockerfile
├── frontend/
│   ├── src/app/          # Páginas Next.js
│   ├── src/components/   # Componentes compartidos
│   ├── src/context/      # Autenticación y notificaciones
│   ├── src/services/     # Cliente de la API
│   ├── src/types/        # Tipos TypeScript
│   └── Dockerfile
├── .env.example
└── docker-compose.yml
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

Para ejecutar el backend fuera de Docker, `DATABASE_URL` debe apuntar a un PostgreSQL accesible y `SECRET_KEY` debe estar exportada en el entorno. Actualmente el repositorio no incluye una suite automatizada de pruebas.

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
- El JWT se almacena actualmente en `localStorage`; por ello deben evitarse scripts de terceros y revisarse cuidadosamente los cambios de frontend que puedan introducir XSS.

## Taller de integración y normalización

El ejercicio de integración se rige por [`CONTRATO_API.md`](CONTRATO_API.md). El programa debe leer los datasets entregados, normalizar sus registros al contrato institucional, validar localmente y enviarlos al servicio HTTP configurado.

La ejecución mínima esperada es:

```bash
python programa.py
pytest
```

`URL_BASE` y `EQUIPO` se suministran como variables de entorno antes de ejecutar el programa. La implementación puede organizar internamente sus módulos como considere conveniente, siempre que respete el contrato y produzca el reporte final requerido.
