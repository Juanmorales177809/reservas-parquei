# auth

## Propósito

Mecánica de autenticación: hash/verificación de contraseñas (bcrypt vía `passlib`) y emisión de JWT (`create_access_token`). No contiene autorización por rol (eso vive en `app/deps.py`) ni routing HTTP (eso vive en `app/api/auth.py`).

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| auth.py | Modificado | Se agregan `NOMBRE_COOKIE_ACCESO`, `atributos_cookie_acceso()` y `max_age_cookie_acceso()`: constantes/helpers compartidos para que `app/api/auth.py` (fija y borra la cookie) y `app/deps.py` (la lee como fallback) usen exactamente los mismos valores, sin duplicar los atributos en dos módulos. `create_access_token` no cambió. |

## Decisiones técnicas

- **Fase dual, no reemplazo**: `POST /auth/login` sigue devolviendo `access_token` en el body (`TokenResponse` sin cambios de contrato) y además fija una cookie HttpOnly con el mismo valor. Decisión de producto explícita: mantener compatibilidad con clientes existentes (E2E, frontend actual) mientras el frontend se migra en una fase posterior (Fase 9F-B, no iniciada).
- **Atributos de la cookie** (`atributos_cookie_acceso()`): `HttpOnly=true`, `SameSite=Lax`, `Path=/`, sin `Domain` explícito, `Secure` solo cuando `ENVIRONMENT=production` está confirmado — mismo gate que `Strict-Transport-Security`/`Cross-Origin-Opener-Policy` en `app/main.py`, para no romper el login en desarrollo local sobre HTTP simple. `Max-Age` (`max_age_cookie_acceso()`) es `ACCESS_TOKEN_EXPIRE_MINUTES * 60`, el mismo tiempo de vida que ya tenía el JWT — no se introduce una expiración distinta.
- **SameSite=Lax es suficiente porque el navegador nunca cruza orígenes**: `frontend/next.config.js` reescribe `/api/:path*` hacia el backend en el servidor de Next.js; el navegador solo ve el origen del frontend. No hace falta `SameSite=None` ni fijar `Domain` manualmente (análisis completo en la Fase 9F, previa a esta implementación).
- **Helpers compartidos entre set y delete**: `atributos_cookie_acceso()` devuelve solo los atributos que ambos métodos de `Response` aceptan (`httponly`, `samesite`, `path`, `secure`); `max_age` queda aparte porque `Response.delete_cookie` no lo acepta.
- **Sin nuevas variables de entorno**: todos los valores aprobados (SameSite, Path, Domain, Max-Age, Secure) se derivan de configuración ya existente (`settings.environment`, `settings.access_token_expire_minutes`); no se tocó `config.py`, `.env.example` ni `docker-compose.yml`.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_api_auth_cookie.py -v
```

Ver también `backend/app/api/README.md` (endpoints `/auth/login` y `/auth/logout`) y `backend/app/README.md` (`get_current_user` y demás dependencias en `deps.py`).

## Impacto y compatibilidad

- `create_access_token` sin cambios de firma ni comportamiento.
- Nueva superficie (`NOMBRE_COOKIE_ACCESO`, `atributos_cookie_acceso`, `max_age_cookie_acceso`) es aditiva; no se elimina ni renombra nada existente en este módulo.

## Riesgos

- Ninguno nuevo introducido en este módulo por sí solo; los riesgos de la fase dual completa (CSRF, superficie de cookie, etc.) están documentados en `backend/app/api/README.md`.

## Pendientes

- Fase 9F-B (no iniciada, requiere aprobación aparte): migrar `frontend/src/context/AuthContext.tsx`, `frontend/src/services/api.ts`, `frontend/e2e/global-setup.ts` y `frontend/e2e/tests/smoke/06-401.spec.ts` para dejar de depender de `localStorage`, y evaluar si se retira `access_token` del body de `TokenResponse` una vez migrados todos los clientes.

## Fase de implementación

Fase 9F-A (backend dual de autenticación).
