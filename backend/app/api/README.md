# api

## Propósito

Routers FastAPI: endpoints HTTP. Esta capa orquesta la validación de entrada (schemas), la autorización (deps) y delega la lógica de negocio en `services/`. No contiene reglas de negocio propias.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| espacios.py | Modificado | `GET /espacios` aplica RN-005 con autenticación opcional: anónimos y rol `usuario` ven solo espacios `activo`; admin/gestor ven todos. El docstring del endpoint se conservó EXACTO para mantener el OpenAPI byte-idéntico |
| admin_dashboard.py | Modificado | El cálculo de ocupación usa el `horario_atencion` real de cada espacio (`HorarioAtencion`) en lugar del rango fijo 7-20; el grid del heatmap conserva el rango 7..19 del contrato del gráfico |
| auth.py | Modificado | `POST /auth/login` (Fase 9F-A) además de devolver `TokenResponse` sin cambios, fija una cookie HttpOnly con el mismo token. Nuevo `POST /auth/logout`: borra la cookie, `204 No Content`, no exige autenticación, idempotente si no existe cookie previa |

## Reglas de negocio relacionadas

- **RN-005** (solo espacios disponibles son visibles): aplicada en `GET /espacios`. Un token de usuario NO permite recuperar espacios no disponibles mediante `skip`/`limit` ni ningún parámetro.
- **RN-028** (información consolidada): la ocupación refleja ahora el horario real configurado por espacio.
- Reglas adicionales del código: convención de franjas [inicio, fin) y días sin atención.

## Decisiones técnicas

- **Autenticación opcional sin cambio de OpenAPI**: la dependencia `get_current_user_optional` (en `app/deps.py`) lee el header Authorization manualmente vía `Request`, sin `OAuth2PasswordBearer` — verificado con Context7 que `OAuth2PasswordBearer` (hereda de `SecurityBase`) sí añadiría un esquema de seguridad al OpenAPI del endpoint. Un token inválido se trata como acceso anónimo.
- **Compatibilidad con la gestión admin**: `GET /espacios` alimenta también el panel admin del frontend; por eso admin/gestor siguen viendo todos los espacios (sin cambios de frontend).
- **Fuente única del horario**: la ocupación precarga los `horario_atencion` por espacio (sin N+1) y reutiliza `HorarioAtencion` del dominio; un horario vacío/inválido (dato legacy) aporta cero horas habilitadas.
- **Límites de franjas**: inicio inclusivo, fin exclusivo (convención vigente).
- **Denominador cero**: cuando no hay horas atendidas, `porcentaje` es 0 (guard existente conservado).

### Fase 9F-A — Autenticación dual por cookie HttpOnly

- **Fase dual aprobada explícitamente**: `POST /auth/login` conserva `TokenResponse.access_token` en el body (sin cambio de contrato) y además fija una cookie HttpOnly con el mismo token, vía los helpers de `app/auth/auth.py` (`atributos_cookie_acceso()`, `max_age_cookie_acceso()`). Objetivo: permitir migrar el frontend a cookie en una fase posterior sin romper clientes existentes (E2E, frontend actual, que siguen usando `Authorization: Bearer`).
- **`POST /auth/logout` nuevo, sin autenticación**: borra la cookie (`response.delete_cookie`) y responde `204 No Content` siempre, exista o no una cookie previa, y con o sin `Authorization` válido. Diseño intencional: un cliente con sesión inválida/expirada debe poder limpiar su cookie igual.
- **Precedencia documentada cuando hay ambos mecanismos**: `app/deps.py` (`get_current_user`, `get_current_user_optional`, `require_admin_dashboard`) da prioridad al header `Authorization` sobre la cookie cuando ambos están presentes — el header es la señal explícita de un cliente que declara sus propias credenciales por request; la cookie es un fallback ambiental para clientes de navegador. Probado en `tests/test_api_auth_cookie.py::TestPrecedenciaCuandoHayAmbosMecanismos`.
- **`oauth2_scheme` con `auto_error=False`**: necesario para que `get_current_user`/`require_admin_dashboard` puedan evaluar la cookie antes de decidir que no hay credenciales. Verificado que no cambia el esquema de seguridad generado en OpenAPI (el snapshot solo ganó la ruta `/auth/logout`, nada más).
- **Sin cambios de CORS/rate limiting**: el navegador real solo llega al backend vía el proxy de Next.js (`frontend/next.config.js`, `/api/:path*`), por lo que la fase dual no requiere tocar `allow_credentials` de CORS ni el limitador de intentos de login — ambos quedan fuera de alcance de esta fase, sin cambios.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_api_espacios.py tests/test_admin_dashboard_ocupacion.py -v
.\.venv\Scripts\python.exe -m pytest tests/test_api_auth_cookie.py -v
```

Resultado esperado: verde (8 tests de RN-005 + 7 de ocupación; 22 de autenticación dual por cookie). Suite completa del backend: 289/289.

## Impacto y compatibilidad

- OpenAPI **byte-idéntico** para Fase 4 (SHA256 verificado antes/después). Fase 9F-A cambia el OpenAPI de forma aprobada: solo agrega la ruta `/auth/logout` (verificado con diff explícito del snapshot regenerado — 15 líneas insertadas, 0 eliminadas, ningún otro path/schema tocado).
- Sin cambios de rutas, métodos, campos, schemas, migraciones ni frontend en Fase 4. Fase 9F-A no toca `TokenResponse`, ni ningún schema existente, ni frontend, ni Docker, ni CI, ni migraciones, ni rate limiting.
- Cambio de comportamiento intencional (Fase 4): la lista pública ya no expone espacios `inactivo`/`mantenimiento` (corrección de RN-005).
- Cambio de comportamiento intencional (Fase 9F-A): los endpoints protegidos ahora también aceptan una cookie `access_token` válida como alternativa al header `Authorization`, además de exponer `POST /auth/logout` (antes inexistente). El resto de códigos de estado (401/403/422/429) queda exactamente igual, verificado con tests explícitos.

## Riesgos

- El heatmap `ocupacion_por_dia_hora` mantiene su grid 7..19 (contrato del gráfico): horas atendidas fuera de ese rango se cuentan en `ocupacion_global` pero no aparecen en el gráfico. Limitación documentada, no bloqueante.
- **CSRF (riesgo aceptado, mitigado, no eliminado)**: al aceptar cookie, el navegador la adjunta automáticamente en peticiones same-origin. Desde la Fase 9F-B, `frontend/src/services/api.ts` sí envía `credentials: 'same-origin'` en cada request, así que la cookie viaja en cada llamada del frontend. `SameSite=Lax` bloquea el envío de la cookie en peticiones state-changing (`POST`/`PUT`/`PATCH`/`DELETE`) disparadas por `fetch`/XHR desde otro origen, pero no se agregó ningún token CSRF de doble envío ni otra defensa adicional — decisión explícita, fuera de alcance de 9F-A y 9F-B. No se afirma que el riesgo esté resuelto, solo mitigado por `SameSite=Lax` mientras la arquitectura siga dependiendo del proxy same-origin de Next.js (`frontend/next.config.js`).
- **`require_admin_dashboard` no tiene cobertura de test propia** (ni antes ni después de esta fase): función sin uso en ningún router actual (verificado); se actualizó por consistencia con `oauth2_scheme`, pero queda sin ejercitar directamente.

## Pendientes

- Si el frontend del panel admin migrara a un endpoint propio de gestión, el filtro podría volverse incondicional (sin distinción por rol).
- Limpiar el docstring/descripción del endpoint requeriría aprobación explícita (cambia OpenAPI).
- ~~Fase 9F-B: migrar `AuthContext`, `api.ts`, `localStorage` y los fixtures E2E para dejar de depender del header como mecanismo primario.~~ **Hecho** — commit `13c341d3c93ae86deb709aad1f5f659cdc74c9bf`, local, pendiente de push.
- Fase 9G (no aprobada ni iniciada): decidir si se retira `access_token` del body de `TokenResponse` y el soporte de `Authorization`, ahora que frontend y E2E ya no dependen de ellos.

## Fase de implementación

Fase 4 (RN-005 y ocupación real). Fase 9F-A (autenticación dual por cookie HttpOnly).
