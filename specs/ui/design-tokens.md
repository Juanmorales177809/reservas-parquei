# Tokens de diseño

## Propósito

Documentar los tokens globales de color, tipografía, espaciado (spacing), radios, sombras y otros valores reutilizables de la interfaz, con alcance transversal a todos los módulos.

## Estado

Colores, tipografía, radios y sombras están definidos, a partir del artifact de diseño «Botones ITM · Corporativo» (opción «Corporativo elevado»). Espaciado queda como catálogo abierto de los valores observados, sin escala formal todavía.

## Colores

Los tokens de color son variables CSS (`--color-*`), con un juego para tema claro y overrides para tema oscuro (`prefers-color-scheme: dark` y `data-theme="dark"` para alternancia manual).

### Base

| Token | Claro | Oscuro | Uso |
|---|---|---|---|
| `--color-bg` | `#F3F5F2` | `#0A100C` | Fondo de página |
| `--color-surface` | `#FFFFFF` | `#121A14` | Fondo de tarjetas y contenedores elevados |
| `--color-text` | `#0F1A12` | `#E9F1EA` | Texto principal |
| `--color-muted` | `#5B6660` | `#9DAA9F` | Texto secundario, metadatos, etiquetas |
| `--color-border` | `#DCE2DC` | `#24322A` | Bordes de tarjetas y contenedores |

### Marca / primary (verde de facultad)

| Token | Valor | Uso |
|---|---|---|
| `--color-primary-1` | `#10A83F` | Extremo claro del degradado primario |
| `--color-primary-2` | `#00681F` | Extremo oscuro del degradado primario |
| `--color-primary-hover-1` | `#0E9737` | Degradado primario, estado hover |
| `--color-primary-hover-2` | `#005A1A` | Degradado primario, estado hover |
| `--color-primary-pressed` | `#00501A` | Color sólido, estado pressed |
| `--color-primary-tint` | `#E3F5E8` (claro) / `#16281C` (oscuro) | Relleno tenue (secondary, ghost, badges de rol/estado) |

### Acento de foco

| Token | Valor | Uso |
|---|---|---|
| `--color-sky` | `#98BF13` | Exclusivo para el anillo de `focus-visible`; no se usa como relleno de botón |

### Success

| Token | Valor | Uso |
|---|---|---|
| `--color-success-1` | `#12B7CF` | Extremo claro del degradado |
| `--color-success-2` | `#007689` | Extremo oscuro del degradado |
| `--color-success-hover-2` | `#006373` | Degradado, estado hover |
| `--color-success-pressed` | `#00505E` | Color sólido, estado pressed |

### Error

| Token | Valor | Uso |
|---|---|---|
| `--color-error-1` | `#F0473F` | Extremo claro del degradado |
| `--color-error-2` | `#C21B1B` | Extremo oscuro del degradado |
| `--color-error-hover-2` | `#A5160F` | Degradado, estado hover |
| `--color-error-pressed` | `#8A1108` | Color sólido, estado pressed |

### Warning

| Token | Valor | Uso |
|---|---|---|
| `--color-warning-1` | `#F5A623` | Extremo claro del degradado |
| `--color-warning-2` | `#C1720A` | Extremo oscuro del degradado |
| `--color-warning-hover-2` | `#A46007` | Degradado, estado hover |
| `--color-warning-pressed` | `#834E05` | Color sólido, estado pressed |

### Neutros de estado

| Token | Claro | Oscuro | Uso |
|---|---|---|---|
| `--color-gray` | `#6B7280` | — | Neutro auxiliar |
| `--color-disabled-bg` | `#E7EBE7` | `#1C261F` | Fondo de cualquier variante en estado disabled |
| `--color-disabled-text` | `#A2AEA4` | `#63705E` | Texto de cualquier variante en estado disabled |

`success`, `error` y `warning` son familias independientes de `primary`: no se derivan del verde de marca. `sky` está reservado en exclusiva para el indicador de foco (ver [Sistema de diseño](design-system.md)), nunca como color de relleno.

## Tipografía

| Token | Valor | Uso |
|---|---|---|
| `--font-display` | `Arial, Helvetica, sans-serif` | Títulos, encabezados de sección, nombres propios destacados |
| `--font-body` | `'Inter', Arial, sans-serif` | Texto de cuerpo, metadatos, contenido de botones |
| `--fs-sm` | `0.750rem` | Etiquetas, texto auxiliar, metadatos |
| `--fs-base` | `1rem` | Texto de cuerpo estándar |
| `--fs-xl` | `1.333rem` | Encabezados de sección (`h2`) |
| `--fs-2xl` | `1.777rem` | Reservado, sin uso fijado todavía |
| `--fs-3xl` | `2.369rem` | Título principal (`h1`) |
| `--fs-4xl` | `3.158rem` | Reservado, sin uso fijado todavía |
| `--fs-5xl` | `4.210rem` | Reservado, sin uso fijado todavía |
| `--fw-normal` | `400` | Peso por defecto |
| `--fw-bold` | `700` | Énfasis, etiquetas, botones, encabezados |

Escala tipográfica de razón ~1.333 (fourth). Familia `Inter` se carga vía Google Fonts (pesos 400 y 700); `--font-display` usa fuentes del sistema, sin carga externa.

## Espaciado

Sin escala formal de tokens todavía. Valores observados en el artifact, a modo de catálogo de referencia mientras no se cierre una escala:

`8px`, `9px`, `10px`, `12px`, `14px`, `16px`, `18px`, `20px`, `22px`, `26px`, `30px`, `44px` (paddings de sección y contenedores; gaps entre botones, tarjetas y filas de lista).

## Radios

| Token | Valor | Uso |
|---|---|---|
| `--radius` | `12px` | Botones y controles interactivos |
| — | `14px` | Miniaturas de color (swatches) |
| — | `16px` | Tarjetas de contenido (reserva, dispositivo de ejemplo) |
| — | `20px` | Contenedores de sección, bloque de handoff |
| — | `999px` (pill) | Chips y badges de estado/rol |

Solo `--radius` está tokenizado como variable; el resto son valores fijos repetidos por tipo de contenedor, candidatos a tokenizarse cuando se implemente en Tailwind (ver [Implementación frontend](frontend-implementation.md)).

## Sombras

| Token | Valor | Uso |
|---|---|---|
| `--shadow-default` | `0 6px 16px -4px rgba(0,60,20,.35)` | Estado default de variantes con relleno sólido |
| `--shadow-hover` | `0 10px 24px -4px rgba(0,60,20,.45)` | Estado hover de variantes con relleno sólido |
| `--shadow-pressed` | `0 2px 6px -1px rgba(0,60,20,.30)` | Estado pressed de variantes con relleno sólido |

Las tres sombras usan el mismo tinte verde (`rgba(0,60,20,*)`) sin importar la variante del botón (success, danger, warning incluidos): la sombra identifica «elevación de acción», no el color semántico de la variante. Variantes con relleno tenue (`secondary`, `ghost`) no llevan sombra.

## Otros valores reutilizables

- Anillo de foco: `0 0 0 4px color-mix(in srgb, var(--color-sky) 55%, transparent)`, aplicado con `box-shadow` en `:focus-visible`, igual para todas las variantes de botón.
- Transición estándar de botón: `box-shadow .18s ease, transform .08s ease, background .18s ease, opacity .15s ease`.

## Convenciones de tokens

- Prefijo por familia: `--color-{rol}-{paso}` (`primary-1`, `primary-2`, `primary-hover-1`, `primary-pressed`, `primary-tint`, …). El paso `1`/`2` marca los extremos de un degradado; `hover`/`pressed` son variantes de estado, no de paso.
- Cada familia semántica (`primary`, `success`, `error`, `warning`) repite la misma forma: extremo 1, extremo 2, hover, pressed. `primary` añade además `tint` porque es la única familia con variantes de relleno tenue (`secondary`, `ghost`).
- Los tokens de superficie (`bg`, `surface`, `text`, `muted`, `border`, `disabled-*`, `primary-tint`) tienen valor distinto por tema; los tokens de marca y semánticos (`primary-1/2`, `success/error/warning-*`) son los mismos en ambos temas.
- Los radios y sombras fuera de `--radius`, `--shadow-*` aún no están tokenizados; se documentan aquí como valores fijos hasta que se decida su nombre definitivo.

## Documentos relacionados

- [Sistema de diseño](design-system.md): reglas de aplicación de estos tokens.
- [Componentes UI](components.md): especificación de cada componente y sus estados.
- [Implementación frontend](frontend-implementation.md): cómo se exponen estos tokens en Tailwind.
