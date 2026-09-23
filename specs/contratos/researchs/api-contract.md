# Contrato de API — Researchs

Contrato de comunicación del módulo `researchs`. Traduce a superficie HTTP el flujo de [user-flow.md](../../modules/researchs/user-flow.md), las reglas de [business-rules.md](../../modules/researchs/business-rules.md) y las entidades de [data-model.md](../../modules/researchs/data-model.md).

---

## 1. Convenciones

Aplica las [convenciones transversales](../README.md). Aquí solo se documenta lo propio de researchs.

| Aspecto | Valor |
|---|---|
| Base path | `/api/investigacion` |
| Permiso administrativo | `usuarios.administrar`, **siempre global**. Un Técnico no administra ningún elemento de este módulo (`RN-INV-15`, `RN-ACT-04`) |
| Identificadores | `id_proyecto`, `id_semillero`, `id_perfil`, `id_actividad` e `id_usuario`, enteros |

**Este contrato no define códigos de error propios.** Todos los que usa pertenecen al [catálogo común](../README.md#catálogo-común-de-códigos).

**Este contrato es el lado administrativo del módulo.** Lo que un Usuario hace con sus propios perfiles y vinculaciones está en el [contrato de usuarios](../usuarios/api-contract.md), que orquesta este dominio sin reimplementar sus reglas. Aquí se administra lo ajeno y lo central: el catálogo de proyectos y semilleros, las actividades institucionales, el catálogo de perfiles y las vinculaciones de terceros.

**Nada se elimina físicamente.** Desactivar conserva el registro, sus asociaciones y las referencias históricas de reservas (`RN-INV-05`, `RN-ACT-03`).

---

## 2. Catálogo de proyectos y semilleros

`proyectos` y `semilleros` son **catálogos administrados centralmente**: sus códigos e identidades son persistentes y no pueden crearse ni modificarse desde el perfil de un Usuario ni desde una reserva (`RN-INV-06`).

### 2.1 `GET /api/investigacion/proyectos` y `GET /api/investigacion/semilleros`

Listado paginado con la envolvente completa. Filtros: `estado` y `busqueda` sobre código y nombre. Orden admitido: `codigo`, `nombre`.

Es el catálogo completo, con alcance administrativo. El catálogo que un Usuario consulta para vincularse está en `GET /api/perfil/vinculaciones/catalogo` del [contrato de usuarios](../usuarios/api-contract.md) y devuelve solo los habilitados.

### 2.2 `PATCH /api/investigacion/proyectos/{id_proyecto}/estado`

Habilita o deshabilita un proyecto. La misma ruta existe para semilleros.

```json
{ "estado": false }
```

Deshabilitar conserva el registro, sus vinculaciones y las referencias históricas de reservas (`RN-IMP-07` de administration). Un proyecto deshabilitado no puede seleccionarse en nuevas vinculaciones ni como contexto de una reserva nueva.

**La creación y la actualización masiva de estos catálogos no se exponen aquí**: se realizan mediante la importación autorizada de [administration](../administration/api-contract.md), conforme a `RN-IMP-01`.

---

## 3. Actividades institucionales

Solo un Administrador con alcance global puede crearlas, modificarlas, activarlas o desactivarlas (`RN-ACT-04`). Flujo `UF-INV-01`.

### 3.1 `POST /api/investigacion/actividades`

```json
{ "nombre": "Semana de la Ingeniería", "dependencia": "Facultad de Ingenierías" }
```

`nombre` y `dependencia` son obligatorios (`RN-ACT-01`).

**`201 Created`** con la actividad, activa.

**Errores:** `422 VALIDACION` si falta alguno de los dos datos o queda vacío.

### 3.2 `GET /api/investigacion/actividades`

Listado paginado con la envolvente completa. Filtros: `estado`, `dependencia`, `busqueda` sobre el nombre.

### 3.3 `PATCH /api/investigacion/actividades/{id_actividad}`

Modifica `nombre` o `dependencia`. No altera las reservas que ya la usaron como contexto, que conservan su copia histórica (`RN-CTX-07` de reservations).

### 3.4 `PATCH /api/investigacion/actividades/{id_actividad}/estado`

Activa o desactiva. **Solo una actividad activa puede utilizarse en una reserva nueva** (`RN-ACT-02`). Desactivar no elimina el registro ni las referencias históricas (`RN-ACT-03`).

---

## 4. Catálogo de perfiles

Un **perfil** describe la situación académica o investigativa de una persona —por ejemplo investigador o estudiante—. Es distinto de una **vinculación**, que la asocia a un proyecto, semillero, pasantía o trabajo de grado concretos. Tener un perfil no concede permisos ni habilita a reservar (`RN-INV-16`).

Solo un Administrador con alcance global administra este catálogo (`RN-INV-15`).

### 4.1 `POST /api/investigacion/perfiles`

```json
{ "nombre": "Investigador", "descripcion": "Participa en proyectos de investigación" }
```

**`201 Created`** con el perfil, habilitado.

### 4.2 `GET /api/investigacion/perfiles`

Listado paginado con la envolvente completa, incluidos los deshabilitados. Filtro: `habilitado`.

El catálogo que un Usuario consulta para elegir los suyos está en `GET /api/perfil/perfiles/catalogo` del contrato de usuarios y devuelve solo los habilitados.

### 4.3 `PATCH /api/investigacion/perfiles/{id_perfil}` y `.../estado`

Modifica el perfil o su habilitación.

**Un perfil deshabilitado no puede asignarse en nuevas operaciones**, pero **conserva las asociaciones existentes** (`RN-INV-14`, `RN-INV-05`). Asignar o retirar un perfil **no modifica retroactivamente** el contexto registrado en operaciones históricas (`RN-INV-13`).

---

## 5. Vinculaciones de terceros

Un Administrador con alcance global puede intervenir sobre las vinculaciones de otro Usuario. Flujo `UF-INV-01`. Un Usuario gestiona únicamente las propias, desde el contrato de usuarios (`RN-INV-16`).

### 5.1 `GET /api/investigacion/usuarios/{id_usuario}/vinculaciones`

Vinculaciones de un Usuario, activas e inactivas, agrupadas por tipo.

```json
{
  "proyectos": [{ "id_proyecto": 12, "codigo": "PRY-001", "nombre": "Ensayos no destructivos", "activa": true }],
  "semilleros": [],
  "pasantias": [],
  "trabajos_grado": []
}
```

### 5.2 `POST /api/investigacion/usuarios/{id_usuario}/vinculaciones/{tipo}`

Crea o reactiva una vinculación ajena. `tipo` admite `proyectos` y `semilleros`.

```json
{ "id_proyecto": 12 }
```

**Si ya existe una relación inactiva para el mismo Usuario y la misma entidad, se reactiva esa fila** en lugar de crear otra (`UF-INV-01`, paso 3). La reactivación conserva el identificador y el historial previos (`RN-HAB-04` de administration).

**`201 Created`**. **Errores:** `409 CONFLICTO` si ya existe una vinculación activa; `404 NO_ENCONTRADO` si el proyecto o semillero no existe o está deshabilitado (`RN-INV-08`).

### 5.3 `DELETE /api/investigacion/usuarios/{id_usuario}/vinculaciones/{tipo}/{id}`

Desactiva una vinculación ajena. **`204 No Content`**.

No elimina el registro: lo marca inactivo y conserva el historial (`RN-INV-05`). Las reservas que la usaron como contexto conservan su referencia e interpretación (`RN-CTX-07` de reservations).

**Advertencia de impacto:** si era la última vinculación activa, ese Usuario deja de poder crear reservas hasta recuperar una (`RN-USR-11` de usuarios). La respuesta lo indica, sin bloquear la operación:

```json
{ "sin_vinculaciones_activas": true }
```

---

## 6. Lo que este contrato no expone

- **Las vinculaciones propias de un Usuario**: pertenecen al [contrato de usuarios](../usuarios/api-contract.md), bajo `/api/perfil`. Aquí solo se administra lo ajeno.
- **La creación de proyectos y semilleros**: llegan por la importación autorizada de [administration](../administration/api-contract.md). Ni el Usuario ni este contrato los crean uno a uno (`RN-INV-06`, `RN-INV-07`).
- **Pasantías y trabajos de grado**: los crea el propio Usuario al registrarlos, desde el contrato de usuarios, porque no son catálogos administrados centralmente. Este contrato solo los consulta dentro de las vinculaciones de una persona.
- **El contexto de una reserva**: qué combinaciones son válidas, su obligatoriedad y su exclusividad los define `RN-CTX` de [reservations](../reservations/api-contract.md). Researchs aporta las entidades, no decide cómo se usan en una reserva.
- **Permisos administrativos**: pertenecer a un proyecto o tener un perfil no concede ninguno (`RN-INV-16`). Las asignaciones se administran en [administration](../administration/api-contract.md).
