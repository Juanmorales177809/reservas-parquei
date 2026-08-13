# domain

## Propósito

Capa de dominio tipada del backend: enums, value objects y protocols que encapsulan las reglas de negocio de horarios, estados y auditoría sin depender de FastAPI, SQLAlchemy, `app.db`, modelos de infraestructura ni HTTP. Es la base de los refactorings de las fases 2 y 3.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| enums.py | Creado | `Rol`, `EstadoEntidad`, `EstadoReserva`, `TipoNotificacion`, `EstadoSlot`, `DiaSemana`, `TRANSICIONES_ESTADO_RESERVA`, `ESTADOS_RESERVA_BLOQUEANTES` |
| valor.py | Creado | `FranjaHoraria` y `HorarioAtencion` (frozen dataclasses con invariantes) |
| protocols.py | Creado | `Reloj` y `RegistroAuditoria` (`@runtime_checkable`, solo tipos primitivos) |
| __init__.py | Creado | Re-exporta la API pública de la capa |

## Reglas de negocio relacionadas

- RN-003 / RN-004: rol único y asignación de espacio del gestor → `Rol`.
- RN-005 / RN-008 (análogos): visibilidad y selección según estado → `EstadoEntidad` y `ESTADOS_RESERVA_BLOQUEANTES`.
- RN-017 / RN-019 / RN-020 / RN-021: ciclo de aprobación → `EstadoReserva` y `TRANSICIONES_ESTADO_RESERVA`.
- Recomendación 11.2 del documento (auditoría funcional) → `RegistroAuditoria`.
- Reglas adicionales del código: bloques de hora completa (`FranjaHoraria`), horario de atención por día (`HorarioAtencion`), anticipación con hora local (`Reloj`), notificaciones (`TipoNotificacion`), disponibilidad (`EstadoSlot`).

## Decisiones técnicas

- `class X(str, Enum)` y NO `StrEnum`: compatibilidad con Python 3.10 (imagen Docker `python:3.10-slim`); `from __future__ import annotations` para las referencias circulares.
- Los valores de los enums conservan exactamente las cadenas JSON actuales de la API (condición de compatibilidad de contrato).
- `TipoNotificacion`: **verificado el origen real** — el constraint `notificaciones_tipo_check` existe en base de datos, declarado en `app/models/notificacion.py` (`__table_args__`) y aplicado por `app/migrations.py` (`DROP CONSTRAINT IF EXISTS` + `ADD CONSTRAINT ... CHECK (tipo IN ('Pendiente','Aprobada','Rechazada','Cancelada'))`). Se documenta como constraint real, no como convención.
- `HorarioAtencion` normaliza claves `str`/`int` a `int` (la DB guarda strings en el JSON; los schemas envían enteros). La fuente única NO se resuelve en esta fase.
- Límite de horas `0..22` replicando el validador de `ConfiguracionEspacioUpdate`; se documenta la tensión con el backfill de migraciones (7..19) y la UI del gestor (6..21).
- `EstadoReserva.puede_transicionar_a()` trata el mismo estado como no-op válido (semántica actual de `validar_transicion_estado`).
- `Reloj` exige datetime naive sin tzinfo (contrato documentado; no es enforceable en runtime).

## Pruebas

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/test_domain_enums.py tests/test_domain_valor.py tests/test_domain_protocols.py -v
```

Resultado esperado: verde, incluyendo invariantes, transiciones, solapamiento/contigüidad y el contrato de los protocols.

## Impacto y compatibilidad

- Cambio estrictamente aditivo: nada importa `domain/` todavía; OpenAPI, base de datos y comportamiento existente intactos. Las 74 pruebas de Fase 0 deben seguir pasando.

## Riesgos

- Los dicts internos de `HorarioAtencion` se exponen solo mediante métodos (`horas_del_dia`, `dias`) para preservar la inmutabilidad.
- Los métodos de `EstadoReserva` replican la semántica del servicio actual; si el servicio cambiara primero, habría que reconciliar (cubierto por pruebas en ambos lados).

## Pendientes

- Fuente única del horario de atención (Fase 4).
- Adaptadores de `Reloj` (→ `services/reloj.py`) y de `RegistroAuditoria` (→ `services/auditoria.py` que hoy recibe `Session` + `Usuario`): Fase 3.
- Contradicciones del documento legado (zonas, tipos de reserva, multi-equipo) fuera del alcance; ver plan v2.

## Fase de implementación

Fase 1 (capa de dominio tipada).
