# Wireframes — Administration

## Alcance, fuentes y lectura

Cinco wireframes de baja fidelidad, uno por cada pantalla de [screens.md](screens.md). Fuentes revisadas: [user-flow.md](user-flow.md), [screen-flow.md](screen-flow.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md) y el [contrato API de Administration](../../contratos/administration/api-contract.md). Las variantes son estados de la misma pantalla, no pantallas nuevas.

Los bloques ASCII representan agrupación y orden de contenido, sin fijar dimensiones, estilos, tipografía, colores ni componentes. Para trasladarlos a Figma, conservar el identificador del wireframe y nombrar sus variantes por estado. Los nombres técnicos y referencias que aparecen fuera de los bloques son anotaciones de trazabilidad, no texto de interfaz.

Convenciones: las mismas de [wireframes.md de auth](../auth/wireframes.md) — `[campo: ______]` es una entrada; `[Acción]` es una acción; `(dato)` es información de solo lectura; `{mensaje}` es una región de respuesta, ausente cuando no hay mensaje; `→ destino` es una anotación de navegación, no un botón.

### Estados y seguridad comunes

| Situación | Representación en la pantalla existente | Respaldo |
|---|---|---|
| Procesamiento | Región de mensaje: «Procesando…», concretada por operación | Estados de screens.md |
| Validación de entradas | Mensaje junto al campo correspondiente; corrección mediante la acción existente | `422 VALIDACION`, contrato §1 |
| Nombre duplicado | Mensaje junto al campo, sin identificar el registro coincidente | `409 CONFLICTO`, contrato §2.1/§2.3 |
| Operación no autorizada | «No se puede realizar esta operación.» | `SEC-AUTZ-01`, `SEC-AUTZ-02`, `SEC-AUTZ-04` de auth |
| Sesión no válida | Interrumpe la operación y conduce a `SCR-AUTH-01` de auth | `UF-AUTH-05`, `SEC-SES-07` de auth |
| Sin alcance global | Rechazo en la superficie que lo recibe | Permiso de la sección con alcance global |

No se muestran SQL, trazas, variables de entorno, hashes, secretos ni tokens (`SEC-INF-04` de auth, por la misma disciplina transversal). La auditoría nunca muestra contraseñas, secretos de sesión, tokens completos ni claves (`SEC-AUD-03` de auth).

## WF-ADM-01 — Gestionar unidades y cargos

Origen:

- SCR-ADM-01.
- Contrato §2 (sin flujo propio).

**Objetivo:** registrar, consultar, modificar y habilitar/deshabilitar unidades y cargos. **Actor:** Administrador global.

**Información visible:** listado de unidades y de cargos; detalle. **Entradas:** nombre, tipo, unidad padre; nombre y unidad del cargo. **Principal:** guardar. **Secundarias:** habilitar/deshabilitar.

### Estado principal

```text
+--------------------------------------------------+
| Unidades y cargos                                  |
|                                                  |
| Unidades                                         |
| (lista: nombre, tipo, estado)        [+ Nueva]   |
| Nombre             [________________________]    |
| Tipo               [seleccionar]                  |
| Unidad padre       [seleccionar, opcional]        |
| [Guardar unidad]                                 |
|                                                  |
| Cargos                                           |
| (lista: nombre, unidad)              [+ Nuevo]   |
| Nombre del cargo   [________________________]    |
| Unidad             [seleccionar]                  |
| [Guardar cargo]                                  |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | `GET /api/unidades`, `GET /api/cargos`, §2.2/§2.6 |
| Guardando | «Guardando…» | `POST`/`PATCH`, §2.1/§2.3/§2.5/§2.6 |
| Nombre duplicado o ciclo | Mensaje junto al campo | `409 CONFLICTO` |
| Padre inexistente o unidad inexistente | Mensaje de no encontrado | `404 NO_ENCONTRADO` |
| Estado cambiado | «Unidad deshabilitada. Conserva todo lo asociado.» | `PATCH .../estado`, §2.4 |

### Navegación

- **Entrada:** navegación de administración.
- **Salida correcta:** permanece con la confirmación; el listado refleja el cambio.
- **Errores:** corrección en esta misma pantalla.

## WF-ADM-02 — Asignar y retirar permisos

Origen:

- SCR-ADM-02.
- Contrato §3 (sin flujo propio).

**Objetivo:** otorgar y retirar permisos con su ámbito. **Actor:** Administrador global con `permisos.asignar`.

**Información visible:** catálogo de códigos; cuenta destino; asignaciones vigentes con ámbito. **Entradas:** cuenta, código, unidad o alcance global. **Principal:** otorgar. **Secundarias:** retirar asignación.

### Estado principal

```text
+--------------------------------------------------+
| Permisos de la cuenta                             |
| (cuenta destino)                                  |
|                                                  |
| Asignaciones vigentes                             |
| (lista: código, ámbito)               [Retirar]  |
|                                                  |
| Otorgar                                          |
| Código             [seleccionar del catálogo]     |
| Unidad             [seleccionar o global]         |
| [Otorgar permiso]                                |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | `GET /api/permisos`, `GET /api/permisos/cuentas/{id}`, §3.1/§3.2 |
| Otorgando/retirando | «Guardando…» | `POST`/`DELETE`, §3.3/§3.4 |
| Asignación duplicada o cuenta/unidad/código inválidos | Mensaje de corrección | `409 CONFLICTO` / `422 VALIDACION` |
| Último permiso global | «No se puede dejar al sistema sin administradores.» | `409 CONFLICTO`, `RN-AUTH-ROL-09` de auth |
| Asignación inexistente al retirar | Mensaje de no encontrado | `404 NO_ENCONTRADO` |

### Navegación

- **Entrada:** navegación de administración, con la cuenta destino localizada.
- **Salida correcta:** permanece con la confirmación.
- **Errores:** corrección en esta misma pantalla.

## WF-ADM-03 — Registrar identidades e invitar

Origen:

- SCR-ADM-03.
- UF-ADM-02, UF-ADM-03.

**Objetivo:** registrar la identidad o ficha e invitar su cuenta. **Actor:** Administrador global.

**Información visible:** datos de la identidad o ficha; resultado de la invitación (nunca el token). **Entradas:** datos personales o de la ficha; correo y unidad para invitar. **Principal:** guardar; invitar. **Secundarias:** localizar ficha existente por correo.

### Estado principal

```text
+--------------------------------------------------+
| Identidades                                       |
|                                                  |
| Tipo: ( ) Usuario  ( ) Personal                   |
|                                                  |
| Nombre             [________________________]    |
| Documento          [________________________]    |
| Correo             [________________________]    |
| Teléfono           [________________________]    |
| Institución / Dependencia  [________] [________] |
|   —o—                                            |
| Cargo              [seleccionar]     (Personal)   |
| [Guardar]  [Localizar por correo]                 |
|                                                  |
| Invitar cuenta                                    |
| Correo             [________________________]    |
| Unidad             [seleccionar]     (Personal)   |
| [Invitar]                                        |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Guardando/invitando | «Guardando…» / «Invitando…» | `POST /api/usuarios`, `POST /api/personal` (usuarios §5–§6); invitación (auth §4) |
| Datos faltantes o duplicados | Mensaje junto al campo | Sin guardar ni invitar |
| Sin ficha activa coincidente | Mensaje de no encontrado | Invitación rechazada desde auth |
| Invitación emitida | Confirmación sin token | Respuesta de emisión de auth |

### Navegación

- **Entrada:** navegación de administración.
- **Salida correcta:** permanece; la ficha queda activa y la invitación emitida.
- **Errores:** corrección en esta misma pantalla.

## WF-ADM-04 — Importar catálogos

Origen:

- SCR-ADM-04.
- UF-ADM-01, UF-ADM-04.

**Objetivo:** validar y confirmar cargas Excel. **Actor:** Administrador global.

**Información visible:** catálogo, unidad destino (equipos), resumen de validación con resultado por fila, historial con totales. **Entradas:** archivo Excel, catálogo, unidad para equipos. **Principal:** validar; confirmar carga confirmable. **Secundarias:** consultar historial y detalle por fila.

### Estado principal

```text
+--------------------------------------------------+
| Importar catálogo                                 |
|                                                  |
| Catálogo  [proyectos | semilleros | equipos]      |
| Unidad    [seleccionar]  (solo equipos)           |
| Archivo   [elegir archivo Excel]  [Validar]       |
|                                                  |
| Resultado de validación                           |
| (resumen: nuevos, actualizados, desactivados,     |
|  errores)                                         |
| (lista por fila: número, código, resultado,       |
|  detalle)                                         |
| [Confirmar importación]  (solo si confirmable)    |
|                                                  |
| Historial                                         |
| (lista: fecha, catálogo, totales)                 |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Validando | «Validando archivo…» | `POST /api/importaciones`, §4.1 |
| Fila en error | Detalle por fila; confirmar no disponible | `confirmable: false`, §4.1 |
| Confirmando | «Confirmando…» | `POST .../confirmacion`, §4.2 |
| Confirmada | Totales definitivos | `200 OK`, §4.2 |
| Carga con error confirmada | Rechazo | `409 CONFLICTO` |
| Archivo ilegible o catálogo inválido | Mensaje de corrección | `422 VALIDACION` |
| Equipos sin unidad | Mensaje de corrección | `400 SOLICITUD_INVALIDA` |

### Navegación

- **Entrada:** navegación de administración.
- **Salida correcta:** permanece con totales; el historial refleja la carga.
- **Errores:** corrección en esta misma pantalla; sin escritura parcial.

## WF-ADM-05 — Consultar auditoría

Origen:

- SCR-ADM-05.
- Contrato §5 (sin flujo propio).

**Objetivo:** consultar el registro administrativo. **Actor:** Administrador global.

**Información visible:** actor, acción, entidad, identificador, momento y cambios; filtros. **Entradas:** filtros de consulta. **Principal:** ninguna acción propia; filtrar y paginar. **Secundarias:** ninguna.

### Estado principal

```text
+--------------------------------------------------+
| Auditoría                                         |
|                                                  |
| Filtros: entidad, actor, acción, fechas           |
| [Filtrar]                                         |
|                                                  |
| (lista: momento, actor, acción, entidad,          |
|  identificador)                                   |
|                                                  |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | `GET /api/auditoria`, §5.1 |
| Sin resultados | Lista vacía con filtros visibles | `200 OK` con envolvente vacía |

### Navegación

- **Entrada:** navegación de administración.
- **Salida correcta:** permanece.
- **Errores:** sesión no válida se resuelve en auth.

## Dependencias y límites del cierre visual

| Pantallas | Información pendiente o límite | Tratamiento en los wireframes |
|---|---|---|
| WF-ADM-01, WF-ADM-02 | Localización de la cuenta destino para permisos (por correo, lista) | Zona funcional representada como cuenta destino; no se inventa un buscador |
| WF-ADM-03 | Localización de ficha existente | Representada como acción, sin mecanismo concreto inventado |
| WF-ADM-04 | Destino tras confirmar | Se representa la confirmación; la navegación externa no se resuelve aquí |
| Todas | Retornos al abandonar no fijados por las fuentes | No se agregan botones de retorno o cancelación |

## Matriz de cobertura y estados

| Wireframe | Screen | User Flow | Estados representados |
|---|---|---|---|
| WF-ADM-01 | SCR-ADM-01 | Contrato §2 | Carga, guardando, duplicado/ciclo, no encontrado, estado cambiado |
| WF-ADM-02 | SCR-ADM-02 | Contrato §3 | Carga, otorgando/retirando, duplicado/inválido, último global, no encontrado |
| WF-ADM-03 | SCR-ADM-03 | UF-ADM-02, UF-ADM-03 | Guardando/invitando, datos/duplicados, sin ficha, invitación emitida |
| WF-ADM-04 | SCR-ADM-04 | UF-ADM-01, UF-ADM-04 | Validando, fila en error, confirmando, confirmada, rechazo, archivo inválido, sin unidad |
| WF-ADM-05 | SCR-ADM-05 | Contrato §5 | Carga, sin resultados |
