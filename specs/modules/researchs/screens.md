# Especificación funcional de pantallas — Researchs

## Alcance y fuentes

Derivado exclusivamente de [user-flow.md](user-flow.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md) y [overview.md](overview.md). La navegación se detalla en [screen-flow.md](screen-flow.md). Los identificadores corresponden a superficies funcionales; no prescriben páginas independientes, rutas HTTP ni componentes.

No se amplían reglas, datos, contratos ni flujos. Los estados de procesamiento describen la espera del resultado de una acción existente, no operaciones nuevas. No se especifican estilos, disposición visual, textos literales de error ni códigos API.

**Fuera de alcance de este documento:** las vinculaciones propias del Usuario titular (viven en `SCR-USR-05`, ya cerrada); la creación masiva por importación (la orquesta `administration`, aquí solo el estado resultante en los catálogos); cualquier asociación de proyecto o semillero con un laboratorio — en este sistema se asocian a personas, no limitan dónde puede reservar el usuario.

## Criterios comunes

- **Actor y ámbito:** Administrador con alcance global en todas las superficies (`RN-INV-10`, `RN-INV-15`, `RN-ACT-04`). El Técnico no administra estos catálogos ni vinculaciones ajenas.
- **Backend:** valida alcance, existencia y reglas de combinación en cada operación. Desactivar conserva registro, vinculaciones e historial (`RN-INV-05`, `RN-ACT-03`).
- **Perfil vs. vinculación:** el perfil describe la situación de la persona; la vinculación la asocia a una entidad concreta. Tener un perfil no habilita a reservar (`RN-INV-16`).
- **Selección, nunca texto libre:** las entidades se seleccionan de catálogos existentes; los códigos son persistentes y no se crean desde el perfil (`RN-INV-06`).

## SCR-INV-01 — Consultar catálogos de proyectos y semilleros

- **Origen:** contrato §2 (sin flujo propio de consulta; fuente: contrato y `RN-INV-06`).
- **Actor:** Administrador global.
- **Objetivo:** consultar los catálogos completos, incluidos deshabilitados, con filtros.
- **Precondiciones:** cuenta activa con alcance global.
- **Información visible:** código, nombre y estado de cada proyecto y semillero.
- **Entradas:** filtros por estado y búsqueda. La creación y actualización masiva llegan por importación, no por formulario.
- **Acciones:** filtrar, paginar, habilitar/deshabilitar.
- **Validaciones visibles:** un elemento deshabilitado no se selecciona en nuevas vinculaciones ni como contexto de reserva nueva.
- **Estados:** consultando, listado disponible, estado cambiado.
- **Errores y respuestas:** sesión no válida se resuelve en auth; deshabilitar conserva vinculaciones y referencias históricas (`RN-IMP-07` de administration).
- **Resultado/navegación:** permanece; el catálogo del Usuario (`usuarios` §4.1) refleja los habilitados.
- **Backend:** lectura paginada; el cambio de estado conserva historial.
- **RN/SEC relacionadas:** `RN-INV-06`, `RN-INV-08`; `RN-IMP-07` de administration.
- **Dependencias:** `administration`, que escribe estos catálogos por importación.

## SCR-INV-02 — Administrar actividades institucionales

- **Origen:** contrato §3; `UF-INV-01` (paso 4).
- **Actor:** Administrador global.
- **Objetivo:** crear, modificar, activar y desactivar actividades.
- **Precondiciones:** cuenta activa con alcance global.
- **Información visible:** nombre, dependencia y estado de cada actividad.
- **Entradas:** nombre y dependencia obligatorios; acción de estado.
- **Acciones:** crear; modificar datos; activar; desactivar.
- **Validaciones visibles:** nombre y dependencia obligatorios (`RN-ACT-01`); solo activas sirven para reservas nuevas (`RN-ACT-02`).
- **Estados:** captura, guardando, corrección requerida, cambio aplicado.
- **Errores y respuestas:** datos faltantes → sin guardar; desactivar conserva registro y referencias (`RN-ACT-03`).
- **Resultado/navegación:** permanece con confirmación.
- **Backend:** valida y persiste; no altera reservas que ya la usaron como contexto (`RN-CTX-07` de reservations).
- **RN/SEC relacionadas:** `RN-ACT-01` a `RN-ACT-04`.
- **Dependencias:** `reservations`, que conserva las copias históricas.

## SCR-INV-03 — Administrar el catálogo de perfiles

- **Origen:** contrato §4; `UF-INV-01` (paso 5).
- **Actor:** Administrador global.
- **Objetivo:** crear, modificar, habilitar y desactivar perfiles.
- **Precondiciones:** cuenta activa con alcance global.
- **Información visible:** nombre, descripción y estado de cada perfil.
- **Entradas:** nombre, descripción, acción de estado.
- **Acciones:** crear; modificar; habilitar; deshabilitar.
- **Validaciones visibles:** solo el catálogo habilitado se ofrece a los Usuarios; deshabilitar impide nuevas asignaciones y conserva las existentes (`RN-INV-14`, `RN-INV-05`).
- **Estados:** captura, guardando, corrección requerida, cambio aplicado.
- **Errores y respuestas:** datos faltantes → sin guardar.
- **Resultado/navegación:** permanece; asignar o retirar no reescribe contextos históricos (`RN-INV-13`).
- **Backend:** valida (`RN-INV-15`) y persiste con identificadores persistentes (`RN-INV-12`).
- **RN/SEC relacionadas:** `RN-INV-12` a `RN-INV-16`, `RN-INV-05`.
- **Dependencias:** `usuarios`, que ofrece el catálogo habilitado a sus titulares.

## SCR-INV-04 — Gestionar vinculaciones ajenas

- **Origen:** `UF-INV-01` (pasos 1–3).
- **Actor:** Administrador global.
- **Objetivo:** crear, desactivar y reactivar vinculaciones de otro Usuario.
- **Precondiciones:** cuenta activa con alcance global; el Usuario y la entidad existen para crear.
- **Información visible:** vinculaciones del Usuario consultado, activas e inactivas, agrupadas por tipo.
- **Entradas:** Usuario, tipo (proyectos o semilleros), entidad; acción de desactivar.
- **Acciones:** crear o reactivar vinculación; desactivar.
- **Validaciones visibles:** entidad existente y habilitada (`RN-INV-08`); sin duplicar activas; con inactiva previa se reactiva la misma fila (`RN-INV-11`).
- **Estados:** consulta por Usuario, creando, desactivando, confirmación, advertencia de última vinculación (`RN-USR-11` de usuarios).
- **Errores y respuestas:** duplicada activa → rechazo; entidad inexistente o deshabilitada → rechazo; desactivar conserva historial; si era la última activa se avisa sin bloquear (`RN-USR-11`).
- **Resultado/navegación:** permanece; las vinculaciones propias del titular se gestionan en `SCR-USR-05`.
- **Backend:** valida y persiste; registra la operación administrativa.
- **RN/SEC relacionadas:** `RN-INV-01`, `RN-INV-04`, `RN-INV-05`, `RN-INV-08`, `RN-INV-09`, `RN-INV-10`, `RN-INV-11`; `RN-USR-11` de usuarios; `RN-HAB-04` de administration.
- **Dependencias:** `usuarios`, propietario de las vinculaciones propias; `auth`, que autoriza el alcance global.

## Cobertura de todos los User Flows

| User Flow revisado | Superficie |
|---|---|
| UF-INV-01 | SCR-INV-01, SCR-INV-02, SCR-INV-03, SCR-INV-04 |

`UF-INV-01` es el único flujo del módulo y cubre las cuatro superficies. Las vinculaciones propias no tienen superficie aquí: viven en `SCR-USR-05`.

## Ambigüedades y límites de las fuentes

1. **Mecanismo de selección de Usuario y entidades:** las fuentes no definen si es lista o buscador. No se inventa un componente de búsqueda.
2. **Destino tras guardar:** ningún flujo lo fija. No se decide aquí.
3. **Retornos y cancelaciones:** ninguna fuente define botones de volver o cancelar en estas superficies; no se agregan.
4. **Presentación del historial de vinculaciones:** se muestran activas e inactivas agrupadas; no se define otro orden ni agrupación.

## Decisiones aplicadas a las ambigüedades de prioridad alta

- Catálogos, actividades, perfiles y vinculaciones ajenas son cuatro superficies separadas porque tienen actores, validaciones y ciclos distintos, aunque compartan el mismo actor global.
- La importación no tiene superficie aquí: sus pantallas viven en `administration` y este documento solo refleja su efecto en los catálogos.
- Ninguna superficie asocia proyectos o semilleros con laboratorios: las fuentes asocian personas con entidades, y esa restricción se deja explícita en vez de suponerla.

## Documentos relacionados

- [Flujos de usuario](user-flow.md): el flujo que origina estas pantallas.
- [Reglas de negocio](business-rules.md): `RN-INV`, `RN-ACT`.
- [Modelo de datos](data-model.md): catálogos, perfiles, actividades y vinculaciones.
- [Navegación funcional](screen-flow.md): cómo se conectan estas cuatro superficies entre sí y con usuarios, administration y reservations.
