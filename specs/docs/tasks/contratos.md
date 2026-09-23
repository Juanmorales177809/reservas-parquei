# Plan de tareas — Contratos de API

Traduce los nueve [contratos de API](../../contratos/README.md) a tareas de implementación de la superficie HTTP. Cada tarea declara objetivo, archivos afectados, dependencias, criterio de aceptación y las reglas que la sustentan.

Plan general y dependencias con la base de datos: [`tasks.md`](../../../tasks.md) de la raíz.

---

## Punto de partida

Los nueve módulos tienen contrato y los nueve comparten la misma forma. La superficie documentada son **122 rutas**, y el backend no implementa ninguna: el anterior se retiró entero porque respondía a un contrato distinto.

| Contrato | Rutas | | Contrato | Rutas |
|---|---:|---|---|---:|
| usuarios | 21 | | espacios | 15 |
| reservations | 20 | | resources | 11 |
| auth | 17 | | notifications | 5 |
| administration | 17 | | reports | 5 |
| researchs | 15 | | | |

Cuatro rutas aparecen en dos contratos —las de `/api/perfil`, que usuarios y researchs comparten—, así que la suma por archivo da 126 y las únicas son 122.

El desglose de auth está en su propio plan: [modules/auth/tasks.md](../../modules/auth/tasks.md).

**Ningún endpoint es implementable antes que las convenciones transversales.** Son lo que hace que los nueve contratos se comporten igual, y reimplementarlas por módulo es la forma más rápida de acabar con nueve APIs distintas.

`API-01` a `API-04` **son** las tareas `BK-04` a `BK-07` del [plan de backend](backend.md), no un trabajo aparte: aquí está el criterio de aceptación escrito como petición, allí los archivos. Se cierran juntas.

---

## Convención de tarea

```markdown
### API-XX — Título

- **Objetivo:** qué queda distinto al terminar.
- **Afectados:** archivos concretos del backend.
- **Dependencias:** qué debe cerrarse antes; qué desbloquea.
- **Aceptación:** condición verificable con una petición, no "quedó implementado".
- **Contrato:** sección que cubre.
- **RN:** reglas aplicadas.
```

Una tarea sin criterio de aceptación verificable no entra al plan. El criterio se escribe como la petición y la respuesta esperada, incluido el caso de error.

---

## 1. Convenciones transversales

Bloquean todo lo demás. Están definidas en [contratos/README.md](../../contratos/README.md).

### API-01 — Envolvente de error y catálogo común

- **Objetivo:** toda respuesta de error usa `{"error": {"codigo", "mensaje", "detalles"}}` con los catorce códigos comunes.
- **Afectados:** manejador de excepciones del backend.
- **Dependencias:** ninguna. **Bloquea todas las demás.**
- **Aceptación:** una petición no autenticada responde `401 NO_AUTENTICADO` con esa forma, no el `detail` de FastAPI. `detalles` nunca contiene trazas, SQL ni variables de entorno.
- **Contrato:** README §2.
- **RN:** `SEC-INF-04`.

### API-02 — Paginación, filtros y orden

- **Objetivo:** todo listado acepta `pagina`, `tamano` y `orden`, y devuelve `datos` + `paginacion`.
- **Afectados:** utilidad de paginación compartida.
- **Dependencias:** API-01.
- **Aceptación:** un filtro desconocido responde `400 SOLICITUD_INVALIDA` en lugar de ignorarse en silencio. Un catálogo cerrado devuelve solo `datos` y rechaza `pagina`.
- **Contrato:** README §4, incluida la excepción de catálogos cerrados.

### API-03 — Sesión por cookie y CSRF de doble envío

- **Objetivo:** la identidad proviene de la sesión, nunca de un identificador enviado por el cliente, y toda operación que modifica estado exige `X-CSRF-Token`.
- **Afectados:** middleware de autenticación y CSRF.
- **Dependencias:** API-01.
- **Aceptación:** una petición `POST` sin el encabezado responde `403 NO_AUTORIZADO` aunque la sesión sea válida. `GET /api/auth/csrf` emite la cookie sin requerir sesión.
- **Contrato:** auth §2, README §3.
- **RN:** `SEC-CSRF-01`, `SEC-CSRF-02`, `SEC-AUTZ-03`.

### API-04 — `exigir_permiso` con ámbito

- **Objetivo:** el permiso y el ámbito organizacional se evalúan en el servidor en cada operación, con información vigente.
- **Afectados:** dependencia de autorización del backend.
- **Dependencias:** API-03, **DB-14**, que crea `auth.permisos` y `auth.cuenta_permisos`, y **DB-09**, que carga el catálogo.
- **Aceptación:** un Técnico que opera sobre una unidad ajena recibe `403 NO_AUTORIZADO`, o `404 NO_ENCONTRADO` cuando revelar la existencia constituya una fuga. Ante imposibilidad de comprobar el permiso, deniega.
- **Contrato:** auth §7, README §3.
- **RN:** `SEC-AUTZ-01`, `SEC-AUTZ-02`, `SEC-AUTZ-04`, `RN-AUTH-ROL-02` a `RN-AUTH-ROL-07`.

---

## 2. Identidad

### API-05 — Contrato de auth

- **Objetivo:** los 17 endpoints de sesión, credenciales, invitaciones y administración de cuentas.
- **Afectados:** ver [modules/auth/tasks.md](../../modules/auth/tasks.md), que lo desglosa en doce tareas a dos carriles.
- **Dependencias:** API-01 a API-04, **DB-14** y `BK-08`.
- **Aceptación:** la definida en ese plan.
- **Contrato:** [auth](../../contratos/auth/api-contract.md).

### API-06 — Identidades funcionales y fichas de Personal

- **Objetivo:** `/api/perfil` para el perfil propio y sus vinculaciones, `/api/usuarios` para las identidades de Usuario y `/api/personal` para las fichas de Personal.
- **Afectados:** módulo de usuarios del backend.
- **Dependencias:** API-05, **DB-06** y **DB-15**, que instalan el estado de la ficha y las columnas objetivo de `usuarios.usuarios`. **Bloquea la invitación de cuentas `PERSONAL`**, que exige una ficha activa previa.
- **Aceptación:** crear una ficha con un documento ya registrado responde `409 DOCUMENTO_DUPLICADO`; modificar el correo de una identidad con cuenta asociada responde `409 CONFLICTO`; el correo se devuelve como solo lectura en `GET /api/perfil`.
- **Contrato:** [usuarios](../../contratos/usuarios/api-contract.md).
- **RN:** `RN-DAT`, `RN-PRS`, `RN-USR-07` a `RN-USR-11`.

---

## 3. Estructura institucional

### API-07 — Unidades, cargos y permisos

- **Objetivo:** `/api/unidades`, `/api/cargos` y `/api/permisos`.
- **Afectados:** módulo de administration del backend.
- **Dependencias:** API-04, API-06 y **DB-03**, **DB-07**, **DB-09**.
- **Aceptación:** asignar un permiso por unidad a una cuenta `PERSONAL` cuyo cargo pertenece a otra unidad responde `422 VALIDACION`; asignarlo a una cuenta `USUARIO` también. Retirar el último permiso global vigente del sistema responde `409 CONFLICTO`.
- **Contrato:** [administration](../../contratos/administration/api-contract.md) §2 y §3.
- **RN:** `RN-UNI`, `RN-PER-08`, `RN-PER-09`, `RN-AUTH-ROL-09`.

### API-08 — Auditoría administrativa

- **Objetivo:** cada operación administrativa deja su registro, y `GET /api/auditoria` lo consulta.
- **Afectados:** módulo de administration del backend.
- **Dependencias:** API-07, **DB-03**.
- **Aceptación:** una asignación de permiso deja una fila con actor, acción, entidad, identificador y momento. **No existe ningún endpoint de escritura sobre la auditoría**, y un intento de modificar un registro no encuentra ruta.
- **Contrato:** [administration](../../contratos/administration/api-contract.md) §5.
- **RN:** `RN-AUD-01` a `RN-AUD-07`.

---

## 4. Catálogos e inventario

### API-09 — Recursos y configuración del laboratorio

- **Objetivo:** `/api/recursos` y `/api/laboratorios`.
- **Afectados:** módulo de resources del backend.
- **Dependencias:** API-04, API-07 y **DB-01**.
- **Aceptación:** un Técnico puede editar un equipo de su unidad pero no crearlo; deshabilitar un recurso `PRINCIPAL` con reservas futuras sin `confirmado` responde `409 CONFLICTO` con el número en `detalles`. Cambiar el horario de la unidad conserva la versión anterior en el histórico.
- **Contrato:** [resources](../../contratos/resources/api-contract.md).
- **RN:** `RN-REC`, `RN-EQP-09`, `RN-DES-06`, `RN-LAB-08`.

### API-10 — Espacios, recursos asociados y campos adicionales

- **Objetivo:** `/api/espacios` completo.
- **Afectados:** módulo de espacios del backend.
- **Dependencias:** API-09, porque asociar un recurso exige que exista.
- **Aceptación:** habilitar un campo `SELECCION` sin ninguna opción habilitada responde `409 CAMPO_SIN_OPCIONES`; asociar un recurso de otra unidad responde `409 UNIDAD_INCOMPATIBLE`. **Ningún endpoint de horario existe** en este módulo.
- **Contrato:** [espacios](../../contratos/espacios/api-contract.md).
- **RN:** `RN-ESP-CAM-02`, `RN-ESP-CAM-03`, `RN-ESP-REC-06`, `RN-ESP-DIS-02`.

### API-11 — Catálogos de investigación

- **Objetivo:** `/api/investigacion` completo, y las vinculaciones propias bajo `/api/perfil`.
- **Afectados:** módulo de researchs del backend.
- **Dependencias:** API-06 y **DB-02**.
- **Aceptación:** crear una vinculación ajena que ya existe inactiva **reactiva esa fila** en lugar de crear otra; desactivar la última vinculación activa devuelve `sin_vinculaciones_activas: true` sin bloquear la operación.
- **Contrato:** [researchs](../../contratos/researchs/api-contract.md).
- **RN:** `RN-INV-05`, `RN-INV-14`, `RN-INV-16`, `RN-ACT`.

### API-12 — Importaciones masivas

- **Objetivo:** `/api/importaciones` en dos pasos: validar y confirmar.
- **Afectados:** módulo de administration del backend.
- **Dependencias:** API-09, API-11 y **DB-03**.
- **Aceptación:** una carga con una sola fila en error devuelve `confirmable: false` y **confirmarla responde `409 CONFLICTO`**; el resultado por fila se conserva aunque no se confirme. Una carga de `EQUIPOS` sin `id_unidad` responde `400 SOLICITUD_INVALIDA`.
- **Contrato:** [administration](../../contratos/administration/api-contract.md) §4.
- **RN:** `RN-IMP-06`, `RN-IMP-09`, `RN-IMP-11`, `RN-IMP-12`.

---

## 5. Reservas

### API-13 — Creación y consulta de reservas

- **Objetivo:** `POST /api/reservas` para los cinco tipos, el listado, el detalle y la disponibilidad.
- **Afectados:** módulo de reservations del backend.
- **Dependencias:** API-10, API-11, **DB-08** y **DB-12**.
- **Aceptación:** crear una reserva solapada responde `409 SOLAPAMIENTO` **por la restricción de la base**, no por una consulta previa. Un Usuario sin vinculación activa recibe `403 VINCULACION_REQUERIDA`.
- **Contrato:** [reservations](../../contratos/reservations/api-contract.md) §2 y §3.
- **RN:** `RN-RES`, `RN-TIP`, `RN-CTX`, `RN-DIS-05`.
- **Aviso:** sin **DB-12** este endpoint puede escribir dos reservas solapadas bajo concurrencia. No se da por correcto hasta cerrarla.

### API-14 — Gestión, propuestas y ejecución

- **Objetivo:** aprobación, rechazo, recursos, propuestas de periodo, ejecución, finalización y cancelación.
- **Afectados:** módulo de reservations del backend.
- **Dependencias:** API-13.
- **Aceptación:** finalizar una reserva de tipo `ESPACIO` responde `409 CONFLICTO`, e iniciar su ejecución responde `409 TIPO_NO_ADMITIDO`: ambas transiciones son automáticas. Finalizar una de recursos sin todos los entregados responde error, no cierre parcial.
- **Contrato:** [reservations](../../contratos/reservations/api-contract.md) §4 a §6.
- **RN:** `RN-APR`, `RN-PROP`, `RN-TIP-PE-25`, `RN-TIP-PE-27`, `RN-TIP-RI-09`.

### API-15 — Órdenes de salida, calendario y exportación

- **Objetivo:** el FGL 030 prellenado, el `.ics` y la exportación del listado.
- **Afectados:** módulo de reservations del backend.
- **Dependencias:** API-14.
- **Aceptación:** la orden de salida **no contiene ningún campo de firma**: los jefes firman sobre el documento impreso. El `.ics` sobre un tipo que no lo admite responde `409 TIPO_NO_ADMITIDO`.
- **Contrato:** [reservations](../../contratos/reservations/api-contract.md) §7 y §8.
- **RN:** `RN-TIP-RC-11` a `RN-TIP-RC-14`, `RN-CAL`.

---

## 6. Procesos automáticos y consulta

### API-16 — Transiciones automáticas de reservas por espacio

- **Objetivo:** las tareas que inician y finalizan una reserva de espacio al llegar su hora.
- **Afectados:** proceso programado del backend.
- **Dependencias:** API-14.
- **Aceptación:** una reserva `APROBADA` pasa a `EN_EJECUCION` al llegar su `hora_inicio` y a `FINALIZADA` al llegar su `hora_fin`. **Detener el proceso no impide reservar un intervalo posterior que no se solapa**: es la prueba de que la disponibilidad no depende de él.
- **Contrato:** no tiene superficie HTTP.
- **RN:** `RN-TIP-PE-25`, `RN-TIP-PE-26`, `RN-TIP-PE-27`, `RN-DIS-11`.

### API-17 — Bandeja y preferencias de notificaciones

- **Objetivo:** `/api/notificaciones` completo.
- **Afectados:** módulo de notifications del backend.
- **Dependencias:** API-04 y **DB-04**, **DB-10**.
- **Aceptación:** consultar una notificación ajena responde `404 NO_ENCONTRADO` sin revelar su existencia; marcar como leída **no altera** el estado de la reserva ni del correo asociado.
- **Contrato:** [notifications](../../contratos/notifications/api-contract.md).
- **RN:** `RN-CON-01`, `RN-EST-04`, `RN-PREF-04`.

### API-18 — Generación y entrega de notificaciones

- **Objetivo:** cada evento de `RN-EVT` produce su ocurrencia, y la tarea programada entrega los correos con su política de reintento.
- **Afectados:** proceso programado del backend y los módulos productores.
- **Dependencias:** API-17.
- **Aceptación:** repetir la misma ocurrencia no genera una segunda notificación; agotar los cinco reintentos deja el envío en `FALLIDO` **sin invalidar la operación de negocio** que lo originó.
- **Contrato:** no tiene superficie HTTP.
- **RN:** `RN-NOT-05`, `RN-COR-03`, `RN-COR-04`, `RN-INT-04`.

### API-19 — Reportes y exportación

- **Objetivo:** `/api/reportes` completo.
- **Afectados:** módulo de reports del backend.
- **Dependencias:** API-13, porque sin reservas no hay qué reportar.
- **Aceptación:** un elemento sin horario de atención definido devuelve `porcentaje_ocupacion: null` y su total de horas, **nunca un cero**. `solicitudes` incluye todos los estados; `ocupacion` solo tres.
- **Contrato:** [reports](../../contratos/reports/api-contract.md).
- **RN:** `RN-OCU-04`, `RN-OCU-05`, `RN-OCU-06`, `RN-EXP`.
