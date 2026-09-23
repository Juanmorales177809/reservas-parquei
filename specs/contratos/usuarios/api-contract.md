# Contrato de API — Usuarios

Contrato de comunicación del módulo `usuarios`. Traduce a superficie HTTP los 11 flujos de [user-flow.md](../../modules/usuarios/user-flow.md), las reglas de [business-rules.md](../../modules/usuarios/business-rules.md) y las entidades de [data-model.md](../../modules/usuarios/data-model.md).

---

## 1. Convenciones

Aplica las [convenciones transversales](../README.md). Aquí solo se documenta lo propio de usuarios.

| Aspecto | Valor |
|---|---|
| Base path | `/api/perfil` para el perfil propio; `/api/usuarios` para la administración |
| Permiso administrativo | `usuarios.administrar`, siempre global, para las rutas bajo `/api/usuarios`. Las rutas bajo `/api/perfil` no exigen permiso: operan sobre la identidad de la sesión |
| Identidad | siempre la de la sesión; el cliente nunca envía `id_usuario` para identificarse (`SEC-AUTZ-03`) |

Códigos de error propios, adicionales al catálogo común:

| HTTP | `codigo` | Uso |
|---|---|---|
| 409 | `DOCUMENTO_DUPLICADO` | Documento ya registrado en otra identidad (`RN-DAT-02`) |
| 409 | `TELEFONO_DUPLICADO` | Teléfono ya registrado en otra identidad (`RN-DAT-02`) |
| 409 | `VINCULACION_DUPLICADA` | La vinculación ya existe para ese usuario |

Este módulo **orquesta** el perfil: cuando la información pertenece a `researchs` —proyectos, semilleros, pasantías y trabajos de grado— delega en ese dominio la validación y la persistencia, sin reimplementar sus reglas.

---

## 2. Perfil propio

### 2.1 `GET /api/perfil`

Perfil consolidado del actor. Flujo `UF-USR-03`.

```json
{
  "id_usuario": 1042,
  "nombre": "Persona de ejemplo",
  "documento": "1000000001",
  "telefono": "+573000000001",
  "institucion": "ITM",
  "dependencia": "Facultad de Ingenierías",
  "correo": "persona@correo.itm.edu.co",
  "actualizacion_inicial_pendiente": false,
  "perfil_actualizado_at": "2026-09-19T14:03:11Z",
  "perfiles": [{ "id_perfil": 2, "nombre": "Investigador" }],
  "vinculaciones": {
    "proyectos": [{ "id_proyecto": 12, "codigo": "PRY-001", "nombre": "Ensayos no destructivos", "estado": true }],
    "semilleros": [],
    "pasantias": [],
    "trabajos_grado": []
  }
}
```

`perfiles` y `vinculaciones` se obtienen de `researchs`; este módulo no los almacena ni decide su validez (`RN-INV-08` de researchs).

Un **perfil** académico o investigativo (`investigacion.perfiles`) describe la situación de la persona —por ejemplo investigador o estudiante— y es distinto de una **vinculación**, que la asocia a un proyecto, semillero, pasantía o trabajo de grado concretos. Solo las vinculaciones cuentan para `RN-USR-07` y `RN-USR-11`: tener un perfil no habilita a reservar.

### 2.2 `PATCH /api/perfil`

Actualiza los datos personales. Flujo `UF-USR-04`. Admite `nombre`, `documento`, `telefono`, `institucion` y `dependencia`.

Los cinco son obligatorios y no admiten valor vacío ni compuesto solo por espacios (`RN-DAT-01`). `documento` y `telefono` son únicos entre todos los registros, incluidos los inactivos, excluyendo el propio al editar (`RN-DAT-02`).

**`200 OK`** con el perfil actualizado.

**Errores:** `409 DOCUMENTO_DUPLICADO`, `409 TELEFONO_DUPLICADO`, `422 VALIDACION`.

### 2.3 `POST /api/perfil/actualizacion-inicial`

Confirma la actualización inicial. Flujos `UF-USR-01` y `UF-USR-02`.

Sin cuerpo: el servidor verifica que los datos obligatorios estén completos y que exista al menos una vinculación activa y válida confirmada por `researchs` (`RN-USR-07`).

**`200 OK`**

```json
{ "perfil_actualizado_at": "2026-09-19T14:03:11Z", "actualizacion_inicial_pendiente": false }
```

Mientras la actualización esté pendiente, las demás operaciones de negocio responden `403 PERFIL_INICIAL_PENDIENTE` (`RN-USR-08`). El recorrido se retoma en el siguiente ingreso sin reiniciarse ni caducar.

**Errores:** `409 CONFLICTO` si falta un dato obligatorio o no hay ninguna vinculación válida; `detalles` indica cuál de las dos condiciones falta.

---

## 3. Perfiles académicos e investigativos

### 3.0 `GET /api/perfil/perfiles/catalogo`

Perfiles disponibles en `investigacion.perfiles`. Solo se devuelven los habilitados. **Catálogo cerrado**: devuelve solo `datos`, sin paginación.

```json
{ "datos": [{ "id_perfil": 2, "nombre": "Investigador" }] }
```

### 3.1 `PUT /api/perfil/perfiles`

Actualiza los perfiles del Usuario. Flujo `UF-USR-05`. Reemplaza el conjunto completo: lo que no venga en la lista queda desactivado.

```json
{ "perfiles": [2, 5] }
```

`researchs` valida las opciones seleccionadas y rechaza las combinaciones que sus reglas no permitan. Desactivar un perfil conserva su historial (`RN-INV-05` de researchs).

**`200 OK`** con los perfiles vigentes.

**Errores:** `409 CONFLICTO` si la combinación no está permitida, `404 NO_ENCONTRADO` si un perfil no existe o está deshabilitado.

---

## 4. Vinculaciones académicas e investigativas

Estas rutas orquestan `researchs`. Los proyectos y semilleros **solo se seleccionan del catálogo**: no pueden crearse ni escribirse por nombre libre (`RN-USR-10`, `RN-INV-06` de researchs).

### 4.1 `GET /api/perfil/vinculaciones/catalogo?tipo=proyectos`

Catálogo disponible para vincular. `tipo` admite `proyectos` y `semilleros`. Listado paginado con la envolvente completa, porque su volumen depende de los datos, con filtro `busqueda` sobre código y nombre.

### 4.2 `POST /api/perfil/vinculaciones/proyectos`

Asocia un proyecto existente. Flujo `UF-USR-06`.

```json
{ "id_proyecto": 12 }
```

**`201 Created`**. Si existe una vinculación inactiva para el mismo proyecto, se reactiva esa misma relación. **Errores:** `409 VINCULACION_DUPLICADA` si ya existe una vinculación activa, `404 NO_ENCONTRADO` si el proyecto no existe o está deshabilitado.

### 4.3 `POST /api/perfil/vinculaciones/semilleros`

Igual que la anterior, con `id_semillero`. Si existe una vinculación inactiva para el mismo semillero, se reactiva esa misma relación. Flujo `UF-USR-07`.

### 4.4 `POST /api/perfil/vinculaciones/pasantias`

Registra una pasantía y la vincula. Flujo `UF-USR-08`.

```json
{
  "universidad": "Universidad de ejemplo",
  "docente_itm_nombre": "Nombre del docente",
  "docente_itm_correo": "docente@itm.edu.co"
}
```

A diferencia de proyectos y semilleros, la pasantía **se crea** en este flujo porque no es un catálogo administrado centralmente.

**`201 Created`** con la pasantía y su vinculación.

### 4.5 `POST /api/perfil/vinculaciones/trabajos-grado`

Registra un trabajo de grado con `director_nombre` y `director_correo`. Flujo `UF-USR-09`.

### 4.6 `DELETE /api/perfil/vinculaciones/{tipo}/{id}`

Desactiva una vinculación propia. Flujo `UF-USR-10`. **`204 No Content`**.

No elimina el registro: lo marca inactivo y conserva el historial (`RN-INV-05` de researchs). Las reservas que la usaron como contexto conservan su referencia e interpretación (`RN-CTX-07` de reservations).

**Advertencia de impacto:** si esta es la última vinculación activa, el Usuario deja de poder crear reservas hasta recuperar una (`RN-USR-11`). La respuesta incluye ese aviso:

```json
{ "sin_vinculaciones_activas": true }
```

No bloquea la operación ni cierra la sesión, y no reinicia la actualización inicial.

---

## 5. Administración de identidades

Requieren el permiso global `usuarios.administrar` (`RN-USR-01` de administration). Los Técnicos no administran identidades de Usuario. El flujo que las conduce es `UF-ADM-02` de administration, que continúa en `UF-AUTH-02` cuando se invita la cuenta.

### 5.1 `POST /api/usuarios`

Crea la identidad funcional de un Usuario, paso previo a invitarlo. Flujo `UF-ADM-02`. Exige los cinco datos obligatorios de `RN-DAT-01`: la invitación no usa datos ficticios para completar el perfil (`RN-USR-06` de administration).

**`201 Created`** con la identidad creada. La cuenta se crea después, desde el contrato de [auth](../auth/api-contract.md).

**Errores:** `409 DOCUMENTO_DUPLICADO`, `409 TELEFONO_DUPLICADO` (`RN-DAT-02`), `422 VALIDACION` si falta alguno de los cinco datos obligatorios o queda vacío.

### 5.2 `GET /api/usuarios` y `GET /api/usuarios/{id_usuario}`

Listado paginado y detalle. Filtros: `estado`, `busqueda` sobre nombre, documento y correo.

**Errores:** `404 NO_ENCONTRADO` si la identidad no existe.

### 5.3 `PATCH /api/usuarios/{id_usuario}`

Modifica datos de una identidad. Flujo `UF-ADM-02`. Si ya existe una cuenta asociada, no puede modificar `correo`; el correo único de la persona y la cuenta es inmutable desde la creación de esa cuenta. No altera retroactivamente reservas ni registros históricos (`RN-USR-02` de administration).

**Errores:** `409 DOCUMENTO_DUPLICADO` y `409 TELEFONO_DUPLICADO`, excluyendo el propio registro de la comprobación (`RN-DAT-02`); `409 CONFLICTO` si se intenta modificar `correo` existiendo cuenta asociada; `422 VALIDACION`.

### 5.4 `PATCH /api/usuarios/{id_usuario}/estado`

Habilita o deshabilita. Deshabilitar impide nuevas operaciones que requieran identidad activa, sin eliminar información histórica (`RN-USR-03` de administration).

---

## 6. Fichas de Personal

`personal.personal` es la otra identidad funcional de este módulo: representa al personal institucional que puede operar como Técnico o Administrador. Requieren el permiso global `usuarios.administrar`. El flujo que las conduce es `UF-ADM-03` de administration, que continúa en `UF-AUTH-02` cuando se invita la cuenta.

**Auth no crea ni completa una ficha.** La captura y valida este dominio antes de que se solicite la invitación (`RN-PRS-05`).

### 6.1 `POST /api/personal`

Registra la ficha de una persona.

```json
{
  "nombre": "Persona de ejemplo",
  "documento": "1000000002",
  "correo": "persona@itm.edu.co",
  "telefono": "+573000000002",
  "id_cargo": 14
}
```

Los cinco datos son obligatorios. Documento, correo y teléfono son únicos en la tabla, y el cargo debe existir: **es el cargo el que determina la unidad organizacional de la persona**, no un campo propio (`RN-PRS-02`, `RN-PRS-03`, `RN-PRS-05`).

**`201 Created`** con la ficha, activa. La cuenta se crea después, desde el contrato de [auth](../auth/api-contract.md), que resuelve `id_persona` por el correo único.

**Errores:** `409 CONFLICTO` si el documento, el correo o el teléfono ya existen en otra ficha; `404 NO_ENCONTRADO` si el cargo no existe; `422 VALIDACION`.

### 6.2 `GET /api/personal` y `GET /api/personal/{id_persona}`

Listado paginado con la envolvente completa, y detalle con el cargo y la unidad que de él se deriva. Filtros: `estado`, `id_unidad`, `busqueda` sobre nombre, documento y correo.

### 6.3 `PATCH /api/personal/{id_persona}`

Modifica los datos de la ficha. **Si ya existe una cuenta asociada, no puede modificarse `correo`**: es el mismo valor inmutable de la cuenta (`RN-AUTH-ID-03` de auth).

Cambiar `id_cargo` **cambia la unidad organizacional de la persona**, y con ella la validez de sus asignaciones de permiso por unidad (`RN-PER-09` de administration). El cambio queda en auditoría (`RN-AUD-06` de administration).

**Errores:** `409 CONFLICTO` por duplicado de documento, correo o teléfono, excluyendo el propio registro, o si se intenta modificar el correo existiendo cuenta asociada.

### 6.4 `PATCH /api/personal/{id_persona}/estado`

Activa o desactiva la ficha.

```json
{ "estado": true }
```

**Personal inactivo no puede realizar nuevas operaciones administrativas**; las acciones históricas ya realizadas se conservan (`RN-PRS-04`). Una ficha inactiva no puede recibir una invitación ni activar una pendiente, y Auth vuelve a comprobarlo al activar la cuenta.

**Errores:** `409 CONFLICTO` si desactivarla dejaría al sistema sin ninguna cuenta con permisos globales vigentes (`RN-AUTH-ROL-09` de auth).

---

## 7. Lo que este contrato no expone

- **Cuenta, credenciales y sesión**: pertenecen a [auth](../auth/api-contract.md). Este módulo administra las dos identidades funcionales —`usuarios.usuarios` y `personal.personal`—, no la autenticación.
- **Cargos y unidades organizacionales**: los administra [administration](../administration/api-contract.md). Una ficha de Personal referencia un cargo existente y deriva su unidad de él; no la declara.
- **Creación de proyectos y semilleros**: son catálogos centrales; se importan desde administration y aquí solo se seleccionan.
- **Iniciar una reserva** (`UF-USR-11`): el flujo continúa en [reservations](../reservations/api-contract.md); este módulo solo aporta la condición del perfil que reservations verifica.
