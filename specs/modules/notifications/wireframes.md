# Wireframes — Notifications

## Alcance, fuentes y lectura

Dos wireframes de baja fidelidad, uno por cada pantalla de [screens.md](screens.md). Fuentes revisadas: [user-flow.md](user-flow.md), [screen-flow.md](screen-flow.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md) y el [contrato API de Notifications](../../contratos/notifications/api-contract.md). Las variantes son estados de la misma pantalla, no pantallas nuevas.

Los bloques ASCII representan agrupación y orden de contenido, sin fijar dimensiones, estilos, tipografía, colores ni componentes. Para trasladarlos a Figma, conservar el identificador del wireframe y nombrar sus variantes por estado. Los nombres técnicos y referencias que aparecen fuera de los bloques son anotaciones de trazabilidad, no texto de interfaz.

Convenciones: las mismas de [wireframes.md de auth](../auth/wireframes.md) — `[campo: ______]` es una entrada; `[Acción]` es una acción; `(dato)` es información de solo lectura; `{mensaje}` es una región de respuesta, ausente cuando no hay mensaje; `→ destino` es una anotación de navegación, no un botón.

### Estados y seguridad comunes

| Situación | Representación en la pantalla existente | Respaldo |
|---|---|---|
| Procesamiento | Región de mensaje: «Procesando…», concretada por operación | Estados de screens.md |
| Operación no autorizada | «No se puede realizar esta operación.» | `SEC-AUTZ-01`, `SEC-AUTZ-02`, `SEC-AUTZ-04` de auth |
| Sesión no válida | Interrumpe la operación y conduce a `SCR-AUTH-01` de auth | `UF-AUTH-05`, `SEC-SES-07` de auth |
| Entidad desactivada después | Sigue apareciendo en la bandeja | `RN-HIS-02` |

No se muestran SQL, trazas, variables de entorno, hashes, secretos ni tokens (`SEC-INF-04` de auth, por la misma disciplina transversal).

## WF-NOT-01 — Bandeja de notificaciones

Origen:

- SCR-NOT-01.
- UF-NOT-01.

**Objetivo:** consultar las propias y marcarlas como leídas. **Actor:** cualquier cuenta autenticada.

**Información visible:** tipo, fecha y hora, estado de lectura y referencia. **Entradas:** filtros; acción de marcar. **Principal:** filtrar; marcar como leída.

### Estado principal

```text
+--------------------------------------------------+
| Notificaciones                                     |
|                                                  |
| Filtros: leídas, tipo de evento     [Filtrar]    |
| (lista: tipo, fecha, estado, referencia)          |
|                                       [Marcar]   |
|                                                  |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | `GET /api/notificaciones`, §2.1 |
| Marcando | «Guardando…» | `POST .../{id}/lectura`, §2.2 |
| Marcada | Instante registrado | `200 OK` con `leida_at` |
| Ajena o inexistente | Ausencia indistinguible | `404 NO_ENCONTRADO` |
| Repetida sobre leída | Mismo instante conservado | `200 OK` |

### Navegación

- **Entrada:** navegación del módulo.
- **Salida correcta:** permanece; la referencia orienta al módulo propietario.
- **Errores:** denegación en esta misma pantalla, sin revelar existencia ajena.

## WF-NOT-02 — Preferencias de correo

Origen:

- SCR-NOT-02.
- UF-NOT-02.

**Objetivo:** ver y fijar preferencias general y por tipo. **Actor:** cualquier cuenta autenticada.

**Información visible:** general vigente y explícitas por tipo. **Entradas:** habilitación general y por tipo. **Principal:** guardar preferencias.

### Estado principal

```text
+--------------------------------------------------+
| Preferencias de correo                             |
|                                                  |
| General              [habilitado / deshabilitado] |
| Por tipo de evento                                |
| (lista: tipo, estado)              [cambiar]      |
| [Guardar preferencias]                            |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | `GET .../preferencias`, §3.1 |
| Guardando | «Guardando…» | `PUT .../preferencias`, §3.2 |
| Tipo inexistente o deshabilitado | Mensaje de corrección | `404 NO_ENCONTRADO` |
| Tipo repetido | Mensaje de corrección | `422 VALIDACION` |
| Guardadas | Confirmación; lo no listado rige por la general | `200 OK` |

### Navegación

- **Entrada:** navegación del módulo.
- **Salida correcta:** permanece con la confirmación.
- **Errores:** corrección en esta misma pantalla.

## Dependencias y límites del cierre visual

| Pantallas | Información pendiente o límite | Tratamiento en los wireframes |
|---|---|---|
| WF-NOT-01 | Destino de la referencia relacionada | Se representa como referencia, sin resolver navegación externa |
| WF-NOT-02 | Destino tras guardar | Se representa la confirmación; la navegación externa no se resuelve aquí |
| Todas | Retornos al abandonar no fijados por las fuentes | No se agregan botones de retorno o cancelación |
| WF-NOT-01 | Estado de envíos de correo | Ausente a propósito: no se consulta desde aquí |

## Matriz de cobertura y estados

| Wireframe | Screen | User Flow | Estados representados |
|---|---|---|---|
| WF-NOT-01 | SCR-NOT-01 | UF-NOT-01 | Carga, marcando, marcada, ajena, repetida |
| WF-NOT-02 | SCR-NOT-02 | UF-NOT-02 | Carga, guardando, tipo inválido, duplicado, guardadas |
