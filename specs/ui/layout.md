# Distribución de la interfaz

## Propósito

Documentar las reglas de distribución y ubicación de los elementos en la interfaz, con alcance transversal a todos los módulos.

## Estado

Definido el shell autenticado: cabecera, navegación y región de contenido, con sus dimensiones, tokens aplicados y adaptación a tamaño de pantalla. Las pantallas públicas de auth (login, registro, activación, recuperación) ya tienen su propia distribución cerrada en [`specs/modules/auth/wireframes.md`](../modules/auth/wireframes.md) y no se redefinen aquí.

## Estructura general de las pantallas

Hay dos shells. El **público**, sin sesión, ya está cerrado por las pantallas de auth: formularios centrados, sin navegación persistente. El **autenticado**, que define este documento, envuelve todas las pantallas de los demás módulos y tiene tres regiones fijas:

```text
┌───────────────────────────────────────────────┐
│ Cabecera (ancho completo)                      │
├───────────┬─────────────────────────────────────┤
│           │                                     │
│ Navega-   │ Región de contenido                 │
│ ción      │ (max-width 1180px, centrada)        │
│           │                                     │
└───────────┴─────────────────────────────────────┘
```

- **Cabecera** — franja horizontal de ancho completo, arriba de todo.
- **Navegación** — columna vertical a la izquierda, debajo de la cabecera, con los destinos autorizados para la sesión.
- **Región de contenido** — donde vive cada pantalla, a la derecha de la navegación.

En viewport móvil y tablet la navegación no ocupa columna propia: se convierte en un panel superpuesto (ver «Adaptación a tamaños de pantalla»), y la cabecera y la región de contenido ocupan el ancho completo.

## Ubicación de elementos

### Cabecera

- **Contexto de pantalla** (título de la vista actual) a la izquierda.
- **Estado de sesión** a la derecha, solo en escritorio: `correo · rol` seguido de «Cerrar sesión», como texto/enlace — no como un componente de badge, que `components.md` todavía no especifica. Se usa `correo`, no el nombre de la persona: `GET /api/auth/sesiones/actual` no devuelve nombre, solo lo hace `GET /api/perfil` del módulo usuarios, una dependencia que el shell no tiene hoy. Si el equipo decide mostrar el nombre real más adelante, es un cambio de texto que implica sumar esa llamada — no estructural, pero tampoco gratuito, y queda anotado en [`decisiones_pendientes_para_revision.md`](../../decisiones_pendientes_para_revision.md).
- En móvil y tablet, la cabecera colapsada solo lleva el título de la pantalla y un botón de texto «Menú» que abre la navegación; el estado de sesión se muda dentro de ese panel, no compite por espacio con el título.

### Navegación

Hasta ocho destinos, en este orden y con estos nombres: **Reservas, Recursos, Espacios, Investigación, Usuarios, Administración, Notificaciones, Reportes**. Auth no es un destino propio: su superficie autenticada (administración de cuentas e invitaciones) vive dentro de Administración.

La visibilidad de cada destino se calcula en el momento de pintar la navegación, contra la respuesta viva de `GET /api/auth/sesiones/actual` para esa sesión — nunca contra una tabla precalculada que ignore la sesión real (`FE-06` lo exige explícitamente). La señal disponible para eso es `rol` — `sesiones/actual` no expone la lista de permisos concretos que en verdad gobierna cada operación, esos solo se conocen al llamar cada endpoint. Cada destino declara para qué roles aparece:

| Destino | `USUARIO` | `TECNICO` | `ADMINISTRADOR` |
|---|---|---|---|
| Reservas, Espacios, Recursos, Investigación, Notificaciones | ✓ | ✓ | ✓ |
| Reportes | | ✓ | ✓ |
| Usuarios, Administración | | | ✓ |

Es una aproximación de grano grueso, no la autorización real: un destino visible puede seguir respondiendo `403` en una operación concreta si esa sesión no tiene el permiso puntual, y eso lo resuelve cada pantalla contra el backend, no este documento. Un destino no visible para el rol de la sesión **no aparece**; no se muestra deshabilitado, porque no es un estado de `Button` — sencillamente no es parte de la respuesta de esa sesión.

Sin contador de notificaciones ni ningún otro indicador numérico en la navegación: requeriría un componente de badge que `components.md` todavía no especifica («Badge de estado/rol: Pendiente»). `Notificaciones` es, por ahora, un ítem de navegación como cualquier otro.

### Región de contenido y acciones

Cada pantalla ubica su acción principal siguiendo la misma regla que ya fija `components.md`: alineada a la derecha del título de la pantalla en escritorio y tablet, `fullWidth` en móvil (ver la regla ya cerrada en «Adaptación a tamaños de pantalla»). Acciones secundarias de una pantalla se ubican junto a la principal o dentro de cada elemento de una lista, según defina el `screens.md` de cada módulo — este documento no prescribe más allá de la posición de la acción principal.

## Distribución y alineación

- Ítems de navegación apilados verticalmente, alineados a la izquierda, con ritmo vertical uniforme (mismo alto y separación entre todos).
- Ítem de navegación activo: fondo `--color-primary-tint`, texto `--color-primary-2` — la misma pareja que ya usan las variantes `secondary` y `ghost` de `Button`, no un tratamiento nuevo.
- Cabecera: contexto de pantalla y estado de sesión distribuidos en los extremos opuestos de la franja (el primero a la izquierda, el segundo a la derecha), nunca centrados ni apilados en escritorio.
- Región de contenido: centrada horizontalmente dentro de su ancho máximo (`margin-inline: auto`).

## Espaciado y dimensiones

### Dimensiones nuevas de este documento

Ninguna estaba tokenizada todavía porque son propias del shell, no de un componente ya cerrado:

| Elemento | Valor |
|---|---|
| Ancho del panel de navegación (persistente o superpuesto: es el mismo componente en ambos casos, solo cambia si está en flujo o flotando) | `240px` |
| Alto de la cabecera | `64px` |

### Dimensiones y espaciados reutilizados

Tomados de precedentes ya cerrados, no inventados para este documento:

| Elemento | Valor | Origen |
|---|---|---|
| Ancho máximo de la región de contenido | `1180px` | Página del artifact de diseño aprobado |
| Padding vertical de la región de contenido | `44px` arriba, `90px` abajo | Misma página del artifact |
| Padding horizontal (gutter) en móvil/tablet | `20px` | Catálogo de espaciado, [`design-tokens.md`](design-tokens.md#espaciado) — coincide con el lateral que usaba el artifact, no es un valor nuevo |
| Padding horizontal (gutter) en escritorio | `30px` | Catálogo de espaciado, [`design-tokens.md`](design-tokens.md#espaciado) |

### Tokens de sistema de diseño aplicados al chrome del shell

Ninguno nuevo: se reutilizan tal como los fija [`design-system.md`](design-system.md).

- Fondo de cabecera y navegación: `--color-surface` — ya descrito como «fondo de tarjetas y contenedores elevados»; la cabecera y la navegación son chrome persistente, no el lienzo de la página.
- Fondo de la región de contenido: `--color-bg` — deliberadamente distinto de `--color-surface`, para que las tarjetas de cada pantalla conserven contraste contra su fondo.
- Separador entre cabecera/navegación y contenido: borde `--color-border` de 1px. Nunca `--shadow-*`: `design-system.md` reserva las sombras a variantes de botón con relleno sólido («la elevación comunica que esta acción tiene peso»), y el chrome estructural no es una acción.
- Radio: ninguno en cabecera ni navegación — es chrome de borde a borde, no una tarjeta. Las tarjetas y secciones dentro de la región de contenido conservan los radios de 16px/20px que ya documenta `design-tokens.md`, sin cambios.
- Foco de un ítem de navegación: el mismo anillo que ya usa `Button` (`--color-sky` al 55%, 4px, `:focus-visible`). `design-system.md` lo fijaba solo para variantes de botón; se deja explícito aquí porque un enlace de navegación es un tipo de elemento interactivo que ese documento no cubría todavía.

## Adaptación a tamaños de pantalla

Dos comportamientos, no tres — móvil y tablet comparten el mismo:

| Categoría | Rango | Navegación |
|---|---|---|
| Móvil | `< 768px` (bajo `md` de Tailwind) | Panel superpuesto |
| Tablet | `768px`–`1023px` (`md` a `lg`) | Panel superpuesto |
| Escritorio | `≥ 1024px` (`lg` en adelante) | Persistente, siempre visible |

Tablet se agrupa con móvil, no con escritorio: un panel de navegación de 240px persistente a 768–1023px deja apenas 528–783px para pantallas con tablas (reportes, listados de reservas, catálogos de recursos y espacios) — insuficiente sin forzar scroll horizontal constante en casi cualquier pantalla con una tabla.

**Panel superpuesto** (móvil y tablet): mismo componente y mismo ancho (240px) que la navegación persistente de escritorio, solo que flota sobre un velo (`scrim`) en vez de ocupar columna propia. Se abre con el botón de texto «Menú» de la cabecera colapsada y se cierra al elegir un destino o al tocar fuera del panel.

Una regla ya fijada, tomada del artifact de diseño «Botones ITM · Corporativo»: en viewport móvil, el botón `primary` de una pantalla usa `fullWidth` (ancho 100%, ver [Componentes UI](components.md#tamaños)). En desktop y tablet conserva su ancho intrínseco. No aplica a otras variantes salvo que se decida lo contrario.

## Documentos relacionados

- [Tokens de diseño](design-tokens.md): valores reutilizables.
- [Sistema de diseño](design-system.md): reglas globales de uso visual.
- [Componentes UI](components.md): elementos reutilizables de la interfaz.
