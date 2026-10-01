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

## Fase 1 — Cimientos · **cerrada**

No depende de ninguna pantalla: es infraestructura y el primer componente compartido. `FE-01` a `FE-04` cerradas: proyecto Next.js levantado, tokens de diseño consumibles desde Tailwind, cliente HTTP con sesión/CSRF, y `Button` completo con pruebas en verde. **El siguiente paso es la Fase 2.**

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

### FE-04 — Componente compartido `Button` · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** el componente `Button` completo, tal como lo fija [`components.md`](../../ui/components.md#botones).
- **Afectados:** `frontend/src/components/ui/Button.tsx`, `frontend/src/components/ui/Button.test.tsx`, y **`frontend/package.json`, `frontend/vitest.config.ts`, `frontend/vitest.setup.ts`** (ampliación de alcance: no existía infraestructura de pruebas todavía — ver Resultado).
- **Dependencias:** FE-02.
- **Aceptación:** las siete variantes, los tres tamaños y `fullWidth` funcionan; `disabled` usa el atributo nativo; `loading` antepone el spinner sin perder el texto; el anillo de foco es igual en las siete variantes; `destructiveConfirm` arma con el primer clic, ejecuta con el segundo dentro de 4s y se desarma solo si no hay segundo clic. Pruebas de React Testing Library cubren el armado/desarmado de `destructiveConfirm` y que `disabled` bloquea el evento de clic. `tsc --noEmit` limpio.
- **Resultado:** `Button` con `forwardRef`, tipado estricto (`ButtonVariant`, `ButtonSize`), sin dependencias nuevas de runtime (composición de clases con un `cx` local, sin `clsx`/`cva`).
  **Ampliación de alcance:** no había infraestructura de pruebas — se añadió Vitest 2.1.9 + `@vitejs/plugin-react` + jsdom + React Testing Library + `jest-dom` + `user-event` como devDependencies, `vitest.config.ts`/`vitest.setup.ts`, y el script `test`. Se fijó Vitest 2.x (no la última 5.x) porque esa exige `@types/node` ≥22 y el proyecto fijó `@types/node` 20.x en `FE-01`; subir esa dependencia no entraba en el alcance de esta tarea.
  Las siete variantes usan los tokens de `FE-02` por nombre (`from-primary-1`, `to-error-hover2`, `bg-primary-pressed`, `shadow-hover`…), nunca un hex. `primary` es la única con `hover-1` propio (única familia con ambos extremos de hover); `success`/`error`/`warning` solo cambian el segundo extremo en hover, igual que ya lo hacía el artifact original.
  **Hallazgo sobre el anillo de foco:** el foco se implementó con las utilidades `ring-*` de Tailwind (`focus-visible:ring-4 focus-visible:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]`), no con el `--shadow-focus` que registró `FE-02`. Verificado en el CSS compilado: `ring-*` y `shadow-*` de Tailwind componen un único `box-shadow` mediante variables internas (`--tw-ring-shadow`, `--tw-shadow`), así que el anillo se **suma** a `shadow-hover`/`shadow-pressed` en vez de reemplazarlos — exactamente lo que pide la aceptación ("no sustituye a hover/pressed: puede combinarse con ellos"). Un `shadow-focus` aplicado como `boxShadow` normal habría *reemplazado* esas sombras en vez de sumarse, porque ambas comparten la misma propiedad CSS. `--shadow-focus` queda en `tokens.css` sin usarse por `Button` — no es incorrecto (la fórmula es la misma), pero es la pieza a retirar si una futura limpieza de tokens la encuentra sin consumidores.
  `destructiveConfirm` usa `data-armed` en el DOM y el modificador de atributo arbitrario `data-[armed=true]:` de Tailwind para su estado armado (fondo sólido + anillo siempre visible, no solo en `:focus-visible`). El texto de ayuda auxiliar («Doble clic requerido…») y su `aria-live` quedan fuera de `Button`, tal como ya lo fija `components.md` — no es un olvido de esta tarea.
  El `!important` en los cuatro overrides de `disabled` (`bg-none`, `bg-disabled-bg`, `text-disabled-text`, `shadow-none`) es deliberado: garantiza que ganen sobre la clase de variante sin depender del orden interno de los *variants* de Tailwind en la hoja compilada — confirmado leyendo el CSS generado.
  Verificado: `npx tsc --noEmit` limpio; `npm run build` limpio; `npm test` — 7 pruebas en verde (siete variantes renderizan, `fullWidth`, `disabled` bloquea el clic sin llamar `onClick`, `loading` antepone el spinner sin perder el texto, y las tres del patrón `destructiveConfirm`: arma sin ejecutar, ejecuta y desarma al segundo clic, se desarma solo a los 4s sin ejecutar). Inspección del CSS compilado confirma que `from-primary-1`, los `color-mix(...)` de foco/pressed/ghost y `data-[armed=true]:` generan exactamente las reglas esperadas.

---

## Fase 2 — Estructura general · **cerrada**

`FE-05` y `FE-06` cerradas: `specs/ui/layout.md` completo y el shell autenticado real en `frontend/app/(app)/layout.tsx`, con navegación filtrada por rol y redirección a login sin sesión. **El siguiente paso es la Fase 3.**

### FE-05 — Completar `specs/ui/layout.md` · **cerrada**

- **Tipo:** Especificación
- **Objetivo:** cerrar la estructura general de pantallas y la ubicación de navegación, contenido y acciones — hoy «Pendiente» salvo la regla de `fullWidth` en móvil.
- **Afectados:** [`specs/ui/layout.md`](../../ui/layout.md).
- **Dependencias:** ninguna técnica; es una decisión de producto/diseño que el equipo tiene que tomar, no una que se infiera del artifact de botones (que no cubre navegación).
- **Aceptación:** `layout.md` no tiene ninguna sección marcada «Pendiente»; `python tools/validar.py` sigue en 0 fallas.
- **Resultado:** shell autenticado de tres regiones (cabecera, navegación, contenido), con la pública de auth referenciada, no redefinida. Navegación: ocho destinos fijos por nombre (Reservas, Recursos, Espacios, Investigación, Usuarios, Administración, Notificaciones, Reportes — auth no es un destino propio, vive dentro de Administración), con visibilidad calculada en runtime contra `GET /api/auth/sesiones/actual`, nunca una tabla fija por rol — así cumple la aceptación de `FE-06` tal cual está escrita.
  **Hallazgo relevante para `FE-06`:** `sesiones/actual` no devuelve nombre, solo `correo` y `rol` (`GET /api/perfil`, de `usuarios`, sí lo tiene, pero `FE-06` no lo lista como dependencia). Se decidió mostrar `correo · rol` en vez del nombre, precisamente para no sumar esa dependencia cruzada en silencio — anotado como pregunta abierta en `decisiones_pendientes_para_revision.md`, junto con la ausencia de marca en la cabecera y de contador de notificaciones (ambas esperan componentes o decisiones de contenido que todavía no existen).
  Móvil y tablet (`<1024px`) comparten el mismo comportamiento de navegación (panel superpuesto de 240px, no persistente): a 768–1023px un panel persistente dejaría 528–783px para pantallas con tablas (reportes, listados de reservas/recursos), insuficiente sin scroll horizontal constante. Dos dimensiones nuevas se documentan como tales (ancho del panel 240px, alto de cabecera 64px); el resto reutiliza precedentes ya cerrados (max-width/padding de contenido del artifact aprobado, gutter del catálogo de `design-tokens.md`) — nada inventado sin marcarlo.
  Tokens de chrome (fondo, borde, ítem activo, foco) reutilizan exactamente los que ya cierra `design-system.md`; ninguno nuevo salvo extender el anillo de foco —ya fijado solo para `Button`— a los ítems de navegación, un tipo de elemento interactivo que ese documento no cubría.
  Verificado: `python tools/validar.py` en 0 fallas.

### FE-06 — Shell de navegación autenticado · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** el layout que envuelve las pantallas autenticadas (`app/(app)/layout.tsx`): navegación, región de contenido, estado de sesión visible.
- **Afectados:** `frontend/app/(app)/layout.tsx`, y **`frontend/src/lib/auth.ts`, `frontend/src/components/shell/AppShell.tsx`, `frontend/src/components/shell/nav-items.ts`, `frontend/vitest.config.ts`** (ampliación de alcance: el layout necesitaba un helper de sesión server-only y un shell interactivo, que no caben en un único archivo de Server Component — ver Resultado).
- **Dependencias:** FE-05, FE-03.
- **Aceptación:** una ruta bajo `(app)/` sin sesión válida redirige a login sin pintar contenido protegido; la navegación refleja únicamente lo que `GET /api/auth/sesiones/actual` autorizó para esa sesión, no un mapa de rutas fijo por rol construido en el cliente.
- **Resultado:** `app/(app)/layout.tsx` es un Server Component `async` que llama a `obtenerSesionActual()` (nuevo, en `src/lib/auth.ts`) y hace `redirect("/login")` antes de pintar nada si no hay sesión — Next.js no invoca `children` cuando el layout redirige, así que no hay parpadeo de contenido protegido. `obtenerSesionActual` lee `cookies()` de `next/headers` y llama a `apiRequest` de `FE-03` con `cookieHeader`; devuelve `null` en un `401`, propaga cualquier otro error. `apiRequest` en sí no cambió — sigue sin importar `next/headers`, tal como fijó `FE-03`.
  **Primer uso real del alias `@/`** que ya declaraba `tsconfig.json` (`"@/*": ["./*"]`, relativo a `frontend/`, no a `frontend/src/`): las importaciones nuevas son `@/src/lib/auth`, `@/src/lib/http`, `@/src/components/ui/Button` — se documenta aquí porque ningún archivo anterior lo había usado y fija la convención para las tareas siguientes. `vitest.config.ts` ganó un `resolve.alias` equivalente; sin él, las pruebas no resolvían el mismo alias que usa Next.js.
  **Navegación:** `sesiones/actual` (contrato §3.4) no expone la lista de permisos concretos, solo `rol`. Se decidió filtrar los ocho destinos por `rol` con una tabla de grano grueso declarada junto a cada ítem (`nav-items.ts`), documentada primero en `layout.md` antes de escribir el código — Reservas/Recursos/Espacios/Investigación/Notificaciones para los tres roles, Reportes para Técnico y Administrador, Usuarios/Administración solo para Administrador. Es una aproximación deliberada, no la autorización real: cada pantalla sigue revalidando contra el backend. Se corrigieron dos imprecisiones de `FE-05` encontradas al implementar —una redundancia entre "padding" y "gutter" de la región de contenido con números que se pisaban, y la falta de mecanismo concreto para "visibilidad calculada en runtime"— ambas ya reflejadas en `layout.md`.
  **Estado de sesión:** `correo · rol` + «Cerrar sesión» (`Button` variant `ghost`) a la derecha de la cabecera en escritorio; en el panel superpuesto de móvil/tablet, al pie del panel, como ya fijaba `layout.md`. Cerrar sesión llama `DELETE /api/auth/sesiones/actual` y fuerza `window.location.href = "/login"` (navegación completa, no `router.push`, para descartar cualquier estado de cliente junto con la cookie que el servidor ya invalidó).
  **Responsive:** navegación persistente `lg:block` (≥1024px) vs. panel superpuesto con velo bajo `lg`, mismo componente y mismo ancho (240px) en ambos casos, tal como pedía `layout.md`. Foco de los ítems de navegación con el mismo anillo que `Button` (`ring-4` + `color-mix(...)` de `--color-sky` al 55%).
  Verificado: `npx tsc --noEmit`, `npm run build` y `npm run lint` limpios; `npm test` — 14 pruebas en verde (2 de `layout.tsx`: redirige sin sesión sin pintar contenido, pinta shell+contenido con sesión; 5 de `AppShell`: filtrado por rol para los tres roles, apertura del panel superpuesto, cierre de sesión llama al `DELETE` correcto; más las 7 de `Button` sin regresión). Sin página real bajo `(app)/` todavía —las pantallas llegan con `FE-07` en adelante—, así que la verificación de "una ruta bajo `(app)/`" se hizo probando el layout directamente, no navegando una URL real.

---

## Fase 3 — Auth · **cerrada**

La especificación de pantallas de auth ya está cerrada (`screens.md`, `wireframes.md`, `screen-flow.md`, del commit `ui_auth`). Es el primer módulo completo del frontend nuevo, igual que auth lo fue para el backend, y **queda como referencia de estilo** para las ocho tareas de implementación que siguen. **El siguiente paso es la Fase 4.**

### FE-07 — Pantallas de auth · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** las nueve pantallas de [`screens.md`](../../modules/auth/screens.md) — login, autorregistro, activación por invitación, recuperación, reautenticación, administración de cuentas e invitaciones — funcionando contra el backend real.
- **Afectados:** `frontend/app/(auth)/**`, rutas de administración de cuentas bajo `(app)/administracion/`. Ampliado con **`frontend/src/lib/auth-api.ts`, `frontend/src/lib/auth-types.ts`, `frontend/src/components/ui/Field.tsx`, `frontend/src/components/ui/Select.tsx`, `frontend/src/components/auth/AuthCard.tsx`, `frontend/src/components/auth/RegionMensaje.tsx`** — ver Resultado.
- **Dependencias:** FE-04, FE-06. Contrato: [`auth/api-contract.md`](../../contratos/auth/api-contract.md), completo.
- **Aceptación:** los nueve wireframes de `wireframes.md` corresponden uno a uno con una ruta; ningún estado de error mostrado usa un texto distinto al fijado ahí (nada de `detail` de FastAPI, nada de SQL ni trazas); un intento de acceder a una pantalla de administración sin el permiso `cuentas.administrar` no muestra ni parpadea el contenido protegido antes de redirigir.
- **Resultado:** las nueve rutas, una por wireframe: `login`, `registro`, `activacion/[token]`, `recuperacion`, `recuperacion/[token]`, `reautenticacion` y `cambiar-contrasena` bajo su grupo correspondiente; `administracion/cuentas/invitar` (WF-AUTH-03, emitir y reenviar como variante de la misma pantalla) y `administracion/cuentas/[idCuenta]` (WF-AUTH-09) bajo `(app)/administracion/`, con un layout propio que redirige a `/reservas` cuando `rol !== "ADMINISTRADOR"` — misma aproximación de grano grueso que ya usa la navegación de `FE-06`, porque `sesiones/actual` tampoco expone aquí el permiso `cuentas.administrar` granular. Prueba dedicada (`administracion/layout.test.tsx`, 4 casos) verifica que ni `TECNICO` ni `USUARIO` ven el contenido antes de la redirección.
  **Andamiaje compartido, no componentes cerrados:** `Field` y `Select` (label + control + error en línea, sobre los tokens de `FE-02`) y `AuthCard`/`RegionMensaje` (tarjeta centrada y región `{mensaje}` con `aria-live`) — `components.md` solo cierra `Button`; esto es infraestructura pragmática de esta tarea, documentada aquí, no una entrada nueva en el catálogo de componentes.
  **`auth-api.ts`** envuelve los doce endpoints del contrato (§3.1–§3.9, §4.1–§4.4, §5.1, §6.1–§6.2) con sus formas tipadas exactas; ninguna pantalla llama a `apiRequest` con una ruta escrita a mano.
  **Corrección de arquitectura encontrada al implementar:** `AppShell` (Client Component) importaba tipos desde `src/lib/auth.ts`, que trae `next/headers` — funcionaba mientras no hubiera ninguna página real bajo `(app)/`, pero en cuanto esta tarea añadió las primeras, `next build` falló («You're importing a component that needs next/headers»): un módulo que importa una API server-only envenena todo su bundle de cliente, no solo el export que de hecho se usa. Se separaron los tipos y `ETIQUETA_ROL` a **`src/lib/auth-types.ts`** (sin `next/headers`, seguro para cliente y servidor); `src/lib/auth.ts` queda solo con `obtenerSesionActual`, server-only. `AppShell.tsx` y `nav-items.ts` (de `FE-06`) se actualizaron para importar del archivo correcto.
  Se intentó envolver `obtenerSesionActual` en `cache()` de `react` para no repetir la petición entre `(app)/layout.tsx` y `(app)/administracion/layout.tsx` — se revirtió: `cache()` no existe en el `react@18.3.1` de npm que usa Vitest (solo en la versión que Next.js empaqueta internamente para build), y rompía las cuatro pruebas de layout con `TypeError: cache is not a function`. Queda como una petición HTTP de más por request en rutas anidadas bajo administración, no como un error; revisitable si el proyecto sube a React 19.
  **Un vacío real del contrato, no inventado:** WF-AUTH-09 exige mostrar cuenta objetivo, correo, estado, tipo e identidad, pero el contrato de auth no expone ninguna consulta de cuenta ajena (§10) y el propio wireframe lo deja explícito («mecanismo de acceso pendiente»). Igual que WF-AUTH-03 ya resolvía el contexto de reenvío por parámetros de URL, `administracion/cuentas/[idCuenta]` usa el mismo mecanismo (`?correo=&estado=&tipo=&identidad=`) para la parte de solo lectura; las acciones reales (cambiar estado, cambiar tipo) sí llaman a `PATCH`/`PUT` contra el `idCuenta` de la ruta. No hay una llamada de consulta inventada.
  **Mensajes de error:** cada pantalla mapea los códigos del contrato al texto literal exacto de su fila en `wireframes.md` (p. ej. login: `401 CREDENCIALES_INVALIDAS` → «No se pudo iniciar sesión con las credenciales proporcionadas.»; cualquier `429` → «La operación está temporalmente limitada.»). Donde el wireframe describe un estado en prosa sin dar una frase literal (p. ej. «identidad no válida» en la activación), se compuso un texto que cumple la misma restricción de seguridad (sin detalles internos) en vez de inventar una distinción que la envolvente de error no permite hacer — ambos casos comparten `422 VALIDACION` sin campo que los diferencie.
  **Destinos no fijados por las fuentes, decisión documentada:** el `screens.md` de auth deja explícitamente sin fijar la pantalla de inicio tras un login exitoso. Se usa `/reservas` (primer destino de la navegación de `FE-06`) como aterrizaje por defecto para cuentas sin actualización inicial pendiente, y `/usuarios/perfil` (todavía no construida, llega con `FE-08`/`FE-09`) para las que sí la tienen pendiente — mismo patrón que `FE-06` usó para `/login` antes de que existiera.
  Verificado: `npx tsc --noEmit`, `npm run build` (11 rutas, 9 de ellas las pantallas de auth) y `npm run lint` limpios. `npm test` — 18 pruebas en verde: las 12 ya existentes de `Button`/`AppShell` sin regresión, más 2 de `(app)/layout.tsx` (ahora con el mensaje `?motivo=sesion_vencida`) y 4 nuevas de `administracion/layout.tsx`. No se escribió una prueba de React Testing Library por cada una de las nueve pantallas — se priorizó la prueba explícitamente pedida por la aceptación (el guard de administración) sobre cobertura exhaustiva de cada formulario, dado el tamaño de la tarea.

---

## Fase 4 — Catálogos e identidad

Un bloque por módulo, en el mismo orden en que el backend los cerró (`tasks.md`, Fase 2–3): primero identidad y estructura, después inventario. Cada módulo repite el mismo par de tareas: **Especificación** de sus pantallas y **Implementación** contra esa especificación ya cerrada.

### FE-08 — Especificación de pantallas — usuarios · **cerrada**

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `usuarios`, con la misma forma que los de auth.
- **Afectados:** `specs/modules/usuarios/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`usuarios/user-flow.md`](../../modules/usuarios/user-flow.md) y [`usuarios/api-contract.md`](../../contratos/usuarios/api-contract.md), ambos cerrados.
- **Aceptación:** `python tools/validar.py` en 0 fallas con los nuevos documentos enlazados desde `usuarios/overview.md`.
- **Resultado:** cinco pantallas, no once — los once flujos `UF-USR-01` a `UF-USR-11` se agrupan por superficie compartida, no uno a uno: `SCR-USR-01` (completar actualización inicial) sirve por igual a `UF-USR-01` y `UF-USR-02`, que la propia fuente describe como «el mismo recorrido»; `SCR-USR-05` agrupa las cinco vinculaciones (`UF-USR-06` a `UF-USR-10`) porque comparten un único contexto (vinculaciones vigentes + catálogo); `UF-USR-11` (iniciar una reserva) queda sin pantalla propia, igual que auth dejó sin pantalla los flujos de continuidad — el efecto ocurre en `reservations`, que solo consulta la condición de perfil de este módulo.
  **Frontera de módulo respetada:** la creación y administración de identidades (`POST /api/usuarios`, `POST /api/personal` del contrato) no tiene pantalla aquí a pesar de vivir bajo las rutas de este módulo — sus flujos de origen (`UF-ADM-02`, `UF-ADM-03`) pertenecen a `administration`, no a los once `UF-USR`. Documentado explícitamente en «Alcance y fuentes» para que no se lea como un olvido.
  `wireframes.md` referencia los doce endpoints del contrato (§2 a §4) con sus tres códigos de error propios (`DOCUMENTO_DUPLICADO`, `TELEFONO_DUPLICADO`, `VINCULACION_DUPLICADA`) más el catálogo común; ninguna sección de ningún documento quedó marcada «Pendiente».
  Verificado: `python tools/validar.py` en 0 fallas — sin referencias colgadas a los `RN-INV-*` de `investigacion` citados, y las tres tareas enlazadas correctamente desde `usuarios/overview.md`.

### FE-09 — Implementación — usuarios · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** las pantallas de `usuarios` funcionando contra el backend real.
- **Afectados:** `frontend/app/(app)/usuarios/**`.
- **Dependencias:** FE-08, FE-04, FE-06.
- **Aceptación:** corresponde uno a uno con los wireframes de FE-08; `tsc --noEmit` limpio.
- **Resultado:** cinco rutas bajo `(app)/usuarios/perfil` (una por wireframe WF-USR-01 a WF-USR-05), Client Components con `useState` + `apiRequest` como FE-07, sin TanStack. Andamiaje: `src/lib/usuarios-api.ts` (12 endpoints §2–§4, ninguna ruta a mano) + `usuarios-types.ts` sin `next/headers`, y `SeccionVinculaciones` compartida entre actualización inicial y gestión (la misma superficie en ambos recorridos, según screen-flow). Textos de error literales de cada fila de `wireframes.md`; sin pantalla para §5–§6 de administration. Verificado: `tsc --noEmit`, `build` (5 rutas), `lint` limpios; `npm test` — 21 en verde (3 nuevas dirigidas: aviso sin vinculación + 409 al continuar, aviso RN-USR-11 al desactivar la última, duplicado junto al campo).

### FE-10 — Especificación de pantallas — administration · **cerrada**

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `administration`.
- **Afectados:** `specs/modules/administration/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`administration/user-flow.md`](../../modules/administration/user-flow.md) y su contrato, cerrados.
- **Aceptación:** igual criterio que FE-08.
- **Resultado:** cinco pantallas agrupadas por superficie compartida: `SCR-ADM-01` unidades/cargos, `SCR-ADM-02` permisos, `SCR-ADM-03` identidades con invitación (UF-ADM-02/03), `SCR-ADM-04` importaciones (UF-ADM-01/04, con unidad destino para equipos y rechazo total), `SCR-ADM-05` auditoría de solo lectura. Las superficies de contrato sin flujo propio (§2, §3, §5) se documentan desde contrato y reglas sin inventar flujos. Cuentas de FE-07 referenciadas, no redefinidas. Verificado: `python tools/validar.py` en 0 fallas, documentos enlazados desde `overview.md`.

### FE-11 — Implementación — administration · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** las pantallas de `administration` (unidades, cargos, permisos, auditoría) funcionando contra el backend real.
- **Afectados:** `frontend/app/(app)/administracion/**`.
- **Dependencias:** FE-10, FE-04, FE-06, FE-07 (comparte área de administración de cuentas con auth).
- **Aceptación:** igual criterio que FE-09. La vista de auditoría no expone contraseñas, secretos de sesión, tokens completos ni claves, igual que exige `SEC-AUD-03`.
- **Resultado:** cinco rutas nuevas (una por wireframe WF-ADM-01 a WF-ADM-05), Client Components con `useState` + `apiRequest` como FE-07/FE-09. Andamiaje: `src/lib/administracion-api.ts` (endpoints §2–§5 con formas tipadas) + `administracion-types.ts` sin `next/headers`; `http.ts` gana passthrough de `FormData` (multipart con boundary del navegador, CSRF intacto) para la carga Excel. Las pantallas de cuentas de FE-07 se reutilizan sin tocarse, salvo precarga de `?correo=&tipo=` al llegar desde identidades. Textos de error literales de cada fila. Verificado: `tsc --noEmit`, `build` (5 rutas), `lint` limpios; `npm test` — 24 en verde (3 dirigidas nuevas: duplicado junto al campo, carga no confirmable, auditoría sin secretos).

### FE-12 — Especificación de pantallas — resources · **cerrada**

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `resources`, incluida la importación masiva de equipos.
- **Afectados:** `specs/modules/resources/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`resources/user-flow.md`](../../modules/resources/user-flow.md) y su contrato, cerrados.
- **Aceptación:** igual criterio que FE-08. La pantalla de importación documenta el resultado por fila y el rechazo total ante cualquier fila con error, conforme a la decisión ya cerrada en `decisiones_pendientes_para_revision.md`.
- **Resultado:** cuatro superficies agrupadas por superficie compartida: `SCR-REC-01` catálogo y registro (UF-REC-01 a UF-REC-05), `SCR-REC-02` edición, estado y unidad (UF-REC-06 a UF-REC-10, UF-REC-12, con advertencia de impacto y confirmación), `SCR-REC-03` laboratorio (UF-REC-13, con versionado de horario), `SCR-REC-04` validaciones de equipos en importación por referencia a `SCR-ADM-04` (sin superficie propia de carga). `UF-REC-11` queda explícitamente sin superficie por ser comunicación entre módulos. Verificado: `python tools/validar.py` en 0 fallas, documentos enlazados desde `overview.md`.

### FE-13 — Implementación — resources · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** las pantallas de `resources` funcionando contra el backend real.
- **Afectados:** `frontend/app/(app)/recursos/**`.
- **Dependencias:** FE-12, FE-04, FE-06.
- **Aceptación:** igual criterio que FE-09. La importación con filas en error no permite confirmar la carga y muestra el resultado por fila.
- **Resultado:** tres rutas (catálogo con registro, detalle con edición/estado/unidad, laboratorio propio para no chocar con `[id]`), Server Components que deciden `puedeGestionar` por rol sin store en cliente. Andamiaje: `src/lib/recursos-api.ts` (endpoints §2–§3) + `recursos-types.ts` sin `next/headers`. Importación reutiliza `administracion/importaciones` sin pantalla propia, como fija FE-12. Verificado: `tsc --noEmit`, `build` (3 rutas), `lint` limpios; `npm test` — 28 en verde (4 dirigidas nuevas: crear por tipo, 403, impacto con confirmación explícita).

### FE-14 — Especificación de pantallas — espacios · **cerrada**

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `espacios`, incluidos los campos adicionales de los cinco tipos cerrados.
- **Afectados:** `specs/modules/espacios/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`espacios/user-flow.md`](../../modules/espacios/user-flow.md) y su contrato, cerrados. FE-12 para reutilizar el patrón de asociación con recursos.
- **Aceptación:** igual criterio que FE-08.
- **Resultado:** cuatro superficies agrupadas por superficie compartida: `SCR-ESP-01` registro, edición y estado (con advertencia de cancelaciones y confirmación explícita), `SCR-ESP-02` recursos asociados (misma unidad, sin doble asociación, retiro que deshabilita), `SCR-ESP-03` campos adicionales (los cinco tipos cerrados, opciones, reorden, deshabilitación sin perder historia), `SCR-ESP-04` consulta con visibilidad por rol. `UF-ESP-14` queda explícitamente sin superficie por ocurrir en `reservations`; disponibilidad temporal y horario propio, fuera por §6 del contrato. Verificado: `python tools/validar.py` en 0 fallas, documentos enlazados desde `overview.md`.

### FE-15 — Implementación — espacios · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** las pantallas de `espacios` funcionando contra el backend real.
- **Afectados:** `frontend/app/(app)/espacios/**`.
- **Dependencias:** FE-14, FE-13 (reutiliza el selector de recursos), FE-06.
- **Aceptación:** igual criterio que FE-09.
- **Resultado:** dos rutas (catálogo con registro, detalle con edición/estado/asociados/campos), Server Components que deciden `puedeGestionar` por rol sin store. Andamiaje: `src/lib/espacios-api.ts` (endpoints §2–§4) + `espacios-types.ts` sin `next/headers`. Impacto previo con conteos antes de deshabilitar; reorden por intercambio de posiciones; `agregarOpciones` envuelto en el lib aunque ninguna pantalla lo usa todavía (la creación con opción inicial cubre el flujo). Verificado: `tsc --noEmit`, `build` (2 rutas), `lint` limpios; `npm test` — 33 en verde (5 dirigidas nuevas: crear, duplicado, impacto con confirmación, lista-sin-opciones).

### FE-16 — Especificación de pantallas — researchs · **cerrada**

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `researchs` (proyectos, semilleros, equipos de investigación).
- **Afectados:** `specs/modules/researchs/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`researchs/user-flow.md`](../../modules/researchs/user-flow.md) y su contrato, cerrados.
- **Aceptación:** igual criterio que FE-08. No introduce ninguna asociación de proyecto o semillero con un laboratorio: en este sistema se asocian a personas, no limitan dónde puede reservar el usuario.
- **Resultado:** cuatro superficies agrupadas por superficie compartida: `SCR-INV-01` catálogos (consulta y estado), `SCR-INV-02` actividades, `SCR-INV-03` perfiles, `SCR-INV-04` vinculaciones ajenas (crear/desactivar/reactivar con aviso de última activa). Vinculaciones propias e importación sin superficie propia (viven en usuarios y administration). Verificado: `python tools/validar.py` en 0 fallas, documentos enlazados desde `overview.md`.

### FE-17 — Implementación — researchs · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** las pantallas de `researchs` funcionando contra el backend real, incluida la importación masiva.
- **Afectados:** `frontend/app/(app)/investigacion/**`.
- **Dependencias:** FE-16, FE-13 (reutiliza el patrón de importación de FE-13), FE-06.
- **Aceptación:** igual criterio que FE-09.
- **Resultado:** cuatro rutas (catálogos con estado, actividades, perfiles, vinculaciones ajenas) tras guard de layout solo-Admin — todo `/api/investigacion/*` exige `usuarios.administrar` global, así que el guard por rol basta y el servidor autoriza cada operación. Andamiaje: `src/lib/investigacion-api.ts` (endpoints §2–§5) + `investigacion-types.ts` sin `next/headers`. Importación sin pantalla propia: enlaza a `administracion/importaciones`. Verificado: `tsc --noEmit`, `build` (4 rutas), `lint` limpios; `npm test` — 37 en verde (4 dirigidas nuevas: guard sin parpadeo, duplicada, reactivación sin duplicar).

---

## Fase 5 — Reservas

El módulo central y el más complejo: cinco tipos de reserva con estrategias distintas (`architecture.md` §6.3–6.4, [`reservations/architecture.md`](../../modules/reservations/architecture.md)).

### FE-18 — Especificación de pantallas — reservations · **cerrada**

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `reservations`: solicitud por tipo, gestión, calendario, lista de espera y transiciones de estado.
- **Afectados:** `specs/modules/reservations/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`reservations/user-flows.md`](../../modules/reservations/user-flows.md) y los cuatro contratos que lo cubren (`API-13` a `API-16`), cerrados. FE-14 para el selector de espacios, FE-12 para el de recursos.
- **Aceptación:** igual criterio que FE-08. Cubre los seis estados de una reserva y las cinco estrategias (espacio, recurso interno, recurso de campus, recurso externo, lista de espera) como flujos de pantalla distintos, no como una sola pantalla genérica con campos condicionales sin documentar.
- **Resultado:** cuatro superficies agrupadas por superficie compartida: `SCR-RES-01` solicitud por estrategia (con disponibilidad consultada sin garantía y edición en solicitada), `SCR-RES-02` gestión del Técnico por tipo y estado, `SCR-RES-03` lista de espera separada, `SCR-RES-04` consulta, calendario y órdenes de solo lectura. Siete flujos de sistema sin superficie propia, documentados en vez de omitidos. Verificado: `python tools/validar.py` en 0 fallas, documentos enlazados desde `overview.md`.

### FE-19 — Implementación — reservations · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** las pantallas de `reservations` funcionando contra el backend real.
- **Afectados:** `frontend/app/(app)/reservas/**`.
- **Dependencias:** FE-18, FE-15, FE-13, FE-06. Es la tarea de implementación más grande del plan; puede dividirse por tipo de reserva al abrirla, siguiendo el mismo criterio que dividió `API-13` a `API-16` en el backend.
- **Aceptación:** igual criterio que FE-09. Ninguna pantalla permite confirmar una reserva sin pasar por la respuesta real del backend — la exclusión de solapamiento y de compromiso físico único la garantiza `DB-12` en el servidor, y el frontend no puede sustituirla con una validación propia.
- **Resultado:** tres rutas (listado con filtros, creación con formularios por estrategia, detalle con gestión por tipo y estado), Client Components con `useState` + `apiRequest` como FE-07/09. Andamiaje: `src/lib/reservas-api.ts` (25 endpoints §2–§8) + `reservas-types.ts` sin `next/headers`. La disponibilidad se consulta sin garantizar asignación; el `409` del servidor manda y sus textos son literales. Verificado: `tsc --noEmit`, `build` (3 rutas), `lint` limpios; `npm test` — 41 en verde (4 dirigidas nuevas: crear por tipo, solapamiento, propuesta aceptada, finalizar sin devolución).

---

## Fase 6 — Notificaciones y reportes

### FE-20 — Especificación de pantallas — notifications · **cerrada**

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `notifications`: bandeja y preferencias.
- **Afectados:** `specs/modules/notifications/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`notifications/user-flow.md`](../../modules/notifications/user-flow.md) y su contrato, cerrados.
- **Aceptación:** igual criterio que FE-08.
- **Resultado:** dos superficies agrupadas por superficie compartida: `SCR-NOT-01` bandeja (propias, filtros, marcar sin efectos colaterales, ajena indistinguible) y `SCR-NOT-02` preferencias (general por defecto, reemplazo completo, solo canal correo). `UF-NOT-03` queda explícitamente sin superficie por ser tarea del sistema; el estado de envíos no se consulta por decisión del contrato. Verificado: `python tools/validar.py` en 0 fallas, documentos enlazados desde `overview.md`.

### FE-21 — Implementación — notifications · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** bandeja y preferencias de `notifications` funcionando contra el backend real.
- **Afectados:** `frontend/app/(app)/notificaciones/**`.
- **Dependencias:** FE-20, FE-06.
- **Aceptación:** igual criterio que FE-09.
- **Resultado:** dos rutas bajo `(app)/notificaciones` (bandeja WF-NOT-01 y `preferencias` WF-NOT-02) sin gate de rol, Client Components con `useState` + `apiRequest` como FE-09. Andamiaje: `src/lib/notificaciones-api.ts` (5 endpoints §2–§3) + `notificaciones-types.ts` sin `next/headers`. La bandeja filtra por estado y tipo, marca con `POST .../lectura` y trata ajena e inexistente igual (`404` → mismo mensaje); las preferencias envían reemplazo completo y lo no listado rige por la general; los tipos vienen de `GET tipos-evento` y `404`/`422` tienen mensaje de corrección propio. Sin estado de envíos, que el contrato no expone. Verificado: `tsc --noEmit`, `build` (2 rutas), `lint` limpios; `npm test` — 47 en verde (6 nuevas dirigidas: marcar conserva el texto, ajena/inexistente indistinguible, ya leída sin acción, reemplazo de preferencias, tipo inexistente, tipo repetido).

### FE-22 — Especificación de pantallas — reports · **cerrada**

- **Tipo:** Especificación
- **Objetivo:** `screens.md`, `wireframes.md` y `screen-flow.md` de `reports`: ocupación, solicitudes, lista de espera y exportación.
- **Afectados:** `specs/modules/reports/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** [`reports/user-flow.md`](../../modules/reports/user-flow.md) y su contrato, cerrados.
- **Aceptación:** igual criterio que FE-08. Fija qué informes se muestran como gráfico (con Recharts, único cargador de gráficos fijado en `architecture.md` §3) y cuáles como tabla exportable, en vez de dejarlo a criterio de quien implemente.
- **Resultado:** tres pantallas, una por informe (`SCR-REP-01` ocupación, `SCR-REP-02` solicitudes, `SCR-REP-03` horas de lista de espera); `UF-REP-02` (exportar) es una acción de cada una y no una pantalla, porque la precondición es tener el reporte a la vista. **Gráfico o tabla, decidido con evidencia:** ocupación lleva tabla más un gráfico de barras horizontales de una sola medida y un solo color (porcentaje en laboratorio, espacio y recurso; horas en proyecto y semillero, que no tienen porcentaje; una fila sin porcentaje no dibuja barra, nunca una en cero); solicitudes y lista de espera son solo tabla. La razón de solicitudes se comprobó con el script de la guía de visualización: los colores de los tokens fallan como paleta categórica de seis series (luminosidad del ámbar, croma del gris, contraste de turquesa y ámbar bajo 3:1), y `FE-23` prohíbe salirse de los tokens; el verde de marca sí pasa como serie única en claro y en oscuro. Sin filas de total: sumarían solo la página a la vista (`RN-VIS-02`). **Dos discrepancias entre contrato y servidor, resueltas en el contrato:** `dimension` en solicitudes solo admite `laboratorio` (el texto decía «la dimensión seleccionada») y su periodo es opcional. Verificado: `python tools/validar.py` en 0 fallas con los documentos enlazados desde `reports/overview.md`.

### FE-23 — Implementación — reports · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** los informes de `reports` funcionando contra el backend real, con sus gráficos y su exportación.
- **Afectados:** `frontend/app/(app)/reportes/**`.
- **Dependencias:** FE-22, FE-06. Es la única tarea del plan que introduce una librería de visualización (Recharts); antes de codificar un gráfico, conviene revisar la guía de la skill `dataviz` de este entorno para mantener paleta y forma consistentes con el resto del sistema de diseño.
- **Aceptación:** igual criterio que FE-09. Ningún gráfico usa un color fuera de la paleta de [`design-tokens.md`](../../ui/design-tokens.md).
- **Resultado:** portada `/reportes` y tres pantallas (`/reportes/ocupacion`, `/solicitudes`, `/lista-espera`) sobre un solo `ReporteClient` guiado por el tipo de informe. Ocupación lleva tabla y gráfico Recharts de barras horizontales de una sola medida y un solo color (`--color-primary-1`); una fila sin porcentaje no dibuja barra y se enumera bajo el gráfico; solicitudes y lista de espera son solo tabla. Unidad, espacio, recurso, proyecto y semillero se eligen por nombre; el periodo propone el mes en curso y la consulta es explícita; exportar CSV/Excel usa los filtros de la **última consulta**, no los del formulario; el vacío, el `422` y el `403` se muestran en la misma pantalla. **Hallazgo cerrado de paso:** `GET /api/unidades` exige `unidades.administrar`, así que un Usuario o Técnico no podía ni elegir la unidad al reservar. Se añadió `GET /api/laboratorios` (contrato de resources §3.0, legible por cualquier cuenta) y `SelectorUnidad` recurre a él ante un `403`; el selector de proyecto y semillero de reportes usa las opciones de la propia cuenta cuando la lista administrativa le está vedada. Quien tiene alcance por unidad ve ofrecidas solo las suyas. Verificado: Vitest 112/112, `tsc` y lint limpios, backend 116/116 contra `reservas_test`, y `e2e/reportes.spec.ts` (8/8) con tabla, gráfico y descarga reales.

### FE-47 — Especificación de pantalla — inicio · **cerrada**

- **Tipo:** Especificación
- **Objetivo:** `SCR-REP-04`, `WF-REP-04` y su `screen-flow.md`: el panel de inicio con el agregado del periodo (`GET /api/reportes/resumen`, contrato §3.4) para quien gestiona y accesos para el Usuario.
- **Afectados:** `specs/modules/reports/screens.md`, `wireframes.md`, `screen-flow.md`, `specs/ui/layout.md` (destino «Inicio» primero, para los tres roles).
- **Dependencias:** FE-22, contrato §3.4 (corregido antes: mapa por cantidad en grid 7–19, top por asignación, Inicio para los tres roles).
- **Aceptación:** `python tools/validar.py` en 0 fallas; ningún gráfico usa más de una tinta de datos fuera de `--color-primary-1`; `por_estado` es tabla.
- **Resultado:** `SCR-REP-04` (indicadores con previo, seis estados, serie por fecha, barras por laboratorio y recursos, mapa de calor por cantidad, enlaces a los tres reportes; sin paginación ni exportación) y `WF-REP-04` con sus estados (incluido Usuario sin permiso, sin llamada al endpoint). `layout.md` suma «Inicio» como primer destino de los tres roles y aterrizaje tras el login. Verificado: `python tools/validar.py` en 0 fallas.

### FE-48 — Implementación — inicio · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** la pantalla `/inicio` funcionando contra el backend real, y el login aterriza en ella para los tres roles.
- **Afectados:** `frontend/app/(app)/inicio/**`, `frontend/src/lib/reportes-api.ts` (`consultarResumen`), `frontend/src/components/shell/nav-items.ts`, `AppShell.tsx` (icono), `frontend/app/(auth)/login/page.tsx` (destino), `frontend/e2e/inicio.spec.ts`.
- **Dependencias:** FE-47, API-20. No toca el contrato.
- **Aceptación:** tras el login se llega a `/inicio`; quien gestiona ve indicadores, tablas y gráficos del periodo con su previo; el Usuario ve accesos sin llamar al resumen; `tsc --noEmit` limpio y pruebas en verde. Ningún gráfico usa un color fuera de [`design-tokens.md`](../../ui/design-tokens.md).
- **Resultado:** `app/(app)/inicio/page.tsx` (Server Component que pasa `rol` y `unidades_autorizadas`) + `InicioClient` (formulario con mes en curso, tarjetas de indicadores con previo, tabla de seis estados, serie por fecha y barras con Recharts en `--color-primary-1`, mapa de calor por cantidad en rejilla de una sola tinta, enlaces a los tres reportes; el Usuario ve accesos sin llamada al endpoint) y `GraficosInicio` aparte. «Inicio» primero en `nav-items.ts` para los tres roles, con icono en `AppShell`; login redirige a `/inicio` (salvo actualización inicial pendiente). Verificado: `tsc` y `lint` limpios, Vitest 155/155 (6 pruebas nuevas: 4 de `InicioClient`, 2 de `GraficosInicio`), backend 129/129, y `e2e/inicio.spec.ts` 3/3 más suite completa 80 passed / 4 skipped (flujo-despliegue, solo pila limpia) contra la pila reconstruida con `reservas_e2e`. **Hallazgo de paso:** un `beforeEach(() => mock.mockReset())` sin llaves devuelve el mock y Vitest lo ejecuta como limpieza, con promesa rechazada sin manejar — documentado en la prueba.

---

## Fase 7 — Brechas frente a las especificaciones

Las tareas `FE-09` a `FE-21` se cerraron con un alcance menor que el de los `screens.md` y las reglas de negocio de sus módulos. Se detectó el 2026-09-29 al probar la aplicación en un navegador real (Playwright y Chrome) y cruzar cada pantalla con sus reglas. Cada tarea de esta fase cita las reglas que cierra por su identificador completo; ninguna toca una regla de otro módulo sin nombrarlo.

### FE-24 — Navegación completa · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** que los ocho destinos de `layout.md` lleven a una pantalla. Hoy `/investigacion`, `/usuarios`, `/administracion` y `/reportes` responden 404: solo existen sus subpáginas.
- **Afectados:** `frontend/app/(app)/investigacion/page.tsx`, `usuarios/page.tsx`, `administracion/page.tsx`, `reportes/page.tsx`; `frontend/e2e/`.
- **Dependencias:** FE-06.
- **Aceptación:** con una sesión de `ADMINISTRADOR`, cada destino del menú responde 200 con un `h1` y enlaces a las subpantallas de su módulo que la sesión puede usar; `/reportes` muestra que el módulo se construye en FE-23 en vez de un 404. La prueba de humo recorre los ocho destinos del menú, no solo las subrutas.
- **Resultado:** cuatro portadas de módulo (`/investigacion`, `/usuarios`, `/administracion`, `/reportes`) con enlaces a sus pantallas, y `IndiceModulo` como componente común. La cabecera suma «Mi perfil» (solo Usuario) y «Cambiar contraseña», que existían como pantallas sin ningún enlace que las alcanzara. `/reportes` es hoy la portada de los tres informes (FE-23). Verificado: `e2e/menu.spec.ts` recorre los enlaces reales del menú con administrador y usuario (8/8). **Contradicción anotada, no resuelta:** `layout.md` muestra «Investigación» a los tres roles, pero todo `/api/investigacion/*` exige `usuarios.administrar`, así que para Usuario y Técnico ese destino redirige a `/reservas`.

### FE-25 — Solicitud de reserva conforme a las reglas · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** que `/reservas/nueva` cumpla `SCR-RES-01`: tipos ofrecidos por la unidad, contexto según el tipo de cuenta, campos adicionales del espacio, acompañantes y apoyo técnico.
- **Afectados:** `frontend/app/(app)/reservas/nueva/**`, `frontend/src/components/reservas/**`, `frontend/src/lib/reservas-api.ts`, `frontend/src/lib/espacios-api.ts`.
- **Dependencias:** FE-19, FE-15, FE-13, FE-17.
- **Aceptación:** cada punto es una petición y su respuesta.
  - Tipos (`RN-TIP-02`, `RN-TIP-03`, `RN-TIP-06`): el selector sale de `GET /api/reservas/tipos?id_unidad=`; con un solo tipo se elige solo; con ninguno se avisa que la unidad no admite reservas y no se puede guardar.
  - Contexto (`RN-CTX-01`, `RN-CTX-04`, `RN-CTX-05`, `RN-CTX-08`, `RN-TIP-PE-08`, `RN-TIP-PE-09`, `RN-TIP-PE-11`): una cuenta `USUARIO` elige entre **sus** vinculaciones activas (proyecto, semillero, pasantía, trabajo de grado) o una actividad institucional, nunca ambas; una cuenta `PERSONAL` elige proyecto y/o semillero del catálogo general. Con una sola vinculación válida se preselecciona.
  - Campos adicionales (`RN-TIP-PE-12`, `RN-TIP-PE-18`, `RN-TIP-PE-19`): al elegir un espacio se muestran sus campos habilitados según su tipo; los obligatorios impiden guardar y viajan en `campos_adicionales`.
  - Recursos asociados (`RN-TIP-PE-12`, `RN-TIP-PE-13`): al elegir espacio y periodo se listan sus recursos asociados marcando cuáles están disponibles; los no disponibles no se envían.
  - Acompañantes (`RN-ACO-01`, `RN-ACO-02`, `RN-ACO-04`, `RN-ACO-05`, `RN-TIP-PE-05`): solo con proyecto o semillero, elegidos por nombre entre las cuentas vinculadas; `asistentes` es su número y no supera la capacidad.
  - Apoyo (`RN-RES-09`, `RN-RES-10`): casilla «requiere técnico», bloqueada en verdadero cuando algún equipo elegido lo exige.
  - Salida (`RN-TIP-RC-12`, `RN-TIP-RE-12`): campo «nombre de la actividad o evento» en campus y externo.
- **Resultado:** `/reservas/nueva` elige la unidad primero y ofrece los tipos que esa unidad habilita (autoselección con uno, aviso con ninguno); el contexto sale de `GET /api/reservas/contexto/opciones` (vinculaciones propias y actividades para `USUARIO`, catálogo general para `PERSONAL`; una actividad institucional excluye lo demás); campos adicionales del espacio según su tipo, con los obligatorios verificados antes de enviar; recursos asociados con su disponibilidad; acompañantes por nombre con asistentes = su número; apoyo técnico bloqueado cuando un equipo lo exige; nombre de actividad en campus y externo. **Contrato ampliado antes de codificar:** `reservations` §2.9 (`GET /api/reservas/contexto/opciones`) y §2.10 (`GET /api/reservas/acompanantes/opciones`), porque `/api/investigacion/*` exige permiso de administrador y ningún endpoint daba las cuentas elegibles. Backend con 2 pruebas nuevas; frontend con 11 pruebas de la página y `e2e/lista-espera.spec.ts` contra el backend real.

### FE-26 — Lista de espera completa · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** que el flujo de `SCR-RES-03` se pueda recorrer entero: solicitar, evaluar viabilidad, diligenciar el formulario por partes, aprobar con recepción de material, ejecutar y finalizar.
- **Afectados:** `frontend/src/components/reservas/GestionReservaClient.tsx` y componentes nuevos de lista de espera; `frontend/src/lib/reservas-api.ts`.
- **Dependencias:** FE-19, FE-25.
- **Aceptación:**
  - Formulario (`RN-TIP-PLE-03`, `RN-TIP-PLE-04`, `RN-TIP-PLE-09`): solo se ofrece con viabilidad positiva; cada actor edita únicamente su parte (`PUT .../formulario` con `datos_usuario` o `datos_tecnico`, nunca ambas); la parte técnica exige la del reservista; si el reservista cambia la suya, la pantalla avisa que la revisión técnica se invalida.
  - Aprobación (`RN-TIP-PLE-05`): `POST .../aprobacion` con `material_recibido: true` tras una confirmación explícita; sin viabilidad, parte del reservista o parte técnica revisada se muestra el `409` del servidor.
  - Rol: las acciones de gestión (aprobar, rechazar, viabilidad, ejecutar, finalizar) solo se ofrecen a quien puede gestionar la unidad; el reservista ve únicamente lo suyo (formulario, adjuntos, cancelar). Desaparece el `esTecnico = true` fijo de `GestionReservaClient`.
  - Aviso `RN-TIP-PLE-09`: cambiar la descripción de una lista `SOLICITADA` con viabilidad avisa que deberá evaluarse de nuevo.
- **Resultado:** `ListaEsperaPanel` (viabilidad con motivo obligatorio si es negativa; formulario por partes, cada actor solo la suya; aprobación con confirmación de recepción de material y lista de lo que falta) y `AdjuntosListaEspera` (subida y descarga). `GestionReservaClient` recibe la sesión y solo ofrece lo que corresponde a cada rol: desaparece el `esTecnico = true` fijo; el reservista responde las propuestas del técnico y el técnico las contrapropuestas (`RN-PROP-03`, `RN-PROP-04`); el principal de un recurso interno no ofrece retiro. `aprobarReserva` envía `material_recibido`. Verificado con `e2e/lista-espera-flujo.spec.ts`: crear → viable → formulario por partes → aprobar con recepción → ejecutar → finalizar con horas.

### FE-27 — Renovación de sesión · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** que la sesión no muera a los 15 minutos (`RN-AUTH-SES-01`, `RN-AUTH-SES-05`) sin abrir la cookie de refresco a las páginas.
- **Afectados:** `frontend/src/lib/http.ts`, `frontend/src/components/shell/**`.
- **Dependencias:** FE-03. Requiere decidir dónde se renueva: la cookie `rp_refresh` tiene `Path=/api/auth/sesiones` y solo la ve el navegador al llamar a la API.
- **Aceptación:** una petición del cliente que recibe `401 NO_AUTENTICADO` llama una vez a `POST /api/auth/sesiones/renovacion` y reintenta la original solo si la renovación tuvo éxito; si falla, redirige a `/login?motivo=sesion_vencida`. Con el token de acceso vencido pero el refresco vigente, la navegación entre pantallas no vuelve a login. Se corrige la nota de `http.ts` que declara «sin reintento en 401».
- **Resultado:** `apiRequest` renueva una sola vez ante `401 NO_AUTENTICADO` en el navegador y repite la petición solo si la renovación funcionó; varias peticiones vencidas comparten una renovación (el refresco rota). Como un Server Component no recibe `rp_refresh`, `AppShell` renueva cada 5 minutos **solo si hubo actividad**, para no anular el tiempo máximo de inactividad (`SEC-SES-09`). Verificado con 5 pruebas de `http.ts` y `e2e/sesion.spec.ts` (se borra `rp_access` y una acción del cliente renueva y continúa).

### FE-28 — Consulta y gestión de reservas · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** cerrar `SCR-RES-02` y `SCR-RES-04`: listado útil, detalle con nombres, edición en `SOLICITADA`, recursos agregables, orden de salida y calendario.
- **Afectados:** `frontend/app/(app)/reservas/**`, `frontend/src/components/reservas/**`, `frontend/src/lib/reservas-api.ts`.
- **Dependencias:** FE-25, FE-26.
- **Aceptación:**
  - Listado: muestra fecha, espacio o recurso por nombre, unidad y solicitante (para quien gestiona); filtros `estado`, `tipo_reserva`, `id_unidad`, `desde`, `hasta`, `espacio_id`, `recurso_id` y paginación real.
  - Detalle: recursos, cuentas, espacio y contexto por nombre; historial con actor y motivo.
  - Edición (`RN-PRO-02`, `RN-PRO-06`): el reservista edita en `SOLICITADA` solo los campos que el tipo permite con `PATCH /api/reservas/{id}`; en otro estado no se ofrece.
  - Recursos (`RN-TIP-PE-21`, `RN-TIP-RI-10`): el técnico puede agregar además de retirar, y el `PRINCIPAL` de interno no ofrece retiro.
  - Cancelación (`RN-CAN-02`): solo se ofrece mientras no haya iniciado la ejecución del tipo.
  - Órdenes y calendario (`RN-TIP-RC-07`, `RN-TIP-RC-11`, `RN-TIP-RE-07`, `RN-CAL-01`): campus y externo muestran la orden y descargan el PDF; espacio e interno aprobadas descargan el `.ics`; donde no aplica no se ofrece.
- **Resultado:** el listado (`/reservas`) muestra cuándo, qué, tipo, unidad, solicitante y estado, con filtros por estado, tipo, unidad y espacio y paginación de a 20, más recientes primero. El detalle muestra unidad, solicitante, espacio, contexto, acompañantes, campos adicionales, recursos e historial con actor **por nombre** (`ResumenReserva`); el reservista edita su solicitud en `SOLICITADA` (periodo, datos de salida, descripción, observación) y solo viaja lo que cambió; el técnico agrega recursos además de retirarlos, y el principal de un recurso interno no ofrece retiro; campus y externo aprobados muestran la orden de salida FGL 030 con su PDF; espacio e interno aprobados ofrecen el `.ics`. **Contrato ampliado antes de codificar:** `reservations` §3.1 (`periodo`, `objeto`, `unidad_nombre`, `solicitante_nombre` por fila) y §3.2 (`unidad_nombre`, `solicitante_nombre`, `detalle.espacio_nombre`, `nombre` por recurso, `acompanantes_detalle`, `actor_nombre` en el historial). Verificado: backend con una prueba nueva, 14 pruebas de listado y detalle y `e2e/reservas.spec.ts`.
- **No cubre (abierto como `FE-31`):** editar desde la pantalla el contexto, los acompañantes, los campos adicionales y los recursos de una solicitud (`RN-PRO-06`); los filtros `desde` y `hasta` del listado, porque el servidor los aplica sobre la fecha de creación y no sobre la fecha de la reserva, lo que el contrato no aclara.

### FE-29 — Recursos, espacios, laboratorio e identidades completos · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** que los formularios cubran los campos que `SCR-REC-01` a `SCR-REC-03`, `SCR-ESP-01` a `SCR-ESP-03` y la administración de identidades piden.
- **Afectados:** `frontend/src/components/recursos/**`, `frontend/src/components/espacios/**`, `frontend/app/(app)/administracion/identidades/**`, `frontend/src/lib/*-api.ts`.
- **Dependencias:** FE-13, FE-15, FE-11.
- **Aceptación:**
  - Equipos (`RN-EQP-08`, `RN-EQP-09`, `RN-REC-10`): categoría, serial, marca, modelo, calibración, `requiere_apoyo`, `acreditado`, bodega, centro de costo y estado operativo, con la restricción de rol del contrato.
  - Mobiliario y otros: descripción.
  - Laboratorio (`RN-LAB-03`, `RN-LAB-04`, `RN-LAB-07`, `RN-APR-02`, `RN-REC-01`): `habilitado_reservas`, días de atención, antelación, aprobación automática, recordatorio y `notificar_por_correo`.
  - Espacios (`RN-ESP-01`, `RN-ESP-02`): ubicación y descripción al crear; edición de los datos; filtros en el listado; opciones de campos de tipo lista (`PATCH .../opciones/{opcion_id}`).
  - Identidades (`RN-USR-01` de administration): listar, editar y habilitar o deshabilitar usuarios y personal (`PATCH /api/usuarios/{id}`, `/estado`, `/api/personal/{id}`, `/estado`).

### FE-31 — Edición completa de la solicitud · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** cerrar `RN-PRO-06`: que el reservista pueda cambiar en `SOLICITADA` también el contexto, los acompañantes, los campos adicionales y los recursos, con los mismos selectores de `FE-25`. Y aclarar en el contrato el sentido de los filtros `desde` y `hasta` de `GET /api/reservas`.
- **Afectados:** `frontend/src/components/reservas/EditarReservaPanel.tsx` y los componentes de `FE-25`; `specs/contratos/reservations/api-contract.md` §3.1.
- **Dependencias:** FE-25, FE-28.
- **Aceptación:** `PATCH /api/reservas/{id}` con cada bloque completo (`contexto`, `recursos`, `acompanantes`, `campos_adicionales`) según §2.8, con la respuesta del servidor ante cada rechazo visible; el contrato dice si `desde` y `hasta` filtran por fecha de creación o por fecha de la reserva, y el servidor y la pantalla lo cumplen.
- **Resultado:** **Recursos:** el alta y la edición de un equipo piden nombre, placa, serial, marca, modelo, operatividad, apoyo técnico, acreditación, calibración (con su próxima fecha), próximo mantenimiento, instalador y guía rápida; mobiliario y otros piden nombre y descripción; bodega, centro de costos y fecha de compra se muestran de solo lectura (llegan por importación); la edición envía solo lo que cambió y un texto vaciado viaja como `null`; el catálogo filtra por unidad, tipo y texto. **Laboratorio:** se ven y editan `habilitado_reservas`, días de atención (lunes a domingo), horario, antelación, aprobación automática, recordatorio y `notificar_por_correo`, con validación de horario y días antes de enviar. **Espacios:** ubicación y descripción al crear, edición de los datos, filtros por unidad, estado y capacidad mínima, y campos adicionales completos (obligatoriedad, nombre, orden hacia arriba y hacia abajo, habilitar y opciones de una lista, que se renombran, deshabilitan y agregan). **Identidades:** nueva pantalla `/administracion/personas` para listar, buscar, filtrar por estado, editar y activar o desactivar usuarios y personal (el correo de quien ya tiene cuenta no se cambia; el cargo se elige por nombre). **Contrato ampliado antes de codificar:** `resources` §3.1 devuelve `notificar_por_correo` (se podía guardar pero no leer). Un `409` al editar un recurso ya no se disfraza de «reservas que exigen confirmación»: se muestra el motivo del servidor. Verificado: backend con una prueba nueva, 92 pruebas del frontend en total (24 archivos) y `e2e/gestion.spec.ts` contra el backend real.
- **No cubre:** la **categoría** del equipo (existe la tabla `recursos.categorias_equipos`, pero está vacía y ningún endpoint del contrato la administra ni la lista); las **frecuencias** de calibración y mantenimiento (el modelo no dice en qué unidad van); registrar un espacio con sus campos en un solo paso (se agregan después, desde su detalle; los recursos sí se asocian al registrar desde FE-38); reordenar las opciones de una lista.
- **Resultado:** `EditarReservaPanel` cubre `RN-PRO-06`: además del periodo, los datos de salida, la descripción y la observación, el reservista cambia el **contexto**, los **recursos** (principal y adicionales, o solo complementarios en espacio), los **acompañantes**, los **campos adicionales** del espacio (con otro espacio se piden de nuevo) y el **apoyo técnico**, con los mismos selectores de `FE-25` y los valores actuales precargados. Cada bloque viaja completo y solo si cambió; el contexto nunca queda vacío; un equipo que exige apoyo lo vuelve obligatorio; en lista de espera se avisa antes de guardar que cambiar la descripción invalida la viabilidad. **Fechas del listado:** `desde` y `hasta` ahora acotan por la **fecha de uso** —la del espacio o interno, o de la salida a la devolución en campus y externo (`RN-DIS-02`)— y no por la de creación; la lista de espera queda fuera al filtrar; un rango invertido o una fecha mal escrita responden `422`. El contrato (§3.1) lo dice y el listado ofrece «Desde» y «Hasta». **Error de backend corregido:** editar una lista de espera respondía siempre `422`, porque el servicio fusiona los valores actuales (listas vacías) y la estrategia las rechazaba; ahora solo se rechaza lo que el cliente envía y no aplica al tipo (`recursos`, `acompanantes`, `campos_adicionales`, `requiere_apoyo`). Verificado: 3 pruebas de backend nuevas (lista de espera, espacio por bloques, fechas de uso), 5 del panel y `e2e/reservas.spec.ts` contra el backend real.
- **No cubre:** el orden `fecha` del listado (`orden=fecha`) sigue ordenando por creación; el contrato lo admite y el servidor lo aproxima.

### FE-32 — Rediseño visual y formularios interactivos · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** que la interfaz deje de verse plana y que los formularios sean más amables de completar, sin cambiar reglas, contratos ni nombres accesibles. Se abre por pedido directo del equipo tras usar la aplicación en un navegador.
- **Afectados:** `specs/ui/design-tokens.md`; `frontend/src/styles/tokens.css`, `frontend/tailwind.config.ts`, `frontend/app/{layout,globals}`; `frontend/src/components/ui/**`, `shell/**`, `auth/AuthCard.tsx`, `app/(auth)/layout.tsx`; el formulario de `frontend/app/(app)/reservas/nueva/page.tsx` y los selectores de casilla que usa.
- **Dependencias:** FE-02, FE-07, FE-24.
- **Aceptación:** los tokens nuevos (bosque, radio y sombra de tarjeta, tipografías) están en `design-tokens.md` antes que en el código; ninguna prueba cambia su consulta por nombre accesible (Vitest 112/112 y E2E 73/73 siguen en verde); los campos responden al puntero, al foco y al error; el formulario de nueva reserva se divide en pasos que aparecen según lo elegido; las casillas son fichas seleccionables; el menú marca la sección activa; el contraste de texto sigue siendo AA.
- **Resultado:** tipografías nuevas (Bricolage Grotesque para títulos, menú y botones; Figtree para el cuerpo) y tokens de bosque, radio y sombra de tarjeta, documentados en `design-tokens.md`. Barra lateral en bosque con iconos, marca lima en la sección activa y avatar en la cabecera; portada de marca en las pantallas públicas. `Field` y `Select` responden al puntero (borde verde), al foco (etiqueta y anillo) y al error (icono y fondo tenue), con flecha propia en el selector. Nuevos `Seccion`, `BarraAcciones`, `CasillaTarjeta` e `Insignia`: el formulario de nueva reserva se divide en pasos que aparecen al elegir el tipo, con barra de acciones fija, fichas seleccionables para recursos, acompañantes y apoyo técnico, y estados de reserva como insignias en el listado. Botones y etiquetas en minúsculas de frase. Se respeta `prefers-reduced-motion`. Los nombres accesibles no cambiaron: Vitest 112/112, `tsc` y lint limpios, `validar.py` en 0 fallas y E2E 73/73 contra el backend real. **No cubre:** el resto de formularios (recursos, espacios, personas, perfil) ganan el aspecto de `Field` y `Select` pero aún no se dividen en pasos con tarjetas.

---

### FE-33 — Acciones de cada reserva en el listado · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** que quien gestiona reservas no tenga que abrir cada una para actuar: el listado muestra, en cada reserva, los botones de las acciones que ese actor puede hacer, y cada botón las resuelve en un modal.
- **Afectados:** `frontend/src/components/reservas/{ListadoReservas,GestionReservaClient}.tsx`, `frontend/src/components/ui/Modal.tsx`, `frontend/src/lib/reservas-acciones.ts`, `frontend/app/(app)/reservas/page.tsx`.
- **Dependencias:** FE-28, FE-31, FE-32. No toca el contrato: usa las mismas operaciones de `reservations` que el detalle.
- **Aceptación:** cada reserva ofrece solo lo que el rol y el estado permiten (el servidor sigue autorizando); un botón abre un modal con esa parte de la gestión, no con toda la página; al completarse una acción el listado se actualiza sin vaciarse; el modal se cierra con Escape o con el fondo, devuelve el foco al botón y enlaza a la página completa; los flujos y los errores del servidor se ven igual que en el detalle.
- **Resultado:** `GestionReservaContenido` extrae el contenido de gestión y lo reutilizan la página de detalle (`vista="todo"`) y el modal (una vista por acción: revisión, propuestas, ejecución, finalización, cancelación, edición, recursos y lista de espera). `accionesDe` decide qué botones corresponden con el mismo criterio del detalle: el técnico de la unidad ve Aprobar, Rechazar, Proponer otro periodo, Registrar entrega o Iniciar, Finalizar y Recursos según tipo y estado; quien solicitó ve Editar y Cancelar; los demás solo «Ver detalle». El listado pasó de tabla a tarjetas con ficha de calendario, insignia de estado, atajos de estado y una fila de acciones. Verificado: Vitest 117/117 (5 pruebas nuevas del modal y de los permisos), `tsc` y lint limpios, y `e2e/listado-acciones.spec.ts` contra el backend real (rechazar desde el modal y ver el listado actualizado).
- **No cubre:** que el listado sepa si hay una propuesta de periodo pendiente para el reservista (el resumen del listado no lo trae: responde desde «Ver detalle»).

---

### FE-34 — Catálogo de recursos: listado y registro en modal · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** separar el catálogo de recursos del formulario de registro y hacer el listado más legible.
- **Afectados:** `frontend/src/components/recursos/RecursosClient.tsx`, `frontend/src/components/ui/Modal.tsx`, `frontend/src/components/selectores/selectores.tsx`.
- **Dependencias:** FE-13, FE-32, FE-33. No toca el contrato.
- **Aceptación:** el registro de un recurso no está en la página hasta pedirlo con «Registrar recurso» y se resuelve en un modal que se cierra al guardar y avisa «Recurso creado.»; el listado muestra por recurso su nombre, la unidad por su nombre (no su número), el tipo y si está deshabilitado; los filtros por tipo, texto y unidad siguen llamando al servidor con los mismos parámetros.
- **Resultado:** el listado pasó de una lista de enlaces a tarjetas en dos columnas con icono por tipo, insignias de tipo y de «Deshabilitado», conteo, estado vacío con salida y atajos de tipo (Todos, Equipos, Mobiliario, Otros) más búsqueda y unidad en una tarjeta de filtros. El registro vive en un modal amplio con los mismos campos de `CamposRecurso`; los errores del servidor se muestran dentro del modal. `Modal` admite ancho `amplio` y `nombresDeUnidades` resuelve los nombres para el listado. Verificado: Vitest y E2E (`gestion.spec.ts` ajustada para abrir el modal) en verde contra el backend real.

---

### FE-35 — Laboratorios, personal y cargos de origen externo · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** ajustar la interfaz a la [decisión del 2026-09-30](../decisions/origen-externo-estructura-institucional.md): los laboratorios, el personal y los cargos vienen de otra base de datos y no se crean aquí, y «unidad» se dice «laboratorio».
- **Afectados:** `frontend/app/(app)/administracion/{unidades,identidades,personas}/page.tsx`, la portada de administración y los textos y etiquetas que decían «unidad» en reservas, recursos, espacios, reportes y permisos.
- **Dependencias:** FE-11, FE-32. Contratos: solo notas (los endpoints de alta se conservan).
- **Aceptación:** «Laboratorios y cargos» lista y configura pero no crea ni renombra; «Identidades» solo registra usuarios; el personal se consulta y su acceso se activa o desactiva, sin editar sus datos; ningún formulario, filtro ni mensaje dice «unidad».
- **Resultado:** ver la decisión. Se renombraron las etiquetas en 25 archivos (fuente, pruebas y E2E). Verificado: Vitest 121/121, `tsc` y lint limpios. **No cubre:** la integración con la base de origen, que queda por abrir; ni el bloqueo en el servidor de renombrar o cambiar el estado de un laboratorio (hoy solo en la interfaz).

---

### FE-36 — Los equipos vienen de LIA: no se registran desde reservas · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** aplicar a los equipos la [decisión del 2026-09-30](../decisions/origen-externo-estructura-institucional.md): vienen de LIA, no se crean aquí y de LIA solo se trae lo necesario para reservar.
- **Afectados:** `frontend/src/components/recursos/RecursosClient.tsx`, `frontend/e2e/gestion.spec.ts`, `backend/seeds/lia_equipos.sql`.
- **Dependencias:** FE-34, FE-35. Contrato: solo una nota en `resources` §2.1.
- **Aceptación:** «Registrar recurso» ofrece únicamente mobiliario y otros, y lo dice; un equipo existente se sigue editando (apoyo técnico, operatividad, serial); el script carga los equipos activos de LIA con lo necesario para reservar.
- **Resultado:** el registro de un equipo desapareció de la interfaz. La carga trae, por equipo, laboratorio, nombre, marca, modelo, placa, serial, estado y si requiere calibración, y deja `requiere_apoyo` y `acreditado` en falso porque no existen en LIA. Se cargaron los 2 equipos activos; los otros 3 de LIA (inactivos, con serial y placa repetidos) quedaron fuera. **No cubre:** la categoría (Patrón o Auxiliar), las frecuencias de calibración y mantenimiento, los archivos y los datos técnicos, que no hacen falta para reservar; ni la integración continua con LIA.

---

### FE-37 — Catálogo de espacios: listado y registro en modal · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** dar al catálogo de espacios el mismo formato que el de recursos ([FE-34](#fe-34--catálogo-de-recursos-listado-y-registro-en-modal--cerrada)): un listado legible y el registro fuera de la página.
- **Afectados:** `frontend/src/components/espacios/EspaciosClient.tsx` y su prueba.
- **Dependencias:** FE-15, FE-32, FE-34. No toca el contrato.
- **Aceptación:** el registro de un espacio no está en la página hasta pedirlo con «Registrar espacio» y se resuelve en un modal que se cierra al guardar y avisa «Espacio creado.»; el listado muestra por espacio su nombre, el laboratorio por su nombre (no su número), su capacidad y si está deshabilitado; los filtros siguen llamando al servidor con los mismos parámetros.
- **Resultado:** el listado pasó de una lista de enlaces a tarjetas en dos columnas con icono, insignia de capacidad y de «Deshabilitado», conteo y estado vacío con salida; atajos de estado (Todos, Habilitados, Deshabilitados), laboratorio y capacidad mínima en una tarjeta de filtros, con «Quitar filtros». El registro vive en un modal con los mismos campos. Verificado: Vitest 123/123 (3 pruebas nuevas), `tsc` y lint limpios, y `e2e/gestion.spec.ts` contra el backend real.

---

### FE-38 — Asociar equipos y recursos al registrar un espacio · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** evitar el doble proceso de crear el espacio y después abrirlo para asociarle sus recursos: que «Registrar espacio» permita elegir, en el mismo paso, los equipos y recursos del laboratorio.
- **Afectados:** `frontend/src/components/espacios/EspaciosClient.tsx`, `frontend/src/components/selectores/SelectorRecursosVarios.tsx`.
- **Dependencias:** FE-31, FE-37. No toca el contrato: `POST /api/espacios` ya admite `recursos` (`espacios` §2.1) y el servidor ya valida que cada recurso exista, sea del mismo laboratorio y no esté asociado a otro espacio.
- **Aceptación:** tras elegir el laboratorio, el modal ofrece sus recursos habilitados (equipos, mobiliario y otros) por su nombre; lo elegido viaja en `recursos` al crear; cambiar de laboratorio descarta la selección; un recurso ya asociado a otro espacio se explica sin cerrar el modal.
- **Resultado:** `SelectorRecursosVarios` ofrece ahora fichas seleccionables (las mismas de los recursos del espacio en una reserva) y acepta `reservable={false}` para listar todos los recursos del laboratorio, no solo los reservables. En el modal, «Equipos y recursos del espacio (opcional)» aparece tras el laboratorio; el `409` de un recurso ya asociado muestra qué hacer. Verificado: Vitest 125/125 (2 pruebas nuevas) y `e2e/gestion.spec.ts` contra el backend real: se registra un espacio con la Cámara Climática de LIA y se comprueba en su detalle. **No cubre:** los campos adicionales del espacio, que se siguen agregando después desde su detalle; ni mostrar desde el modal a qué espacio pertenece ya un recurso ocupado (el servidor no lo informa en el listado).

---

### FE-39 — Personas: listado en tarjetas, edición y registro en modal · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** dar a la administración de personas el mismo formato que los catálogos de recursos y espacios: un listado legible y los formularios fuera de la página.
- **Afectados:** `frontend/app/(app)/administracion/personas/page.tsx`, `frontend/app/(app)/administracion/identidades/page.tsx`, `frontend/src/components/administracion/RegistrarUsuarioForm.tsx`.
- **Dependencias:** FE-29, FE-32, FE-35. No toca el contrato.
- **Aceptación:** cada persona se ve con su nombre, correo, documento, teléfono, afiliación o cargo con su laboratorio, y si tiene cuenta o está inactiva; editar y registrar se resuelven en modales; quien no tiene cuenta se puede invitar desde su tarjeta; el personal sigue siendo de solo consulta, con su acceso activable o desactivable ([decisión 2026-09-30](../decisions/origen-externo-estructura-institucional.md)).
- **Resultado:** el listado pasó de filas de texto a tarjetas con inicial, insignias «Con cuenta» o «Sin cuenta» e «Inactivo», conteo y estado vacío; «Usuarios» y «Personal» y el estado son atajos, con búsqueda y «Quitar filtros». «Editar» abre un modal con los mismos campos (el correo sigue bloqueado si ya hay cuenta) y «Registrar usuario» abre otro que reutiliza `RegistrarUsuarioForm`, el mismo formulario de la pantalla de identidades, y ofrece invitar la cuenta al guardar. Verificado: Vitest 127/127 (3 pruebas nuevas), `tsc` y lint limpios, y `e2e/gestion.spec.ts` contra el backend real.

---

### FE-40 — Quitar la pantalla de permisos: los permisos los define el rol · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** aplicar la [decisión del 2026-09-30](../decisions/origen-externo-estructura-institucional.md#los-permisos-los-define-el-rol-2026-09-30): el usuario solo reserva, el técnico gestiona su laboratorio y el administrador todo; los permisos no se otorgan a mano.
- **Afectados:** la portada de administración, `frontend/app/(app)/administracion/permisos/`, `frontend/src/lib/administracion-api.ts` y `administracion-types.ts`, `frontend/e2e/humo.spec.ts`.
- **Dependencias:** FE-24, FE-35.
- **Aceptación:** la portada de Administración no ofrece «Permisos»; la ruta `/administracion/permisos` ya no existe; no queda código del cliente para otorgar o retirar permisos.
- **Resultado:** se eliminó la pantalla, su tarjeta y las cuatro funciones y dos tipos que solo ella usaba. La introducción de Administración y la descripción de «Identidades e invitaciones» se corrigieron (ya no hablan de permisos ni de personal). **No cubre, y queda abierto:** alinear el servidor. Hoy `/api/permisos` sigue siendo la única fuente de permisos por cuenta, así que sin asignaciones sembradas un técnico no puede gestionar; hay que abrir una tarea de backend y de spec que derive los permisos del rol y del laboratorio del cargo (`UF-AUTH-09`, `RN-PER-*`).

---

### FE-41 — Roles fijos en el servidor: el administrador es una cuenta propia · **cerrada**

- **Tipo:** Implementación (servidor, base y spec; se lleva en este plan porque cierra el hueco que dejó FE-40)
- **Objetivo:** que el rol defina los permisos de verdad ([decisión 2026-09-30](../decisions/origen-externo-estructura-institucional.md#los-permisos-los-define-el-rol-2026-09-30)): el usuario solo reserva, el técnico gestiona el laboratorio de su cargo y el administrador todo, y el administrador es una cuenta de Reservas que no viene de LIA.
- **Afectados:** `backend/migrations/014_cuenta_administrador.sql`, `backend/app/core/{authz,deps}.py`, `backend/app/scripts/crear_administrador.py`, los módulos `auth`, `administration`, `usuarios`, `notifications` y `reservations`, las pruebas, `specs/modules/auth/{business-rules,data-model}.md`, los contratos de auth y administration y `frontend/src/lib/*types.ts`.
- **Dependencias:** FE-35, FE-40.
- **Aceptación:** una cuenta `ADMINISTRADOR` entra sin ficha y puede todo; un técnico con un cargo de laboratorio ejerce solo los permisos de ámbito de laboratorio y solo sobre ese laboratorio, y se le deniega lo global; un usuario no ejerce ninguno; no existe `/api/permisos`; el administrador se crea por script sin que la contraseña viaje por argumentos; el sistema no puede quedarse sin administrador.
- **Resultado:** `authz.py` deriva el rol del tipo de cuenta y del cargo y fija en código el conjunto del técnico; la migración 014 amplía las restricciones de `auth.cuentas` (aplicada en la base de pruebas y en la copia, **no** en la viva); se eliminaron los endpoints, el servicio, el repositorio y los esquemas de asignación de permisos; las reglas `RN-AUTH-ROL-02`, `-03`, `-06`, `-07` y `-09` se redefinieron y el modelo de datos de auth se corrigió; las notificaciones a técnicos salen ahora del cargo y no de una asignación; una reserva de administrador muestra «Administrador» como solicitante. Verificado: backend 124/124 contra `reservas_test` (15 pruebas de roles, incluido el script), Vitest 127/127 y E2E 74/74 contra el backend real con la cuenta de prueba convertida a `ADMINISTRADOR`. **No cubre, y queda abierto:** aplicar la migración en la base viva y crear allí el primer administrador (con autorización expresa); retirar los identificadores `RN-PER-*` y `UF-AUTH-09`; retirar `auth.cuenta_permisos`.

---

### FE-42 — Detalle de la reserva en dos columnas, con tarjetas y línea de tiempo · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** que el detalle de una reserva se entienda de un vistazo: qué es y cuál es su estado, qué se puede hacer con ella y qué le ha pasado.
- **Afectados:** `frontend/src/components/reservas/{GestionReservaClient,ResumenReserva}.tsx`.
- **Dependencias:** FE-28, FE-31, FE-33, FE-32. No toca el contrato.
- **Aceptación:** la página separa los datos de la reserva (izquierda) de lo que se puede hacer con ella (derecha); el estado se ve junto al título; el historial se lee como una línea de tiempo; dentro del modal del listado, cada vista sigue mostrando solo su parte, sin tarjetas anidadas; los nombres accesibles y los textos que las pruebas consultan no cambian.
- **Resultado:** cada bloque es una tarjeta: a la izquierda el resumen, la edición, la lista de espera y sus adjuntos y los recursos; a la derecha el calendario, la orden de salida, la revisión, las propuestas, la ejecución, la finalización, la cancelación (ahora con título «Cancelar») y el historial. En una pantalla angosta todo se apila. El estado es una insignia junto a «Reserva #N»; el enlace «← Volver a las reservas» sustituye a buscar el menú. Los recursos son filas con su botón «Retirar»; la lista de recursos por agregar se acota con desplazamiento para que no ocupe la pantalla. En el modal no hay tarjetas (`Tarjeta` es plana). Verificado: Vitest 127/127, `tsc` y lint limpios y E2E 74/74.

---

### FE-43 — Despliegue completo con Docker Compose · **cerrada**

- **Tipo:** Implementación (infraestructura)
- **Objetivo:** que toda la aplicación se levante con `docker compose up -d --build` en un servidor, sin instalar nada más en él.
- **Afectados:** `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, `backend/migrations/aplicar.sh`, `backend/app/core/{config,security}.py`, `.env.example`, `.gitattributes`, `.dockerignore`, `frontend/public/`, `DESPLIEGUE.md`.
- **Dependencias:** FE-41 (el administrador se crea por script).
- **Aceptación:** desde una base vacía, un solo `up` deja base, backend y frontend sanos, con el esquema construido y los datos de LIA cargados; el administrador se crea con el script y puede iniciar sesión por el frontend; repetir `up` no cambia nada; en `ENTORNO=produccion` no arranca con la clave o el secreto de ejemplo; la base nunca se publica.
- **Resultado:** el compose pasó de dos servicios (base y backend) a la pila completa: `db`, `migrar` (construye el esquema en una base vacía en el orden documentado y aplica migraciones pendientes en una que ya lo tiene; nunca borra), `ajustar_volumenes`, `backend` y `frontend`, con `depends_on` por salud; pgAdmin pasó a un perfil opcional. Se corrigieron cuatro bloqueos que habrían roto un servidor: las cookies de sesión siempre eran `Secure` y no funcionan por HTTP (ahora `COOKIE_SECURE`, por defecto `true`); faltaba la carpeta `public` que copia el Dockerfile del frontend; el servidor standalone de Next no escuchaba fuera del contenedor (`HOSTNAME=0.0.0.0`); y el backend corría como root (ahora usuario 10001, con `ajustar_volumenes` para volúmenes anteriores). El backend expone su salud, y faltaban en el compose las variables de correo y `APP_URL`. Verificado en una pila aparte con volúmenes y puertos propios: base vacía con 66 tablas, 5 laboratorios, 3 cargos y 2 equipos; administrador creado y `201` al iniciar sesión por el frontend; segunda corrida sin cambios; y las tres protecciones de producción rechazan los valores de ejemplo. El flujo completo (administrador configura el laboratorio y registra un espacio con un equipo, una usuaria pide la reserva, el técnico la aprueba desde el listado y la usuaria la ve aprobada) se verificó sobre esa misma pila con `e2e/flujo-despliegue.spec.ts` (4/4), que queda como prueba de humo de despliegue. **No cubre:** TLS (se documenta un proxy inverso) ni el respaldo automático (se documentan los comandos).

---

### FE-44 — El usuario solo reserva: menú por rol y rutas protegidas · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** que cada rol vea solo lo suyo, según la regla de roles fijos: el usuario solo reserva, el técnico gestiona su laboratorio y el administrador todo.
- **Afectados:** `frontend/src/components/shell/nav-items.ts`, `frontend/app/(app)/{recursos,espacios,laboratorios}/layout.tsx`, `specs/ui/layout.md`, las pruebas de menú y de humo.
- **Dependencias:** FE-24, FE-41. No toca el contrato: el servidor ya abre los catálogos que el formulario de reserva lee.
- **Aceptación:** el menú del usuario es solo «Reservas»; el del técnico, Reservas, Recursos, Espacios y Reportes; el del administrador, todos menos Notificaciones; un usuario que llega a `/recursos`, `/espacios` o `/laboratorios` por la dirección vuelve a `/reservas`.
- **Resultado:** `layout.md` ofrecía casi todo a todos los roles y mostraba «Investigación» a quien el servidor la deniega; se redefinió su tabla de visibilidad. Verificado: Vitest, y E2E contra el backend real con un usuario cuyo menú es exactamente «Reservas».

---

### FE-45 — Campanita de notificaciones con avisos emergentes · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** sacar las notificaciones del menú: una campanita en la cabecera, junto al perfil, que muestre lo pendiente y avise al entrar abajo a la derecha.
- **Afectados:** `frontend/src/components/shell/{CentroDeAlertas,AppShell}.tsx`, `specs/ui/layout.md`.
- **Dependencias:** FE-21, FE-32, FE-44. No toca el contrato: usa la bandeja y la marca de lectura de `notifications` §2.
- **Aceptación:** la campanita cuenta lo no leído; su panel lista lo último y permite leer una (que lleva a su reserva), marcar todas y ver el historial; al entrar aparecen hasta tres avisos abajo a la derecha, una vez por sesión del navegador, que se cierran solos; una bandeja que falla no rompe la pantalla.
- **Resultado:** un componente que consulta cada minuto con la pestaña visible, guarda en `sessionStorage` lo ya avisado (y funciona sin él), y deja `/notificaciones` como historial. El destino «Notificaciones» se quitó del menú. Verificado: 8 pruebas del componente, la del shell por rol y E2E en el navegador real.

---

### FE-46 — Formulario de reserva en un modal · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** pedir una reserva sin salir del listado, con un formulario más amable.
- **Afectados:** `frontend/src/components/reservas/{NuevaReservaForm,ListadoReservas}.tsx`, `frontend/app/(app)/reservas/nueva/page.tsx`, `frontend/src/components/ui/Seccion.tsx`.
- **Dependencias:** FE-25, FE-32, FE-33. No toca el contrato.
- **Aceptación:** «Nueva reserva» abre el formulario en un modal sin cambiar de página; los pasos van numerados; la barra de acciones queda pegada al pie y siempre ofrece «Cancelar»; al guardar se abre el detalle de la reserva; `/reservas/nueva` sigue funcionando para enlaces directos.
- **Resultado:** el formulario salió de la página a `NuevaReservaForm`, que usan la página y el modal. Los cuatro pasos («¿Qué quieres reservar?», «Detalles», «¿Para quién es?», «Últimos detalles») son una secuencia real, así que llevan número; dentro del modal no son tarjetas sino bloques separados por una línea, y la barra de acciones es el pie del modal. La disponibilidad consultada se muestra en una tarjeta. **No cubre:** cambiar los controles (el tipo sigue siendo una lista desplegable) para no romper el uso por teclado ni las pruebas.

---

### FE-30 — Pruebas de extremo a extremo con Playwright · **cerrada**

- **Tipo:** Implementación
- **Objetivo:** dejar como parte del plan las pruebas E2E que hoy viven sin tarea en `frontend/e2e/`. Esto **cambia** la nota de «Lo que no está en este plan»: los E2E de navegador pasan a estar dentro.
- **Afectados:** `frontend/e2e/**`, `frontend/playwright.config.ts`, `frontend/package.json`.
- **Dependencias:** FE-24 a FE-29 (cada una añade sus pruebas).
- **Aceptación:** `npm run e2e` contra la aplicación levantada en `localhost:3000` recorre los ocho destinos del menú, el login con cookie `HttpOnly`, y los flujos de reserva (espacio con recursos, recurso interno con varios recursos, lista de espera con adjunto). Documenta en `e2e/README.md` las cuentas y datos que necesita y que se siembran en una **copia** de la base, nunca en la viva.
- **Resultado:** `frontend/e2e/` con la sesión guardada de administrador y de usuario (`preparacion.setup.ts`), y especificaciones de autenticación, menú, humo, sesión, reservas, gestión, lista de espera (formulario y flujo completo), un **usuario común** que reserva y edita sin permisos administrativos, y reportes: 73 pruebas contra el backend real, todas en verde. Se siembran en la copia `reservas_e2e`, no en la base viva. El límite de login (5 intentos en 15 minutos por cuenta) obliga a reiniciar `reservas_backend` antes de una corrida completa; está en `e2e/README.md`.

---

## Orden sugerido

```text
Fase 1   FE-01 → FE-02 → FE-03 → FE-04           (cimientos, en paralelo cuando no compartan archivo)
Fase 2   FE-05 → FE-06
Fase 3   FE-07                                    (referencia de estilo del resto)
Fase 4   FE-08/09 → FE-10/11 → FE-12/13 → FE-14/15 → FE-16/17
Fase 5   FE-18/19
Fase 6   FE-20/21 → FE-22/23 → FE-47/48 → FE-49 → FE-50 → FE-51

Fase 7   FE-24 → FE-25 → FE-26 → FE-27 → FE-28 → FE-31 → FE-29 → FE-30 → FE-32 → FE-33 → FE-34 → FE-35 → FE-36 → FE-37 → FE-38 → FE-39 → FE-40 → FE-41 → FE-42 → FE-43 → FE-44 → FE-45 → FE-46 → FE-47 → FE-48 → FE-49 → FE-50   (brechas frente a las reglas)
```

Dentro de cada módulo de Fase 4 a 6, la tarea de **Especificación** siempre cierra antes que su **Implementación**. Entre módulos distintos, el orden sugerido no es una dependencia dura salvo donde se anota explícitamente (p. ej. FE-15 reutiliza el selector de recursos de FE-13).

---

### FE-49 — Inicio con el último mes ya consultado · **cerrada**

- **Tipo:** Implementación (con enmienda de spec: `SCR-REP-04`/`WF-REP-04` pasan a mes anterior con consulta automática al entrar, enmendados primero en esta misma tarea).
- **Objetivo:** al abrir `/inicio`, el resumen del mes calendario anterior ya está consultado, sin pulsar «Consultar»; cambiar filtros sigue exigiendo consultar.
- **Afectados:** `frontend/src/components/inicio/InicioClient.tsx` y su prueba, `frontend/e2e/inicio.spec.ts`, `specs/modules/reports/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** FE-48. No toca el contrato.
- **Aceptación:** al entrar se ve «Consultando…» y después el agregado del mes anterior sin ninguna acción; el Usuario sigue viendo accesos sin llamada; `tsc --noEmit` limpio y pruebas en verde.
- **Resultado:** `PanelGestion` propone el mes anterior (`mesAnterior()`, exportado para la prueba) y lo pide una sola vez al montar (guardia con `useRef`); el formulario conserva «Consultar» para otros filtros. Verificado: `tsc` limpio, Vitest 156/156 y `e2e/inicio.spec.ts` 6/6 contra la pila con `reservas_e2e`.

---

### FE-50 — Inicio con el mes en curso y periodos rápidos · **cerrada**

- **Tipo:** Implementación (con enmienda de spec: `SCR-REP-04` cambia el periodo propuesto, enmendada primero en esta misma tarea).
- **Objetivo:** que «Inicio» abra con datos útiles: el mes en curso, y un clic para cambiar a «Mes pasado», «Este mes» o «Próximos 30 días». El mes anterior solía estar vacío en un sistema que reserva hacia adelante.
- **Afectados:** `frontend/src/components/inicio/InicioClient.tsx` y su prueba, `frontend/e2e/inicio.spec.ts`, `specs/modules/reports/screens.md`, `wireframes.md`, `screen-flow.md`.
- **Dependencias:** FE-49. No toca el contrato.
- **Aceptación:** al entrar se consulta el mes en curso sin pulsar nada; pulsar un periodo rápido cambia las fechas y consulta al instante, conservando el laboratorio; editar una fecha pasa a «Personalizado» sin consultar; `tsc --noEmit` limpio y pruebas en verde.
- **Resultado:** `periodoRapido()` calcula los tres periodos; la fila de periodos es un grupo de botones con `aria-pressed`.

---

### FE-51 — Reservas pendientes en el inicio, con sus acciones · **cerrada**

- **Tipo:** Implementación (con enmienda de spec: `SCR-REP-04` y `WF-REP-04` ganan la sección «Pendientes de decisión», enmendadas primero en esta misma tarea).
- **Objetivo:** que quien gestiona vea, apenas entra, las reservas esperando decisión y pueda aprobarlas, rechazarlas o proponer otro periodo sin ir al listado.
- **Afectados:** `frontend/src/components/inicio/{ReservasPendientes,InicioClient}.tsx` y sus pruebas, `frontend/src/components/reservas/ListadoReservas.tsx` (exporta `TarjetaReserva`), `frontend/app/(app)/inicio/page.tsx`, `specs/modules/reports/screens.md`, `wireframes.md`.
- **Dependencias:** FE-33, FE-50. No toca el contrato: usa el listado de reservas con `estado=SOLICITADA`.
- **Aceptación:** al entrar, el técnico y el administrador ven las reservas `SOLICITADA` de su ámbito (hasta cinco y el total) con las acciones de `accionesDe`; pulsar una acción abre el modal de gestión y, al resolver, la lista se actualiza; sin pendientes dice «No hay reservas pendientes.»; el Usuario no la ve ni llama al listado desde Inicio; una sesión caducada lleva al login; `tsc` limpio y pruebas en verde.
- **Resultado:** `ReservasPendientes` reutiliza `TarjetaReserva` y `GestionReservaContenido`, así que la autorización y las acciones son exactamente las del listado.

---
## Lo que no está en este plan

- **El despliegue del frontend en un entorno real.** `plan.md` §8 ya señala que no hay entorno desplegado; este plan construye contra un backend local.
- **Tests end-to-end de navegador** en las Fases 1 a 6: esas cubren pruebas de componente (React Testing Library). Los E2E con Playwright entran en `FE-30` (Fase 7).
- **La redacción de los textos de interfaz.** Los wireframes fijan estructura y contenido tipo, no la redacción final de cada mensaje — igual que ya aclara `wireframes.md` de auth.
