# Especificación funcional de pantallas — Resources

## Alcance y fuentes

Derivado exclusivamente de [user-flow.md](user-flow.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md) y [overview.md](overview.md). La navegación se detalla en [screen-flow.md](screen-flow.md). Los identificadores corresponden a superficies funcionales; no prescriben páginas independientes, rutas HTTP ni componentes.

No se amplían reglas, datos, contratos ni flujos. Los estados de procesamiento describen la espera del resultado de una acción existente, no operaciones nuevas. No se especifican estilos, disposición visual, textos literales de error ni códigos API.

**Fuera de alcance de este documento:** la disponibilidad temporal de un recurso para una reserva (la calcula `reservations`, aquí solo se consulta existencia, clasificación y estado); las vinculaciones y catálogos de investigación (`researchs`); la carga masiva como orquestación (`UF-ADM-04` de `administration` — aquí solo las validaciones propias de equipos que esa superficie muestra).

## Criterios comunes

- **Actor y ámbito:** el Técnico solo opera sobre su unidad (`RN-ROL-01`); el Administrador tiene alcance global (`RN-ROL-03`). El Técnico no crea ni elimina equipos, pero edita los de su unidad con `recursos.editar_equipos` (`RN-EQP-09`).
- **Backend:** valida permiso, pertenencia a la unidad y restricciones de cada tipo en cada operación. La creación de raíz y especialización es atómica.
- **Identidad por PK, no por nombre:** el nombre de un recurso puede repetirse; la identidad es su clave primaria (`RN-REC-06`).
- **Habilitado vs. operativo:** `recursos.recursos.habilitado` y `recursos.equipos.estado` son condiciones independientes (`RN-EQP-04`); se cambian por vías distintas.
- **Selección, nunca texto libre:** la unidad responsable y la categoría se seleccionan de catálogos existentes.

## SCR-REC-01 — Registrar y consultar recursos

- **User Flows de origen:** `UF-REC-01`, `UF-REC-02`, `UF-REC-03`, `UF-REC-04`, `UF-REC-05`.
- **Actores:** Técnico de la unidad (mobiliario y otros) o Administrador (también equipos); cualquier cuenta autenticada consulta.
- **Objetivo:** registrar mobiliario, otros recursos y equipos, y consultar el catálogo con su detalle.
- **Precondiciones:** cuenta autenticada; para crear, permiso sobre la unidad (`recursos.administrar_equipos` global para equipos).
- **Información visible:** catálogo con tipo, unidad, habilitación y estado operativo; detalle consolidado con la especialización; filtro `reservable` que excluye acreditados (`RN-REC-11`).
- **Entradas:** unidad responsable, tipo, datos generales y especializados (placa, nombre del equipo, categoría, datos de inventario).
- **Acciones:** registrar mobiliario u otro; registrar equipo (solo Administrador o importación); consultar y filtrar el catálogo; ver el detalle.
- **Validaciones visibles:** datos obligatorios por tipo; unidad existente y autorizada; placa e identidad por PK.
- **Estados:** captura, guardando, corrección requerida, registro creado; consulta con filtros.
- **Errores y respuestas:** datos faltantes o tipo incompatible → sin crear; unidad ajena o sin permiso → rechazo; el Técnico no crea equipos.
- **Resultado/navegación:** el recurso queda en el catálogo de su unidad; permanece con filtros y detalle.
- **Backend:** crea raíz y especialización en una transacción; revierte ambas si algo falla.
- **RN/SEC relacionadas:** `RN-REC-01`, `RN-REC-02`, `RN-REC-03`, `RN-REC-06`, `RN-REC-07`, `RN-REC-11`; `RN-EQP-01`, `RN-EQP-02`, `RN-EQP-03`, `RN-EQP-08`, `RN-EQP-09`, `RN-EQP-11`; `RN-MOB-01` a `RN-MOB-03`; `RN-OTR-01` a `RN-OTR-03`; `RN-ROL-01` a `RN-ROL-03`.
- **Dependencias:** `unidadOrganizacional`, propietaria de las unidades; `auth`, que autoriza cada operación.

## SCR-REC-02 — Editar, habilitar y reasignar recursos

- **User Flows de origen:** `UF-REC-06`, `UF-REC-07`, `UF-REC-08`, `UF-REC-09`, `UF-REC-10`, `UF-REC-12`.
- **Actores:** Técnico de la unidad o Administrador.
- **Objetivo:** modificar datos, cambiar habilitación con advertencia de impacto, y reasignar la unidad responsable.
- **Precondiciones:** el recurso existe; permiso sobre su unidad (`recursos.editar_equipos` para equipos del Técnico).
- **Información visible:** datos editables; conteo previo de reservas a cancelar y a retirar; unidad responsable vigente.
- **Entradas:** datos generales y especializados; acción de habilitar/deshabilitar con confirmación; nueva unidad.
- **Acciones:** editar; habilitar; deshabilitar con confirmación; reasignar unidad.
- **Validaciones visibles:** campos admitidos por tipo; sin crear ni eliminar el registro ni cambiar su unidad por esta vía (salvo la reasignación explícita con su permiso); la deshabilitación con reservas `PRINCIPAL` futuras exige confirmación explícita (`RN-DES-06`), sin ella no se ejecuta.
- **Estados:** captura, guardando, advertencia de impacto con conteo, confirmación pendiente, cambio aplicado.
- **Errores y respuestas:** validación fallida → sin cambios; sin confirmación → sin cambios ni reservas tocadas; reasignación a unidad incompatible → rechazo.
- **Resultado/navegación:** el recurso conserva registro, relaciones e historial (`RN-DES-01`, `RN-REC-08`); las reservas afectadas las trata `reservations` (`RN-CAN-04`, `RN-CAN-05`), no esta pantalla.
- **Backend:** valida, aplica en transacción, conserva historial y trazabilidad del cambio de unidad.
- **RN/SEC relacionadas:** `RN-EQP-04`, `RN-EQP-05`, `RN-EQP-06`, `RN-EQP-09`, `RN-EQP-11`; `RN-DES-01` a `RN-DES-07`; `RN-REC-07`, `RN-REC-08`, `RN-REC-09`; `RN-MOB-05`; `RN-OTR-05`.
- **Dependencias:** `reservations`, que aplica cancelaciones y retiros; `auth`, que autoriza.

## SCR-REC-03 — Configurar el laboratorio

- **User Flow de origen:** `UF-REC-13`.
- **Actores:** Técnico de la unidad; Administrador sobre cualquier unidad.
- **Objetivo:** ver y modificar la configuración de reservas de la unidad.
- **Precondiciones:** cuenta autenticada; `laboratorios.configurar` sobre la unidad.
- **Información visible:** aceptación de reservas, horario y días, antelación, aprobación automática, anticipación del recordatorio, notificación por correo, visibilidad y tipos de reserva habilitados.
- **Entradas:** cada valor configurable; lista de tipos ofrecidos.
- **Acciones:** guardar configuración; definir tipos; ajustar visibilidad.
- **Validaciones visibles:** cierre posterior a apertura; antelación y anticipación mayores que cero; lista de tipos vacía deja la unidad sin reservas posibles (`RN-TIP-06` de reservations).
- **Estados:** consulta vigente, captura, guardando, corrección requerida, configuración guardada.
- **Errores y respuestas:** horario inválido o valores no positivos → sin guardar; unidad ajena al Técnico → rechazo.
- **Resultado/navegación:** los valores rigen desde ese momento para nuevas validaciones; el cambio de horario versiona el anterior (`RN-LAB-08`) sin reinterpretar reservas aprobadas.
- **Backend:** valida cada valor; versiona el horario en el histórico; audita según corresponda.
- **RN/SEC relacionadas:** `RN-LAB-01` a `RN-LAB-08`; `RN-TIP-05`, `RN-TIP-06`, `RN-HOR-07`, `RN-DIS-07`, `RN-DIS-09`, `RN-DIS-10`, `RN-DIS-11` de reservations; `RN-ESP-DIS-02` de espacios; `RN-REC-01` de notificaciones.
- **Dependencias:** `reservations`, que valida con la configuración vigente; `unidadOrganizacional`, propietaria de la unidad.

## SCR-REC-04 — Validaciones de equipos en importación masiva

- **Origen:** `UF-ADM-04` de `administration` (orquestación) con validaciones propias `RN-IMP-02`, `RN-IMP-03`, `RN-IMP-06` de este módulo. Sin superficie propia de carga: la carga, el resumen y la confirmación viven en `SCR-ADM-04`.
- **Objetivo:** documentar qué muestra esa superficie por cuenta de este módulo, sin redefinirla.
- **Información visible (en `SCR-ADM-04`):** placa y descripción obligatorias; bodega, centro de costos, fecha de inicio opcionales; costo leído y descartado; duplicados de placa; resultado por fila.
- **Acciones:** ninguna propia; la confirmación la ejecuta `administration`.
- **Validaciones visibles:** placa obligatoria y válida; descripción obligatoria; fecha válida; sin duplicados en la planilla.
- **Estados:** los de `SCR-ADM-04`; una placa existente actualiza, no duplica.
- **Errores y respuestas:** fila sin placa o inválida → fila en error y carga no confirmable; la importación nunca deshabilita (`RN-IMP-07`).
- **Resultado/navegación:** equipos creados o actualizados en su unidad; reservas históricas intactas (`RN-IMP-04`).
- **RN/SEC relacionadas:** `RN-IMP-02`, `RN-IMP-03`, `RN-IMP-06`, `RN-IMP-04`, `RN-IMP-07`, `RN-IMP-09`, `RN-IMP-11`.
- **Dependencias:** `administration`, propietaria de la orquestación y la confirmación.

## Cobertura de todos los User Flows

| User Flow revisado | Superficie |
|---|---|
| UF-REC-01 | SCR-REC-01 |
| UF-REC-02 | SCR-REC-01 |
| UF-REC-03 | SCR-REC-01 |
| UF-REC-04 | SCR-REC-01 |
| UF-REC-05 | SCR-REC-01 |
| UF-REC-06 | SCR-REC-02 |
| UF-REC-07 | SCR-REC-02 |
| UF-REC-08 | SCR-REC-02 |
| UF-REC-09 | SCR-REC-02 |
| UF-REC-10 | SCR-REC-02 |
| UF-REC-11 | Sin superficie: flujo módulo a módulo, no de persona |
| UF-REC-12 | SCR-REC-02 |
| UF-REC-13 | SCR-REC-03 |
| UF-ADM-04 (importación) | SCR-REC-04, por referencia a SCR-ADM-04 |

## Ambigüedades y límites de las fuentes

1. **Mecanismo de selección de unidad y categoría:** las fuentes no definen si es lista o buscador. No se inventa un componente de búsqueda.
2. **Destino tras guardar o confirmar:** ningún flujo lo fija. No se decide aquí.
3. **Retornos y cancelaciones:** ninguna fuente define botones de volver o cancelar en estas superficies; no se agregan.
4. **Contenido del selector de tipos de reserva:** proviene del catálogo de `reservations`; no se redefine aquí.

## Decisiones aplicadas a las ambigüedades de prioridad alta

- Registro y consulta comparten `SCR-REC-01` porque el alta nace del catálogo y vuelve a él; edición, estado y unidad comparten `SCR-REC-02` porque operan sobre el detalle ya consultado.
- La importación de equipos no tiene superficie propia: se documenta por referencia a la pantalla que sí la tiene (`SCR-ADM-04`), con solo las validaciones que este módulo aporta.
- `UF-REC-11` queda explícitamente sin superficie por ser comunicación entre módulos, no interacción de persona.

## Documentos relacionados

- [Flujos de usuario](user-flow.md): los trece flujos que originan estas pantallas.
- [Reglas de negocio](business-rules.md): `RN-LAB`, `RN-REC`, `RN-EQP`, `RN-MOB`, `RN-OTR`, `RN-ROL`, `RN-DES`, `RN-IMP`.
- [Modelo de datos](data-model.md): `recursos.recursos`, especializaciones y configuración de laboratorio.
- [Navegación funcional](screen-flow.md): cómo se conectan estas cuatro superficies entre sí y con administration, reservations y espacios.
