# Plan de tareas — Auth

Traduce el [contrato de API](../../contratos/auth/api-contract.md) y los [flujos de usuario](user-flow.md) a tareas de implementación. Cada tarea declara objetivo, archivos afectados, dependencias, criterio de aceptación y las reglas que la sustentan.

Plan dimensionado para **dos personas en paralelo**. Los carriles se reparten por propiedad de archivos, no por capas, para evitar conflictos de merge.

---

## Estado actual frente al contrato

El módulo ya está implementado contra un contrato anterior. Estas son las diferencias que originan las tareas:

| Aspecto | Hoy | Contrato |
|---|---|---|
| Credencial de entrada | `username` + `password` contra la tabla heredada de usuarios (`app/crud/usuarios.py`) | `correo` + `contrasena` contra `auth.cuentas` |
| Transporte del token | `access_token` en el cuerpo, tipo `bearer`, leído por el cliente | Cookie `HttpOnly` (`SEC-SES-03`, `SEC-SES-05`) |
| Claims del JWT | Incluye `rol` y `role` | Sin rol ni permisos (`SEC-JWT-04`) |
| Sesiones | No existe el modelo `auth.sesiones`; no hay logout, renovación ni revocación | Sesión persistida y revocable (`SEC-SES-01`, `SEC-SES-07`) |
| Endpoints | Solo `POST /auth/login` | 16 endpoints (§3–§6 del contrato) |
| CSRF | Ausente | Doble envío obligatorio (`SEC-CSRF-01`) |
| Errores | `detail` de FastAPI | Envolvente `error.codigo` (§1) |

`backend/app/models/auth.py` ya define `Cuenta` conforme al modelo de datos: esa parte no se rehace.

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

| Carril | Responsabilidad | Archivos propios |
|---|---|---|
| **A** | Sesión, credenciales propias y autorización | `app/auth/auth.py`, `app/deps.py`, `app/models/auth.py`, `app/api/auth.py` |
| **B** | Alta de cuentas, invitaciones, recuperación y administración | `app/api/auth_cuentas.py`, `app/api/auth_invitaciones.py`, `app/crud/auth.py`, `app/schemas/auth.py` |

Los endpoints de B viven en routers nuevos y separados precisamente para que ambos carriles no editen `app/api/auth.py` a la vez.

**Puntos de sincronización obligatorios:**

1. `app/main.py` — registro de routers y manejadores de error. Lo toca **solo A**; B le pide el registro de su router.
2. `app/deps.py` — B consume `obtener_contexto` y `exigir_permiso` de A, no los redefine. Hasta que AUTH-A6 cierre, B trabaja contra la firma acordada, no contra la implementación.
3. `app/schemas/auth.py` — lo crea B en AUTH-B1; A solo lo lee.

---

## Fase 0 — Desbloqueo

Ambos carriles arrancan a la vez porque no comparten archivos. B trabaja en especificación mientras A monta la persistencia de sesión.

### AUTH-D1 — Definir persistencia de invitaciones y recuperación ✅ CERRADA

Resuelta durante la revisión de specs. `auth.invitaciones` y `auth.tokens_recuperacion` están definidas en [data-model.md](data-model.md), con token almacenado como hash, vigencia y marca de uso. Las vigencias por defecto son 7 días para una invitación y 1 hora para un token de recuperación. Ya no bloquea AUTH-B2 ni AUTH-B3.

### AUTH-D2 — Definir persistencia de permisos y ámbito ✅ CERRADA

Resuelta en el modelo objetivo de [data-model.md](data-model.md). `auth.cuenta_permisos` tiene una PK sustituta `id_cuenta_permiso`; `id_unidad` queda nullable fuera de la PK, y dos índices únicos parciales evitan duplicados para asignaciones por unidad y globales. El rol se deriva considerando cuenta, identidad activa, cargo, unidad vigente y permisos; una asignación no puede ampliar el ámbito del Técnico. Esta definición ya no bloquea AUTH-A6 ni AUTH-B4; su aplicación a la base de datos corresponde a las tareas de implementación del esquema.

El catálogo de códigos de `auth.permisos` también quedó definido (OQ-01), así que `AUTH-A6` ya no tiene dependencias de diseño abiertas.

### AUTH-A1 — Modelo y migración de `auth.sesiones`

- **Carril:** A
- **Objetivo:** crear la entidad de sesión que hoy no existe en el ORM.
- **Afectados:** `backend/app/models/auth.py`, nueva migración en `backend/migrations/`.
- **Dependencias:** ninguna. Bloquea AUTH-A3, AUTH-A4 y AUTH-A5.
- **Aceptación:** existe `auth.sesiones` con `id_sesion` UUID por defecto, `id_cuenta` con `ON DELETE CASCADE`, `refresh_token_hash`, `expires_at` con CHECK `> created_at` y `revoked_at` nulo; una instalación limpia la crea sin pasos manuales.
- **Contrato:** §2
- **RN:** `SEC-SES-01`, [data-model.md](data-model.md)

---

## Fase 1 — Implementación paralela

### Carril A — Sesión, credenciales y autorización

#### AUTH-A2 — Rehacer la emisión y validación del JWT

- **Carril:** A
- **Objetivo:** eliminar `rol`/`role` de los claims y fijar la validación completa.
- **Afectados:** `backend/app/auth/auth.py`, `backend/app/config.py`.
- **Dependencias:** ninguna. Bloquea AUTH-A3.
- **Aceptación:** el token emitido contiene `iss`, `aud`, `sub`, `sid`, `typ`, `iat`, `exp` y ningún permiso; un token con `alg: none`, algoritmo distinto, `aud` ajena o `typ` incorrecto se rechaza; un token con firma válida cuya sesión fue revocada también se rechaza.
- **Contrato:** §2
- **RN:** `SEC-JWT-01`, `SEC-JWT-02`, `SEC-JWT-04`, `SEC-JWT-05`

#### AUTH-A3 — Transporte por cookie y protección CSRF

- **Carril:** A
- **Objetivo:** sacar el token del cuerpo de la respuesta y llevarlo a cookies, con doble envío CSRF.
- **Afectados:** `backend/app/api/auth.py`, `backend/app/deps.py`, `backend/app/main.py`.
- **Dependencias:** AUTH-A1, AUTH-A2. Bloquea AUTH-F1.
- **Aceptación:** la respuesta de inicio de sesión no contiene el token; `rp_access` y `rp_refresh` son `HttpOnly` y `Secure`; `rp_refresh` limita su `Path` al endpoint de renovación; una operación de escritura sin `X-CSRF-Token` coincidente responde `403`.
- **Contrato:** §2
- **RN:** `SEC-SES-03`, `SEC-SES-04`, `SEC-SES-05`, `SEC-CSRF-01`, `SEC-CSRF-02`

#### AUTH-A4 — Reescribir el inicio de sesión contra `auth.cuentas`

- **Carril:** A
- **Objetivo:** autenticar por correo contra `auth.cuentas`, no por `username` contra la tabla heredada.
- **Afectados:** `backend/app/api/auth.py`, `backend/app/crud/usuarios.py`, `backend/app/schemas/usuario.py`.
- **Dependencias:** AUTH-A1, AUTH-A3.
- **Aceptación:** contraseña incorrecta, correo inexistente, cuenta inactiva e identidad inactiva devuelven el mismo `401 CREDENCIALES_INVALIDAS`, sin diferencias observables de cuerpo ni de tiempo; el inicio exitoso crea fila en `auth.sesiones` y regenera el identificador previo.
- **Contrato:** §3.2
- **RN:** `RN-AUTH-ID-01`, `RN-AUTH-ID-02`, `RN-AUTH-ID-05`, `SEC-ABU-02`, `SEC-SES-13`

#### AUTH-A5 — Sesión actual, renovación y cierre

- **Carril:** A
- **Objetivo:** completar el ciclo de vida de la sesión, hoy inexistente.
- **Afectados:** `backend/app/api/auth.py`, `backend/app/crud/auth.py`.
- **Dependencias:** AUTH-A4.
- **Aceptación:** cerrar sesión marca `revoked_at` y borra las cookies; una sesión revocada o vencida responde `401` aunque el cliente conserve la cookie; la renovación rota el secreto y rechaza superado el límite de inactividad o la vigencia máxima.
- **Contrato:** §3.3, §3.4, §3.5
- **RN:** `RN-AUTH-SES-01`, `RN-AUTH-SES-02`, `SEC-SES-07`, `SEC-SES-08`, `SEC-SES-09`

#### AUTH-A6 — Contexto autenticado, autorización y envolvente de error

- **Carril:** A
- **Objetivo:** sustituir `get_current_user` por el contrato interno que consumirán todos los módulos.
- **Afectados:** `backend/app/deps.py`, `backend/app/main.py`.
- **Dependencias:** AUTH-A5, AUTH-D2. Bloquea el consumo desde reservas y recursos.
- **Aceptación:** `obtener_contexto` resuelve identidad desde la sesión y rechaza cuenta o identidad inactiva; `exigir_permiso` evalúa permiso y unidad con datos vigentes y deniega cuando no puede comprobarlos; todo error del módulo responde con la envolvente `error.codigo` del contrato.
- **Contrato:** §1, §7
- **RN:** `SEC-AUTZ-01`, `SEC-AUTZ-02`, `SEC-AUTZ-03`, `SEC-AUTZ-04`, `RN-AUTH-ROL-05`

### Carril B — Alta de cuentas, invitaciones y administración

#### AUTH-B1 — Autorregistro

- **Carril:** B
- **Objetivo:** habilitar el alta sin invitación, hoy inexistente.
- **Afectados:** `backend/app/api/auth_cuentas.py`, `backend/app/schemas/auth.py`, `backend/app/crud/auth.py`.
- **Dependencias:** ninguna.
- **Aceptación:** la respuesta es `202` idéntica exista o no el correo; una contraseña fuera del rango admitido se rechaza con `422`; la cuenta creada es `USUARIO`, activa, vinculada a una sola identidad y sin permisos.
- **Contrato:** §3.1
- **RN:** `RN-AUTH-ID-02`, `RN-AUTH-ID-03`, `RN-AUTH-ROL-04`, `SEC-PWD-07`, `SEC-ABU-02`

#### AUTH-B2 — Recuperación de contraseña

- **Carril:** B
- **Objetivo:** implementar solicitud, validación previa y restablecimiento.
- **Afectados:** `backend/app/api/auth_cuentas.py`, `backend/app/crud/auth.py`, integración con `notificaciones`.
- **Dependencias:** AUTH-D1.
- **Aceptación:** la solicitud responde igual exista o no la cuenta; el token es de un solo uso y reutilizarlo devuelve `410`; el restablecimiento revoca todas las sesiones de la cuenta y dispara la notificación del cambio.
- **Contrato:** §3.6, §3.7, §3.8
- **RN:** `SEC-REC-01`, `SEC-REC-02`, `SEC-REC-03`, `SEC-REC-04`, `SEC-REC-05`

#### AUTH-B3 — Invitaciones

- **Carril:** B
- **Objetivo:** emitir, reenviar, validar y activar invitaciones.
- **Afectados:** `backend/app/api/auth_invitaciones.py`, `backend/app/crud/auth.py`.
- **Dependencias:** AUTH-D1, AUTH-A6 para la verificación de permiso.
- **Aceptación:** la respuesta de emisión nunca contiene el token; reenviar invalida el token anterior; una invitación vencida, usada o revocada no completa el alta; la activación respeta el tipo e identidad almacenados, no los enviados por el cliente.
- **Contrato:** §4
- **RN:** `SEC-INV-01`, `SEC-INV-02`, `SEC-INV-03`, `SEC-INV-04`, `SEC-AUTZ-03`

#### AUTH-B4 — Administración de cuentas

- **Carril:** B
- **Objetivo:** activar, desactivar y cambiar el tipo de identidad de una cuenta.
- **Afectados:** `backend/app/api/auth_cuentas.py`, `backend/app/crud/auth.py`.
- **Dependencias:** AUTH-A6, AUTH-D2.
- **Aceptación:** desactivar revoca las sesiones activas y conserva el historial; reactivar no crea identidad nueva; el cambio de identidad mantiene exactamente una vinculación; la operación que dejaría al sistema sin administradores responde `409`.
- **Contrato:** §6
- **RN:** `RN-AUTH-ID-03`, `RN-AUTH-ID-05`, `RN-CUE-04`, `RN-HAB-04`, `SEC-SES-10`

#### AUTH-B5 — Reautenticación y operaciones sensibles

- **Carril:** B
- **Objetivo:** proteger cambio de contraseña y cambio de identidad.
- **Afectados:** `backend/app/api/auth_cuentas.py`, `backend/app/deps.py` (consumo, no definición).
- **Dependencias:** AUTH-A6, AUTH-B4.
- **Aceptación:** una operación sensible sin autenticación reciente responde `401 REAUTENTICACION_REQUERIDA`; la reautenticación exitosa regenera el identificador de sesión; el cambio de contraseña revoca sesiones y notifica.
- **Contrato:** §3.9, §5
- **RN:** `SEC-REAUTH-01`, `SEC-REAUTH-02`, `SEC-REAUTH-03`, `SEC-REAUTH-04`

---

## Fase 2 — Integración, pruebas y limpieza

### AUTH-F1 — Cliente HTTP del frontend

- **Carril:** A
- **Objetivo:** consumir la API por cookies y dejar de manipular tokens en el cliente.
- **Afectados:** cliente HTTP y contexto de sesión en `frontend/`.
- **Dependencias:** AUTH-A3, AUTH-A5.
- **Aceptación:** ninguna ruta del frontend lee, guarda ni envía el token; las peticiones viajan con credenciales y `X-CSRF-Token`; un `401` redirige a inicio de sesión sin exponer detalles.
- **Contrato:** §2
- **RN:** `SEC-SES-05`, `SEC-AUTZ-01`

### AUTH-F2 — Pantallas de alta y recuperación

- **Carril:** B
- **Objetivo:** interfaces de registro, recuperación, activación por invitación y reautenticación.
- **Afectados:** vistas y formularios en `frontend/`.
- **Dependencias:** AUTH-B1, AUTH-B2, AUTH-B3, AUTH-B5.
- **Aceptación:** los mensajes mostrados no revelan si una cuenta existe; un token no vigente presenta el estado correspondiente y ofrece reiniciar el proceso.
- **Contrato:** §3.1, §3.6–§3.8, §4
- **RN:** `SEC-ABU-02`, `SEC-REC-01`

### AUTH-T1 — Pruebas de sesión y autorización

- **Carril:** A
- **Objetivo:** cubrir el ciclo de sesión y la denegación por defecto.
- **Afectados:** pruebas de `backend/`.
- **Dependencias:** AUTH-A6.
- **Aceptación:** existen pruebas para sesión revocada, sesión vencida, inactividad superada, token con algoritmo alterado, operación fuera de ámbito y operación sin permiso comprobable.
- **Contrato:** §2, §7
- **RN:** `SEC-SES-07`, `SEC-JWT-01`, `SEC-AUTZ-02`, `SEC-AUTZ-04`

### AUTH-T2 — Pruebas de tokens y no enumeración

- **Carril:** B
- **Objetivo:** cubrir un solo uso, vencimiento y equivalencia de respuestas.
- **Afectados:** pruebas de `backend/`.
- **Dependencias:** AUTH-B3, AUTH-B5.
- **Aceptación:** existen pruebas que verifican que reutilizar un token de recuperación o invitación falla, que reemitir invalida el anterior, y que registro, recuperación e inicio de sesión responden igual con correo existente e inexistente.
- **Contrato:** §3.1, §3.2, §3.6, §4
- **RN:** `SEC-TOK-05`, `SEC-INV-03`, `SEC-REC-01`, `SEC-ABU-02`

### AUTH-C1 — Retirar el inicio de sesión heredado

- **Carril:** A
- **Objetivo:** eliminar el contrato anterior una vez migrado el frontend.
- **Afectados:** `backend/app/api/auth.py`, `backend/app/deps.py`, `backend/app/schemas/usuario.py`.
- **Dependencias:** AUTH-F1, AUTH-T1. Última tarea del módulo.
- **Aceptación:** no queda `OAuth2PasswordBearer`, ni `TokenResponse` con token en el cuerpo, ni autenticación por `username`; ningún módulo importa `get_current_user`.
- **Contrato:** §2, §7
- **RN:** `SEC-SES-03`, `SEC-JWT-04`

---

## Orden sugerido

```text
Fase 0   A: AUTH-A1              │ B: AUTH-D1 ✅  AUTH-D2 ✅
         ───────────────────────────────────────────────
Fase 1   A: AUTH-A2 → A3 → A4    │ B: AUTH-B1 → B2
            → A5 → A6            │    → B3 → B4 → B5
                                 │    (B3/B4 esperan A6)
         ───────────────────────────────────────────────
Fase 2   A: AUTH-F1 → AUTH-T1    │ B: AUTH-F2 → AUTH-T2
         A: AUTH-C1 (al cierre)  │
```

El único punto donde B espera a A es AUTH-A6: hasta entonces B avanza con AUTH-B1 y AUTH-B2, que no requieren evaluación de permisos.
