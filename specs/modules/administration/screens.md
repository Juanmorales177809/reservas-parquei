# Especificación funcional de pantallas — Administration

## Alcance y fuentes

Derivado exclusivamente de [user-flow.md](user-flow.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md) y [overview.md](overview.md). La navegación se detalla en [screen-flow.md](screen-flow.md). Los identificadores corresponden a superficies funcionales; no prescriben páginas independientes, rutas HTTP ni componentes.

No se amplían reglas, datos, contratos ni flujos. Los estados de procesamiento describen la espera del resultado de una acción existente, no operaciones nuevas. No se especifican estilos, disposición visual, textos literales de error ni códigos API.

**Fuera de alcance de este documento:** las cuentas, credenciales, sesiones e invitaciones pertenecen a `auth` y ya tienen pantallas (`FE-07`); las identidades funcionales (`usuarios.usuarios`, `personal.personal`) pertenecen al contrato de `usuarios`, y `UF-ADM-02`/`UF-ADM-03` las orquestan sin duplicarlas aquí — este documento especifica los formularios de captura que esos flujos describen, no la persistencia, que es de `usuarios`. Los catálogos que se importan pertenecen a `researchs` y `recursos`.

## Criterios comunes

- **Actor y ámbito:** todas las superficies exigen cuenta activa con alcance global y el permiso de su sección (`unidades.administrar`, `permisos.asignar`, `importacion.ejecutar`); la auditoría se consulta con `unidades.administrar` global. Sin ese alcance, la operación se rechaza.
- **Backend:** valida identidad, permiso, ámbito y reglas del módulo propietario en cada operación. Ocultar una acción no autoriza la operación.
- **Correo:** donde aparece (identidades), es dato de captura para una ficha nueva o de solo lectura informativa; una vez existe cuenta asociada es inmutable y compartido con `auth.cuentas`.
- **Selección, nunca texto libre:** unidades, cargos, permisos y catálogos de importación se seleccionan de catálogos existentes; no se crean por nombre libre donde la fuente exige selección.
- **Auditoría:** es solo lectura en todas las superficies; ningún formulario la edita.

## SCR-ADM-01 — Gestionar unidades organizacionales y cargos

- **Origen:** contrato §2 (sin flujo propio en `user-flow.md`: las operaciones de estructura no tienen UF; la fuente es el contrato y `RN-UNI`).
- **Actor:** Administrador global.
- **Objetivo:** registrar, consultar, modificar y habilitar/deshabilitar unidades y cargos.
- **Precondiciones:** cuenta activa con `unidades.administrar` global.
- **Información visible:** listado de unidades (nombre, tipo, estado, unidad padre) y de cargos (nombre, unidad); detalle de cada una.
- **Entradas:** nombre, tipo, unidad padre (opcional) para unidades; nombre y unidad para cargos; acción de habilitar/deshabilitar.
- **Acciones:** crear unidad; modificar nombre, tipo o padre; habilitar/deshabilitar unidad; crear cargo; modificar nombre o unidad del cargo.
- **Validaciones visibles:** nombre único; padre existente; sin ciclos de jerarquía; el cargo determina únicamente la unidad de pertenencia, no concede permisos (`RN-PRS-03` de usuarios).
- **Estados:** listado, captura, guardando, corrección requerida, cambio guardado; deshabilitación con advertencia de alcance (no elimina ni propaga, `RN-UNI-04`, `RN-HAB-05`).
- **Errores y respuestas:** nombre duplicado → corrección; padre inexistente o ciclo → corrección; unidad deshabilitada conserva todo lo asociado y no sirve para nuevas operaciones que exijan unidad activa (`RN-UNI-05`).
- **Resultado/navegación:** permanece con confirmación; el listado refleja el cambio.
- **Backend:** persiste con identidad interna independiente del nombre (`RN-UNI-02`, `RN-UNI-03`); audita los cambios (`RN-AUD-06`).
- **RN/SEC relacionadas:** `RN-UNI-01` a `RN-UNI-07`, `RN-HAB-01` a `RN-HAB-05`; `RN-PRS-03` de usuarios.
- **Dependencias:** ninguna externa más allá de la autorización.

## SCR-ADM-02 — Asignar y retirar permisos

- **Origen:** contrato §3 (sin flujo propio; fuente: contrato y `RN-PER`).
- **Actor:** Administrador global con `permisos.asignar`.
- **Objetivo:** otorgar y retirar permisos administrativos a cuentas, con su ámbito.
- **Precondiciones:** cuenta activa con `permisos.asignar` global.
- **Información visible:** catálogo de códigos con su ámbito previsto; asignaciones vigentes de la cuenta consultada con su ámbito efectivo.
- **Entradas:** cuenta destino, código del catálogo, unidad o alcance global (`id_unidad` nulo).
- **Acciones:** otorgar permiso; retirar asignación.
- **Validaciones visibles:** solo cuentas activas `PERSONAL` con ficha activa reciben permisos (`RN-PER-08`); la unidad debe coincidir con la del cargo vigente (`RN-PER-09`); el código existe en el catálogo (`RN-PER-01`); no se amplía el ámbito propio (`RN-PER-03`).
- **Estados:** consulta de catálogo y asignaciones, otorgando, retirando, confirmación.
- **Errores y respuestas:** asignación duplicada, cuenta no `PERSONAL`/inactiva, unidad ajena al cargo o código inexistente → corrección sin guardar; retirar el último permiso global vigente → rechazo (`RN-AUTH-ROL-09` de auth).
- **Resultado/navegación:** permanece con confirmación; retirar afecta solo decisiones futuras (`RN-PER-04`), sin reescribir historial (`RN-PER-05`).
- **Backend:** valida cada restricción en el servidor; audita otorgamientos y retiros.
- **RN/SEC relacionadas:** `RN-PER-01` a `RN-PER-09`; `RN-AUTH-ROL-03`, `RN-AUTH-ROL-09` de auth.
- **Dependencias:** `auth`, que evalúa las asignaciones en cada operación (este módulo las administra, no las evalúa).

## SCR-ADM-03 — Registrar identidades e invitar cuentas

- **User Flows de origen:** `UF-ADM-02`, `UF-ADM-03`.
- **Actor:** Administrador global.
- **Objetivo:** registrar o actualizar la identidad de un Usuario o la ficha de Personal, e invitar su cuenta.
- **Precondiciones:** cuenta activa con alcance global; para Personal, el cargo existe y pertenece a la unidad asignada.
- **Información visible:** datos de la identidad o ficha (nueva o localizada por correo); resultado de la emisión de la invitación. Nunca el token.
- **Entradas:** nombre, documento, correo, teléfono, institución y dependencia (Usuario); nombre, documento, correo, teléfono y cargo (Personal); correo y unidad para invitar (Personal).
- **Acciones:** guardar identidad o ficha; localizar ficha existente por correo; emitir invitación; continuar al alta de cuenta.
- **Validaciones visibles:** datos obligatorios y unicidades de `usuarios` (`RN-DAT`); cargo existente con su unidad (`RN-PRS-05` de usuarios); ficha activa para invitar; correo y unidad coincidentes para `PERSONAL`.
- **Estados:** captura, localización de ficha existente, guardando, invitando, corrección requerida, invitación emitida.
- **Errores y respuestas:** datos faltantes, duplicados o cargo inválido → sin guardar ni invitar; sin ficha activa coincidente o unidad ajena al ámbito → la invitación se rechaza desde `auth`.
- **Resultado/navegación:** la ficha queda activa para invitar; la invitación no concede permisos (se asignan en `SCR-ADM-02`); el alta no marca la actualización inicial como completada.
- **Backend:** `usuarios` valida y persiste la identidad; `auth` resuelve la ficha, almacena la identidad en la invitación y envía el enlace.
- **RN/SEC relacionadas:** `RN-DAT`, `RN-PRS-05`, `RN-USR` de usuarios; invitación según `auth`.
- **Dependencias:** `usuarios`, propietario de la persistencia; `auth`, propietario de la invitación.

## SCR-ADM-04 — Importar catálogos masivos

- **User Flows de origen:** `UF-ADM-01`, `UF-ADM-04`.
- **Actor:** Administrador global.
- **Objetivo:** validar y confirmar cargas Excel de proyectos, semilleros o equipos.
- **Precondiciones:** cuenta activa con `importacion.ejecutar` global.
- **Información visible:** tipo de catálogo; para equipos, unidad destino seleccionada; resumen de validación (nuevos, actualizados, desactivados, errores) con el resultado por fila; historial de cargas con sus totales.
- **Entradas:** archivo Excel; catálogo (`PROYECTOS`, `SEMILLEROS`, `EQUIPOS`); unidad destino solo para equipos.
- **Acciones:** cargar y validar; revisar el resultado por fila; confirmar la carga confirmable; consultar el historial y el detalle por fila.
- **Validaciones visibles:** formato, columnas y campos obligatorios; estados `ACTIVO`/`INACTIVO` en investigación; placas y descripciones en equipos; duplicados dentro del archivo; costo leído y descartado.
- **Estados:** selección de catálogo (y unidad para equipos), validando, resultado revisable, confirmable o no confirmable, confirmando, confirmada.
- **Errores y respuestas:** al menos una fila en error → no confirmable, sin escritura parcial (`RN-IMP-06`); archivo ilegible, columnas faltantes o catálogo inválido → corrección; falta de unidad en equipos → corrección; carga ya confirmada → rechazo.
- **Resultado/navegación:** al confirmar, las entidades se escriben en el módulo propietario sin tocar vinculaciones (`RN-IMP-05`) y sin deshabilitar equipos (`RN-IMP-09`); el resultado por fila se conserva para corregir sin reprocesar.
- **Backend:** valida sin escribir; confirma en transacción del propietario; registra trazabilidad con actor, fecha, catálogo, archivo y totales (`RN-IMP-08`).
- **RN/SEC relacionadas:** `RN-IMP-01` a `RN-IMP-12`; `RN-IMP-02`, `RN-IMP-06` de resources.
- **Dependencias:** `researchs` y `recursos`, propietarios de las entidades y sus validaciones.

## SCR-ADM-05 — Consultar auditoría administrativa

- **Origen:** contrato §5 (sin flujo propio; fuente: contrato y `RN-AUD`).
- **Actor:** Administrador global.
- **Objetivo:** consultar el registro de operaciones administrativas.
- **Precondiciones:** cuenta activa con `unidades.administrar` global.
- **Información visible:** actor, acción, entidad, identificador, momento y cambios cuando corresponda; filtros por entidad, identificador, actor, acción y rango de fechas.
- **Entradas:** filtros de consulta. Ninguna escritura: no existe endpoint que modifique la auditoría.
- **Acciones:** filtrar y paginar el registro.
- **Validaciones visibles:** ninguna de negocio; es consulta de solo lectura.
- **Estados:** consultando, registro disponible.
- **Errores y respuestas:** sin sesión válida se resuelve en auth; los registros se conservan aunque la cuenta o entidad se desactive (`RN-AUD-04`) y no se modifican para reflejar valores actuales (`RN-AUD-05`).
- **Resultado/navegación:** permanece; el actor se identifica por cuenta, sin duplicar identidades (`RN-AUD-07`).
- **Backend:** lectura paginada ordenada por creación descendente; jamás expone contraseñas, secretos, tokens ni claves (`SEC-AUD-03` de auth).
- **RN/SEC relacionadas:** `RN-AUD-01` a `RN-AUD-07`; `SEC-AUD-03` de auth.
- **Dependencias:** ninguna externa más allá de la autorización.

## Cobertura de todos los User Flows

| User Flow revisado | Superficie |
|---|---|
| UF-ADM-01 | SCR-ADM-04 |
| UF-ADM-02 | SCR-ADM-03 |
| UF-ADM-03 | SCR-ADM-03 |
| UF-ADM-04 | SCR-ADM-04 |

Las superficies de contrato sin flujo propio (§2 unidades/cargos, §3 permisos, §5 auditoría) se especifican en `SCR-ADM-01`, `SCR-ADM-02` y `SCR-ADM-05` a partir del contrato y sus reglas; no se inventan flujos para cubrirlas.

## Ambigüedades y límites de las fuentes

1. **Mecanismo de selección de unidad/cargo/permiso en formularios:** las fuentes no definen si es lista o buscador. No se inventa un componente de búsqueda.
2. **Destino tras guardar o confirmar:** ningún flujo fija a dónde continúa el Administrador. No se decide aquí.
3. **Retornos y cancelaciones:** ninguna fuente define botones de volver o cancelar en estas superficies; no se agregan.
4. **Contenido del historial de importaciones:** el contrato fija filtros (catálogo, fechas) y detalle por fila; no se agregan otros criterios.

## Decisiones aplicadas a las ambigüedades de prioridad alta

- `SCR-ADM-03` agrupa alta de Usuario y ficha de Personal con su invitación en una sola superficie, porque `UF-ADM-03` encadena ficha e invitación en el mismo recorrido y `UF-ADM-02` prevé continuar a invitar tras el alta.
- Las superficies sin flujo propio no generan flujos inventados: se documentan desde el contrato y sus reglas, y la matriz anterior solo mapea los cuatro `UF-ADM` reales.
- La auditoría no tiene acciones de escritura en ninguna superficie, porque el contrato no expone ningún endpoint que la modifique.

## Documentos relacionados

- [Flujos de usuario](user-flow.md): los cuatro flujos que originan estas pantallas.
- [Reglas de negocio](business-rules.md): `RN-UNI`, `RN-PER`, `RN-AUD`, `RN-IMP`, `RN-HAB`.
- [Modelo de datos](data-model.md): unidades, cargos, auditoría e importaciones.
- [Navegación funcional](screen-flow.md): cómo se conectan estas cinco pantallas entre sí y con auth, usuarios, researchs y recursos.
