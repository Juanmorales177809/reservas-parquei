# Plan de tareas — Frontend

Cómo se construye `frontend/` desde cero. Plan general: [`tasks.md`](../../../tasks.md) de la raíz, que lo cita como `FE-00` en su Fase 6.

---

## Punto de partida

| Qué | Estado |
|---|---|
| `frontend/` | **No existe.** Se borró junto con el backend anterior y nunca se reintrodujo (`tasks.md`, «Qué no está en ningún plan») |
| Los nueve contratos de API | Cerrados y con sus 19 tareas `API-XX` cerradas: hay superficie HTTP real contra la que construir |
| Auth de punta a punta | Cerrada (`BK-09`): hay sesión real por cookie que consumir, no un simulacro |
| [Tokens de diseño](../../ui/design-tokens.md) | Cerrados: paleta, tipografía, radios y sombras, con tema oscuro |
| [Sistema de diseño](../../ui/design-system.md) | Cerrado: reglas de uso del color, la tipografía y los estados |
| [Componentes UI](../../ui/components.md) | `Button` cerrado por completo, con su API objetivo en React. El resto de componentes, pendiente |
| [Distribución de la interfaz](../../ui/layout.md) | Solo fija una regla (fullWidth en móvil para `primary`). El resto, pendiente |
| Pantallas por módulo (`screens.md`, `wireframes.md`, `screen-flow.md`) | Solo existen para **auth**. Los otros ocho módulos solo tienen `user-flow.md` (flujo funcional, sin pantalla) |

**El backend está completo.** Los cinco riesgos que bloqueaban el frontend en `plan.md` §8 («construirlo exige antes una API contra la que trabajar») ya no aplican: las 56 tareas de base de datos, contratos y backend están cerradas. Lo que falta no es API — es especificación de pantalla, y después, código.

Por eso este plan mezcla dos tipos de tarea, marcados en el campo **Tipo**:

- **Especificación** — escribir `screens.md` / `wireframes.md` / `screen-flow.md` de un módulo, siguiendo el patrón ya cerrado de [`specs/modules/auth/`](../../modules/auth/). No es código; es la spec que falta antes de poder escribir código, igual que un contrato tiene que existir antes de un endpoint.
- **Implementación** — código en `frontend/`, contra una especificación de pantalla ya cerrada.

Una tarea de **Implementación** no se abre antes que la tarea de **Especificación** de su propio módulo, por la misma razón que una `API-XX` no se cierra antes que su `DB-XX`: código contra una pantalla que no está definida da una falsa sensación de terminado.

---

## Decisiones que fija este plan

`architecture.md` §3 fija el stack (Next.js 14, React 18, TypeScript, Tailwind CSS, Recharts) pero no la arquitectura interna del frontend — a diferencia del backend, que tiene su propia sección en `plan.md` §3. Lo que sigue **no estaba decidido en ningún documento anterior** y se fija aquí por primera vez:

| Decisión | Elegido | Por qué |
|---|---|---|
| Router de Next.js 14 | **App Router**, no Pages Router | Es el router recomendado desde Next 13+; permite Server Components para las vistas de solo lectura (listados, reportes) sin enviar ese código al cliente |
| Componentes por defecto | **Server Component**, `'use client'` solo donde hay estado o interacción (formularios, `Button` con `loading`, alternancia de tema) | Minimiza el JavaScript enviado al navegador; coincide con la guía de la skill `react-expert` de preferir RSC cuando no hay estado de cliente |
| Datos en lectura inicial | `fetch` nativo desde Server Components, reenviando la cookie de sesión | No hay que duplicar el estado de sesión en el cliente para la carga inicial de una pantalla |
| Mutaciones y refetch (aprobar, rechazar, cancelar, exportar) | **TanStack Query** en Client Components | Da estados de carga/error/reintento consistentes sin reinventarlos por pantalla; es el patrón que documenta `references/state-management.md` de `react-expert` |
| Estado de sesión y permisos en el cliente | **Ninguno persistido.** El cliente nunca guarda rol ni permisos propios; cada acción sensible se reintenta contra el backend, que es quien autoriza (`architecture.md` §11.2) | Es la misma regla que ya rige la cookie de sesión: «no contiene rol ni permisos: se revalidan en el servidor en cada operación» (`AGENTS.md`). Un store de cliente con el rol sería una segunda fuente de verdad que puede quedar desactualizada |
| Componentes compartidos | `frontend/src/components/ui/`, uno por archivo, tipados en TypeScript estricto, con pruebas de React Testing Library para los que tengan lógica de estado propia (p. ej. `destructive-confirm`) | Convención de la skill `react-expert`: tipos estrictos, pruebas para lógica no trivial |

**Esto es una decisión técnica nueva, no una confirmación de algo ya escrito en `architecture.md`.** Se anota también en [`decisiones_pendientes_para_revision.md`](../../../decisiones_pendientes_para_revision.md) para que el equipo la revise; si se corrige, se corrige este documento primero, igual que un contrato.

---

## Dónde vive

```text
frontend/
  app/                        Next.js App Router
    (auth)/                   rutas publicas: login, registro, activacion, recuperacion
      login/page.tsx
      registro/page.tsx
      ...
    (app)/                    rutas autenticadas, una carpeta por modulo
      reservas/
      recursos/
      espacios/
      investigacion/
      usuarios/
      administracion/
      notificaciones/
      reportes/
      layout.tsx              shell de navegacion (FE-06)
    layout.tsx                shell global: fuentes, tokens, tema
    globals.css                importa styles/tokens.css
  src/
    components/ui/            Button (FE-04) y los que se sumen despues
    lib/
      http.ts                 cliente HTTP: cookie + CSRF de doble envio (FE-03)
      queries/                hooks de TanStack Query, uno por modulo
    styles/
      tokens.css              variables --color-*, --radius, --shadow-*, --fs-*, --fw-* (FE-02)
  tests/
  package.json
  tailwind.config.ts
  Dockerfile
```

Un directorio por módulo dentro de `app/(app)/`, con los mismos nombres que los nueve módulos de la especificación — la misma regla que ya rige `backend/app/modules/`: un directorio que no corresponda a un módulo documentado es señal de que la superficie se está inventando.

---

## Convención de tarea

```markdown
### FE-XX — Título

- **Tipo:** Especificación o Implementación.
- **Objetivo:** qué queda distinto al terminar.
- **Afectados:** archivos o directorios concretos.
- **Dependencias:** qué debe cerrarse antes.
- **Aceptación:** condición verificable, no «quedó implementado». Para una tarea de Especificación, verificable contra el patrón ya cerrado de auth (mismos documentos, mismo nivel de detalle) y contra `python tools/validar.py`. Para una tarea de Implementación, verificable con `tsc --noEmit` limpio y las pruebas de React Testing Library en verde, siguiendo el flujo de la skill `react-expert`: analizar → implementar con tipos estrictos → `tsc --noEmit` → pruebas.
```

---

## Fase 1 — Cimientos

No depende de ninguna pantalla: es infraestructura y el primer componente compartido. Puede empezar de inmediato.

### FE-01 — Inicialización del proyecto · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** `frontend/` existe, levanta con `npm run dev` y sirve una página en blanco.
- **Afectados:** `frontend/package.json`, `frontend/app/layout.tsx`, `frontend/app/page.tsx`, `frontend/tsconfig.json`, `frontend/Dockerfile`.
- **Dependencias:** ninguna.
- **Aceptación:** `npm run build` termina sin errores de TypeScript (`strict: true`); `npm run dev` sirve `/` en `200`. Sin conexión al backend todavía — es infraestructura, no una pantalla.
- **Resultado:** scaffold `create-next-app@14` (Next 14.2.35, React 18.3.1, TS 5.9.3, Tailwind 3.4.19, todo pineado exacto) recortado a página en blanco con `lang="es"` y título propio; `Dockerfile` multietapa sin cablear en compose. Política global `allow-scripts` documentada en `frontend/.npmrc` (`unrs-resolver`, única excepción). Verificado: `npm run build` y `npx tsc --noEmit` limpios, `/` en `200`.

### FE-02 — Tokens de diseño en Tailwind · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** los tokens de [`design-tokens.md`](../../ui/design-tokens.md) están disponibles como variables CSS y consumibles desde Tailwind.
- **Afectados:** `frontend/src/styles/tokens.css`, `frontend/app/globals.css`, `frontend/tailwind.config.ts`, y **`frontend/app/layout.tsx`** (ampliación de alcance, ver Resultado).
- **Dependencias:** FE-01.
- **Aceptación:** las variables `--color-*`, `--radius`, `--shadow-*`, `--fs-*` y `--fw-*` existen con los valores exactos del documento, en tema claro y oscuro (`prefers-color-scheme` + `data-theme`). Ningún componente posterior declara un color, radio o sombra fuera de estas variables.
- **Resultado:** `tokens.css` con las tres familias del documento (superficie con par claro/oscuro, marca/semánticos con valor único, tipografía/radio/sombras), verificado valor por valor contra `design-tokens.md`. Se añadió `--shadow-focus` (la fórmula de foco que el documento ya fijaba en prosa, promovida a variable para no reescribirla en cada componente interactivo) — sigue siendo `--shadow-*`, cumple la aceptación tal cual está escrita.
  Los tokens se registraron **por nombre en `theme.extend`** (`bg-primary-1`, `shadow-hover`, `rounded-control`, …), no por valor hex literal: la fuente de verdad queda en un solo archivo y una clase con un hex fuera de estos nombres ya incumple la aceptación, sea cual sea su sintaxis. `rounded-control` no sobreescribe el `rounded` por defecto de Tailwind —`--radius` es específico de controles, no un reemplazo global— y `fontSize.sm` sí redefine el `text-sm` de Tailwind (14px → 12px) a propósito, porque el token reemplaza la escala por defecto.
  **Ampliación de alcance:** `--font-body` referenciaba `'Inter'`, pero ningún archivo de la lista original podía cargarlo — se añadió `next/font/google` en `layout.tsx` (pesos 400/700, variable `--font-inter`) para que el token no cayera en silencio a Arial.
  Verificado: `npx tsc --noEmit` y `npm run build` limpios, sin más aviso que "no se detectaron clases de utilidad" (esperado: `page.tsx` sigue en blanco, es tarea de FE-04 en adelante). Los radios de 14/16/20px y el de píldora (999px) siguen sin tokenizar, tal como ya lo dejaba `design-tokens.md` ("candidatos a tokenizarse") — no es una omisión de esta tarea. La verificación mecánica de "ningún color fuera de los tokens" (p. ej. Stylelint) queda pendiente como mejora opcional, no como parte de esta tarea; el primer consumidor real de los tokens es `FE-04`.

### FE-03 — Cliente HTTP y sesión · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** un módulo único que llama al backend con la cookie de sesión y el CSRF de doble envío, y traduce la envolvente de error común a un tipo de TypeScript.
- **Afectados:** `frontend/src/lib/http.ts`.
- **Dependencias:** FE-01. Contrato: `contratos/README.md` §2 (envolvente de error), `contratos/auth/api-contract.md` §2 y §9 (cookie y CSRF).
- **Aceptación:** una respuesta `401` no reintenta silenciosamente con credenciales viejas; toda mutación (`POST`/`PUT`/`PATCH`/`DELETE`) envía el token CSRF obtenido de `GET /api/auth/csrf`; el tipo de error del cliente tiene exactamente `codigo`, `mensaje` y `detalles`, igual que el contrato.
- **Resultado:** `apiRequest<T>(path, options)`, único punto de entrada. `rp_access`/`rp_refresh` (`HttpOnly`) las adjunta el navegador solo con `credentials: "include"` — el módulo nunca las lee ni las guarda. Para mutaciones, `rp_csrf` (legible, no `HttpOnly`) se lee de `document.cookie` y, si no existe todavía, se pide una vez a `GET /api/auth/csrf` antes de reintentar la lectura, conforme a §3.0. Sin lógica de reintento en ningún código de estado: un `401` se propaga como `ApiRequestError` (con `status` y el `ApiError` del contrato) para que quien llame decida — así se cumple la aceptación de que un `401` no reintenta con credenciales viejas, por ausencia de ese mecanismo, no por manejarlo con cuidado.
  `ApiError` tiene exactamente `codigo: string`, `mensaje: string`, `detalles: unknown[]`, igual que `contratos/README.md` §2; si el cuerpo de un error no trae esa forma (p. ej. un `502` de un proxy intermedio, no del backend), se sustituye por `{ codigo: "ERROR_INTERNO", mensaje: "Error no controlado.", detalles: [] }` en vez de propagar un cuerpo con forma desconocida.
  El módulo no importa `next/headers`, para poder usarse igual desde Client Components (mutaciones, vía TanStack Query en tareas posteriores) y desde Server Components (lecturas iniciales): estos últimos deben leer `cookies()` ellos mismos y pasar el resultado como `cookieHeader`, porque un `fetch` desde un Server Component no reenvía automáticamente las cookies de la petición entrante — eso se resuelve en la tarea que use el módulo (a partir de `FE-06`), no aquí.
  `NEXT_PUBLIC_API_URL` con default `http://localhost:8000` (mismo puerto que `BACKEND_HOST_PORT` en `.env.example`); no se tocó ningún archivo de entorno, es solo el valor por defecto del módulo.
  Verificado: `npx tsc --noEmit` y `npm run build` limpios. Sin consumidor real todavía (ninguna pantalla existe): la prueba de comportamiento en runtime queda para `FE-06`/`FE-07`, primeros consumidores reales.

### FE-04 — Componente compartido `Button`

- **Tipo:** Implementación
- **Objetivo:** el componente `Button` completo, tal como lo fija [`components.md`](../../ui/components.md#botones).
- **Afectados:** `frontend/src/components/ui/Button.tsx`, `frontend/src/components/ui/Button.test.tsx`.
- **Dependencias:** FE-02.
- **Aceptación:** las siete variantes, los tres tamaños y `fullWidth` funcionan; `disabled` usa el atributo nativo; `loading` antepone el spinner sin perder el texto; el anillo de foco es igual en las siete variantes; `destructiveConfirm` arma con el primer clic, ejecuta con el segundo dentro de 4s y se desarma solo si no hay segundo clic. Pruebas de React Testing Library cubren el armado/desarmado de `destructiveConfirm` y que `disabled` bloquea el evento de clic. `tsc --noEmit` limpio.

---

## Fase 2 — Estructura general

Bloqueada en parte por specs/ui, que todavía no fija la distribución general.

### FE-05 — Completar `specs/ui/layout.md`

- **Tipo:** Especificación
- **Objetivo:** cerrar la estructura general de pantallas y la ubicación de navegación, contenido y acciones — hoy «Pendiente» salvo la regla de `fullWidth` en móvil.
- **Afectados:** [`specs/ui/layout.md`](../../ui/layout.md).
- **Dependencias:** ninguna técnica; es una decisión de producto/diseño que el equipo tiene que tomar, no una que se infiera del artifact de botones (que no cubre navegación).
- **Aceptación:** `layout.md` no tiene ninguna sección marcada «Pendiente»; `python tools/validar.py` sigue en 0 fallas.

### FE-06 — Shell de navegación autenticado

- **Tipo:** Implementación
- **Objetivo:** el layout que envuelve las pantallas autenticadas (`app/(app)/layout.tsx`): navegación, región de contenido, estado de sesión visible.
- **Afectados:** `frontend/app/(app)/layout.tsx`.
- **Dependencias:** FE-05, FE-03.
- **Aceptación:** una ruta bajo `(app)/` sin sesión válida redirige a login sin pintar contenido protegido; la navegación refleja únicamente lo que `GET /api/auth/sesiones/actual` autorizó para esa sesión, no un mapa de rutas fijo por rol construido en el cliente.

---

## Fase 3 — Auth

La especificación de pantallas de auth ya está cerrada (`screens.md`, `wireframes.md`, `screen-flow.md`, del commit `ui_auth`). Es el primer módulo completo del frontend nuevo, igual que auth lo fue para el backend, y **queda como referencia de estilo** para las ocho tareas de implementación que siguen.

### FE-07 — Pantallas de auth

- **Tipo:** Implementación
- **Objetivo:** las nueve pantallas de [`screens.md`](../../modules/auth/screens.md) — login, autorregistro, activación por invitación, recuperación, reautenticación, administración de cuentas e invitaciones — funcionando contra el backend real.
- **Afectados:** `frontend/app/(auth)/**`, rutas de administración de cuentas bajo `(app)/administracion/`.
- **Dependencias:** FE-04, FE-06. Contrato: [`auth/api-contract.md`](../../contratos/auth/api-contract.md), completo.
- **Aceptación:** los nueve wireframes de `wireframes.md` corresponden uno a uno con una ruta; ningún estado de error mostrado usa un texto distinto al fijado ahí (nada de `detail` de FastAPI, nada de SQL ni trazas); un intento de acceder a una pantalla de administración sin el permiso `cuentas.administrar` no muestra ni parpadea el contenido protegido antes de redirigir.

---

## Fase 4 — Catálogos e identidad

Un bloque por módulo, en el mismo orden en que el backend los cerró (`tasks.md`, Fase 2–3): primero identidad y estructura, después inventario. Cada módulo repite el mismo par de tareas: **Especificación** de sus pantallas y **Implementación** contra esa especificación ya cerrada.

### FE-08 — Especificación de pantallas — usuarios

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `usuarios`, con la misma forma que los de auth.
- **Afectados:** `specs/modules/usuarios/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`usuarios/user-flow.md`](../../modules/usuarios/user-flow.md) y [`usuarios/api-contract.md`](../../contratos/usuarios/api-contract.md), ambos cerrados.
- **Aceptación:** `python tools/validar.py` en 0 fallas con los nuevos documentos enlazados desde `usuarios/overview.md`.

### FE-09 — Implementación — usuarios

- **Tipo:** Implementación
- **Objetivo:** las pantallas de `usuarios` funcionando contra el backend real.
- **Afectados:** `frontend/app/(app)/usuarios/**`.
- **Dependencias:** FE-08, FE-04, FE-06.
- **Aceptación:** corresponde uno a uno con los wireframes de FE-08; `tsc --noEmit` limpio.

### FE-10 — Especificación de pantallas — administration

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `administration`.
- **Afectados:** `specs/modules/administration/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`administration/user-flow.md`](../../modules/administration/user-flow.md) y su contrato, cerrados.
- **Aceptación:** igual criterio que FE-08.

### FE-11 — Implementación — administration

- **Tipo:** Implementación
- **Objetivo:** las pantallas de `administration` (unidades, cargos, permisos, auditoría) funcionando contra el backend real.
- **Afectados:** `frontend/app/(app)/administracion/**`.
- **Dependencias:** FE-10, FE-04, FE-06, FE-07 (comparte área de administración de cuentas con auth).
- **Aceptación:** igual criterio que FE-09. La vista de auditoría no expone contraseñas, secretos de sesión, tokens completos ni claves, igual que exige `SEC-AUD-03`.

### FE-12 — Especificación de pantallas — resources

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `resources`, incluida la importación masiva de equipos.
- **Afectados:** `specs/modules/resources/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`resources/user-flow.md`](../../modules/resources/user-flow.md) y su contrato, cerrados.
- **Aceptación:** igual criterio que FE-08. La pantalla de importación documenta el resultado por fila y el rechazo total ante cualquier fila con error, conforme a la decisión ya cerrada en `decisiones_pendientes_para_revision.md`.

### FE-13 — Implementación — resources

- **Tipo:** Implementación
- **Objetivo:** las pantallas de `resources` funcionando contra el backend real.
- **Afectados:** `frontend/app/(app)/recursos/**`.
- **Dependencias:** FE-12, FE-04, FE-06.
- **Aceptación:** igual criterio que FE-09. La importación con filas en error no permite confirmar la carga y muestra el resultado por fila.

### FE-14 — Especificación de pantallas — espacios

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `espacios`, incluidos los campos adicionales de los cinco tipos cerrados.
- **Afectados:** `specs/modules/espacios/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`espacios/user-flow.md`](../../modules/espacios/user-flow.md) y su contrato, cerrados. FE-12 para reutilizar el patrón de asociación con recursos.
- **Aceptación:** igual criterio que FE-08.

### FE-15 — Implementación — espacios

- **Tipo:** Implementación
- **Objetivo:** las pantallas de `espacios` funcionando contra el backend real.
- **Afectados:** `frontend/app/(app)/espacios/**`.
- **Dependencias:** FE-14, FE-13 (reutiliza el selector de recursos), FE-06.
- **Aceptación:** igual criterio que FE-09.

### FE-16 — Especificación de pantallas — researchs

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `researchs` (proyectos, semilleros, equipos de investigación).
- **Afectados:** `specs/modules/researchs/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`researchs/user-flow.md`](../../modules/researchs/user-flow.md) y su contrato, cerrados.
- **Aceptación:** igual criterio que FE-08. No introduce ninguna asociación de proyecto o semillero con un laboratorio: en este sistema se asocian a personas, no limitan dónde puede reservar el usuario.

### FE-17 — Implementación — researchs

- **Tipo:** Implementación
- **Objetivo:** las pantallas de `researchs` funcionando contra el backend real, incluida la importación masiva.
- **Afectados:** `frontend/app/(app)/investigacion/**`.
- **Dependencias:** FE-16, FE-13 (reutiliza el patrón de importación de FE-13), FE-06.
- **Aceptación:** igual criterio que FE-09.

---

## Fase 5 — Reservas

El módulo central y el más complejo: cinco tipos de reserva con estrategias distintas (`architecture.md` §6.3–6.4, [`reservations/architecture.md`](../../modules/reservations/architecture.md)).

### FE-18 — Especificación de pantallas — reservations

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `reservations`: solicitud por tipo, gestión, calendario, lista de espera y transiciones de estado.
- **Afectados:** `specs/modules/reservations/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`reservations/user-flows.md`](../../modules/reservations/user-flows.md) y los cuatro contratos que lo cubren (`API-13` a `API-16`), cerrados. FE-14 para el selector de espacios, FE-12 para el de recursos.
- **Aceptación:** igual criterio que FE-08. Cubre los seis estados de una reserva y las cinco estrategias (espacio, recurso interno, recurso de campus, recurso externo, lista de espera) como flujos de pantalla distintos, no como una sola pantalla genérica con campos condicionales sin documentar.

### FE-19 — Implementación — reservations

- **Tipo:** Implementación
- **Objetivo:** las pantallas de `reservations` funcionando contra el backend real.
- **Afectados:** `frontend/app/(app)/reservas/**`.
- **Dependencias:** FE-18, FE-15, FE-13, FE-06. Es la tarea de implementación más grande del plan; puede dividirse por tipo de reserva al abrirla, siguiendo el mismo criterio que dividió `API-13` a `API-16` en el backend.
- **Aceptación:** igual criterio que FE-09. Ninguna pantalla permite confirmar una reserva sin pasar por la respuesta real del backend — la exclusión de solapamiento y de compromiso físico único la garantiza `DB-12` en el servidor, y el frontend no puede sustituirla con una validación propia.

---

## Fase 6 — Notificaciones y reportes

### FE-20 — Especificación de pantallas — notifications

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `notifications`: bandeja y preferencias.
- **Afectados:** `specs/modules/notifications/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`notifications/user-flow.md`](../../modules/notifications/user-flow.md) y su contrato, cerrados.
- **Aceptación:** igual criterio que FE-08.

### FE-21 — Implementación — notifications

- **Tipo:** Implementación
- **Objetivo:** bandeja y preferencias de `notifications` funcionando contra el backend real.
- **Afectados:** `frontend/app/(app)/notificaciones/**`.
- **Dependencias:** FE-20, FE-06.
- **Aceptación:** igual criterio que FE-09.

### FE-22 — Especificación de pantallas — reports

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `reports`: ocupación, solicitudes, lista de espera y exportación.
- **Afectados:** `specs/modules/reports/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`reports/user-flow.md`](../../modules/reports/user-flow.md) y su contrato, cerrados.
- **Aceptación:** igual criterio que FE-08. Fija qué informes se muestran como gráfico (con Recharts, único cargador de gráficos fijado en `architecture.md` §3) y cuáles como tabla exportable, en vez de dejarlo a criterio de quien implemente.

### FE-23 — Implementación — reports

- **Tipo:** Implementación
- **Objetivo:** los informes de `reports` funcionando contra el backend real, con sus gráficos y su exportación.
- **Afectados:** `frontend/app/(app)/reportes/**`.
- **Dependencias:** FE-22, FE-06. Es la única tarea del plan que introduce una librería de visualización (Recharts); antes de codificar un gráfico, conviene revisar la guía de la skill `dataviz` de este entorno para mantener paleta y forma consistentes con el resto del sistema de diseño.
- **Aceptación:** igual criterio que FE-09. Ningún gráfico usa un color fuera de la paleta de [`design-tokens.md`](../../ui/design-tokens.md).

---

## Orden sugerido

```text
Fase 1   FE-01 → FE-02 → FE-03 → FE-04           (cimientos, en paralelo cuando no compartan archivo)
Fase 2   FE-05 → FE-06
Fase 3   FE-07                                    (referencia de estilo del resto)
Fase 4   FE-08/09 → FE-10/11 → FE-12/13 → FE-14/15 → FE-16/17
Fase 5   FE-18/19
Fase 6   FE-20/21 → FE-22/23
```

Dentro de cada módulo de Fase 4 a 6, la tarea de **Especificación** siempre cierra antes que su **Implementación**. Entre módulos distintos, el orden sugerido no es una dependencia dura salvo donde se anota explícitamente (p. ej. FE-15 reutiliza el selector de recursos de FE-13).

---

## Lo que no está en este plan

- **El despliegue del frontend en un entorno real.** `plan.md` §8 ya señala que no hay entorno desplegado; este plan construye contra un backend local.
- **Tests end-to-end de navegador.** Este plan cubre pruebas de componente (React Testing Library). Un plan de `e2e` (Playwright u otro) es una decisión aparte, no asumida aquí.
- **La redacción de los textos de interfaz.** Los wireframes fijan estructura y contenido tipo, no la redacción final de cada mensaje — igual que ya aclara `wireframes.md` de auth.
