# Especificación funcional de pantallas — Usuarios

## Alcance y fuentes

Derivado exclusivamente de [user-flow.md](user-flow.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md) y [overview.md](overview.md). La navegación se detalla en [screen-flow.md](screen-flow.md). Los identificadores corresponden a superficies funcionales; no prescriben páginas independientes, rutas HTTP ni componentes.

No se amplían reglas, datos, contratos ni flujos. Los estados de procesamiento describen la espera del resultado de una acción existente, no operaciones nuevas. No se especifican estilos, disposición visual, textos literales de error ni códigos API.

**Fuera de alcance de este documento:** la creación y administración de identidades (`POST /api/usuarios`, `POST /api/personal` y sus operaciones asociadas) pertenece a los flujos `UF-ADM-02` y `UF-ADM-03` de `administration` — son operaciones de un actor administrativo sobre identidades ajenas, no de los once flujos `UF-USR` de este módulo, que son todos de autoservicio del propio Usuario. Sus pantallas se especifican cuando se cierre `screens.md` de `administration`, no aquí.

## Criterios comunes

- **Interfaz:** recoge las entradas descritas por cada flujo y comunica validaciones, resultados y advertencias de impacto en la superficie de origen; no requieren pantallas independientes.
- **Backend:** toma la identidad siempre de la sesión — ninguna pantalla envía `id_usuario` para identificarse (`SEC-AUTZ-03` de auth). Aplica `RN-DAT` en toda alta o edición y delega en `investigacion` la validación y persistencia de perfiles y vinculaciones, sin reimplementar sus reglas.
- **Correo:** en todas las pantallas de este módulo es un dato de solo lectura. Una vez existe cuenta asociada es inmutable y compartido con `auth.cuentas` (`RN-AUTH-ID-02`, `RN-AUTH-ID-03`, `RN-AUTH-ID-12` de auth); ninguna pantalla de este módulo lo ofrece como campo editable.
- **Bloqueo por actualización inicial pendiente:** mientras `perfil_actualizado_at` sea NULL, el Usuario solo puede completar su perfil, gestionar sus vinculaciones y cerrar sesión (`RN-USR-08`). Las operaciones de negocio de otros módulos rechazan con `403 PERFIL_INICIAL_PENDIENTE`; este documento no amplía esa regla ni dibuja esa pantalla, que pertenece al módulo que la aplica.
- **Selección, nunca texto libre:** proyectos y semilleros se seleccionan de catálogos existentes de `investigacion`; el Usuario no puede crearlos ni escribir su nombre o código (`RN-USR-10`).

## SCR-USR-01 — Completar actualización inicial

- **User Flows de origen:** `UF-USR-01`, `UF-USR-02`.
- **Actor:** Usuario, recién autorregistrado o recién activado por invitación.
- **Objetivo:** revisar o completar los datos personales y registrar al menos una vinculación académica o investigativa activa y válida, para levantar el bloqueo de la actualización inicial.
- **Precondiciones:** cuenta activa y autenticada; `perfil_actualizado_at` pendiente, sea por primer ingreso o por un intento anterior incompleto. El recorrido es el mismo sin importar si el origen fue autorregistro o invitación (`UF-USR-01` paso 1; `UF-USR-02` paso 1).
- **Información visible:** los cinco datos personales ya registrados en el alta (autorregistro o alta administrativa), listos para revisar o corregir; catálogo de perfiles académicos/investigativos habilitados; catálogo de proyectos y semilleros vigentes; formularios de pasantía y trabajo de grado; vinculaciones ya registradas en un intento anterior, si las hay; condición de completitud.
- **Entradas:** nombre, documento, teléfono, institución, dependencia; selección de perfiles académicos/investigativos; selección de proyecto o semillero del catálogo; universidad, nombre y correo del docente responsable (pasantía); nombre y correo del director (trabajo de grado).
- **Acciones:** confirmar o corregir datos personales; seleccionar perfiles; asociar un proyecto; asociar un semillero; registrar una pasantía; registrar un trabajo de grado; continuar cuando exista al menos una vinculación activa y válida.
- **Validaciones visibles:** los cinco datos personales obligatorios, no vacíos ni compuestos solo de espacios; documento y teléfono únicos; al menos una vinculación activa y válida antes de poder continuar.
- **Estados:** revisión de datos precargados, selección de vinculaciones, verificación en `investigacion`, corrección requerida, sin vinculación válida todavía (con indicación de qué falta), actualización inicial completada.
- **Errores y respuestas:** dato obligatorio vacío o inválido, o documento/teléfono duplicado → corrección sin avanzar; ninguna vinculación activa y válida → no se registra `perfil_actualizado_at`, se indica qué completar; una vinculación rechazada por `investigacion` → esa vinculación no se registra, el resto del progreso se conserva.
- **Resultado/navegación:** al completarse, se registra `perfil_actualizado_at` y se levanta el bloqueo de `RN-USR-08`; el Usuario continúa a las operaciones ya autorizadas del módulo que corresponda — la fuente no fija cuál (igual que ya lo deja abierto `auth` para el destino tras iniciar sesión). Si la persona abandona antes de terminar, los datos y vinculaciones ya registrados se conservan y el mismo recorrido se retoma en el siguiente ingreso, sin plazo de caducidad.
- **Backend:** valida los datos personales y su unicidad; consulta y delega en `investigacion` la validación y persistencia de perfiles y vinculaciones; verifica que exista al menos una activa y válida; registra `perfil_actualizado_at` solo cuando ambas condiciones se cumplen.
- **RN/SEC relacionadas:** `RN-USR-07`, `RN-USR-08`, `RN-USR-09`, `RN-USR-10`, `RN-DAT-01`, `RN-DAT-02`, `RN-DAT-03`; `RN-AUTH-SES-04` de auth, que conduce aquí.
- **Dependencias:** `investigacion`, para el catálogo de perfiles, proyectos y semilleros y la validación de pasantías y trabajos de grado; `auth`, que conduce a esta pantalla y consulta su resultado.

## SCR-USR-02 — Ver mi perfil

- **User Flow de origen:** `UF-USR-03`.
- **Actor:** Usuario.
- **Objetivo:** consultar la información consolidada del propio perfil.
- **Precondiciones:** cuenta autenticada.
- **Información visible:** los cinco datos personales, correo de solo lectura, condición de la actualización inicial, perfiles académicos/investigativos vigentes y vinculaciones (proyectos, semilleros, pasantías, trabajos de grado) con su estado.
- **Entradas:** ninguna.
- **Acciones:** acceder a la edición de datos personales, a la actualización de perfiles y a la gestión de vinculaciones.
- **Validaciones visibles:** ninguna; es una pantalla de consulta.
- **Estados:** cargando, información consolidada disponible.
- **Errores y respuestas:** sesión no válida interrumpe la consulta y conduce a auth (`UF-AUTH-05`); no es un error de este módulo.
- **Resultado/navegación:** permanece en esta pantalla; ofrece acceso a `SCR-USR-03`, `SCR-USR-04` y `SCR-USR-05`.
- **Backend:** obtiene la información funcional propia y consulta a `investigacion` los perfiles y vinculaciones que deban mostrarse.
- **RN/SEC relacionadas:** `RN-USR-01`.
- **Dependencias:** `investigacion`, para perfiles y vinculaciones.

## SCR-USR-03 — Editar mis datos personales

- **User Flow de origen:** `UF-USR-04`.
- **Actor:** Usuario.
- **Objetivo:** modificar los datos personales editables.
- **Precondiciones:** cuenta autenticada; existe un perfil funcional asociado. La fuente no restringe esta pantalla a que la actualización inicial esté completa: corregir datos personales es, en sí, una de las operaciones que `RN-USR-08` admite mientras está pendiente.
- **Información visible:** los cinco datos personales editables; correo, de solo lectura.
- **Entradas:** nombre, documento, teléfono, institución, dependencia.
- **Acciones:** guardar los cambios.
- **Validaciones visibles:** los cinco datos obligatorios, no vacíos; documento y teléfono únicos, sin considerar el propio registro como duplicado.
- **Estados:** captura, guardando, corrección requerida, cambios guardados.
- **Errores y respuestas:** dato obligatorio vacío o inválido → rechazo sin guardar; documento o teléfono ya registrado en otra identidad → rechazo sin guardar.
- **Resultado/navegación:** confirmación en la misma pantalla; retorno a `SCR-USR-02` con los datos actualizados.
- **Backend:** valida y persiste; aplica la unicidad de documento y teléfono excluyendo el propio registro.
- **RN/SEC relacionadas:** `RN-DAT-01`, `RN-DAT-02`, `RN-DAT-03`; `RN-AUTH-ID-02`, `RN-AUTH-ID-03`, `RN-AUTH-ID-12` de auth, por la inmutabilidad del correo.
- **Dependencias:** ninguna externa más allá de la validación común de datos personales.

## SCR-USR-04 — Actualizar mis perfiles académicos o investigativos

- **User Flow de origen:** `UF-USR-05`.
- **Actor:** Usuario.
- **Objetivo:** seleccionar los perfiles académicos o investigativos propios del catálogo habilitado.
- **Precondiciones:** cuenta autenticada; perfil funcional existente.
- **Información visible:** catálogo de perfiles habilitados (los deshabilitados no se ofrecen); selección vigente.
- **Entradas:** selección de uno o más perfiles del catálogo.
- **Acciones:** guardar la selección, que reemplaza el conjunto completo vigente.
- **Validaciones visibles:** la combinación seleccionada debe ser una que `investigacion` permita.
- **Estados:** catálogo cargando, selección en curso, guardando, combinación rechazada, selección guardada.
- **Errores y respuestas:** combinación no permitida por las reglas de `investigacion` → rechazo, sin aplicar el cambio.
- **Resultado/navegación:** el perfil consolidado (`SCR-USR-02`) refleja la selección vigente; retirar un perfil conserva su historial y no reinterpreta reservas anteriores.
- **Backend:** consulta el catálogo habilitado, valida la combinación conforme a las reglas de `investigacion` y reemplaza el conjunto vigente.
- **RN/SEC relacionadas:** `RN-USR-06`; `RN-INV-12` a `RN-INV-16`, `RN-INV-05`, `RN-INV-13`, `RN-INV-14` de `investigacion`, que este módulo no redefine.
- **Dependencias:** `investigacion`, propietaria de las reglas de combinación y del catálogo.

## SCR-USR-05 — Gestionar mis vinculaciones académicas o investigativas

- **User Flows de origen:** `UF-USR-06`, `UF-USR-07`, `UF-USR-08`, `UF-USR-09`, `UF-USR-10`.
- **Actores:** Usuario titular; también Administrador global únicamente para desactivar una vinculación ajena (`UF-USR-10`).
- **Objetivo:** asociar proyectos o semilleros existentes, registrar pasantías o trabajos de grado, y desactivar vinculaciones propias.
- **Precondiciones:** cuenta autenticada. Para asociar, el proyecto o semillero existe en `investigacion`. Para desactivar, existe una vinculación vigente.
- **Información visible:** las vinculaciones actuales del Usuario (proyectos, semilleros, pasantías, trabajos de grado) con su estado; catálogo de proyectos y semilleros vigentes disponibles para asociar.
- **Entradas:** selección de un proyecto o semillero del catálogo, sin texto libre (`RN-USR-10`); universidad, nombre y correo del docente responsable, para una pasantía; nombre y correo del director, para un trabajo de grado; acción de desactivar sobre una vinculación existente.
- **Acciones:** asociar un proyecto; asociar un semillero; registrar una pasantía; registrar un trabajo de grado; desactivar una vinculación propia (o, si el actor es Administrador global, una ajena).
- **Validaciones visibles:** la selección de proyecto/semillero queda restringida al catálogo vigente; los campos de pasantía y trabajo de grado son obligatorios, incluido el formato del correo del docente o director; una vinculación ya activa para el mismo proyecto o semillero no se duplica — si existía inactiva, se reactiva esa misma relación.
- **Estados:** consultando catálogo y vinculaciones vigentes, capturando datos de pasantía o trabajo de grado, guardando, relación rechazada, relación registrada o reactivada, desactivación confirmada, actor no autorizado para desactivar una vinculación ajena.
- **Errores y respuestas:** relación no válida conforme a `investigacion` → no se crea; campo obligatorio ausente o correo con formato inválido, en pasantía o trabajo de grado → corrección requerida; actor distinto del titular y sin ser Administrador global → la vinculación no se modifica.
- **Resultado/navegación:** la vinculación queda disponible como contexto en procesos que la admitan, como una reserva. Al desactivar, si era la última vinculación activa y válida, se muestra en esta misma pantalla la advertencia de que quedan bloqueadas las nuevas reservas hasta recuperar una (`RN-USR-11`) — sin cerrar sesión, sin reiniciar la actualización inicial y sin afectar reservas ya existentes.
- **Backend:** valida y delega en `investigacion` la persistencia; los proyectos y semilleros solo se seleccionan de su catálogo vigente, mientras que la pasantía y el trabajo de grado se crean en este mismo flujo, porque no son catálogos administrados centralmente. Desactivar conserva el historial de la relación; las reservas que la usaron como contexto conservan su referencia.
- **RN/SEC relacionadas:** `RN-USR-06`, `RN-USR-10`; `RN-INV-05`, `RN-INV-06`, `RN-INV-13` de `investigacion`; referencia histórica conservada conforme al dominio de reservas.
- **Dependencias:** `investigacion`, propietaria de la validación y persistencia de proyectos, semilleros, pasantías, trabajos de grado y sus vinculaciones; `reservations`, que conserva las referencias históricas sin reinterpretarlas.

## Cobertura de todos los User Flows

| User Flow revisado | Superficie o efecto de interfaz |
|---|---|
| UF-USR-01 | SCR-USR-01 |
| UF-USR-02 | SCR-USR-01 |
| UF-USR-03 | SCR-USR-02 |
| UF-USR-04 | SCR-USR-03 |
| UF-USR-05 | SCR-USR-04 |
| UF-USR-06 | SCR-USR-05 |
| UF-USR-07 | SCR-USR-05 |
| UF-USR-08 | SCR-USR-05 |
| UF-USR-09 | SCR-USR-05 |
| UF-USR-10 | SCR-USR-05 |
| UF-USR-11 | Sin pantalla propia: efecto en el módulo `reservations` — perfil pendiente conduce a `SCR-USR-01`; sin ninguna vinculación activa y válida, bloquea la creación de nuevas reservas en la pantalla de `reservations`, con orientación a `SCR-USR-05` |

## Ambigüedades y límites de las fuentes

1. **Mecanismo de selección del catálogo de proyectos/semilleros:** las fuentes no definen si es una lista, un buscador o ambos, ni el volumen esperado. No se inventa un componente de búsqueda ni un límite de resultados.
2. **Destino tras completar la actualización inicial:** `UF-USR-01` y `UF-USR-02` dicen que el Usuario «puede continuar con las funcionalidades permitidas», sin fijar una pantalla. Igual que ya lo deja auth para el destino tras iniciar sesión, este documento no lo decide.
3. **Retornos y cancelaciones:** ninguna fuente define un botón de cancelar o volver en `SCR-USR-01`, `SCR-USR-04` o `SCR-USR-05`; no se agregan.
4. **Alcance de la advertencia de `RN-USR-11`:** `screens.md` (este documento) la muestra en `SCR-USR-05` porque es donde ocurre la desactivación; las fuentes no describen si también debería anticiparse en `SCR-USR-02`. No se amplía a una segunda superficie sin esa base.

## Decisiones aplicadas a las ambigüedades de prioridad alta

- `SCR-USR-01` sirve por igual a `UF-USR-01` y `UF-USR-02`: ambos flujos describen el mismo recorrido de revisión de datos y vinculaciones, solo difieren en el origen (autorregistro o invitación), y la propia fuente dice que «el recorrido es el mismo y no requiere reiniciar el alta».
- `SCR-USR-03` (editar datos personales) es accesible tanto con la actualización inicial pendiente como después de completarla: `RN-USR-08` admite explícitamente «las operaciones necesarias para completar su perfil» mientras está pendiente, y corregir un dato personal lo es.
- Las cinco vinculaciones de `UF-USR-06` a `UF-USR-10` se agrupan en una sola superficie (`SCR-USR-05`) en vez de cinco pantallas separadas, porque todas se alcanzan desde «la sección de vinculaciones» del perfil y comparten la misma información de contexto (vinculaciones vigentes, catálogo disponible).
- La creación y administración de identidades (`POST /api/usuarios`, `POST /api/personal`) no tiene pantalla en este documento: sus flujos de origen (`UF-ADM-02`, `UF-ADM-03`) pertenecen a `administration`, no a los once `UF-USR` de este módulo.

## Documentos relacionados

- [Flujos de usuario](user-flow.md): los once flujos que originan estas pantallas.
- [Reglas de negocio](business-rules.md): `RN-USR` y `RN-DAT`.
- [Modelo de datos](data-model.md): `usuarios.usuarios` y sus restricciones.
- [Navegación funcional](screen-flow.md): cómo se conectan estas cinco pantallas entre sí y con auth, investigacion y reservations.
