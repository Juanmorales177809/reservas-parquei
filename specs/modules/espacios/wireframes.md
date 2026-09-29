# Wireframes — Espacios

## Alcance, fuentes y lectura

Cuatro wireframes de baja fidelidad, uno por cada pantalla de [screens.md](screens.md). Fuentes revisadas: [user-flow.md](user-flow.md), [screen-flow.md](screen-flow.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md) y el [contrato API de Espacios](../../contratos/espacios/api-contract.md). Las variantes son estados de la misma pantalla, no pantallas nuevas.

Los bloques ASCII representan agrupación y orden de contenido, sin fijar dimensiones, estilos, tipografía, colores ni componentes. Para trasladarlos a Figma, conservar el identificador del wireframe y nombrar sus variantes por estado. Los nombres técnicos y referencias que aparecen fuera de los bloques son anotaciones de trazabilidad, no texto de interfaz.

Convenciones: las mismas de [wireframes.md de auth](../auth/wireframes.md) — `[campo: ______]` es una entrada; `[Acción]` es una acción; `(dato)` es información de solo lectura; `{mensaje}` es una región de respuesta, ausente cuando no hay mensaje; `→ destino` es una anotación de navegación, no un botón.

### Estados y seguridad comunes

| Situación | Representación en la pantalla existente | Respaldo |
|---|---|---|
| Procesamiento | Región de mensaje: «Procesando…», concretada por operación | Estados de screens.md |
| Validación de entradas | Mensaje junto al campo correspondiente; corrección mediante la acción existente | `422 VALIDACION`, contrato §1 |
| Nombre duplicado | Mensaje junto al campo, sin identificar el registro coincidente | `409 NOMBRE_DUPLICADO`, §2.1 |
| Capacidad inválida | Mensaje junto al campo | `422 VALIDACION`, `RN-ESP-02` |
| Operación no autorizada | «No se puede realizar esta operación.» | `SEC-AUTZ-01`, `SEC-AUTZ-02`, `SEC-AUTZ-04` de auth |
| Sesión no válida | Interrumpe la operación y conduce a `SCR-AUTH-01` de auth | `UF-AUTH-05`, `SEC-SES-07` de auth |

No se muestran SQL, trazas, variables de entorno, hashes, secretos ni tokens (`SEC-INF-04` de auth, por la misma disciplina transversal).

## WF-ESP-01 — Registrar, editar y habilitar espacios

Origen:

- SCR-ESP-01.
- UF-ESP-01, UF-ESP-02, UF-ESP-10, UF-ESP-11.

**Objetivo:** crear y modificar espacios, y cambiar su habilitación con advertencia. **Actor:** Técnico de la unidad o Administrador.

**Información visible:** listado con filtros; detalle con horario heredado; conteo de impacto. **Entradas:** datos generales; confirmación. **Principal:** guardar; confirmar deshabilitación. **Secundarias:** habilitar, editar.

### Estado principal

```text
+--------------------------------------------------+
| Espacios                                          |
|                                                  |
| Filtros: unidad, estado, capacidad mínima         |
| [Filtrar]                                         |
| (lista: nombre, capacidad, estado)                |
|                                                  |
| Registrar                                        |
| Unidad             [seleccionar]                  |
| Nombre             [________________________]    |
| Ubicación          [________________________]    |
| Capacidad          [________]                     |
| Descripción        [________________________]    |
| [Guardar espacio]                                |
|                                                  |
| Detalle                                          |
| (datos, horario heredado de la unidad)            |
| [Editar datos]   [Habilitar/Deshabilitar]         |
|                                                  |
| Advertencia de impacto                            |
| (reservas futuras a cancelar: N)                  |
| [Confirmar deshabilitación]                       |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | `GET /api/espacios`, §2.3 |
| Guardando | «Guardando…» | `POST`/`PATCH`, §2.1/§2.2 |
| Nombre duplicado o capacidad inválida | Mensaje junto al campo | `409 NOMBRE_DUPLICADO` / `422 VALIDACION` |
| Impacto previo | Conteo sin ejecutar | `GET .../impacto-deshabilitacion`, §2.6 |
| Sin confirmar | Sin cambios ni reservas tocadas | `409 CONFLICTO` |
| Confirmada | Totales de canceladas | `200 OK` con totales, §2.5 |

### Navegación

- **Entrada:** navegación del módulo.
- **Salida correcta:** permanece con la confirmación.
- **Errores:** corrección en esta misma pantalla.

## WF-ESP-02 — Asociar y retirar recursos

Origen:

- SCR-ESP-02.
- UF-ESP-03, UF-ESP-04.

**Objetivo:** asociar recursos y retirar asociaciones. **Actor:** Técnico de la unidad o Administrador.

**Información visible:** asociados vigentes; catálogo disponible. **Entradas:** selección de recursos; confirmación de retiro. **Principal:** asociar; confirmar retiro.

### Estado principal

```text
+--------------------------------------------------+
| Recursos del espacio                              |
| (asociados vigentes)                 [Retirar]   |
|                                                  |
| Asociar                                          |
| Recurso            [seleccionar del catálogo]     |
| [Asociar recursos]                               |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | Detalle con asociados, §2.4 |
| Asociando | «Asociando…» | `POST .../recursos`, §3.1 |
| Recurso de otra unidad o ya asociado | Mensaje de corrección | `409 UNIDAD_INCOMPATIBLE` / `409 CONFLICTO` |
| Retiro confirmado | Asociación deshabilitada, historial intacto | `204`, §3.2 |

### Navegación

- **Entrada:** detalle desde `SCR-ESP-01`.
- **Salida correcta:** permanece con la confirmación.
- **Errores:** corrección en esta misma pantalla.

## WF-ESP-03 — Configurar campos adicionales

Origen:

- SCR-ESP-03.
- UF-ESP-05, UF-ESP-06, UF-ESP-07, UF-ESP-08, UF-ESP-09.

**Objetivo:** definir campos con sus opciones y mantenerlos. **Actor:** Técnico de la unidad o Administrador.

**Información visible:** campos con tipo, obligatoriedad, orden y estado; opciones. **Entradas:** definición del campo; reorden; habilitación. **Principal:** guardar campo; guardar orden.

### Estado principal

```text
+--------------------------------------------------+
| Campos adicionales                                |
| (lista: nombre, tipo, obligatorio, orden, estado) |
|                                                  |
| Agregar                                         |
| Nombre             [________________________]    |
| Tipo               [texto | largo | número |     |
|                      sí/no | lista]             |
| Obligatorio        [sí/no]  Orden  [________]    |
| Opciones (lista)   [valor]           [+ Agregar] |
| [Guardar campo]                                  |
|                                                  |
| Reordenar          [subir/bajar por campo]        |
| [Guardar orden]    [Habilitar/Deshabilitar]       |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | Detalle con campos, §2.4 |
| Guardando | «Guardando…» | `POST`/`PATCH`, §4.1/§4.2 |
| Lista sin opciones | Mensaje de corrección | `409 CAMPO_SIN_OPCIONES` |
| Nombre duplicado en el espacio | Mensaje junto al campo | `409 CONFLICTO` |
| Deshabilitado | Oculto para nuevas reservas, historia intacta | `PATCH .../estado`, §4.3 |

### Navegación

- **Entrada:** detalle desde `SCR-ESP-01`.
- **Salida correcta:** permanece con la confirmación.
- **Errores:** corrección en esta misma pantalla.

## WF-ESP-04 — Consultar espacios

Origen:

- SCR-ESP-04.
- UF-ESP-12, UF-ESP-13.

**Objetivo:** listar con filtros y ver el detalle. **Actor:** Usuario autenticado.

**Información visible:** información general, capacidad, estado, unidad, horario heredado, asociados y campos. **Entradas:** filtros. **Principal:** ninguna acción propia; filtrar y ver detalle.

### Estado principal

```text
+--------------------------------------------------+
| Espacios                                          |
|                                                  |
| Filtros: unidad, estado, capacidad mínima         |
| [Filtrar]                                         |
| (lista: nombre, capacidad, estado)                |
|                                                  |
| Detalle                                          |
| (datos, horario heredado, asociados, campos)      |
|                                                  |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | `GET /api/espacios`, §2.3 |
| Detalle | Consolidado con horario y asociados | `GET /api/espacios/{id}`, §2.4 |
| Visibilidad por rol | El Usuario solo ve habilitados | Filtros de §2.3 |

### Navegación

- **Entrada:** navegación del módulo.
- **Salida correcta:** permanece; enlaza a gestión según el rol.
- **Errores:** sesión no válida se resuelve en auth.

## Dependencias y límites del cierre visual

| Pantallas | Información pendiente o límite | Tratamiento en los wireframes |
|---|---|---|
| WF-ESP-01, WF-ESP-02, WF-ESP-03 | Mecanismo de selección de catálogos | Zona funcional representada como selección; no se inventa un buscador |
| WF-ESP-01 | Destino tras guardar o confirmar | Se representa la confirmación; la navegación externa no se resuelve aquí |
| Todas | Retornos al abandonar no fijados por las fuentes | No se agregan botones de retorno o cancelación |
| WF-ESP-04 | Disponibilidad temporal | Ausente a propósito: la resuelve reservations (§6 del contrato) |

## Matriz de cobertura y estados

| Wireframe | Screen | User Flow | Estados representados |
|---|---|---|---|
| WF-ESP-01 | SCR-ESP-01 | UF-ESP-01, UF-ESP-02, UF-ESP-10, UF-ESP-11 | Carga, guardando, duplicado/inválido, impacto previo, sin confirmar, confirmada |
| WF-ESP-02 | SCR-ESP-02 | UF-ESP-03, UF-ESP-04 | Carga, asociando, unidad/ya asociado, retiro confirmado |
| WF-ESP-03 | SCR-ESP-03 | UF-ESP-05 a UF-ESP-09 | Carga, guardando, lista sin opciones, duplicado, deshabilitado |
| WF-ESP-04 | SCR-ESP-04 | UF-ESP-12, UF-ESP-13 | Carga, detalle, visibilidad por rol |
