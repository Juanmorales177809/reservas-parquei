# Contrato de API — Administration

Contrato de comunicación del módulo `administration`. Traduce a superficie HTTP los 4 flujos de [user-flow.md](../../modules/administration/user-flow.md), las reglas de [business-rules.md](../../modules/administration/business-rules.md) y las entidades de [data-model.md](../../modules/administration/data-model.md).

---

## 1. Convenciones

Aplica las [convenciones transversales](../README.md). Aquí solo se documenta lo propio de administration.

| Aspecto | Valor |
|---|---|
| Base path | `/api/unidades` y `/api/cargos` para la estructura institucional; `/api/permisos` para las asignaciones; `/api/importaciones` para las cargas masivas; `/api/auditoria` para la trazabilidad |
| Permiso administrativo | `unidades.administrar` para unidades y cargos, `permisos.asignar` para las asignaciones e `importacion.ejecutar` para las cargas. Los tres son **siempre globales**: un Técnico no puede ejercerlos |
| Identificadores | `id_unidad` e `id_cargo` enteros; `id_cuenta` entero de 64 bits; `id` entero de una importación |

**Este contrato no define códigos de error propios.** Todos los que usa pertenecen al [catálogo común](../README.md#catálogo-común-de-códigos).

**Administration no duplica identidades.** No expone cuentas, que pertenecen a [auth](../auth/api-contract.md), ni identidades funcionales, que pertenecen a [usuarios](../usuarios/api-contract.md). Administra la estructura institucional, las asignaciones de permisos, las importaciones autorizadas y su propia auditoría.

---

## 2. Unidades organizacionales y cargos

Todas las rutas de esta sección exigen `unidades.administrar` con alcance global (`RN-UNI-01`).

### 2.1 `POST /api/unidades`

Registra una unidad organizacional.

**Origen externo ([decisión 2026-09-30](../../docs/decisions/origen-externo-estructura-institucional.md)).** Los laboratorios (las unidades) vienen de otra base de datos: la interfaz no los da de alta. Este endpoint se conserva como vía de carga hasta que se diseñe la integración.

```json
{ "nombre": "Laboratorio de Metrología", "tipo": "LABORATORIO", "id_unidad_padre": 3 }
```

`id_unidad_padre` es opcional y permite la jerarquía. El identificador interno es persistente e independiente del nombre visible (`RN-UNI-02`).

**`201 Created`** con la unidad creada, activa.

**Errores:** `409 CONFLICTO` si el nombre ya existe; `404 NO_ENCONTRADO` si la unidad padre no existe; `422 VALIDACION`.

### 2.2 `GET /api/unidades` y `GET /api/unidades/{id_unidad}`

Listado paginado con la envolvente completa, y detalle. Filtros: `estado`, `tipo`, `id_unidad_padre`, `busqueda` sobre el nombre.

### 2.3 `PATCH /api/unidades/{id_unidad}`

Modifica `nombre`, `tipo` o `id_unidad_padre`. **Cambiar el nombre no cambia la identidad interna** de la unidad ni sus relaciones (`RN-UNI-03`).

**Errores:** `409 CONFLICTO` si el nombre ya existe o si el cambio de padre crea un ciclo en la jerarquía.

### 2.4 `PATCH /api/unidades/{id_unidad}/estado`

Habilita o deshabilita.

```json
{ "estado": false }
```

Deshabilitar **no elimina** usuarios, personal, reservas, recursos ni información histórica asociada (`RN-UNI-04`, `RN-HAB-03`), y **no se propaga** automáticamente a otras entidades (`RN-HAB-05`). Una unidad deshabilitada no puede utilizarse en nuevas configuraciones u operaciones que exijan una unidad activa (`RN-UNI-05`).

Que una unidad exista no implica que pueda recibir reservas: eso lo determina la configuración de laboratorio de [resources](../resources/api-contract.md) (`RN-UNI-06`, `RN-UNI-07`).

### 2.5 `POST /api/cargos`

Registra un cargo dentro de una unidad.

**Origen externo ([decisión 2026-09-30](../../docs/decisions/origen-externo-estructura-institucional.md)).** Los cargos vienen de otra base de datos: la interfaz no los da de alta. Este endpoint se conserva como vía de carga hasta que se diseñe la integración.

```json
{ "nombre_cargo": "Técnico de laboratorio", "id_unidad": 7 }
```

El cargo determina **únicamente** la unidad organizacional de pertenencia del personal; no concede permisos (`RN-PRS-03` de usuarios).

**`201 Created`**. **Errores:** `404 NO_ENCONTRADO` si la unidad no existe; `422 VALIDACION`.

### 2.6 `GET /api/cargos` y `PATCH /api/cargos/{id_cargo}`

Listado paginado con la envolvente completa, filtrable por `id_unidad`, y modificación del nombre o la unidad del cargo.

Cambiar la unidad de un cargo **cambia el ámbito del personal que lo ocupa**, y con él la validez de sus asignaciones de permiso por unidad (`RN-PER-09`). El cambio queda registrado en auditoría (`RN-AUD-06`).

---

## 3. Asignación de permisos

**La interfaz ya no usa esta sección** ([decisión 2026-09-30](../../docs/decisions/origen-externo-estructura-institucional.md#los-permisos-los-define-el-rol-2026-09-30)): los permisos los define el rol y no se otorgan a mano. Los endpoints se conservan hasta que el servidor derive los permisos del rol y del laboratorio del cargo.

Todas las rutas de esta sección exigen `permisos.asignar` con alcance global (`RN-PER-03`).

Administration **administra** las asignaciones; [auth](../auth/api-contract.md) las **evalúa** en cada operación. El catálogo de códigos está en su [modelo](../../modules/auth/data-model.md#catálogo-inicial) y no se amplía desde aquí (`RN-PER-01`).

### 3.1 `GET /api/permisos`

Catálogo de permisos asignables. **Catálogo cerrado**: devuelve solo `datos`, sin paginación.

```json
{ "datos": [{ "codigo": "reservas.administrar", "descripcion": "Gestionar reservas de la unidad", "ambito": "unidad" }] }
```

`ambito` indica el uso previsto; el alcance efectivo lo fija `id_unidad` en cada asignación (`RN-PER-06`).

### 3.2 `GET /api/permisos/cuentas/{id_cuenta}`

Asignaciones vigentes de una cuenta, con su ámbito.

### 3.3 `POST /api/permisos/cuentas/{id_cuenta}`

Otorga un permiso.

```json
{ "codigo": "reservas.administrar", "id_unidad": 7 }
```

`id_unidad` nulo significa asignación global.

**Solo una cuenta activa de tipo `PERSONAL`, vinculada a un registro activo de `personal.personal`, puede recibir permisos administrativos.** Una cuenta `USUARIO` nunca (`RN-PER-08`). Si la asignación está acotada a unidad, esa unidad debe coincidir con la del cargo vigente de la persona; el sistema rechaza cualquier otra (`RN-PER-09`).

`permisos.asignar` **no permite ampliar el ámbito propio del actor** ni omitir estas restricciones.

**Errores:** `409 CONFLICTO` si la asignación ya existe; `422 VALIDACION` si la cuenta no es `PERSONAL` activa, si la unidad no coincide con la de su cargo, o si el código no existe en el catálogo.

### 3.4 `DELETE /api/permisos/cuentas/{id_cuenta}/{codigo}`

Retira un permiso. **`204 No Content`**.

Retirar afecta las **nuevas** decisiones de autorización desde que el cambio entra en vigencia (`RN-PER-04`) y **no invalida retroactivamente** las acciones ejecutadas cuando la autorización era válida (`RN-PER-05`).

**Errores:** `409 CONFLICTO` si la operación dejaría al sistema sin ninguna cuenta con permisos globales vigentes (`RN-AUTH-ROL-09` de auth); `404 NO_ENCONTRADO` si la asignación no existe.

---

## 4. Importaciones masivas

Todas las rutas de esta sección exigen `importacion.ejecutar` con alcance global (`RN-IMP-01`).

La carga se realiza en dos pasos: primero se valida y se obtiene un resumen, después se confirma. **Una carga con al menos una fila en error no puede confirmarse** (`RN-IMP-06`).

### 4.1 `POST /api/importaciones`

Carga y valida un archivo sin escribir nada. Flujos `UF-ADM-01` para proyectos y semilleros, `UF-ADM-04` para equipos.

Solicitud `multipart/form-data`:

| Campo | Valor |
|---|---|
| `archivo` | El libro de Excel |
| `catalogo` | `PROYECTOS`, `SEMILLEROS` o `EQUIPOS` (`RN-IMP-01`) |
| `id_unidad` | **Obligatorio solo para `EQUIPOS`.** La planilla no trae unidad y esta se aplica a los equipos que la carga cree (`RN-IMP-12`) |

Las columnas esperadas dependen del catálogo: `codigo`, `nombre` y `estado` para los de investigación (`RN-IMP-02`); `PLACA`, `DESCRIPCIÓN`, `CODIGO BODEGA`, `CENTRO DE COSTOS`, `FECHA INICIO` y `COSTO` para equipos, de las cuales el costo se lee y se descarta (`RN-IMP-11`).

**`201 Created`** con la validación, sin escribir catálogo alguno.

```json
{
  "id": 88,
  "catalogo": "EQUIPOS",
  "id_unidad": 7,
  "archivo_referencia": "equipos_metrologia.xlsx",
  "confirmable": false,
  "totales": { "a_crear": 112, "a_actualizar": 6, "con_error": 2 },
  "resultados": [
    { "numero_fila": 41, "codigo": "EQ-0112", "resultado": "CREADO", "detalle": null },
    { "numero_fila": 57, "codigo": null, "resultado": "ERROR", "detalle": "La fila no trae placa" }
  ]
}
```

`confirmable` es `false` cuando `con_error` es mayor que cero. El resultado por fila se conserva aunque la carga no llegue a confirmarse, para que el Administrador sepa qué corregir sin volver a procesar el archivo (`RN-IMP-08`).

**Errores:** `422 VALIDACION` si el archivo no es legible, le faltan columnas o el catálogo no es uno de los tres; `400 SOLICITUD_INVALIDA` si falta `id_unidad` en una carga de equipos.

### 4.2 `POST /api/importaciones/{id}/confirmacion`

Confirma una carga previamente validada. Sin cuerpo.

Al confirmar, las entidades se escriben en el **módulo propietario**: `investigacion` para proyectos y semilleros, `recursos` para equipos (`RN-IMP-10`). Administration no las escribe eludiendo sus reglas.

**`200 OK`** con los totales definitivos de creados, actualizados y desactivados.

La importación **no crea ni modifica vinculaciones de usuarios** (`RN-IMP-05`), y una carga de equipos **nunca deshabilita**: su contador de desactivados es siempre cero (`RN-IMP-09`).

**Errores:** `409 CONFLICTO` si la carga contiene filas en error y por tanto no es confirmable, o si ya fue confirmada.

### 4.3 `GET /api/importaciones` y `GET /api/importaciones/{id}`

Historial paginado con la envolvente completa, filtrable por `catalogo` y rango de fechas, y detalle con el resultado de cada fila.

---

## 5. Auditoría administrativa

### 5.1 `GET /api/auditoria`

Registro de las operaciones administrativas. Listado paginado con la envolvente completa. Permiso: `unidades.administrar` con alcance global.

Filtros: `entidad`, `entidad_id`, `actor_cuenta_id`, `accion`, `desde` y `hasta`. Orden: `created_at`, descendente por defecto.

**`200 OK`**

```json
{
  "datos": [
    {
      "id": 4471,
      "actor_cuenta_id": 1042,
      "entidad": "auth.cuenta_permisos",
      "entidad_id": "310",
      "accion": "ASIGNAR_PERMISO",
      "datos_anteriores": null,
      "datos_nuevos": { "codigo": "reservas.administrar", "id_unidad": 7 },
      "motivo": null,
      "created_at": "2026-09-23T11:04:02Z"
    }
  ],
  "paginacion": { "pagina": 1, "tamano": 20, "total": 318, "paginas": 16 }
}
```

Cada registro identifica actor, acción, entidad afectada, identificador y momento (`RN-AUD-02`), y `datos_anteriores` y `datos_nuevos` permiten reconstruir el cambio cuando corresponde (`RN-AUD-03`).

**No existe ningún endpoint de escritura sobre la auditoría.** Los registros los genera el sistema al ejecutar cada operación y **no se modifican** para reflejar valores actuales (`RN-AUD-05`). Se conservan aunque la cuenta o la entidad se desactiven después (`RN-AUD-04`).

El actor se identifica por `actor_cuenta_id`; la auditoría no duplica identidades de `usuarios.usuarios`, `personal.personal` ni `auth.cuentas` (`RN-AUD-07`).

---

## 6. Lo que este contrato no expone

- **Cuentas, credenciales y sesiones**: pertenecen a [auth](../auth/api-contract.md). Administration solicita la invitación; no crea cuentas.
- **Identidades funcionales**: `usuarios.usuarios` y `personal.personal` pertenecen a [usuarios](../usuarios/api-contract.md). `UF-ADM-02` y `UF-ADM-03` orquestan esos endpoints y los de auth, sin duplicarlos aquí.
- **Los catálogos que importa**: proyectos y semilleros pertenecen a [researchs](../researchs/api-contract.md) y los equipos a [resources](../resources/api-contract.md). La importación los escribe mediante sus reglas, y este contrato solo expone la orquestación.
- **Vinculaciones de usuarios con proyectos o semilleros**: pertenecen a researchs y la importación no las toca (`RN-IMP-05`).
- **Configuración de reservas por unidad**: horario, antelación, aprobación automática y tipos de reserva pertenecen a [resources](../resources/api-contract.md) (`RN-UNI-07`).
- **La auditoría de reservas**: está fuera del alcance funcional actual. El historial de una reserva se limita a sus transiciones de estado, en reservations.
