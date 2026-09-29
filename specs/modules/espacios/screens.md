# Especificación funcional de pantallas — Espacios

## Alcance y fuentes

Derivado exclusivamente de [user-flow.md](user-flow.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md) y [overview.md](overview.md). La navegación se detalla en [screen-flow.md](screen-flow.md). Los identificadores corresponden a superficies funcionales; no prescriben páginas independientes, rutas HTTP ni componentes.

No se amplían reglas, datos, contratos ni flujos. Los estados de procesamiento describen la espera del resultado de una acción existente, no operaciones nuevas. No se especifican estilos, disposición visual, textos literales de error ni códigos API.

**Fuera de alcance de este documento:** el horario (no existe por espacio: es el de la unidad, de `resources`); la disponibilidad temporal (la resuelve `reservations`); el uso del espacio durante una reserva (`UF-ESP-14`, flujo de `reservations`).

## Criterios comunes

- **Actor y ámbito:** el Técnico administra solo su unidad (`RN-ESP-03`); el Administrador, cualquiera; el Usuario consulta (`UF-ESP-12`, `UF-ESP-13`).
- **Backend:** valida permiso, pertenencia a la unidad y restricciones de cada tipo en cada operación. La creación con recursos y campos es atómica.
- **Horario heredado:** ningún formulario pide horario; el detalle lo muestra como lectura de la unidad (`RN-ESP-DIS-02`).
- **Historia intacta:** editar, deshabilitar o reordenar nunca reescribe reservas pasadas (`RN-ESP-CAM-05`, `RN-ESP-HAB-02`, `RN-ESP-HAB-04`).
- **Selección, nunca texto libre:** recursos y opciones se seleccionan de catálogos existentes; los cinco tipos de campo son cerrados (`RN-ESP-CAM-02`).

## SCR-ESP-01 — Registrar, editar y habilitar espacios

- **User Flows de origen:** `UF-ESP-01`, `UF-ESP-02`, `UF-ESP-10`, `UF-ESP-11`.
- **Actores:** Técnico de la unidad o Administrador; Usuario solo consulta el resultado.
- **Objetivo:** crear espacios con capacidad obligatoria, modificar sus datos y cambiar su habilitación con advertencia de impacto.
- **Precondiciones:** cuenta autenticada; para administrar, permiso sobre la unidad.
- **Información visible:** listado con filtros; detalle con horario heredado; conteo previo de reservas a cancelar.
- **Entradas:** nombre, ubicación, capacidad mayor que cero, descripción; recursos y campos opcionales al crear; confirmación explícita al deshabilitar con reservas futuras.
- **Acciones:** crear; editar datos; habilitar; deshabilitar con confirmación.
- **Validaciones visibles:** capacidad obligatoria y mayor que cero (`RN-ESP-02`); nombre duplicado; sin confirmar no hay deshabilitación con cancelaciones (`RN-ESP-HAB-05`).
- **Estados:** listado, captura, guardando, corrección requerida, advertencia de impacto, confirmación pendiente, cambio aplicado.
- **Errores y respuestas:** datos inválidos → sin crear; duplicado → corrección; sin confirmar → sin cambios ni reservas tocadas; deshabilitar conserva todo y cierra nuevas reservas (`RN-ESP-HAB-01`, `RN-ESP-HAB-02`).
- **Resultado/navegación:** permanece con confirmación; el espacio usa el horario de su unidad sin copiarlo.
- **Backend:** valida y persiste; las cancelaciones las aplica `reservations` (`RN-CAN-04`).
- **RN/SEC relacionadas:** `RN-ESP-01`, `RN-ESP-02`, `RN-ESP-03`; `RN-ESP-HAB-01`, `RN-ESP-HAB-02`, `RN-ESP-HAB-04`, `RN-ESP-HAB-05`; `RN-ESP-DIS-01`, `RN-ESP-DIS-02`; `RN-DES-06`, `RN-DES-07` de resources.
- **Dependencias:** `resources`, propietaria de la configuración horaria de la unidad; `reservations`, que cancela futuras al deshabilitar.

## SCR-ESP-02 — Asociar y retirar recursos

- **User Flows de origen:** `UF-ESP-03`, `UF-ESP-04`.
- **Actor:** Técnico de la unidad o Administrador.
- **Objetivo:** asociar recursos al espacio y retirar asociaciones.
- **Precondiciones:** el espacio existe; los recursos existen en `recursos`.
- **Información visible:** asociados vigentes; catálogo disponible para asociar.
- **Entradas:** selección de uno o más recursos; confirmación de retiro.
- **Acciones:** asociar; retirar con confirmación.
- **Validaciones visibles:** misma unidad (`RN-ESP-REC-06`); sin otra asociación activa (`RN-ESP-REC-07`); asociar no crea recursos ni implica disponibilidad (`RN-ESP-REC-02`, `RN-ESP-REC-04`).
- **Estados:** consultando, asociando, confirmación de retiro, asociación registrada o retirada.
- **Errores y respuestas:** recurso de otra unidad o ya asociado → rechazo; retirar deshabilita la fila, no la borra.
- **Resultado/navegación:** permanece; las reservas históricas conservan sus referencias.
- **Backend:** valida pertenencia y asociación única; conserva historial.
- **RN/SEC relacionadas:** `RN-ESP-REC-01` a `RN-ESP-REC-07`.
- **Dependencias:** `recursos`, propietario del catálogo (patrón reutilizado de `FE-12`).

## SCR-ESP-03 — Configurar campos adicionales

- **User Flows de origen:** `UF-ESP-05`, `UF-ESP-06`, `UF-ESP-07`, `UF-ESP-08`, `UF-ESP-09`.
- **Actor:** Técnico de la unidad o Administrador.
- **Objetivo:** definir campos con sus opciones, editarlos, reordenarlos y deshabilitarlos.
- **Precondiciones:** el espacio existe o está en creación.
- **Información visible:** campos con tipo, obligatoriedad, orden y estado; opciones de los de selección.
- **Entradas:** nombre, tipo (uno de los cinco cerrados), obligatoriedad, orden, habilitación; valores y orden de opciones.
- **Acciones:** agregar campo; editar; configurar opciones; reordenar; habilitar/deshabilitar.
- **Validaciones visibles:** definición mínima completa (`RN-ESP-CAM-02`); selección sin opciones válidas no queda habilitada; el reorden conserva valores históricos.
- **Estados:** captura, guardando, corrección requerida, campo guardado, reordenado, deshabilitado.
- **Errores y respuestas:** definición incompleta → sin guardar; un campo usado nunca se elimina, se deshabilita (`RN-ESP-CAM-05`).
- **Resultado/navegación:** permanece; las nuevas reservas usan la configuración vigente.
- **Backend:** valida y persiste; conserva interpretación histórica.
- **RN/SEC relacionadas:** `RN-ESP-CAM-01` a `RN-ESP-CAM-05`.
- **Dependencias:** `reservations`, que exige los obligatorios al reservar.

## SCR-ESP-04 — Consultar espacios

- **User Flows de origen:** `UF-ESP-12`, `UF-ESP-13`.
- **Actor:** Usuario autenticado (también Técnico y Administrador).
- **Objetivo:** listar con filtros y consultar el detalle consolidado.
- **Precondiciones:** cuenta autenticada.
- **Información visible:** información general, capacidad, estado, unidad, horario heredado, asociados y campos habilitados.
- **Entradas:** filtros de listado. Ninguna escritura.
- **Acciones:** filtrar, paginar, ver detalle.
- **Validaciones visibles:** el Usuario solo ve habilitados; el Técnico, también los deshabilitados de su unidad.
- **Estados:** consultando, listado o detalle disponible.
- **Errores y respuestas:** sesión no válida se resuelve en auth.
- **Resultado/navegación:** permanece; el detalle enlaza a las superficies de gestión según el rol.
- **Backend:** lectura con visibilidad por rol; el horario es lectura de la unidad.
- **RN/SEC relacionadas:** `RN-ESP-DIS-01`, `RN-ESP-DIS-02`, `RN-ESP-DIS-03`.
- **Dependencias:** `resources`, propietaria del horario mostrado.

## Cobertura de todos los User Flows

| User Flow revisado | Superficie |
|---|---|
| UF-ESP-01 | SCR-ESP-01 |
| UF-ESP-02 | SCR-ESP-01 |
| UF-ESP-03 | SCR-ESP-02 |
| UF-ESP-04 | SCR-ESP-02 |
| UF-ESP-05 | SCR-ESP-03 |
| UF-ESP-06 | SCR-ESP-03 |
| UF-ESP-07 | SCR-ESP-03 |
| UF-ESP-08 | SCR-ESP-03 |
| UF-ESP-09 | SCR-ESP-03 |
| UF-ESP-10 | SCR-ESP-01 |
| UF-ESP-11 | SCR-ESP-01 |
| UF-ESP-12 | SCR-ESP-04 |
| UF-ESP-13 | SCR-ESP-04 |
| UF-ESP-14 | Sin pantalla propia: efecto en el módulo `reservations` |

## Ambigüedades y límites de las fuentes

1. **Mecanismo de selección de recursos y catálogos:** las fuentes no definen si es lista o buscador. No se inventa un componente de búsqueda (mismo criterio que `FE-12`).
2. **Destino tras guardar o confirmar:** ningún flujo lo fija. No se decide aquí.
3. **Retornos y cancelaciones:** ninguna fuente define botones de volver o cancelar en estas superficies; no se agregan.
4. **Presentación del horario heredado:** se muestra como lectura; no se define formato ni posición.

## Decisiones aplicadas a las ambigüedades de prioridad alta

- Registro, edición y estado comparten `SCR-ESP-01` porque operan sobre la misma ficha del espacio; consulta tiene superficie propia (`SCR-ESP-04`) porque sus actores y permisos difieren (Usuario incluido).
- Los cinco flujos de campos se agrupan en `SCR-ESP-03` porque comparten la misma configuración del espacio.
- `UF-ESP-14` queda explícitamente sin superficie por ocurrir en `reservations`, igual que `UF-USR-11`.

## Documentos relacionados

- [Flujos de usuario](user-flow.md): los catorce flujos que originan estas pantallas.
- [Reglas de negocio](business-rules.md): `RN-ESP`, `RN-ESP-REC`, `RN-ESP-CAM`, `RN-ESP-DIS`, `RN-ESP-HAB`.
- [Modelo de datos](data-model.md): espacios, asociaciones y campos.
- [Navegación funcional](screen-flow.md): cómo se conectan estas cuatro superficies entre sí y con resources y reservations.
