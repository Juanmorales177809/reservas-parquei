# Despliegue en OpenShift — Gestión de Reservas

Guía paso a paso para desplegar el sistema en Red Hat OpenShift usando la consola web (web console). No requiere `oc` CLI.

## Requisitos

- Acceso a la consola web de OpenShift con permisos de proyecto
- Repositorio Git accesible desde OpenShift (GitHub, GitLab, etc.)

---

## 1. Crear el proyecto

1. En la consola web, ir a **Home → Projects**
2. Click **Create Project**
3. Nombre: `gestion-reservas` (o el que prefieras)
4. Click **Create**

---

## 2. Crear PostgreSQL desde Developer Catalog

1. Ir a **Developer** → **Add**
2. Click **Developer Catalog** → **Database**
3. Seleccionar **PostgreSQL** (la versión 15 si está disponible, sino 13+)
4. Click **Instantiate Template**
5. Configurar los parámetros:

   | Parámetro | Valor |
   |-----------|-------|
   | Namespace | `gestion-reservas` |
   | Database Service Name | `db` |
   | PostgreSQL Connection Username | `postgres` |
   | PostgreSQL Connection Password | `postgres` (o una más segura) |
   | PostgreSQL Database Name | `reservas_db` |

6. Click **Create**
7. Esperar a que el pod de PostgreSQL esté **Running**

> La instancia Postgres crea un Service llamado `db` y un Secret con las credenciales.

---

## 3. Crear el backend desde Git

1. Ir a **Developer** → **Add**
2. Click **Import from Git**
3. Completar:

   | Campo | Valor |
   |-------|-------|
   | Git Repo URL | `https://github.com/<tu-usuario>/<tu-repo>.git` |
   | Git Reference | `main` (o la rama a desplegar) |
   | Context Directory | `backend` |
   | Builder Image | **Dockerfile** |

4. Click **Show Advanced Options** o ir directo a la sección **Deployment**

### Variables de entorno del backend

En la sección **Environment Variables** (build & runtime), agregar:

| Variable | Valor esperado |
|----------|----------------|
| `DATABASE_URL` | `postgresql://postgres:<password>@db:5432/reservas_db` |
| `SECRET_KEY` | Generar con `openssl rand -hex 32` y copiar el resultado |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
| `BACKEND_CORS_ORIGINS` | `http://<frontend-route>` (se obtiene en el paso 5) |

> `DATABASE_URL` usa `db` como host porque es el nombre del Service de PostgreSQL.
> Si el password contiene caracteres especiales, usar URL-encoding.

5. Click **Create**
6. Esperar a que la build termine y el pod esté **Running**

### Health check (liveness/readiness)

Una vez creado el Deployment, ir a **Topology** → click en backend → **Actions** → **Edit Health Checks**:

| Tipo | Path | Puerto |
|------|------|--------|
| Liveness probe | `/health` | `8000` |
| Readiness probe | `/health` | `8000` |
| Startup probe | `/health` | `8000` |

Configurar `Initial Delay: 10` segundos para los tres.

---

## 4. Exponer la ruta del backend

1. En **Topology**, click en el servicio `backend`
2. Ir a la pestaña **Routes**
3. Click **Create Route**
4. Dejar los valores por defecto y click **Create**
5. Copiar la URL generada, ejemplo: `http://backend-gestion-reservas.apps.openshift.example.com`

---

## 5. Crear el frontend desde Git

1. Ir a **Developer** → **Add**
2. Click **Import from Git**
3. Completar:

   | Campo | Valor |
   |-------|-------|
   | Git Repo URL | `https://github.com/<tu-usuario>/<tu-repo>.git` |
   | Git Reference | `main` |
   | Context Directory | `frontend` |
   | Builder Image | **Dockerfile** |

### Build environment variable (obligatoria)

En la sección **Build Environment Variables** (no Runtime), agregar:

| Variable | Valor |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://<backend-route>` (la URL del paso 4) |

> `NEXT_PUBLIC_API_URL` se inyecta en tiempo de build (Next.js la reemplaza en el JS compilado). Si cambia la ruta del backend, hay que re-ejecutar la build.

4. Click **Create**
5. Esperar a que la build termine y el pod esté **Running**

### Health check del frontend

Añadir probes:

| Tipo | Path | Puerto |
|------|------|--------|
| Liveness probe | `/` | `3000` |
| Readiness probe | `/` | `3000` |

### Exponer ruta del frontend

1. Ir a **Topology** → click en `frontend`
2. **Routes** → **Create Route**
3. Copiar la URL del frontend, ejemplo: `http://frontend-gestion-reservas.apps.openshift.example.com`

---

## 6. Configurar CORS con la ruta del frontend

1. Ir a **Topology** → click en `backend`
2. Ir a la pestaña **Environment**
3. Editar `BACKEND_CORS_ORIGINS` (o agregarla si no se creó antes):
   ```
   https://frontend-gestion-reservas.apps.openshift.example.com
   ```
4. Si hay múltiples orígenes (por ejemplo localhost para pruebas), separar con comas:
   ```
   http://localhost:3000,https://frontend-gestion-reservas.apps.openshift.example.com
   ```
5. Ir a **Workloads** → **Deployments** → click en `backend` → **Actions** → **Restart Rollout**
6. Esperar a que el nuevo pod esté **Running**

---

## 7. Verificar el despliegue

1. Abrir la URL del frontend en el navegador
2. Debería cargar la página de login del sistema
3. Ingresar con las credenciales por defecto:
   - **Usuario**: `admin`
   - **Contraseña**: `admin123`
4. Probar navegación, creación de espacios y reservas

> Cambiar la contraseña del admin después del primer ingreso.

---

## Resumen de variables de entorno

| Variable | Dónde se define | Propósito |
|----------|----------------|-----------|
| `DATABASE_URL` | Backend Runtime | Conexión a PostgreSQL |
| `SECRET_KEY` | Backend Runtime | Firma de tokens JWT |
| `ALGORITHM` | Backend Runtime | Algoritmo JWT (siempre `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Backend Runtime | Tiempo de expiración del token |
| `BACKEND_CORS_ORIGINS` | Backend Runtime | URLs permitidas por CORS |
| `NEXT_PUBLIC_API_URL` | Frontend Build | URL del backend para el frontend |

---

## Solución de errores comunes

### El pod del backend no inicia

```text
Error: connection refused a la base de datos
```

- Verificar que PostgreSQL esté **Running**
- Verificar que `DATABASE_URL` apunte al host `db` (nombre del Service, no `localhost`)
- Verificar credenciales en el Secret de PostgreSQL

### El frontend carga pero la API no responde

1. Abrir las **Developer Tools** del navegador (F12)
2. Ir a la pestaña **Network** y buscar errores CORS o 404
3. Verificar `NEXT_PUBLIC_API_URL` apunte a la ruta del backend (con `https://`)
4. Verificar `BACKEND_CORS_ORIGINS` incluya la ruta del frontend

### Build falla en Dockerfile

- Verificar que el **Context Directory** sea `frontend` o `backend` según corresponda
- Verificar que el repositorio esté accesible (sin autenticación)
- En la build del frontend, revisar logs de build: **Builds** → click en build → **Logs**
- Error común: el build intenta instalar dependencias pero no encuentra `package-lock.json` si no se copia correctamente

### Error "Forbidden" al acceder al pod

OpenShift asigna un UID aleatorio. Los Dockerfiles ya incluyen `chgrp -R 0 /app && chmod -R g+rwX /app` para permitir acceso con cualquier UID. Si persiste:

1. Ir a **Administration** → **Namespace**
2. Verificar que el SCC asignado sea `restricted` o `anyuid`

### El frontend no encuentra assets estáticos

Si el CSS/JS no carga:

1. Revisar que la ruta del frontend esté correcta en **Routes**
2. Verificar los logs del pod del frontend: **Workloads** → **Pods** → click en pod → **Logs**
3. Revisar que el `next.config.js` tenga `output: 'standalone'` (ya está configurado)

---

## Notas importantes

- `SECRET_KEY` debe ser única y segura por despliegue. No reutilizar entre entornos.
- `NEXT_PUBLIC_API_URL` se fija en tiempo de build. Si la ruta del backend cambia, hay que re-ejecutar la build del frontend.
- Los valores de `docker-compose.yml` no se usan en OpenShift. Las variables se configuran directamente en la consola.
- El sistema no necesita volúmenes persistentes además del que crea PostgreSQL automáticamente.
