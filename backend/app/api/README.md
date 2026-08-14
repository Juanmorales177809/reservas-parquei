# api

## Propósito

Routers FastAPI: endpoints HTTP. Esta capa orquesta la validación de entrada (schemas), la autorización (deps) y delega la lógica de negocio en `services/`. No contiene reglas de negocio propias.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| espacios.py | Modificado | `GET /espacios` aplica RN-005 con autenticación opcional: anónimos y rol `usuario` ven solo espacios `activo`; admin/gestor ven todos. El docstring del endpoint se conservó EXACTO para mantener el OpenAPI byte-idéntico |
| admin_dashboard.py | Modificado | El cálculo de ocupación usa el `horario_atencion` real de cada espacio (`HorarioAtencion`) en lugar del rango fijo 7-20; el grid del heatmap conserva el rango 7..19 del contrato del gráfico |

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

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_api_espacios.py tests/test_admin_dashboard_ocupacion.py -v
```

Resultado esperado: verde (8 tests de RN-005 + 7 de ocupación).

## Impacto y compatibilidad

- OpenAPI **byte-idéntico** (SHA256 verificado antes/después).
- Sin cambios de rutas, métodos, campos, schemas, migraciones ni frontend.
- Cambio de comportamiento intencional: la lista pública ya no expone espacios `inactivo`/`mantenimiento` (corrección de RN-005).

## Riesgos

- El heatmap `ocupacion_por_dia_hora` mantiene su grid 7..19 (contrato del gráfico): horas atendidas fuera de ese rango se cuentan en `ocupacion_global` pero no aparecen en el gráfico. Limitación documentada, no bloqueante.

## Pendientes

- Si el frontend del panel admin migrara a un endpoint propio de gestión, el filtro podría volverse incondicional (sin distinción por rol).
- Limpiar el docstring/descripción del endpoint requeriría aprobación explícita (cambia OpenAPI).

## Fase de implementación

Fase 4 (RN-005 y ocupación real).
