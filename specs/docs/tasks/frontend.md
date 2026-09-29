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
