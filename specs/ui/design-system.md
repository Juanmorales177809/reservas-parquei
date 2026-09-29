# Sistema de diseño

## Propósito

Documentar las reglas globales de uso visual de la interfaz, con alcance transversal a todos los módulos.

## Estado

Opción visual decidida: **«Corporativo elevado»** — degradados de dos tonos, esquinas de 12px, sombras marcadas y tipografía geométrica. Definida a partir del artifact de diseño «Botones ITM · Corporativo». Cubre color, tipografía, espaciado/radios/sombras y estados de botón; el resto de componentes queda pendiente (ver [Componentes UI](components.md)).

## Uso del color

- **`primary`** (verde de facultad, degradado `--color-primary-1` → `--color-primary-2`) es el color de marca y de la acción principal de cada pantalla (p. ej. «Reservar»). No se reutiliza como color de éxito: `success` es una familia propia (cian/teal), para no confundir «acción principal» con «operación aprobada».
- **`success`**, **`error`** y **`warning`** son familias semánticas independientes, cada una con su propio degradado de dos tonos. Se usan solo para comunicar el resultado o la naturaleza de una acción (aprobar, rechazar, confirmar), nunca como alternativa decorativa de `primary`.
- **`sky`** (verde lima institucional) está reservado en exclusiva para el anillo de `focus-visible`. No se usa como fondo de botón, badge ni superficie: mezclarlo con las familias semánticas rompería el significado de «esto tiene el foco del teclado».
- Las variantes de relleno **tenue** (`secondary`, `ghost`) usan `--color-primary-tint` como fondo en vez de un borde. El borde queda reservado para contenedores (tarjetas, secciones), no para botones.
- El estado **disabled** es siempre el mismo par de grises (`--color-disabled-bg` / `--color-disabled-text`), sin importar la variante semántica del botón. Un botón `danger` deshabilitado no se ve rojo atenuado: se ve gris, igual que un `primary` deshabilitado.
- Todo color tiene su contraparte para tema oscuro (ver [Tokens de diseño](design-tokens.md)); los pares oscuros conservan el mismo rol semántico que su versión clara.

## Uso de la tipografía

- `--font-display` (Arial/Helvetica) se usa en títulos, encabezados de sección y elementos de marca — es la tipografía «geométrica» de la opción Corporativo elevado.
- `--font-body` (Inter) se usa en texto de cuerpo, metadatos y el contenido de los botones.
- `--fw-bold` marca jerarquía y énfasis: encabezados, etiquetas de formulario, texto de botón, nombres en listas. `--fw-normal` es el peso por defecto del texto de cuerpo y metadatos.
- La escala de tamaños (`--fs-sm` a `--fs-5xl`) sigue una razón fija (~1.333); no se salta ni se interpolan tamaños fuera de la escala.

## Uso del espaciado, radios y sombras

- `--radius` (12px) es el radio estándar de cualquier control interactivo (botones). Los contenedores (tarjetas, secciones) usan radios mayores (16–20px) y los elementos tipo etiqueta (chips, badges) usan radio de píldora (999px) — un radio distinto por tipo de superficie, no una escala continua.
- Las sombras (`--shadow-default/hover/pressed`) se aplican **solo** a variantes de botón con relleno sólido (`primary`, `success`, `danger`, `warning`, `destructive-confirm`). Las variantes de relleno tenue (`secondary`, `ghost`) no llevan sombra: la elevación comunica «esta acción tiene peso», y una acción secundaria no debe competir visualmente con la principal.
- El espaciado sigue los valores observados en [Tokens de diseño](design-tokens.md#espaciado) hasta que se cierre una escala formal.

## Coherencia visual y accesibilidad

- El anillo de `focus-visible` es idéntico en forma y color (`--color-sky` al 55%, 4px) para **todas** las variantes de botón, incluida `destructive-confirm`. El foco de teclado no cambia de color según la acción: es una señal de navegación, no de significado.
- El estado disabled se marca con el atributo HTML `disabled` (no solo con estilo), de forma que un botón inhabilitado también sea inaccesible por teclado y para lectores de pantalla.
- El estado loading conserva el texto del botón y añade un indicador (`spinner`) delante; no se reemplaza la etiqueta por el spinner ni se vacía el botón.
- El tema oscuro se activa por preferencia del sistema (`prefers-color-scheme: dark`) y admite una alternancia manual (`data-theme="dark"` / `data-theme="light"`) que sobrescribe la preferencia del sistema.

## Uso de componentes y estados

- Todo botón interactivo define, como mínimo, los seis estados fijos: `default`, `hover`, `pressed`, `focus-visible`, `disabled`, `loading`. Ningún componente introduce un estado visual fuera de este conjunto sin documentarlo en [Componentes UI](components.md).
- La especificación completa de variantes, tamaños y estados de botón vive en [Componentes UI](components.md); este documento fija solo las reglas transversales de color, tipografía y elevación que esa especificación debe respetar.

## Documentos relacionados

- [Tokens de diseño](design-tokens.md): valores reutilizables.
- [Componentes UI](components.md): especificación de cada componente y sus estados.
- [Distribución de la interfaz](layout.md): distribución y ubicación de elementos.
