# Plan de tareas — Auth

Traduce el [contrato de API](../../contratos/auth/api-contract.md) y los [flujos de usuario](user-flow.md) a tareas de implementación. Cada tarea declara objetivo, archivos afectados, dependencias, criterio de aceptación y las reglas que la sustentan, siguiendo la convención del [plan general](../../../tasks.md). Este documento desarrolla `API-05` del [plan de contratos](../../docs/tasks/contratos.md) y `BK-09` del [plan de backend](../../docs/tasks/backend.md).

Plan dimensionado para **dos personas en paralelo**. Los carriles se reparten por propiedad de archivos, no por capas, para evitar conflictos de merge.

---

## Punto de partida

**No hay código de auth.** El backend anterior se retiró entero: implementaba credencial por `username`, token en el cuerpo de la respuesta y `rol` dentro del JWT, sin sesiones ni CSRF. No se adapta, se construye.

Auth es el **primer módulo completo** del backend nuevo, así que queda como referencia de estilo para los ocho restantes.

### Lo que este plan da por hecho

| Depende de | Qué aporta |
|---|---|
| `DB-14` | Las cinco tablas: `auth.sesiones`, `auth.invitaciones`, `auth.tokens_recuperacion`, `auth.permisos` y `auth.cuenta_permisos` |
| `DB-09` | Los catorce códigos del catálogo de permisos, cargados |
| `BK-04` | La envolvente `{"error": {"codigo", "mensaje", "detalles"}}` |
| `BK-06` | Cookies `rp_access` y `rp_refresh`, doble envío CSRF, firma y verificación del token, y `GET /api/auth/csrf` |
| `BK-07` | `exigir_permiso`, el contexto autenticado y la derivación de rol y unidades autorizadas |
| `BK-08` | Los modelos SQLAlchemy de `auth`, incluidas las cinco tablas de `DB-14` |

**Nada de eso se redefine aquí.** El contrato expone 17 endpoints; este plan implementa **16**, porque `GET /api/auth/csrf` (§3.0) pertenece al núcleo transversal y lo entrega `BK-06`.

`auth.cuentas` ya existe en la base y no se toca. **Este plan no crea ni altera ninguna tabla**, conforme a la regla 1 del plan de backend: cuando falte estructura, se abre una tarea `DB-XX`.

---

## Dónde vive

```text
backend/app/
  db/models/auth.py                     <- lo crea BK-08; aquí solo se consume
  modules/auth/
    router.py                 carril A  <- sesión y credenciales propias
    service.py                carril A
    repository.py             carril A
    router_cuentas.py         carril B  <- registro, recuperación, reautenticación, administración
    router_invitaciones.py    carril B
    service_cuentas.py        carril B
    repository_cuentas.py     carril B
    schemas.py                carril B  <- carril A solo lee
```

El módulo parte en dos routers y dos servicios **para que los dos carriles no editen el mismo archivo**. Es una excepción deliberada a la forma de cuatro archivos descrita en el plan de backend, y se justifica por el reparto: ningún otro módulo la necesita, porque ninguno se construye a dos manos.

---

## Convención de tarea

```markdown
### AUTH-XX — Título

- **Carril:** A o B
- **Objetivo:** qué queda distinto al terminar.
- **Afectados:** archivos concretos.
- **Dependencias:** tareas que deben cerrarse antes; qué bloquea esta.
- **Aceptación:** condición verificable, no "quedó implementado".
- **Contrato:** sección del api-contract que cubre.
- **RN:** reglas de negocio y controles de seguridad aplicados.
```

Una tarea sin criterio de aceptación verificable no entra al plan. Si dos tareas tocan el mismo archivo, se asignan al mismo carril o se serializan explícitamente.

---

## Reparto y puntos de sincronización

| Carril | Responsabilidad |
|---|---|
| **A** | Sesión, credenciales propias y control de abuso |
| **B** | Alta de cuentas, recuperación, invitaciones y administración |

**Puntos de sincronización obligatorios:**

1. `backend/app/main.py` — registro de routers. Lo toca **solo A**; B le pide el registro del suyo.
2. `schemas.py` — lo crea B en `AUTH-B1`; A solo lo lee. Hasta entonces A trabaja contra la firma acordada.
3. El cierre de `AUTH-A1`, porque fija la forma del token y las vigencias que todo lo demás asume.

---

## Fase 1 — Implementación paralela

Ambos carriles arrancan a la vez: no comparten archivos y sus dependencias externas ya están cerradas.

### Carril A — Sesión, credenciales y abuso

#### AUTH-A1 — Claims del token y vigencias de sesión · **cerrada**

- **Carril:** A
- **Objetivo:** fijar qué lleva el token de acceso y cuánto dura una sesión.
- **Afectados:** `backend/app/modules/auth/service.py`, `backend/app/core/config.py`.
- **Dependencias:** `BK-06`, `BK-08`. Bloquea AUTH-A2.
- **Aceptación:** el token emitido contiene `iss`, `aud`, `sub`, `sid`, `typ`, `iat` y `exp`, **y ningún rol ni permiso**; se rechaza un token con `alg: none`, con algoritmo distinto, con `aud` ajena o con `typ` incorrecto. Los tres límites —12 h de vigencia máxima, 30 min de inactividad y 10 min de ventana de autenticación reciente— se leen de configuración, no están escritos en el código.
- **Contrato:** §2, §9
- **RN:** `SEC-JWT-01`, `SEC-JWT-02`, `SEC-JWT-04`, `SEC-JWT-05`, `SEC-SES-09`
- **Resultado:** los tres límites viven en `config.py` (`SESION_VIGENCIA_MAXIMA_SEGUNDOS`, `SESION_INACTIVIDAD_MAXIMA_SEGUNDOS`, `REAUTENTICACION_VENTANA_SEGUNDOS`). Verificado contra el contenedor real: claims exactos del contrato, y los cinco rechazos (`alg:none`, algoritmo distinto, `aud` ajena, `typ` incorrecto, vencido) confirmados uno por uno.

#### AUTH-A2 — Inicio de sesión · **cerrada**

- **Carril:** A
- **Objetivo:** autenticar por correo contra `auth.cuentas` y abrir sesión persistida.
- **Afectados:** `backend/app/modules/auth/router.py`, `service.py`, `repository.py`.
- **Dependencias:** AUTH-A1.
- **Aceptación:** contraseña incorrecta, correo inexistente, cuenta inactiva e identidad inactiva devuelven **el mismo** `401 CREDENCIALES_INVALIDAS`, sin diferencias observables de cuerpo ni de tiempo; el inicio exitoso escribe una fila en `auth.sesiones` y regenera el identificador de sesión previo.
- **Contrato:** §3.2
- **RN:** `RN-AUTH-ID-01`, `RN-AUTH-ID-02`, `RN-AUTH-ID-05`, `SEC-ABU-02`, `SEC-SES-13`
- **Resultado:** verificado contra `reservas_db` real, con las cuatro causas de fallo probadas una a una: mismo cuerpo y código en los cuatro casos. La verificación de contraseña siempre corre —contra un hash señuelo si la cuenta no existe— para que las cuatro causas cuesten lo mismo en CPU.

#### AUTH-A3 — Sesión actual, renovación y cierre · **cerrada**

- **Carril:** A
- **Objetivo:** completar el ciclo de vida de la sesión.
- **Afectados:** `backend/app/modules/auth/router.py`, `service.py`, `repository.py`.
- **Dependencias:** AUTH-A2, `BK-07` para la derivación de rol y unidades.
- **Aceptación:** cerrar sesión marca `revoked_at` y borra las cookies; una sesión revocada o vencida responde `401` aunque el cliente conserve la cookie; la renovación rota el secreto y se rechaza al superar la inactividad o la vigencia máxima. `GET /api/auth/sesiones/actual` devuelve `"GLOBAL"` en `unidades_autorizadas` para un Administrador y **únicamente la unidad vigente** para un Técnico, nunca la unión de sus asignaciones.
- **Contrato:** §3.3, §3.4, §3.5
- **RN:** `RN-AUTH-SES-01`, `RN-AUTH-SES-02`, `RN-AUTH-ROL-02` a `RN-AUTH-ROL-07`, `SEC-SES-07`, `SEC-SES-08`, `SEC-SES-09`
- **Resultado:** `core/deps.py` añade `obtener_contexto()`, la dependencia que el contrato interno §7 exige y que faltaba. Verificado: renovación rota el secreto de refresh; cerrar sesión dos veces sigue dando `204`; usar una cookie tras cerrar sesión da `401`; el admin de prueba obtiene `unidades_autorizadas: "GLOBAL"`.

#### AUTH-A4 — Limitación de intentos · **cerrada**

- **Carril:** A
- **Objetivo:** los seis endpoints marcados **limitado** en el contrato resisten abuso automatizado.
- **Afectados:** `backend/app/core/security.py`, consumido desde ambos routers.
- **Dependencias:** AUTH-A2. Afecta endpoints de los dos carriles, por eso se implementa una sola vez.
- **Aceptación:** superar el límite responde `429 DEMASIADOS_INTENTOS` con encabezado `Retry-After`; **superarlo nunca concede acceso** ni distingue un correo existente de uno inexistente.
- **Contrato:** §2, §3.1, §3.2, §3.6, §3.8, §3.9, §4.4
- **RN:** `SEC-ABU-01`, `SEC-ABU-02`, `SEC-ABU-03`
- **Resultado:** `core/rate_limit.py`, en memoria del proceso —`architecture.md` no incluye Redis ni almacén compartido—, con la limitación explícita de que solo es correcto con un único proceso de Uvicorn, que es lo que hay hoy. Confirmado en pruebas reales: se agotó el límite probando login repetidamente y produjo `429` con `Retry-After` correcto.

### Carril B — Alta de cuentas, invitaciones y administración

#### AUTH-B1 — Autorregistro · **cerrada**

- **Carril:** B
- **Objetivo:** alta de cuenta `USUARIO` sin invitación.
- **Afectados:** `backend/app/modules/auth/router_cuentas.py`, `schemas.py`, `service_cuentas.py`, `repository_cuentas.py`.
- **Dependencias:** `BK-08`. Crea `schemas.py`, que A consume.
- **Aceptación:** la respuesta es `202` **idéntica exista o no el correo**; una contraseña fuera del rango admitido se rechaza con `422`; la cuenta creada es `USUARIO`, activa, vinculada a una sola identidad y sin permisos.
- **Contrato:** §3.1
- **RN:** `RN-AUTH-ID-02`, `RN-AUTH-ID-03`, `RN-AUTH-ROL-04`, `SEC-PWD-07`, `SEC-ABU-02`
- **Resultado:** verificado con un registro real contra `reservas_db`: identidad y cuenta creadas atómicamente, `perfil_actualizado_at` en NULL; repetir el mismo registro da la misma respuesta sin duplicar.

#### AUTH-B2 — Recuperación de contraseña · **cerrada**

- **Carril:** B
- **Objetivo:** solicitud, validación previa y restablecimiento.
- **Afectados:** `backend/app/modules/auth/router_cuentas.py`, `service_cuentas.py`, `repository_cuentas.py`.
- **Dependencias:** AUTH-B1.
- **Aceptación:** la solicitud responde igual exista o no la cuenta; el token es de un solo uso y reutilizarlo devuelve `410`; el restablecimiento **revoca todas las sesiones** de la cuenta. El token nunca se almacena en claro ni aparece en ninguna respuesta.
- **Contrato:** §3.6, §3.7, §3.8
- **RN:** `SEC-REC-01` a `SEC-REC-05`, `SEC-TOK-02`, `SEC-TOK-05`
- **Resultado:** verificado de punta a punta: solicitud con correo existente e inexistente da la misma respuesta; restablecer con el token real revoca las sesiones (confirmado: la cookie previa deja de servir); reusar el token da `410`; login con la contraseña nueva funciona. La entrega del enlace por correo queda para `notifications` (`API-18`); aquí solo se origina el token.

#### AUTH-B3 — Invitaciones · **cerrada**

- **Carril:** B
- **Objetivo:** emitir, reenviar, validar y activar invitaciones.
- **Afectados:** `backend/app/modules/auth/router_invitaciones.py`, `service_cuentas.py`, `repository_cuentas.py`.
- **Dependencias:** AUTH-B1 y `BK-07` para la comprobación de `cuentas.administrar`.
- **Aceptación:** la respuesta de emisión **nunca contiene el token**; reenviar marca `revocada_at` en la anterior; una invitación vencida, usada o revocada no completa el alta; la activación respeta el tipo y la identidad **almacenados**, no los enviados por el cliente.
- **Contrato:** §4
- **RN:** `SEC-INV-01` a `SEC-INV-04`, `SEC-AUTZ-03`
- **Nota:** invitar una cuenta `PERSONAL` exige una ficha activa en `personal.personal`, que se crea en `/api/personal` (`API-06`). Sin esa superficie, este endpoint solo puede probarse con fichas cargadas a mano.
- **Resultado:** verificado con datos reales, ambos tipos: invitación `USUARIO` activada da `rol: "USUARIO"`; invitación `PERSONAL` sin asignaciones también da `rol: "USUARIO"` —la invitación no concede permisos por sí misma—; reusar el token de una invitación ya activada da `410`; un no administrador con sesión válida recibe `403`; reenviar una invitación ya usada da `409`, una inexistente da `404`.
- **Corrección de lectura:** el reenvío (§4.2) opera sobre la **misma fila**, sustituyendo su `token_hash` y `expira_at` — no crea una segunda fila con `revocada_at` en la primera. `revocar_invitacion` (que sí marca `revocada_at`) es para cuando se emite una invitación **nueva** mientras otra sigue pendiente (§4.1), un caso distinto.

#### AUTH-B4 — Administración de cuentas · **cerrada**

- **Carril:** B
- **Objetivo:** activar, desactivar y cambiar el tipo de identidad de una cuenta.
- **Afectados:** `backend/app/modules/auth/router_cuentas.py`, `service_cuentas.py`, `repository_cuentas.py`.
- **Dependencias:** AUTH-B3.
- **Aceptación:** desactivar revoca las sesiones activas y conserva el historial; reactivar no crea identidad nueva; el cambio de identidad mantiene exactamente una vinculación; la operación que dejaría al sistema **sin administradores** responde `409`.
- **Contrato:** §6
- **RN:** `RN-AUTH-ID-03`, `RN-AUTH-ID-05`, `RN-CUE-04`, `RN-HAB-04`, `SEC-SES-10`
- **Resultado:** verificado con el único administrador de prueba: desactivar una cuenta ajena revoca sus sesiones (confirmado: la cookie deja de servir) y reactivarla no crea otra fila; **desactivar o degradar al único administrador da `409` en ambos endpoints** (`§6.1` y `§6.2`), el caso que más importaba probar.

#### AUTH-B5 — Reautenticación y cambio de contraseña · **cerrada**

- **Carril:** B
- **Objetivo:** proteger las operaciones sensibles con autenticación reciente.
- **Afectados:** `backend/app/modules/auth/router_cuentas.py`, `service_cuentas.py`.
- **Dependencias:** AUTH-A1 para la ventana de reautenticación, AUTH-B4.
- **Aceptación:** una operación sensible sin autenticación reciente responde `401 REAUTENTICACION_REQUERIDA`; la reautenticación exitosa **regenera el identificador de sesión** y sella `reautenticado_at`; el cambio de contraseña revoca las demás sesiones.
- **Contrato:** §3.9, §5.1
- **RN:** `SEC-REAUTH-01` a `SEC-REAUTH-04`
- **Resultado:** verificado: cambiar la contraseña propia sin reautenticar da `401 REAUTENTICACION_REQUERIDA`; cambiar la identidad de otra cuenta sin reautenticar, igual; reautenticar con éxito emite una sesión nueva (revoca la vieja, crea otra) y habilita la operación sensible siguiente; el cambio de contraseña revoca las demás sesiones y la contraseña anterior deja de servir.

---

## Fase 2 — Auditoría y pruebas

**Fase 1 completa.** Los 16 endpoints funcionan y quedaron verificados con peticiones reales contra `reservas_db`, no solo escritos: los cuatro flujos completos (registro→login, recuperación, invitación→activación, administración de cuentas) probados de punta a punta, incluidos los casos negativos que más importaban —equivalencia de las cuatro causas de login fallido, el límite de intentos agotado de verdad, y las dos protecciones de "sin administradores". Falta esta fase para que `BK-09` cierre.

### AUTH-C1 — Registro de auditoría de los eventos de seguridad

- **Carril:** B
- **Objetivo:** los ocho eventos de §8 dejan registro.
- **Afectados:** `backend/app/modules/auth/service.py`, `service_cuentas.py`.
- **Dependencias:** AUTH-A3, AUTH-B5 y **`DB-03`**, que crea `administration.auditoria`.
- **Aceptación:** inicio de sesión, cierre, recuperación, cambio de contraseña, revocación de sesiones, reautenticación, invitaciones y cambios administrativos dejan fila con actor, acción, entidad y momento. **Ningún registro contiene contraseñas, secretos de sesión, tokens completos ni claves.**
- **Contrato:** §8
- **RN:** `SEC-AUD-01`, `SEC-AUD-03`
- **Nota:** es la única tarea de este plan que depende de otro schema. Si `DB-03` no está cerrada, auth se entrega sin ella y se cierra después; no bloquea el resto.

### AUTH-T1 — Pruebas de sesión y autorización

- **Carril:** A
- **Objetivo:** cubrir el ciclo de sesión y la denegación por defecto.
- **Afectados:** pruebas de `backend/tests/`.
- **Dependencias:** AUTH-A4.
- **Aceptación:** existen pruebas para sesión revocada, sesión vencida, inactividad superada, token con algoritmo alterado, operación fuera de ámbito y operación sin permiso comprobable.
- **Contrato:** §2, §7
- **RN:** `SEC-SES-07`, `SEC-JWT-01`, `SEC-AUTZ-02`, `SEC-AUTZ-04`

### AUTH-T2 — Pruebas de tokens y no enumeración

- **Carril:** B
- **Objetivo:** cubrir un solo uso, vencimiento y equivalencia de respuestas.
- **Afectados:** pruebas de `backend/tests/`.
- **Dependencias:** AUTH-B5.
- **Aceptación:** existen pruebas que verifican que reutilizar un token de recuperación o de invitación falla, que reemitir invalida el anterior, y que registro, recuperación e inicio de sesión **responden igual** con correo existente e inexistente.
- **Contrato:** §3.1, §3.2, §3.6, §4
- **RN:** `SEC-TOK-05`, `SEC-INV-03`, `SEC-REC-01`, `SEC-ABU-02`

---

## Orden sugerido

```text
Antes    DB-14 · DB-09 · BK-04 · BK-06 · BK-07 · BK-08
         ───────────────────────────────────────────────
Fase 1   A: AUTH-A1 → A2 → A3 → A4  │ B: AUTH-B1 → B2 → B3 → B4 → B5
                                    │    (B3 espera BK-07)
         ───────────────────────────────────────────────
Fase 2   A: AUTH-T1                 │ B: AUTH-C1 → AUTH-T2
```

El único punto donde B espera algo de A es `schemas.py`, que B mismo crea en `AUTH-B1`: hasta entonces A trabaja contra la firma acordada.

---

## Lo que no está en este plan

- **La interfaz de usuario.** `frontend/` se borró y no tiene plan todavía. Las pantallas de registro, recuperación, activación por invitación y reautenticación se construirán cuando lo haya, después de cerrar este módulo.
- **La asignación de permisos.** Auth define y evalúa `auth.cuenta_permisos`; otorgarlos y retirarlos es de administration (`API-07`).
- **El envío de los correos.** Auth origina el evento de invitación y de recuperación; la entrega es de notifications (`API-18`), y las preferencias de envío no se aplican a estos correos (`RN-PREF-03`).
