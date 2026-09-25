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

### API-06 — Identidades funcionales y fichas de Personal · **cerrada**

- **Objetivo:** `/api/perfil` para el perfil propio y sus vinculaciones, `/api/usuarios` para las identidades de Usuario y `/api/personal` para las fichas de Personal.
- **Afectados:** módulo de usuarios del backend.
- **Dependencias:** API-05, **DB-06** y **DB-15**, que instalan el estado de la ficha y las columnas objetivo de `usuarios.usuarios`. **Bloquea la invitación de cuentas `PERSONAL`**, que exige una ficha activa previa.
- **Aceptación:** crear una ficha con un documento ya registrado responde `409 DOCUMENTO_DUPLICADO`; modificar el correo de una identidad con cuenta asociada responde `409 CONFLICTO`; el correo se devuelve como solo lectura en `GET /api/perfil`.
- **Contrato:** [usuarios](../../contratos/usuarios/api-contract.md).
- **RN:** `RN-DAT-01`, `RN-DAT-02`, `RN-PRS-05` (usuarios); `RN-USR-01`, `RN-USR-02`, `RN-USR-03`, `RN-USR-06`, `RN-USR-07` (administration); `RN-AUTH-ID-02`, `RN-AUTH-ID-03`, `RN-AUTH-ID-12`, `RN-AUTH-ROL-09` (auth).
- **Alcance:** §2.1, §2.2, §5 y §6. §2.3, §3 y §4 (perfiles, vinculaciones, actualización inicial con vinculación) quedan para `API-11`, que implementa researchs; `GET /api/perfil` devuelve perfiles y vinculaciones vacíos hasta entonces. Una cuenta `PERSONAL` recibe `404 NO_ENCONTRADO` en `GET /api/perfil`: el perfil es concepto de Usuario.
- **Resultado:** `backend/app/modules/usuarios/` (`router.py` perfil propio, `router_admin.py` con `usuarios.administrar` global, `schemas.py`, `service.py`, `repository.py`) + códigos propios `DOCUMENTO_DUPLICADO`/`TELEFONO_DUPLICADO`/`VINCULACION_DUPLICADA` en `errors.py`. `auth.registrar` delega la creación de identidad en `usuarios.service` (límite 4). 13 pruebas en `test_usuarios.py` (T-USR-01/02/03/04/06/07/08 + guarda RN-AUTH-ROL-09 y UF-USR-04) en verde contra `reservas_test`; las 13 de auth siguen verdes como regresión. Se corrigieron las citas de `tests.md` de usuarios, que apuntaban a reglas inexistentes con esos números.

---

## 3. Estructura institucional

### API-07 — Unidades, cargos y permisos · **cerrada**

- **Objetivo:** `/api/unidades`, `/api/cargos` y `/api/permisos`.
- **Afectados:** módulo de administration del backend.
- **Dependencias:** API-04, API-06 y **DB-03**, **DB-07**, **DB-09**.
- **Aceptación:** asignar un permiso por unidad a una cuenta `PERSONAL` cuyo cargo pertenece a otra unidad responde `422 VALIDACION`; asignarlo a una cuenta `USUARIO` también. Retirar el último permiso global vigente del sistema responde `409 CONFLICTO`.
- **Contrato:** [administration](../../contratos/administration/api-contract.md) §2 y §3.
- **RN:** `RN-UNI-01`, `RN-UNI-02`, `RN-UNI-03`, `RN-UNI-04`, `RN-UNI-05`, `RN-PER-03`, `RN-PER-04`, `RN-PER-05`, `RN-PER-06`, `RN-PER-08`, `RN-PER-09` (administration); `RN-AUTH-ROL-06`, `RN-AUTH-ROL-09` (auth).
- **Alcance:** §2 (unidades y cargos) y §3 (permisos). §4 (importaciones) es `API-12` y §5 (auditoría) es `API-08`.
- **Decisiones:** `DELETE /api/permisos/cuentas/{id}/{codigo}` retira todas las asignaciones de ese código (global y por unidad), auditando cada fila; `404` si no hay ninguna. `ambito` de `GET /api/permisos` sale de la tabla de ámbito habitual de `auth/data-model.md` (solo display). `GET` lista los 14 códigos; `POST` rechaza con `422` un código deshabilitado.
- **Resultado:** `backend/app/modules/administration/` (`router_estructura.py` con `unidades.administrar`, `router_permisos.py` con `permisos.asignar`, `schemas.py`, `service.py`, `repository.py`; sin modelos nuevos, BK-08 ya los mapeó). Cada escritura audita en la misma transacción (`CREAR/EDITAR/CAMBIAR_ESTADO_UNIDAD`, `CREAR/EDITAR_CARGO`, `ASIGNAR/RETIRAR_PERMISO`). 9 pruebas en `test_administration.py` (T-ADM-01..06 más jerarquía, catálogo y unidad activa) en verde; suite completa 35/35. Se corrigieron 4 citas de `tests.md` de administration.

### API-08 — Auditoría administrativa · **cerrada**

- **Objetivo:** cada operación administrativa deja su registro, y `GET /api/auditoria` lo consulta.
- **Afectados:** módulo de administration del backend.
- **Dependencias:** API-07, **DB-03**.
- **Aceptación:** una asignación de permiso deja una fila con actor, acción, entidad, identificador y momento. **No existe ningún endpoint de escritura sobre la auditoría**, y un intento de modificar un registro no encuentra ruta.
- **Contrato:** [administration](../../contratos/administration/api-contract.md) §5.
- **RN:** `RN-AUD-01` a `RN-AUD-07`.
- **Resultado:** `GET /api/auditoria` (permiso `unidades.administrar` global; filtros `entidad`, `entidad_id`, `actor_cuenta_id`, `accion`, `desde`, `hasta`; orden `created_at` desc por defecto) + modelo `Auditoria` en `db/models/administration.py` (solo lectura; las escrituras siguen por `core/audit.py`). 3 pruebas (T-ADM-07/08/09) en verde; suite completa 38/38. Con esto cierra la Fase 2: BK-09, API-06, API-07 y API-08.

---

## 4. Catálogos e inventario

### API-09 — Recursos y configuración del laboratorio · **cerrada**

- **Objetivo:** `/api/recursos` y `/api/laboratorios`.
- **Afectados:** módulo de resources del backend.
- **Dependencias:** API-04, API-07 y **DB-01**.
- **Aceptación:** un Técnico puede editar un equipo de su unidad pero no crearlo; deshabilitar un recurso `PRINCIPAL` con reservas futuras sin `confirmado` responde `409 CONFLICTO` con el número en `detalles`. Cambiar el horario de la unidad conserva la versión anterior en el histórico.
- **Contrato:** [resources](../../contratos/resources/api-contract.md).
- **RN:** `RN-REC`, `RN-EQP-09`, `RN-DES-06`, `RN-LAB-08`.
- **Resultado:** modelos `db/models/recursos.py` (`Recursos`, `Equipos`, `Mobiliarios`, `OtrosRecursos`, `CategoriasEquipos`) + módulo `modules/resources/` completo (`schemas`, `repository`, `service`, `router`), 11 endpoints en `router_recursos` (`/api/recursos`) y `router_laboratorios` (`/api/laboratorios`). El efecto mínimo de `RN-CAN-04`/`RN-CAN-05` (cancelar/retirar reservas al deshabilitar un recurso `PRINCIPAL`/`ADICIONAL`) se implementa aquí porque el servicio de escritura de reservations (`API-13`/`API-14`) todavía no existe; se documenta en `service.py` para moverse allí cuando exista. De paso corrige un bug real en `core/audit.py`: `json.dumps` no toleraba tipos `date`/`time` (afectaba a cualquier módulo que auditara ese tipo de dato), y añade la validación `409 UNIDAD_INCOMPATIBLE` de §2.7 (recurso asociado a un espacio de otra unidad; inerte hoy porque `espacios`/`API-10` no existe todavía, correcta para cuando empiece a escribir). Verificado por HTTP real contra el contenedor: creación de mobiliario/equipo con los permisos correctos y su rechazo cruzado (`403`), edición con lista blanca de campos por tipo, listado con filtro `reservable` excluyendo equipos acreditados (`RN-REC-11`), configuración de laboratorio creada por primera vez con versión en histórico (`RN-LAB-08`), impacto y deshabilitación con confirmación (conteo, `409` sin confirmar, `200` con cancelación real de una reserva `PRINCIPAL` verificada en BD), reasignación de unidad por el Administrador global y su rechazo para el Técnico, y el nuevo `409 UNIDAD_INCOMPATIBLE` con una asociación a espacio real sembrada para la prueba. Todos los datos de prueba (unidades, cuentas, recurso, reserva, espacio) se limpiaron después.

### API-10 — Espacios, recursos asociados y campos adicionales · **cerrada**

- **Objetivo:** `/api/espacios` completo.
- **Afectados:** módulo de espacios del backend.
- **Dependencias:** API-09, porque asociar un recurso exige que exista.
- **Aceptación:** habilitar un campo `SELECCION` sin ninguna opción habilitada responde `409 CAMPO_SIN_OPCIONES`; asociar un recurso de otra unidad responde `409 UNIDAD_INCOMPATIBLE`. **Ningún endpoint de horario existe** en este módulo.
- **Contrato:** [espacios](../../contratos/espacios/api-contract.md).
- **RN:** `RN-ESP-CAM-02`, `RN-ESP-CAM-03`, `RN-ESP-REC-06`, `RN-ESP-DIS-02`.
- **Resultado:** módulo `modules/espacios/` completo (`schemas`, `repository`, `service`, `router`), 14 endpoints bajo `/api/espacios` (los 14 flujos del contrato), sin crear modelos nuevos: reutiliza los que `BK-08` ya generó en `db/models/reservas.py` (`Espacios`, `EspacioRecursos`, `EspacioCampos`, `EspacioCampoOpciones`, `ReservaEspacio`). El efecto mínimo de `RN-CAN-04` (cancelar la reserva al deshabilitar el espacio) se implementa aquí por la misma razón documentada en `API-09`: el servicio de escritura de reservations todavía no existe. El listado (§2.3) varía por rol —Usuario solo ve espacios habilitados, Técnico también los deshabilitados de su propia unidad, Administrador sin restricción— resuelto con una cláusula de visibilidad separada del filtro explícito del cliente, para que combinarlos nunca abra una fuga silenciosa. Añade dos códigos de error propios a `core/errors.py`: `NombreDuplicado` y `CampoSinOpciones`. Verificado por HTTP real contra el contenedor: creación de un espacio con recurso y campo `SELECCION` asociados atómicamente, `409 CAMPO_SIN_OPCIONES`/`NOMBRE_DUPLICADO`/`UNIDAD_INCOMPATIBLE` en la creación, asociar/retirar/reasociar un recurso, editar y reordenar campos, agregar opciones, la regla de no poder deshabilitar la última opción habilitada de un campo habilitado (y su inversa al reactivar el campo), impacto y deshabilitación del espacio con confirmación y cancelación real de una reserva por espacio verificada en BD (conservando recursos y campos asociados, RN-ESP-HAB-04), la visibilidad por rol con cuentas Usuario/Técnico reales, y el `403` de un Usuario intentando administrar. Todos los datos de prueba se limpiaron después. `tools/validar.py` en 0 fallas.

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

### API-13 — Arquitectura, creación, edición y consulta de reservas

- **Objetivo:** establecer la [arquitectura Strategy de Reservations](../../modules/reservations/architecture.md) e implementar creación de los cinco tipos, edición en SOLICITADA, listado, detalle, disponibilidad y operaciones de preparación de lista de espera. Incluye el componente compartido de generación/persistencia de FGL 030 necesario para la creación autoaprobada; API-14 lo reutiliza al aprobar manualmente.
- **Afectados:** `backend/app/modules/reservations/`: `router.py`, `schemas.py`, `service.py`, `repository.py`, `domain/reserva.py`, `strategies/` y `policies/`; pruebas del módulo bajo `backend/tests/`.
- **Dependencias:** API-10, API-11, **DB-08** y **DB-12**.
- **Implementación:** `Reserva` es Context; `ReservationStrategy` define validación y determinación de cambios. Selector con `EspacioStrategy`, `RecursoInternoStrategy`, `RecursoCampusStrategy`, `RecursoExternoStrategy` y `ListaEsperaStrategy`. Policies de acceso, contexto, apoyo, horario, disponibilidad y propuestas; `PrestamoFisicoPolicy` compartida por campus/externo, sin sexta Strategy. El servicio controla acceso/transacción y usa el repositorio; Context/Strategy no ejecutan SQL.
- **Aceptación:**
  - Se cumplen cuerpos y respuestas de §2 y §3. Solapamiento temporal: `409 SOLAPAMIENTO`; compromiso físico ajeno incluso con otras fechas: `409 CONFLICTO`, con protección de DB-12. Usuario sin vinculación activa: `403 VINCULACION_REQUERIDA`.
  - Edición directa solo en SOLICITADA; revalidación y efectos atómicos, sin campos inmutables ni cambios parciales. El retiro automático de complementarios conserva historial; no cancela el espacio ni restaura recursos al cancelar el préstamo.
  - Lista de espera: viabilidad explícita, adjuntos conforme al contrato, formulario posterior a viabilidad y partes por actor. Cambiar descripción invalida evaluación y revisión como especificado; no crea estados ni tablas nuevos.
  - La separación de capas y las cinco estrategias se verifica con los casos de servicio y contrato de [tests.md](../../modules/reservations/tests.md), sin duplicar reglas particulares en el router o el servicio.
- **Contrato:** [reservations](../../contratos/reservations/api-contract.md) §2 y §3; la creación autoaprobada genera y conserva la FGL conforme a §4.1 y §7, mediante el componente que reutiliza API-14.
- **RN:** `RN-RES-12`, `RN-PRO-06`, `RN-DIS-05`, `RN-DIS-06`, `RN-TIP-PE-28`, `RN-TIP-PLE-03`, `RN-TIP-PLE-04`, `RN-TIP-PLE-09`.
- **Cierre:** incluye probar creación autoaprobada y su FGL inmutable; no depende de una tarea posterior para cerrar ese caso. Las garantías de DB-12 son obligatorias.

### API-14 — Gestión, propuestas y ejecución por tipo

- **Objetivo:** completar las estrategias con aprobación, rechazo, recursos, propuestas, ejecución, finalización y cancelación; generar y persistir FGL 030 al aprobar campus/externo dentro del proceso de salida.
- **Afectados:** servicio, estrategias, políticas y repositorio de Reservations; pruebas de servicio/contrato bajo `backend/tests/`.
- **Dependencias:** API-13.
- **Aceptación:**
  - Agregar/retirar genéricos solo en ESPACIO y RECURSO_INTERNO, en los estados y roles admitidos. El principal de interno no se retira; retiro manual sin historial ni metadatos. Otros tipos: `409 TIPO_NO_ADMITIDO`.
  - En APROBADA solo espacio/interno negocian periodo; al aceptar se revalida y conserva aprobación, o se revierte todo. Campus/externo bloquean datos de la FGL generada, incluidas propuestas anteriores.
  - Lista de espera recibe material y aprueba en una operación atómica; inicia fabricación/prestación sin recursos y finaliza con horas válidas, sin entrega/devolución física.
  - Campus/externo generan FGL al aprobar, también en autoaprobación, dentro del mismo proceso que registra entrega e inicio de ejecución por las rutas actuales. Orden inmutable, sin regeneración ni versiones; composición fija desde la salida hasta devolución. El retiro por deshabilitación solo aplica antes de ese proceso.
  - Iniciar o finalizar manualmente espacio/interno responde `409 TIPO_NO_ADMITIDO`. Préstamos requieren devolución completa para finalizar. Operación incompatible con estado: `409 ESTADO_INCOMPATIBLE`; los demás errores son los específicos del contrato.
- **Contrato:** [reservations](../../contratos/reservations/api-contract.md) §4 a §6; persistencia de la orden consultada en §7.
- **RN:** `RN-TIP-PE-21`, `RN-TIP-RI-10`, `RN-PROP-05`, `RN-TIP-PLE-05`, `RN-TIP-PLE-07`, `RN-TIP-PLE-08`, `RN-TIP-RC-07`, `RN-TIP-RE-07`, `RN-CAN-06`.

### API-15 — Consulta de órdenes, calendario y exportación

- **Objetivo:** consultar y exportar la FGL 030 ya generada por API-13/API-14, el `.ics` y el listado.
- **Afectados:** router, esquemas, servicio y consultas del repositorio de Reservations; pruebas de contrato bajo `backend/tests/`.
- **Dependencias:** API-14.
- **Aceptación:** GET de orden/PDF usa snapshots originales, sin generar, modificar o versionar la orden. No captura firmas: se diligencian en papel. Tipo ajeno a FGL: `409 TIPO_NO_ADMITIDO`; orden aún no generada: `404 NO_ENCONTRADO`. El `.ics` admite únicamente espacio/interno y conserva los errores del contrato. Exportación respeta formato, filtros y ámbito autorizado.
- **Contrato:** [reservations](../../contratos/reservations/api-contract.md) §7 y §8.
- **RN:** `RN-TIP-RC-07`, `RN-TIP-RE-07`, `RN-TIP-RC-14`, `RN-TIP-RE-14`, `RN-CAL-01`, `RN-CAL-02`.

---

## 6. Procesos automáticos y consulta

### API-16 — Transiciones automáticas de espacio e interno

- **Objetivo:** ejecutar por el servicio las decisiones horarias de EspacioStrategy y RecursoInternoStrategy, sin entrega/devolución física.
- **Afectados:** proceso programado del backend y casos de uso del servicio de Reservations; pruebas de servicio e integración.
- **Dependencias:** API-14.
- **Aceptación:**
  - ESPACIO aprobado inicia en hora_inicio. Si se aprueba durante la franja, aprobación e inicio son inmediatos y conjuntos. En hora_fin, SOLICITADA pasa a CANCELADA y APROBADA/EN_EJECUCION a FINALIZADA.
  - RECURSO_INTERNO aprobado inicia en hora_inicio y en ejecución finaliza en hora_fin. Desde EN_EJECUCION no se cancela. No se crean registros de entrega/devolución.
  - RECHAZADA y CANCELADA no cambian automáticamente. Detener el proceso no bloquea intervalos posteriores no solapados. La carrera con retiro por préstamo respeta DB-12 y no retira complementarios de un espacio ya en ejecución.
- **Contrato:** sin endpoint propio; [reservations](../../contratos/reservations/api-contract.md) §4.1 y §10; UF-RES-21 y UF-RES-22.
- **RN:** `RN-TIP-PE-25`, `RN-TIP-PE-27`, `RN-TIP-PE-28`, `RN-TIP-RI-08`, `RN-TIP-RI-09`, `RN-TIP-RI-13`, `RN-DIS-11`.

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
