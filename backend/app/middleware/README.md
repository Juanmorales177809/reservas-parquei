# middleware

## Propósito

Middleware HTTP de la aplicación. Hoy contiene un solo componente: el middleware de **Request ID** (`request_id.py`), que resuelve/valida el header `X-Request-ID` de cada petición y lo agrega a toda respuesta, y su integración con el handler global de excepciones de `app/main.py`.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| request_id.py | Nuevo | Middleware ASGI `RequestIdMiddleware` + `resolver_request_id()` (normaliza y valida el id según el contrato) + constantes `HEADER`/`MAXIMO_LONGITUD` |
| __init__.py | Nuevo | Marcador de paquete |
| main.py | Modificado | Registra `RequestIdMiddleware` como el primer middleware de `app`; `manejar_excepcion_no_controlada` incluye `request_id` en el log y agrega el header a la respuesta 500 |

## Contrato de Request ID (aprobado)

1. Leer `X-Request-ID` de la petición.
2. Normalizar: `strip` + minúsculas.
3. Aceptar solamente el UUID canónico `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`.
4. Si falta, excede 128 caracteres o no coincide: generar `uuid4` nuevo.
5. Guardar el id en `request.state.request_id`.
6. Agregar `X-Request-ID` a toda respuesta normal y controlada.
7. En excepciones no controladas (500): el mismo id en el log y en la respuesta; body genérico sin detalles internos.
8. Nunca registrar `Authorization`, cookies, tokens, contraseñas, cuerpos ni headers completos.
9. Sin access log adicional. 10. Sin documentación en OpenAPI. 11. Sin ContextVar.

## Decisiones técnicas

- **Middleware ASGI puro, no `BaseHTTPMiddleware`**: registrado con `app.add_middleware(RequestIdMiddleware)` **antes** de CORS y de las cabeceras de seguridad. En el stack de Starlette (`ServerError → [middlewares de usuario] → Exception → router`) queda como el primero de los de usuario, por fuera del `ExceptionMiddleware` interno: las respuestas de rutas, de validación (422) y de errores HTTP controlados (401/403/404/409/429) lo atraviesan y reciben el header vía un wrapper del paso `http.response.start` (`MutableHeaders`).
- **El 500 no atraviesa el wrapper**: lo genera el `ServerErrorMiddleware` (el más externo de todos, fuera de cualquier middleware de usuario). Por eso el **handler** `manejar_excepcion_no_controlada` de `main.py` agrega el header él mismo, leyendo `request.state.request_id` (el mismo id que anotó el middleware), e incluye ese id en el log junto con método, ruta y tipo de excepción. El body sigue siendo el mensaje genérico estable, sin `str(exc)` ni traceback.
- **Sin ContextVar**: el único log de negocio hoy es el handler de errores (que recibe `request`), así que no hace falta propagar contexto por `contextvars`; el id viaja en `request.state`. Si en el futuro se agregaran más loggers request-scoped, evaluar como extensión (no parte de esta fase).
- **Nunca se rechaza la petición por un header malformado**: se reemplaza con un `uuid4` (decisión de disponibilidad).

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_request_id.py -v   # Fase Request ID
.\.venv\Scripts\python.exe -m pytest tests/test_exception_handler.py tests/test_security_headers.py -v   # regresión directa
```

Cubre: respuesta exitosa con UUID; dos requests con ids distintos; UUID válido (y en mayúsculas) conservado/normalizado; header inválido, con espacios internos, con caracteres de control y de más de 128 caracteres → reemplazado sin propagarse; 422/401/429 con `X-Request-ID`; 500 con `X-Request-ID` igual al id del log; body genérico sin detalles internos; logs sin `Authorization`/cookies/tokens/contraseñas.

## Impacto y compatibilidad

- Sin cambios de contrato: los headers de respuesta no forman parte del OpenAPI generado — el snapshot no se regenera y `test_openapi_contrato.py` se mantiene como estaba.
- Sin cambios en frontend ni E2E (header aditivo en las respuestas a través del proxy).
- Sin cambios en schemas, modelos, migraciones, Docker, rate limiting, autenticación ni `control_cambios`.

## Riesgos

- Header espoleado por el cliente: el id es de correlación, no de seguridad; si el cliente envía uno válido se conserva, si no se genera uno nuevo.
- Sin inyección por el header: el patrón excluye caracteres de control y espacios internos; el valor se valida con regex antes de usarlo en logs/respuestas.
- El `X-Request-ID` del 500 depende de que el middleware haya corrido (siempre en requests HTTP reales); el handler genera un `uuid4` de respaldo si el estado no estuviera presente (caso defensivo, no esperado).

## Fase de implementación

Fase "Request ID y trazabilidad" — cierre de la deuda operacional señalada en la Fase 9D (sin infraestructura de correlación). RED → GREEN completo.