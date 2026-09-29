# Wireframes — Resources

## Alcance, fuentes y lectura

Cuatro wireframes de baja fidelidad, uno por cada pantalla de [screens.md](screens.md). Fuentes revisadas: [user-flow.md](user-flow.md), [screen-flow.md](screen-flow.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md) y el [contrato API de Resources](../../contratos/resources/api-contract.md). Las variantes son estados de la misma pantalla, no pantallas nuevas.

Los bloques ASCII representan agrupación y orden de contenido, sin fijar dimensiones, estilos, tipografía, colores ni componentes. Para trasladarlos a Figma, conservar el identificador del wireframe y nombrar sus variantes por estado. Los nombres técnicos y referencias que aparecen fuera de los bloques son anotaciones de trazabilidad, no texto de interfaz.

Convenciones: las mismas de [wireframes.md de auth](../auth/wireframes.md) — `[campo: ______]` es una entrada; `[Acción]` es una acción; `(dato)` es información de solo lectura; `{mensaje}` es una región de respuesta, ausente cuando no hay mensaje; `→ destino` es una anotación de navegación, no un botón.

### Estados y seguridad comunes

| Situación | Representación en la pantalla existente | Respaldo |
|---|---|---|
| Procesamiento | Región de mensaje: «Procesando…», concretada por operación | Estados de screens.md |
| Validación de entradas | Mensaje junto al campo correspondiente; corrección mediante la acción existente | `422 VALIDACION`, contrato §1 |
| Tipo o unidad incompatible | Mensaje de corrección | `409 TIPO_INCOMPATIBLE` / `409 UNIDAD_INCOMPATIBLE` |
| Operación no autorizada | «No se puede realizar esta operación.» | `SEC-AUTZ-01`, `SEC-AUTZ-02`, `SEC-AUTZ-04` de auth |
| Sesión no válida | Interrumpe la operación y conduce a `SCR-AUTH-01` de auth | `UF-AUTH-05`, `SEC-SES-07` de auth |
| Técnico creando equipos | Rechazo: solo edita los de su unidad | `RN-EQP-09`, `403 NO_AUTORIZADO` |

No se muestran SQL, trazas, variables de entorno, hashes, secretos ni tokens (`SEC-INF-04` de auth, por la misma disciplina transversal).

## WF-REC-01 — Registrar y consultar recursos

Origen:

- SCR-REC-01.
- UF-REC-01, UF-REC-02, UF-REC-03, UF-REC-04, UF-REC-05.

**Objetivo:** registrar mobiliario, otros y equipos, y consultar el catálogo. **Actores:** Técnico (no equipos al crear) o Administrador.

**Información visible:** catálogo con filtros; detalle con especialización. **Entradas:** unidad, tipo, datos generales y especializados. **Principal:** guardar; consultar. **Secundarias:** filtrar, ver detalle.

### Estado principal

```text
+--------------------------------------------------+
| Recursos                                          |
|                                                  |
| Filtros: tipo, habilitado, búsqueda               |
| [Filtrar]                                         |
| (lista: nombre/placa, tipo, unidad, estado)       |
|                                                  |
| Registrar                                        |
| Unidad             [seleccionar]                  |
| Tipo               [mobiliario | otro | equipo]   |
| Nombre             [________________________]    |
| Placa              [________________________]    |
| (campos especializados según tipo)                |
| [Guardar recurso]                                |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | `GET /api/recursos`, §2.2 |
| Guardando | «Guardando…» | `POST /api/recursos`, §2.1 |
| Datos faltantes o tipo incompatible | Mensaje junto al campo | `422 VALIDACION` / `409 TIPO_INCOMPATIBLE` |
| Unidad ajena o sin permiso | Mensaje de denegación | `403 NO_AUTORIZADO` / `409 UNIDAD_INCOMPATIBLE` |
| Detalle | Especialización consolidada | `GET /api/recursos/{id}`, §2.3 |
| Acreditado | Marca de no reservable en consulta | `RN-REC-11`, filtro `reservable` |

### Navegación

- **Entrada:** navegación del módulo.
- **Salida correcta:** permanece; el catálogo refleja el registro.
- **Errores:** corrección en esta misma pantalla.

## WF-REC-02 — Editar, habilitar y reasignar

Origen:

- SCR-REC-02.
- UF-REC-06, UF-REC-07, UF-REC-08, UF-REC-09, UF-REC-10, UF-REC-12.

**Objetivo:** modificar datos, cambiar habilitación con advertencia y reasignar unidad. **Actores:** Técnico de la unidad o Administrador.

**Información visible:** datos editables; conteo de impacto; unidad vigente. **Entradas:** datos; confirmación; nueva unidad. **Principal:** guardar; confirmar deshabilitación. **Secundarias:** habilitar, reasignar.

### Estado principal

```text
+--------------------------------------------------+
| Detalle del recurso                               |
| (datos generales y especializados)                |
| [Editar datos]            [Habilitar/Deshabilitar]|
|                                                  |
| Advertencia de impacto                            |
| (reservas a cancelar: N, a retirar: M)            |
| [Confirmar deshabilitación]                       |
|                                                  |
| Reasignar unidad                                  |
| Unidad             [seleccionar]   [Reasignar]    |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Cargando detalle | «Cargando…» | `GET /api/recursos/{id}`, §2.3 |
| Guardando | «Guardando…» | `PATCH /api/recursos/{id}`, §2.4 |
| Impacto previo | Conteo sin ejecutar | `GET .../impacto-deshabilitacion`, §2.6 |
| Sin confirmar | Sin cambios ni reservas tocadas | `409 CONFLICTO` |
| Confirmada | Totales de canceladas y afectadas | `200 OK` con totales, §2.5 |
| Reasignación incompatible | Mensaje de corrección | `409 UNIDAD_INCOMPATIBLE` |

### Navegación

- **Entrada:** detalle desde `SCR-REC-01`.
- **Salida correcta:** permanece con la confirmación.
- **Errores:** corrección en esta misma pantalla.

## WF-REC-03 — Configurar el laboratorio

Origen:

- SCR-REC-03.
- UF-REC-13.

**Objetivo:** ver y modificar la configuración de la unidad. **Actores:** Técnico de la unidad o Administrador.

**Información visible:** valores vigentes, tipos ofrecidos, visibilidad. **Entradas:** cada valor configurable. **Principal:** guardar. **Secundarias:** definir tipos, ajustar visibilidad.

### Estado principal

```text
+--------------------------------------------------+
| Configuración del laboratorio                     |
|                                                  |
| Acepta reservas        [sí/no]                    |
| Días de atención       [selección múltiple]       |
| Apertura               [__:__]  Cierre  [__:__]   |
| Antelación (horas)     [________]                 |
| Aprobación automática  [sí/no]                    |
| Recordatorio (horas)   [________]                 |
| Notificar por correo   [sí/no]                    |
| [Guardar configuración]                           |
|                                                  |
| Tipos de reserva       [selección múltiple]       |
| [Guardar tipos]                                   |
|                                                  |
| Visibilidad            [estado] [reservista]      |
| [Guardar visibilidad]                             |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | `GET .../configuracion`, §3.1 |
| Guardando | «Guardando…» | `PATCH`, `PUT`, §3.2/§3.3/§3.4 |
| Horario inválido o valores no positivos | Mensaje junto al campo | `422 VALIDACION` |
| Guardado | Confirmación; el horario versiona el anterior | `200 OK` |

### Navegación

- **Entrada:** navegación del módulo.
- **Salida correcta:** permanece con la confirmación.
- **Errores:** corrección en esta misma pantalla.

## WF-REC-04 — Validaciones de equipos en importación

Origen:

- SCR-REC-04, por referencia a `SCR-ADM-04` de administration.
- `RN-IMP-02`, `RN-IMP-03`, `RN-IMP-06` de este módulo.

**Objetivo:** documentar qué validaciones propias muestra la superficie de importación. Sin superficie ni wireframe propio: la carga, el resumen y la confirmación viven en `WF-ADM-04`.

### Estados alternos

| Estado | Variación visual (en WF-ADM-04) | Compatibilidad API |
|---|---|---|
| Placa o descripción ausente | Fila en error | Validaciones de equipos |
| Fecha inválida o placa duplicada | Fila en error | Validaciones de equipos |
| Placa existente | Actualiza, no duplica | `RN-IMP-02` de resources |
| Nunca deshabilita | Sin estado de baja en la carga | `RN-IMP-07` |

## Dependencias y límites del cierre visual

| Pantallas | Información pendiente o límite | Tratamiento en los wireframes |
|---|---|---|
| WF-REC-01, WF-REC-02 | Mecanismo de selección de unidad/categoría | Zona funcional representada como selección; no se inventa un buscador |
| WF-REC-03 | Destino tras guardar | Se representa la confirmación; la navegación externa no se resuelve aquí |
| Todas | Retornos al abandonar no fijados por las fuentes | No se agregan botones de retorno o cancelación |
| WF-REC-04 | Superficie de carga | Referenciada, no dibujada: vive en administration |

## Matriz de cobertura y estados

| Wireframe | Screen | User Flow | Estados representados |
|---|---|---|---|
| WF-REC-01 | SCR-REC-01 | UF-REC-01 a UF-REC-05 | Carga, guardando, validación, incompatible, denegación, detalle, acreditado |
| WF-REC-02 | SCR-REC-02 | UF-REC-06 a UF-REC-10, UF-REC-12 | Cargando, guardando, impacto previo, sin confirmar, confirmada, reasignación |
| WF-REC-03 | SCR-REC-03 | UF-REC-13 | Carga, guardando, horario inválido, guardado |
| WF-REC-04 | SCR-REC-04 | UF-ADM-04 (referencia) | Filas en error, actualización, nunca deshabilita |
