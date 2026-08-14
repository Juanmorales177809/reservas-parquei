# services

## Propósito

Reglas de negocio de la aplicación: validaciones de reserva, horarios, hora local de negocio y auditoría. Tras la Fase 3, esta capa consume los enums, value objects y protocols de `app/domain/` sin cambiar los contratos de la API.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| reloj.py | Modificado | Nueva clase `RelojLocal` que implementa el protocolo `Reloj` (datetime NAIVE en `APP_TIMEZONE`); `ahora_local()` queda como wrapper de compatibilidad |
| horarios.py | Modificado | `horas_atencion_dia` y `horario_cubre_reserva` delegan en `HorarioAtencion`/`FranjaHoraria` con guard explícito para horario vacío |
| reservas.py | Modificado | `TRANSICIONES_ESTADO` duplicado eliminado → `EstadoReserva.puede_transicionar_a()`; `validar_anticipacion` acepta `Reloj` inyectable (default `RelojLocal`); literales de estado/rol/notificación reemplazados por enums usando siempre `.value` |
| auditoria.py | Modificado | Nueva `AuditoriaSesion` (adaptador de `RegistroAuditoria`, solo primitivas); `registrar_cambio()` conservado como wrapper |

## Reglas de negocio relacionadas

- RN-017, RN-019, RN-020, RN-021: ciclo de aprobación → `EstadoReserva`/`TipoNotificacion` (mensajes y estados idénticos a los actuales).
- RN-005 / RN-008 (análogos): estado activo → `EstadoEntidad.ACTIVO.value`.
- Recomendación 11.2 del documento (auditoría) → `AuditoriaSesion`.
- Reglas adicionales del código: bloques de hora completa, anticipación mínima (reloj inyectable), horario de atención por día.

## Decisiones técnicas

- **`Reloj` inyectable**: `validar_anticipacion(..., reloj: Reloj | None = None)` usa `RelojLocal()` por defecto. `ahora_local()` se conserva como wrapper porque `api/espacios.py` y `api/recursos.py` lo importan.
- **Guard de horario vacío**: un `horario_atencion` totalmente vacío devuelve `[]`/`False` (comportamiento actual conservado). Un horario con horas fuera de 0..22 se deja propagar como error de configuración (no se oculta).
- **`.value` en comparaciones y mensajes**: `str(miembro_de_enum)` difiere entre Python 3.10 (imagen Docker) y 3.11+ (local), así que los mensajes de error y las comparaciones contra columnas de la DB usan siempre `.value`.
- **Adaptador de auditoría**: el protocolo del dominio solo maneja primitivas; `AuditoriaSesion` crea la fila `ControlCambio` y el commit sigue siendo responsabilidad del flujo, igual que antes.

## Pruebas

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/test_reloj.py tests/test_horarios.py tests/test_reservas_validaciones.py tests/test_auditoria_dominio.py -v
```

Resultado esperado: verde. El test de anticipación usa `_RelojFijo` en lugar de `monkeypatch`.

## Impacto y compatibilidad

- API, mensajes, estados y OpenAPI sin cambios (snapshot `openapi.json` verificado byte-idéntico en Fase 3).
- Sin cambios en `api/`, `schemas/`, migraciones ni frontend.

## Riesgos

- Si el dominio cambia la semántica de horarios vacíos o transiciones, esta capa debe re-verificarse (tests de contrato cubren ambos lados).

## Pendientes

- N/A para esta fase.

## Fase de implementación

Fase 3 (integración de la capa de dominio).
