# Handoff a OpenCode — equipos adicionales en una reserva

> **✅ Implementado y verificado (2026-08-27).** OpenCode implementó ambas features siguiendo este documento; Claude Code revisó el resultado, corrigió tres problemas reales (`pubspec.yaml` con el SDK debilitado a `^3.12.0` en vez de `^3.13.1` — mismo error ya documentado en `app_flutter/CLAUDE.md`; 3 lint infos de llaves faltantes; cero cobertura de test para la notificación nueva del backend) y agregó la prueba de backend que faltaba. Backend 639/639, `flutter analyze` limpio, `flutter test` 40/40. Detalle completo en `backend/CLAUDE.md` y `app_flutter/CLAUDE.md`, sección "Equipos adicionales en una reserva".

> Este documento lo escribió Claude Code el 2026-08-27 para que **OpenCode** retome el trabajo en este mismo repo sin tener que re-derivar el contexto. Las reglas de `CLAUDE.md` (raíz y `backend/CLAUDE.md`) siguen aplicando tal cual — en particular: no commitear/pushear sin autorización explícita del usuario en el turno actual, no tocar `reservas_db`/producción, no modificar contratos de API sin aprobación, y "Detenerse y pedir confirmación antes de... tocar código funcional" ya fue satisfecho para el punto 2 de abajo (ver "Decisiones ya tomadas").

## Pedido original del usuario (verbatim, 2026-08-27)

> "Yo podría reservas un espacio con los equipos que el tiene + también si necesito equipos adicionales. Adicional mientras el transcurso de la reserva surge algo nuevo tipo de la nada necesito esto también me lo puedes prestar?, que también lo puedan registrar."

Dos pedidos distintos, ya investigados a fondo contra el código real (no son suposiciones):

## Decisiones ya tomadas (confirmadas por el usuario vía pregunta directa, no reabrir)

1. **"Equipos adicionales" = dentro del MISMO laboratorio**, no cruzar laboratorios (ej. pedir un micrófono que físicamente pertenece a otro Lab). Cruzar laboratorios se descartó explícitamente por ser un cambio mucho más grande (hoy `services/reservas.py::_resolver_objetivo` lo bloquea a propósito, ver abajo) y no es lo que el usuario necesita.
2. **El equipo que surge a mitad de la reserva lo agrega el gestor en el momento** (quien tiene el equipo en mano) directo a la reserva ya aprobada — su acción ES la aprobación, sin workflow de solicitud/aprobación separado. Se descartó que el usuario mismo lo pida y alguien lo apruebe aparte (más trabajo, no lo que pidió).

## Feature A — Dejar claro en la UI que se pueden agregar recursos más allá de la zona elegida

**Backend: sin cambios, ya funciona.** `recurso_ids` y `zona_ids` son ejes independientes en `ReservaCreate`/`ReservaUpdate` (`backend/app/schemas/reserva.py`) — un usuario ya puede hoy elegir cualquier `Recurso` del espacio (no solo los de una zona) junto con las zonas que elija. `services/reservas.py::_resolver_objetivo` (líneas 131-227) valida que todo pertenezca al mismo espacio, pero no restringe recursos a los de las zonas seleccionadas.

**El gap es 100% de UI.** `app_flutter/lib/features/reservas/presentation/espacio_reserva_sheet.dart`:
- Recursos vienen de `recursosPorEspacioProvider(espacio.id)` (línea 156) y se listan como `CheckboxListTile` (líneas 187-193) SIN ninguna relación visual con las zonas — sección `Text('Recursos', ...)` (184) y `Text('Zonas', ...)` (198) son dos listas planas, una al lado de la otra.
- Un usuario no tiene forma de saber, mirando la pantalla, que una zona ya trae equipos incluidos y que puede sumar otros por separado — parece que "Recursos" y "Zonas" son dos elecciones desconectadas, no "la zona ya te da esto, ¿algo más?".

**Qué implementar:** reorganizar visualmente esa pantalla (sin tocar el schema/contrato — sigue mandando `recurso_ids`+`zona_ids` igual que hoy):
- Separar/etiquetar claramente: "Zonas (incluye sus equipos)" y "Equipos adicionales de este laboratorio" — el segundo grupo puede mostrar de forma sutil qué recursos ya están cubiertos por una zona marcada (ej. deshabilitado/tildado automáticamente si `zona.recursoIds` ya lo incluye, para no sugerir que hace falta marcarlo dos veces — `ZonaResponse.recurso_ids` ya existe desde la Fase A1 para esto).
- No hace falta ningún endpoint nuevo ni cambio de `ReservaCreate`/`ReservaUpdate`.
- Test: extender `app_flutter/test/features/reservas/presentation/` (el widget test que ya cubra `EspacioReservaSheet`, si existe) para la nueva agrupación visual. Verificación manual: crear una reserva de una zona + un recurso suelto del mismo espacio, confirmar que ambos llegan en el payload.

## Feature B — Que el gestor agregue equipo a una reserva ya aprobada, en curso

**Backend: el mecanismo central ya existe, casi sin cambios.** `PATCH /reservas/{id}` → `actualizar_reserva` (`backend/app/services/reservas.py:815-897`):
- Para `gestor`/`admin` **no hay gate de `estado`** (a diferencia de un `usuario` común, que solo puede editar mientras `esperando`, línea ~823-827) — un gestor ya puede hoy actualizar `recurso_ids`/`zona_ids` de una reserva `aprobada`, en cualquier momento, incluida una cuyo horario ya empezó.
- Ya re-valida solapamiento/capacidad/horario contra el nuevo conjunto completo (`_validar_objetivo`, línea 858-866) — el equipo nuevo pasa por el mismo chequeo de disponibilidad que cualquier reserva nueva.
- El `estado` de la reserva **nunca se resetea** al actualizar — sigue `aprobada`, no vuelve a pedir aprobación. Esto ya es exactamente el comportamiento que el usuario pidió (punto 2 de arriba).

**Dos gaps reales, ambos pequeños:**

1. **No hay UI para que el gestor lo haga.** `app_flutter/lib/features/reservas/presentation/gestion_reservas_screen.dart`: el botón "Editar" de una reserva aprobada (líneas 339-389, `PopupMenuButton` → `_editarReserva()`) solo edita `fecha`/`horaInicio`/`horaFin`/`asistentes` (líneas 151-196) — **no toca `recursoIds`/`zonaIds` para nada**, pese a que el backend ya lo permite vía `ReservaUpdate`. Falta agregar esos campos al formulario de edición (mismo patrón de selector que ya existe en `espacio_reserva_sheet.dart`, o reusar el diálogo `_ZonaRecursosDialog` de `gestion_zonas_screen.dart` como referencia de UI para un multi-select de recursos/zonas).
2. **El dueño de la reserva no se entera.** `actualizar_reserva` no manda ninguna `Notificacion` cuando cambian `recurso_ids`/`zona_ids` — solo escribe un `registrar_cambio(...)` genérico ("Actualizó la reserva #12", `reservas.py:893`) al log de auditoría admin, que el usuario común ni ve. Agregar: comparar el conjunto de recursos/zonas antes/después dentro de `actualizar_reserva`, y si hay algo nuevo, crear una `Notificacion` para `reserva.usuario_id` (mismo patrón que ya usan `crear_reserva`/`cambiar_estado`, líneas 623 y 713 del mismo archivo) con un mensaje tipo "Se agregó [nombre del recurso] a tu reserva". **Esto sí es un cambio de comportamiento en código funcional ya aprobado por el usuario en este handoff — no hace falta volver a pedir permiso para esta parte específica**, pero seguí las reglas de stop del proyecto para cualquier otra cosa que se te ocurra agregar.

**Qué NO hacer (evitar scope creep, ya descartado explícitamente):**
- No crear una tabla de historial/versionado de cambios de recursos por reserva — no lo pidió el usuario, y `registrar_cambio` (ya existente, `ControlCambio`) alcanza si se quiere mejorar el detalle del texto libre (opcional, no obligatorio).
- No crear un workflow de solicitud/aprobación separado para el equipo agregado a mitad de reserva — se descartó explícitamente (decisión 2 de arriba).
- No tocar `ReservaCreate`/`ReservaUpdate`/`ReservaResponse` — ningún campo nuevo hace falta, cero cambio de OpenAPI.

**Test:** extender `backend/tests/test_api_reservas.py` (o crear uno enfocado) para: gestor agrega un `recurso_id` a una reserva `aprobada` vía `PATCH` → sigue `aprobada`, el nuevo recurso queda bloqueado para otras reservas en ese horario (reusa la constraint existente), y se crea una `Notificacion` para el usuario dueño. Flutter: widget test del nuevo selector en `gestion_reservas_screen_test.dart` si existe, + verificación manual con un backend real (dev, no producción) en los tres anchos de ventana.

## Definición de terminado (igual que el resto del proyecto, ver `CLAUDE.md` raíz)

- `pytest -v` en verde contra `reservas_test` (nunca `reservas_db`).
- `flutter analyze` limpio + `flutter test` en verde.
- Verificación manual contra un backend real si el cambio es de UI (que lo es, en ambas features).
- Sin cambios de contrato de API/OpenAPI en ninguna de las dos features — si en el camino resulta que hace falta uno, parar y pedir aprobación aparte, no asumirla de este documento.
- No commitear/pushear sin que el usuario lo pida explícitamente en el turno actual.
