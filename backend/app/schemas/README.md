# schemas

## Propósito

Contratos Pydantic de la API FastAPI: modelos de entrada (creación/actualización), de respuesta y de configuración. Tras la Fase 2, los valores de estado y rol están tipados con los enums de `app/domain/enums.py`, conservando exactamente los JSON que ya consumía el frontend.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| usuario.py | Modificado | `rol` pasa de `str`+pattern a `Rol` en `AdminUsuarioCreate`, `UsuarioUpdate` y `UsuarioResponse`. El validador manual de email se conserva |
| reserva.py | Modificado | `estado` pasa de `Literal`+validator manual a `EstadoReserva`; `nuevo_estado` pasa a `Literal[EstadoReserva.APROBADA, RECHAZADA, CANCELADA]` (sigue sin permitir `esperando`); `rol`/`estado` de los sub-modelos de respuesta pasan a `Rol`/`EstadoEntidad`; se eliminó el alias `ReservaEstado` y el validator duplicado `validar_estado` |
| espacio.py | Modificado | `estado` pasa a `EstadoEntidad` en Create/Update/Response; el validador de `horario_atencion` conserva su contrato exacto y agrega validación de respaldo con `HorarioAtencion` (opción A) |
| recurso.py | Modificado | `estado` pasa a `EstadoEntidad` en Create/Update/Response. `TipoRecursoResponse.activo` se conserva como `str` (columna de otro significado, fuera del alcance) |
| notificacion.py | Modificado | `tipo` pasa de `Literal` a `TipoNotificacion` |
| disponibilidad.py | Modificado | `estado` pasa de `str` a `EstadoSlot` |

## Reglas de negocio relacionadas

- RN-003 / RN-004: roles válidos (`usuario`/`gestor`/`admin`) → `Rol`.
- RN-005 / RN-008 (análogos): estados de espacio/recurso → `EstadoEntidad`.
- RN-017 / RN-019..RN-021: estados de reserva y cambios de estado permitidos (sin `esperando` como destino) → `EstadoReserva` + `Literal` de subconjunto.
- Reglas adicionales del código: disponibilidad (`EstadoSlot`), notificaciones (`TipoNotificacion`), horario de atención por día validado con `HorarioAtencion`.

## Decisiones técnicas

- **Enums del dominio** (`str, Enum`, Python 3.10): reemplazan `pattern` y `Literal` donde el resultado JSON/OpenAPI es equivalente. Verificado con snapshot de `openapi.json` antes/después (diff limitado a pattern→enum y Literal→enum).
- **Opción A (compatibilidad de contrato)**: el validador de `ConfiguracionEspacioUpdate.horario_atencion` conserva EXACTAMENTE la salida actual, incluidas las claves de días vacíos con listas `[]` (`{1: [], 2: [9]}` sigue devolviendo `{1: [], 2: [9]}`). `HorarioAtencion` se usa solo como respaldo de invariantes de dominio (claves 0–6, horas 0–22, al menos una franja, orden/dedupe) y NO reemplaza la salida pública: el dominio elimina días vacíos solo en su normalización interna, y `api/espacios.py` filtra posteriormente las listas vacías. La normalización del dominio nunca debe cambiar silenciosamente los JSON de la API.
- **Mensajes de validación**: los 3 mensajes de horario se conservan exactos; los mensajes 422 de rol/estado cambian de "pattern" a "Input should be..." (propio del cambio pattern→enum, documentado).
- **EmailStr descartado en esta fase**: no se añadió la dependencia `email-validator`; el validador manual actual se conserva (ver Pendientes).

## Pruebas

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/test_schemas_contrato.py -v
.\.venv\Scripts\python.exe -m pytest -v
```

Resultado esperado: 21 tests de contrato + suite completa en verde (157 en Fase 2).

## Impacto y compatibilidad

- JSON de respuestas y peticiones idénticos para datos válidos; sin cambios de campos, rutas ni defaults.
- OpenAPI: `pattern`→`$ref` de enums y nuevos schemas de componentes (`Rol`, `EstadoEntidad`, `EstadoReserva`, `EstadoSlot`, `TipoNotificacion`). Verificado por diff de snapshot.
- Sin cambios en services, models, api, migraciones ni frontend.

## Riesgos

- Textos de error 422 para valores inválidos de rol/estado cambian de texto (documentado arriba).
- `ReservaResponse.estado` con `EstadoReserva`: si la DB contuviera un valor corrupto, la serialización fallaría (protegido por el CheckConstraint de DB).

## Pendientes

- **EmailStr + `email-validator`**: reemplazo del validador manual de email en una fase posterior (requiere añadir la dependencia a `requirements.txt` y aprobación).
- Fuente única del horario de atención (Fase 4).
- Limpieza de tipos TypeScript del frontend con `| string` (Fase 5).

## Fase de implementación

Fase 2 (alineación de schemas con el dominio).
