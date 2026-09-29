# Wireframes — Usuarios

## Alcance, fuentes y lectura

Cinco wireframes de baja fidelidad, uno por cada pantalla de [screens.md](screens.md). Fuentes revisadas: [user-flow.md](user-flow.md), [screen-flow.md](screen-flow.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md) y el [contrato API de Usuarios](../../contratos/usuarios/api-contract.md). Las variantes son estados de la misma pantalla, no pantallas nuevas.

Los bloques ASCII representan agrupación y orden de contenido, sin fijar dimensiones, estilos, tipografía, colores ni componentes. Para trasladarlos a Figma, conservar el identificador del wireframe y nombrar sus variantes por estado. Los nombres técnicos y referencias que aparecen fuera de los bloques son anotaciones de trazabilidad, no texto de interfaz.

Convenciones: las mismas de [wireframes.md de auth](../auth/wireframes.md) — `[campo: ______]` es una entrada; `[Acción]` es una acción; `(dato)` es información de solo lectura; `{mensaje}` es una región de respuesta, ausente cuando no hay mensaje; `→ destino` es una anotación de navegación, no un botón.

### Estados y seguridad comunes

| Situación | Representación en la pantalla existente | Respaldo |
|---|---|---|
| Procesamiento | Región de mensaje: «Procesando…», concretada por operación | Estados de screens.md |
| Validación de entradas | Mensaje junto al campo correspondiente; corrección y envío mediante la acción existente | `422 VALIDACION`, contrato §1 |
| Documento o teléfono duplicado | Mensaje junto al campo afectado, sin identificar el registro con el que coincide | `409 DOCUMENTO_DUPLICADO` / `409 TELEFONO_DUPLICADO`, contrato §1 |
| Vinculación duplicada | «Ya tienes una vinculación activa con este proyecto/semillero.»; no crea una segunda | `409 VINCULACION_DUPLICADA`, contrato §1 |
| Operación no autorizada | «No se puede realizar esta operación.» | `SEC-AUTZ-01`, `SEC-AUTZ-02`, `SEC-AUTZ-04` de auth |
| Sesión no válida | Interrumpe la operación y conduce a `SCR-AUTH-01` de auth | `UF-AUTH-05`, `SEC-SES-07` de auth |
| Actualización inicial pendiente fuera de este módulo | No es un estado de estas pantallas: lo aplican las pantallas de otros módulos que reciben `403 PERFIL_INICIAL_PENDIENTE` | `RN-USR-08`; criterios comunes de screens.md |

No se muestran SQL, trazas, variables de entorno, hashes, secretos ni tokens (`SEC-INF-04` de auth, por la misma disciplina transversal).

## WF-USR-01 — Completar actualización inicial

Origen:

- SCR-USR-01.
- UF-USR-01, UF-USR-02.

**Objetivo:** revisar o completar datos personales y registrar al menos una vinculación válida. **Actor:** Usuario recién autorregistrado o recién activado por invitación.

**Información visible:** datos personales precargados, catálogo de perfiles, catálogo de proyectos/semilleros, formularios de pasantía/trabajo de grado, vinculaciones ya registradas. **Entradas:** los cinco datos personales; selección de perfiles; selección de proyecto/semillero; datos de pasantía o trabajo de grado. **Principal:** continuar (disponible solo con al menos una vinculación válida). **Secundarias:** asociar proyecto, asociar semillero, registrar pasantía, registrar trabajo de grado.

### Estado principal

```text
+--------------------------------------------------+
| Completa tu perfil                                |
| Revisa tus datos y agrega al menos una vinculación|
| académica o investigativa para continuar.         |
|                                                  |
| Nombre             [________________________]    |
| Documento          [________________________]    |
| Teléfono           [________________________]    |
| Institución        [________________________]    |
| Dependencia        [________________________]    |
| {Validación de datos personales}                  |
|                                                  |
| Perfiles académicos/investigativos                |
| [ ] Perfil A   [ ] Perfil B   [ ] Perfil C        |
|                                                  |
| Vinculaciones                                     |
| (lista de vinculaciones ya registradas, si hay)   |
| Proyecto      [seleccionar del catálogo] [Asociar]|
| Semillero     [seleccionar del catálogo] [Asociar]|
| [Registrar pasantía]  [Registrar trabajo de grado]|
| {Resultado de la última vinculación}              |
|                                                  |
| {Aviso: aún no tienes ninguna vinculación válida} |
| [Continuar]                                      |
+--------------------------------------------------+
```

Registrar pasantía y registrar trabajo de grado son formularios propios dentro de la misma superficie (universidad/docente para pasantía; director para trabajo de grado), no pantallas nuevas — igual criterio que auth usa para variantes contextuales de una misma Screen.

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga inicial | «Cargando tu perfil…» | `GET /api/perfil`, §2.1; catálogos de §3.0 y §4.1 |
| Validación de datos personales | Mensaje junto al campo afectado | `422 VALIDACION`, §2.2 |
| Documento/teléfono duplicado | Mensaje común de duplicado junto al campo | `409 DOCUMENTO_DUPLICADO` / `409 TELEFONO_DUPLICADO`, §2.2 |
| Asociando vinculación | «Asociando proyecto…» / «Asociando semillero…» / «Registrando pasantía…» / «Registrando trabajo de grado…» | §4.2–§4.5 |
| Vinculación duplicada | Mensaje común de vinculación duplicada; si estaba inactiva, se reactiva sin mostrarlo como error | `409 VINCULACION_DUPLICADA`, §4.2/§4.3 |
| Vinculación no encontrada | «El proyecto o semillero seleccionado ya no está disponible.» | `404 NO_ENCONTRADO`, §4.2/§4.3 |
| Sin vinculación válida todavía | «Aún no tienes ninguna vinculación académica o investigativa activa y válida.»; `[Continuar]` no completa la actualización | `409 CONFLICTO` de §2.3, condición de vinculación |
| Confirmando actualización inicial | «Confirmando…» | `POST /api/perfil/actualizacion-inicial`, §2.3 |
| Datos incompletos al confirmar | «Completa los datos obligatorios antes de continuar.» | `409 CONFLICTO` de §2.3, condición de datos |
| Actualización inicial completada | «Perfil completado.» y continuación | `200 OK`, §2.3 |

### Navegación

- **Entrada:** primer ingreso o ingreso posterior con la actualización todavía pendiente, conducido por auth (`RN-AUTH-SES-04`).
- **Salida correcta:** continúa a las operaciones ya autorizadas; destino no fijado por las fuentes.
- **Errores:** permanecen en esta pantalla; ninguno interrumpe el progreso ya guardado.
- **Abandono:** los datos y vinculaciones registrados se conservan; el mismo recorrido se retoma en el siguiente ingreso.

## WF-USR-02 — Ver mi perfil

Origen:

- SCR-USR-02.
- UF-USR-03.

**Objetivo:** consultar la información consolidada del perfil. **Actor:** Usuario.

**Información visible:** datos personales, correo, condición de actualización inicial, perfiles y vinculaciones. **Entradas:** ninguna. **Principal:** ninguna acción propia; accesos a las otras pantallas. **Secundarias:** editar datos personales, actualizar perfiles, gestionar vinculaciones.

### Estado principal

```text
+--------------------------------------------------+
| Mi perfil                                         |
|                                                  |
| Nombre:            (nombre)                       |
| Documento:         (documento)                    |
| Teléfono:          (teléfono)                     |
| Institución:       (institución)                  |
| Dependencia:       (dependencia)                  |
| Correo:            (correo, solo lectura)          |
| Actualización inicial: (completada / pendiente)   |
|                                                  |
| Perfiles académicos/investigativos                |
| (lista de perfiles vigentes)                      |
|                                                  |
| Vinculaciones                                     |
| (lista: proyectos, semilleros, pasantías,         |
|  trabajos de grado, con su estado)                |
|                                                  |
| [Editar datos]  [Actualizar perfiles]             |
| [Gestionar vinculaciones]                         |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando tu perfil…» | `GET /api/perfil`, §2.1 |
| Consolidado disponible | Bloque anterior | `200 OK` |
| Sesión no válida | Interrumpe y conduce a `SCR-AUTH-01` | `401 NO_AUTENTICADO`; `UF-AUTH-05` de auth |

### Navegación

- **Entrada:** opción de acceso al perfil desde el contexto autenticado; localización pendiente de definición fuera de este módulo.
- **Salida:** `[Editar datos]` → `SCR-USR-03`; `[Actualizar perfiles]` → `SCR-USR-04`; `[Gestionar vinculaciones]` → `SCR-USR-05`.
- **Errores:** sesión no válida se resuelve en auth, no en esta pantalla.

## WF-USR-03 — Editar mis datos personales

Origen:

- SCR-USR-03.
- UF-USR-04.

**Objetivo:** modificar los datos personales editables. **Actor:** Usuario.

**Información visible:** los cinco datos editables; correo de solo lectura. **Entradas:** nombre, documento, teléfono, institución, dependencia. **Principal:** guardar cambios. **Secundarias:** ninguna definida en SCR-USR-03.

### Estado principal

```text
+--------------------------------------------------+
| Editar mis datos                                  |
|                                                  |
| Correo (no editable): (correo)                     |
| Nombre             [________________________]    |
| Documento          [________________________]    |
| Teléfono           [________________________]    |
| Institución        [________________________]    |
| Dependencia        [________________________]    |
|                                                  |
| {Validación o resultado}                          |
| [Guardar cambios]                                 |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Guardando cambios…» | `PATCH /api/perfil`, §2.2 |
| Validación | Mensaje junto al campo afectado por dato vacío o inválido | `422 VALIDACION` |
| Duplicado | Mensaje común de duplicado junto al campo afectado | `409 DOCUMENTO_DUPLICADO` / `409 TELEFONO_DUPLICADO` |
| Guardado | «Datos actualizados.» | `200 OK` con el perfil actualizado |

### Navegación

- **Entrada:** opción «Editar datos» desde `SCR-USR-02`.
- **Salida correcta:** permanece con la confirmación; retorno a `SCR-USR-02`.
- **Errores:** corrección en esta misma pantalla.

## WF-USR-04 — Actualizar mis perfiles académicos o investigativos

Origen:

- SCR-USR-04.
- UF-USR-05.

**Objetivo:** seleccionar los perfiles propios del catálogo habilitado. **Actor:** Usuario.

**Información visible:** catálogo de perfiles habilitados; selección vigente. **Entradas:** selección de uno o más perfiles. **Principal:** guardar selección. **Secundarias:** ninguna definida en SCR-USR-04.

### Estado principal

```text
+--------------------------------------------------+
| Mis perfiles académicos/investigativos            |
|                                                  |
| [ ] Perfil A                                      |
| [ ] Perfil B                                      |
| [ ] Perfil C                                      |
| (catálogo habilitado; los deshabilitados no       |
|  aparecen)                                        |
|                                                  |
| {Resultado}                                       |
| [Guardar selección]                              |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga del catálogo | «Cargando perfiles…» | `GET /api/perfil/perfiles/catalogo`, §3.0 |
| Guardando | «Guardando selección…» | `PUT /api/perfil/perfiles`, §3.1 |
| Combinación rechazada | «Esta combinación de perfiles no está permitida.» | `409 CONFLICTO` |
| Perfil no disponible | «Uno de los perfiles seleccionados ya no está disponible.» | `404 NO_ENCONTRADO` |
| Guardado | «Perfiles actualizados.» | `200 OK` con los perfiles vigentes |

### Navegación

- **Entrada:** opción «Actualizar perfiles» desde `SCR-USR-02`.
- **Salida correcta:** permanece con la confirmación; el perfil consolidado de `SCR-USR-02` refleja la selección.
- **Errores:** corrección en esta misma pantalla.

## WF-USR-05 — Gestionar mis vinculaciones académicas o investigativas

Origen:

- SCR-USR-05.
- UF-USR-06, UF-USR-07, UF-USR-08, UF-USR-09, UF-USR-10.

**Objetivo:** asociar proyectos o semilleros, registrar pasantías o trabajos de grado, y desactivar vinculaciones. **Actor:** Usuario titular; Administrador global solo para desactivar una vinculación ajena.

**Información visible:** vinculaciones vigentes con su estado; catálogo de proyectos/semilleros disponibles. **Entradas:** selección de proyecto/semillero; datos de pasantía o trabajo de grado; acción de desactivar. **Principales:** asociar proyecto, asociar semillero, registrar pasantía, registrar trabajo de grado, desactivar una vinculación.

### Estado principal

```text
+--------------------------------------------------+
| Mis vinculaciones                                 |
|                                                  |
| Proyectos                                        |
| (lista de proyectos vinculados)      [Desactivar]|
| Asociar   [seleccionar del catálogo]   [Asociar] |
|                                                  |
| Semilleros                                       |
| (lista de semilleros vinculados)     [Desactivar]|
| Asociar   [seleccionar del catálogo]   [Asociar] |
|                                                  |
| Pasantías                                        |
| (lista de pasantías registradas)     [Desactivar]|
| Universidad        [________________________]   |
| Docente ITM        [________________________]   |
| Correo del docente [________________________]   |
| [Registrar pasantía]                             |
|                                                  |
| Trabajo de grado                                 |
| (lista de trabajos de grado registrados)         |
|                                       [Desactivar]|
| Director           [________________________]   |
| Correo del director[________________________]   |
| [Registrar trabajo de grado]                     |
|                                                  |
| {Resultado de la última operación}                |
| {Aviso: sin vinculaciones activas tras desactivar}|
+--------------------------------------------------+
```

Las cuatro secciones son parte de una misma superficie (`SCR-USR-05`), no cuatro pantallas: comparten el mismo contexto de vinculaciones vigentes.

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando tus vinculaciones…» | `GET /api/perfil`, §2.1; catálogo de §4.1 |
| Asociando proyecto/semillero | «Asociando…» | `POST /api/perfil/vinculaciones/proyectos` o `/semilleros`, §4.2/§4.3 |
| Vinculación duplicada | Mensaje común de vinculación duplicada; si estaba inactiva, se reactiva | `409 VINCULACION_DUPLICADA` |
| Proyecto/semillero no disponible | «El proyecto o semillero seleccionado ya no está disponible.» | `404 NO_ENCONTRADO` |
| Registrando pasantía/trabajo de grado | «Registrando…» | `POST /api/perfil/vinculaciones/pasantias` o `/trabajos-grado`, §4.4/§4.5 |
| Validación de pasantía/trabajo de grado | Mensaje junto al campo afectado, incluido el formato de correo | `422 VALIDACION` |
| Desactivando | «Desactivando vinculación…» | `DELETE /api/perfil/vinculaciones/{tipo}/{id}`, §4.6 |
| Desactivada, sin otras activas | «Vinculación desactivada. Ya no tienes ninguna vinculación activa: no podrás crear nuevas reservas hasta recuperar una.» | `200 OK` con `sin_vinculaciones_activas: true`, §4.6 |
| Desactivada, con otras activas | «Vinculación desactivada.» | `200 OK` con `sin_vinculaciones_activas: false` |
| Acceso denegado a desactivar una vinculación ajena | Mensaje común de operación no autorizada | `SEC-AUTZ-02` de auth; `UF-USR-10` |

### Navegación

- **Entrada:** opción «Gestionar vinculaciones» desde `SCR-USR-02`; también accesible desde `SCR-USR-01` mientras la actualización inicial está pendiente, como la misma superficie de vinculaciones.
- **Salida correcta:** permanece con la confirmación; el perfil consolidado de `SCR-USR-02` refleja los cambios.
- **Errores:** corrección o denegación en esta misma pantalla.

## Dependencias y límites del cierre visual

| Pantallas | Información pendiente o límite | Tratamiento en los wireframes |
|---|---|---|
| SCR-USR-01, SCR-USR-05 | Mecanismo de selección del catálogo de proyectos/semilleros (lista, buscador) | Zona funcional representada como selección; no se inventa un buscador ni un límite de resultados |
| SCR-USR-01 | Destino concreto tras completar la actualización inicial | Se representa la confirmación; la navegación externa no se resuelve aquí, igual que auth deja abierto el destino tras iniciar sesión |
| Todas | Retornos al abandonar no fijados por las fuentes | No se agregan botones de retorno o cancelación |

## Matriz de cobertura y estados

| Wireframe | Screen | User Flow | Estados representados |
|---|---|---|---|
| WF-USR-01 | SCR-USR-01 | UF-USR-01, UF-USR-02 | Carga, validación, duplicado, asociando vinculación, vinculación duplicada/no encontrada, sin vinculación válida, confirmando, datos incompletos, completado |
| WF-USR-02 | SCR-USR-02 | UF-USR-03 | Carga, consolidado disponible, sesión no válida |
| WF-USR-03 | SCR-USR-03 | UF-USR-04 | Carga, validación, duplicado, guardado |
| WF-USR-04 | SCR-USR-04 | UF-USR-05 | Carga de catálogo, guardando, combinación rechazada, perfil no disponible, guardado |
| WF-USR-05 | SCR-USR-05 | UF-USR-06, UF-USR-07, UF-USR-08, UF-USR-09, UF-USR-10 | Carga, asociando, duplicada/no disponible, registrando, validación, desactivando (con y sin otras activas), acceso denegado |
