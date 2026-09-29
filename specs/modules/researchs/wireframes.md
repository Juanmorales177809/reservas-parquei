# Wireframes — Researchs

## Alcance, fuentes y lectura

Cuatro wireframes de baja fidelidad, uno por cada pantalla de [screens.md](screens.md). Fuentes revisadas: [user-flow.md](user-flow.md), [screen-flow.md](screen-flow.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md) y el [contrato API de Researchs](../../contratos/researchs/api-contract.md). Las variantes son estados de la misma pantalla, no pantallas nuevas.

Los bloques ASCII representan agrupación y orden de contenido, sin fijar dimensiones, estilos, tipografía, colores ni componentes. Para trasladarlos a Figma, conservar el identificador del wireframe y nombrar sus variantes por estado. Los nombres técnicos y referencias que aparecen fuera de los bloques son anotaciones de trazabilidad, no texto de interfaz.

Convenciones: las mismas de [wireframes.md de auth](../auth/wireframes.md) — `[campo: ______]` es una entrada; `[Acción]` es una acción; `(dato)` es información de solo lectura; `{mensaje}` es una región de respuesta, ausente cuando no hay mensaje; `→ destino` es una anotación de navegación, no un botón.

### Estados y seguridad comunes

| Situación | Representación en la pantalla existente | Respaldo |
|---|---|---|
| Procesamiento | Región de mensaje: «Procesando…», concretada por operación | Estados de screens.md |
| Validación de entradas | Mensaje junto al campo correspondiente; corrección mediante la acción existente | `422 VALIDACION`, contrato §1 |
| Elemento inexistente o deshabilitado | Mensaje de no encontrado | `404 NO_ENCONTRADO` |
| Operación no autorizada | «No se puede realizar esta operación.» | `SEC-AUTZ-01`, `SEC-AUTZ-02`, `SEC-AUTZ-04` de auth |
| Sesión no válida | Interrumpe la operación y conduce a `SCR-AUTH-01` de auth | `UF-AUTH-05`, `SEC-SES-07` de auth |
| Sin alcance global | Rechazo en la superficie que lo recibe | `RN-INV-10`, `RN-INV-15`, `RN-ACT-04` |

No se muestran SQL, trazas, variables de entorno, hashes, secretos ni tokens (`SEC-INF-04` de auth, por la misma disciplina transversal).

## WF-INV-01 — Catálogos de proyectos y semilleros

Origen:

- SCR-INV-01.
- Contrato §2.

**Objetivo:** consultar catálogos y cambiar su estado. **Actor:** Administrador global.

**Información visible:** código, nombre y estado. **Entradas:** filtros; acción de estado. **Principal:** filtrar; habilitar/deshabilitar.

### Estado principal

```text
+--------------------------------------------------+
| Proyectos y semilleros                            |
|                                                  |
| Filtros: estado, búsqueda            [Filtrar]   |
| (lista: código, nombre, estado)                   |
|                                       [Cambiar]  |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | `GET .../proyectos`, `GET .../semilleros`, §2.1 |
| Estado cambiado | Confirmación; historial intacto | `PATCH .../estado`, §2.2 |

### Navegación

- **Entrada:** navegación del módulo.
- **Salida correcta:** permanece con la confirmación.
- **Errores:** corrección en esta misma pantalla.

## WF-INV-02 — Actividades institucionales

Origen:

- SCR-INV-02.
- UF-INV-01 (paso 4), contrato §3.

**Objetivo:** crear, modificar, activar y desactivar actividades. **Actor:** Administrador global.

**Información visible:** nombre, dependencia y estado. **Entradas:** nombre, dependencia, estado. **Principal:** guardar.

### Estado principal

```text
+--------------------------------------------------+
| Actividades institucionales                       |
|                                                  |
| (lista: nombre, dependencia, estado)              |
|                                                  |
| Nombre             [________________________]    |
| Dependencia        [________________________]    |
| [Guardar actividad]                               |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | `GET /api/investigacion/actividades`, §3.2 |
| Guardando | «Guardando…» | `POST`/`PATCH`, §3.1/§3.3 |
| Datos faltantes | Mensaje junto al campo | `422 VALIDACION` |
| Estado cambiado | Confirmación; referencias intactas | `PATCH .../estado`, §3.4 |

### Navegación

- **Entrada:** navegación del módulo.
- **Salida correcta:** permanece con la confirmación.
- **Errores:** corrección en esta misma pantalla.

## WF-INV-03 — Catálogo de perfiles

Origen:

- SCR-INV-03.
- UF-INV-01 (paso 5), contrato §4.

**Objetivo:** crear, modificar, habilitar y desactivar perfiles. **Actor:** Administrador global.

**Información visible:** nombre, descripción y estado. **Entradas:** nombre, descripción, estado. **Principal:** guardar.

### Estado principal

```text
+--------------------------------------------------+
| Perfiles                                          |
|                                                  |
| (lista: nombre, estado)                           |
|                                                  |
| Nombre             [________________________]    |
| Descripción        [________________________]    |
| [Guardar perfil]                                  |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | `GET /api/investigacion/perfiles`, §4.2 |
| Guardando | «Guardando…» | `POST`/`PATCH`, §4.1/§4.3 |
| Datos faltantes | Mensaje junto al campo | `422 VALIDACION` |
| Deshabilitado | Ya no ofrecido; asociaciones intactas | `RN-INV-14`, `RN-INV-05` |

### Navegación

- **Entrada:** navegación del módulo.
- **Salida correcta:** permanece con la confirmación.
- **Errores:** corrección en esta misma pantalla.

## WF-INV-04 — Vinculaciones ajenas

Origen:

- SCR-INV-04.
- UF-INV-01 (pasos 1–3), contrato §5.

**Objetivo:** crear, desactivar y reactivar vinculaciones de otro Usuario. **Actor:** Administrador global.

**Información visible:** vinculaciones del Usuario por tipo, con estado. **Entradas:** Usuario, tipo, entidad. **Principal:** crear; desactivar.

### Estado principal

```text
+--------------------------------------------------+
| Vinculaciones de terceros                         |
|                                                  |
| Usuario            [seleccionar]                  |
| (proyectos, semilleros, pasantías, trabajos)      |
| Tipo               [proyectos | semilleros]       |
| Entidad            [seleccionar]     [Crear]      |
|                                                  |
| (lista con estado)                   [Desactivar]|
|                                                  |
| {Resultado}  {Aviso: última vinculación}          |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | `GET .../usuarios/{id}/vinculaciones`, §5.1 |
| Creando | «Guardando…» | `POST .../vinculaciones/{tipo}`, §5.2 |
| Duplicada activa | Mensaje de corrección | `409 CONFLICTO` |
| Inactiva previa | Se reactiva la misma fila | `201 Created`, `RN-INV-11` |
| Entidad inexistente o deshabilitada | Mensaje de no encontrado | `404 NO_ENCONTRADO` |
| Desactivada, última activa | Aviso sin bloquear | `sin_vinculaciones_activas`, `RN-USR-11` de usuarios |
| Desactivada | Confirmación, historial intacto | `204`, §5.3 |

### Navegación

- **Entrada:** navegación del módulo.
- **Salida correcta:** permanece con la confirmación.
- **Errores:** corrección en esta misma pantalla.

## Dependencias y límites del cierre visual

| Pantallas | Información pendiente o límite | Tratamiento en los wireframes |
|---|---|---|
| WF-INV-04 | Localización del Usuario y de la entidad | Zona funcional representada como selección; no se inventa un buscador |
| WF-INV-01 | Destino tras cambiar estado | Se representa la confirmación; la navegación externa no se resuelve aquí |
| Todas | Retornos al abandonar no fijados por las fuentes | No se agregan botones de retorno o cancelación |
| WF-INV-02/03 | Textos de dependencia y descripción | Entradas libres previstas por el contrato; no se inventan catálogos |

## Matriz de cobertura y estados

| Wireframe | Screen | User Flow | Estados representados |
|---|---|---|---|
| WF-INV-01 | SCR-INV-01 | Contrato §2 | Carga, estado cambiado |
| WF-INV-02 | SCR-INV-02 | UF-INV-01 | Carga, guardando, datos faltantes, estado cambiado |
| WF-INV-03 | SCR-INV-03 | UF-INV-01 | Carga, guardando, datos faltantes, deshabilitado |
| WF-INV-04 | SCR-INV-04 | UF-INV-01 | Carga, creando, duplicada, reactivada, no encontrado, última activa, desactivada |
