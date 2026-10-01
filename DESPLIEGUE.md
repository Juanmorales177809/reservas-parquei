# Despliegue en un servidor

Todo corre con Docker Compose: base de datos, preparación de la base, backend y frontend. No hace falta instalar Python, Node ni PostgreSQL en el servidor.

## Qué levanta

| Servicio | Qué hace | Se publica |
|---|---|---|
| `db` | PostgreSQL 13 con su volumen | No, nunca |
| `migrar` | Deja la base lista y termina (no queda vivo) | No |
| `ajustar_volumenes` | Devuelve al backend (que corre sin privilegios) el dueño del volumen de adjuntos y termina | No |
| `backend` | API (FastAPI) | Solo en `127.0.0.1` del servidor |
| `frontend` | La aplicación web (Next.js); reenvía `/api` al backend por la red interna | Sí, en `FRONTEND_HOST_PORT` |
| `pgadmin` | Inspección de la base, **opcional** (perfil `herramientas`) | Solo en `127.0.0.1` |

El orden de arranque lo garantiza Compose: `db` sana, luego `migrar` y `ajustar_volumenes` terminan bien, luego `backend` sano, luego `frontend`. Si `migrar` falla, el backend no arranca.

## Requisitos

- Docker Engine y el plugin Compose (`docker compose version`).
- Acceso al repositorio.
- Un nombre o IP por el que los usuarios abrirán la aplicación y, recomendado, un certificado TLS.

## Primer despliegue

```bash
git clone https://github.com/Juanmorales177809/reservas-parquei.git
cd reservas-parquei
cp .env.example .env
```

Edite `.env`. Lo que **debe** cambiar en un servidor:

| Variable | Qué poner |
|---|---|
| `ENTORNO` | `produccion`. Con esto, `migrar` se niega a arrancar con valores de ejemplo |
| `POSTGRES_PASSWORD` | Una clave larga propia; no `postgres` |
| `JWT_SECRET` | Generado: `python3 -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `APP_URL` | La URL pública, p. ej. `https://reservas.itm.edu.co`. De ella salen los enlaces de los correos |
| `COOKIE_SECURE` | `true` si hay HTTPS delante (lo recomendado). `false` **solo** si sirve por HTTP plano, o nadie podrá iniciar sesión |
| `EMAIL_TRANSPORT` y `SMTP_*` | `smtp` con sus datos. Con `log` no llega ninguna invitación ni recuperación de contraseña |
| `FRONTEND_HOST_PORT` | `80` si no hay proxy; `3000` si hay un proxy que apunta a él |

Levante todo:

```bash
docker compose up -d --build
docker compose ps          # todos "running"/"healthy"; `migrar` aparece como "exited (0)"
docker compose logs migrar # qué hizo con la base
```

En una **base vacía**, `migrar` construye el esquema desde cero, carga los catálogos (tipos de reserva, estados, permisos, tipos de evento) y, si `CARGAR_DATOS_LIA=true`, los 5 laboratorios, 3 cargos y 2 equipos de LIA. En una base que **ya tiene esquema** no la reconstruye nunca: solo aplica las migraciones pendientes.

### Crear el primer administrador

La base nueva no tiene cuentas, y para entrar a la aplicación hace falta una. El administrador es una cuenta propia de Reservas (no viene de LIA) y se crea por terminal:

```bash
docker compose exec backend python -m app.scripts.crear_administrador --correo admin@su-dominio
```

Pide la contraseña (8 a 64 caracteres) sin mostrarla: no queda en el historial del shell ni en `docker inspect`. Si se le pasa el mismo correo otra vez, restablece la contraseña.

Entre a la URL pública con ese correo y **cambie la contraseña** desde «Cambiar contraseña».

### Después del primer arranque

- Cada laboratorio necesita su **configuración de reservas** («Administración → Laboratorios y cargos → Configurar») para aparecer al reservar.
- El personal de LIA todavía no se carga automáticamente; hasta entonces los técnicos no pueden entrar.

## HTTPS

Las cookies de sesión son `HttpOnly` y `Secure`: el navegador solo las envía por HTTPS. Ponga un proxy inverso con TLS delante del frontend y deje `COOKIE_SECURE=true`. Ejemplo mínimo con Caddy (certificado automático):

```
reservas.itm.edu.co {
    reverse_proxy localhost:3000
}
```

En ese caso deje `FRONTEND_HOST_PORT=3000` y no abra ese puerto al exterior (firewall): solo 80 y 443.

## Probar el flujo completo en un despliegue nuevo

`frontend/e2e/flujo-despliegue.spec.ts` recorre el flujo con tres personas distintas: el administrador configura un laboratorio y registra un espacio con un equipo; una usuaria pide la reserva; el técnico del laboratorio la aprueba desde el listado; y la usuaria la ve aprobada. No corre con la suite normal: se activa a propósito contra una base recién desplegada.

Necesita tres cuentas: el administrador (`crear_administrador`), un técnico (personal cuyo cargo es del laboratorio «Laboratorio de sistemas de Control y Robotica») y una usuaria vinculada a un proyecto. Después:

```bash
cd frontend
FLUJO_DESPLIEGUE=1 E2E_BASE_URL=http://localhost:3000 FLUJO_ADMIN="correo:clave" FLUJO_TECNICO="correo:clave" FLUJO_USUARIA="correo:clave" npx playwright test -c playwright.despliegue.config.ts            # añada --headed y E2E_SLOWMO=400 para verlo
```

Úsela sobre una base de **prueba**, no sobre la de producción: crea una reserva y un espacio.

## Actualizar a una versión nueva

```bash
git pull
docker compose up -d --build
```

`migrar` vuelve a correr y aplica solo lo nuevo. Los datos viven en volúmenes con nombre (`reservas_postgres_data`, `reservas_adjuntos_data`) y sobreviven a `up`, `down` y a reconstruir imágenes.

## Copias de seguridad

```bash
# Base de datos (un archivo SQL con todo)
docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > reservas_$(date +%F).sql

# Restaurar en una base vacía
docker compose exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB" < reservas_2026-10-01.sql
```

Respalde también el volumen de adjuntos (`reservas_adjuntos_data`): los archivos de lista de espera no están en la base.

**Nunca** ejecute `docker compose down -v`: borra los volúmenes, es decir, la base y los adjuntos.

## Problemas frecuentes

| Síntoma | Causa y arreglo |
|---|---|
| `migrar` falla con «JWT_SECRET vacío o de ejemplo» | Es la protección de `ENTORNO=produccion`: genere un secreto propio |
| Inicia sesión y la página vuelve al login | `COOKIE_SECURE=true` sin HTTPS. Ponga un proxy TLS, o `COOKIE_SECURE=false` si es una red interna sin TLS |
| Los enlaces de invitación apuntan a `localhost` | `APP_URL` sin ajustar |
| No llegan correos | `EMAIL_TRANSPORT=log` (solo registra). Use `smtp` y complete `SMTP_*` |
| El frontend no arranca | `docker compose logs backend`: el frontend espera a que el backend esté sano |
| Quiere entrar a la base | `docker compose exec db psql -U "$POSTGRES_USER" "$POSTGRES_DB"`, o pgAdmin: `docker compose --profile herramientas up -d pgadmin` y un túnel SSH al puerto 8085 |

## Datos que trae de LIA

Los laboratorios, cargos y equipos vienen de LIA (decisión del 2026-09-30, en `specs/docs/decisions/origen-externo-estructura-institucional.md`) y no se crean desde la aplicación. La carga inicial está en `backend/seeds/`. El personal no se carga todavía.
