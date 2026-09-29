# Componentes UI

## Propósito

Especificar los componentes UI reutilizables y sus estados, con alcance transversal a todos los módulos.

## Estado

`Button` está especificado por completo, a partir del artifact de diseño «Botones ITM · Corporativo». El resto de componentes visibles en ese mismo artifact (badge de estado/rol, tarjeta de reserva, fila de usuario) todavía no tienen especificación propia: aparecen ahí solo como contexto de uso de `Button`, no como componentes cerrados.

## Catálogo de componentes

| Componente | Estado |
|---|---|
| `Button` | Especificado (esta sección) |
| Badge de estado / rol | Pendiente — visto en contexto en el artifact, sin especificación propia |
| Tarjeta de reserva | Pendiente |
| Fila de usuario | Pendiente |

## Botones

### Propósito y casos de uso

Acción interactiva primaria de la interfaz: disparar una operación (reservar, aprobar, rechazar, exportar) o navegar a una vista de detalle. Sin iconos: el contenido del botón es siempre texto.

### Variantes

| Variante | Relleno | Uso |
|---|---|---|
| `primary` | Degradado `--color-primary-1` → `--color-primary-2`, texto blanco, mayúsculas | Acción principal de la pantalla (p. ej. «Reservar») |
| `secondary` | `--color-primary-tint`, texto `--color-primary-2` | Acción alternativa no destructiva (p. ej. «Ver detalle», «Exportar CSV») |
| `success` | Degradado cian/teal (`--color-success-1` → `--color-success-2`) | Confirmar una operación positiva (p. ej. «Aprobar», «Finalizar») |
| `danger` | Degradado rojo (`--color-error-1` → `--color-error-2`) | Rechazar o denegar (p. ej. «Rechazar») |
| `warning` | Degradado ámbar (`--color-warning-1` → `--color-warning-2`) | Confirmar con advertencia (p. ej. «Confirmar») |
| `ghost` | Transparente, texto `--color-muted`; relleno tenue solo en hover/pressed | Acción de bajo énfasis (p. ej. «Editar», «Marcar leída») |
| `destructive-confirm` | Igual paleta que `danger`, con patrón de doble confirmación | Acción destructiva irreversible en un solo botón (p. ej. «Cancelar reserva») |

`primary` es la única variante que usa texto en mayúsculas (`btn-uppercase`); el resto conserva el texto tal como se escribe.

### Tamaños

| Tamaño | Alto | Padding horizontal | Tipografía |
|---|---|---|---|
| `sm` | 34px | 16px | `12.5px` |
| `md` | 44px | 22px | `14px` |
| `lg` | 52px | 28px | `15.5px` |

Más un modificador `fullWidth` (`btn-block`, ancho 100%), independiente del tamaño — ver regla de uso en [Distribución de la interfaz](layout.md#adaptación-a-tamaños-de-pantalla).

### Estados y comportamiento asociado

Estados fijos, iguales para todas las variantes salvo lo indicado:

- **default** — apariencia base de la variante.
- **hover** — degradado más oscuro (`--color-*-hover-*`) y `--shadow-hover`, en variantes con relleno sólido; en `secondary`/`ghost`, oscurece ligeramente el tinte.
- **pressed** (`:active`) — color sólido más oscuro (`--color-*-pressed`), `--shadow-pressed`, y desplazamiento de 1px hacia abajo (`transform: translateY(1px)`).
- **focus-visible** — anillo de 4px en `--color-sky` al 55%, igual en forma y color para todas las variantes (ver [Sistema de diseño](design-system.md#coherencia-visual-y-accesibilidad)). No sustituye a hover/pressed: puede combinarse con ellos.
- **disabled** — fondo y texto fijos (`--color-disabled-bg` / `--color-disabled-text`), sin sombra, `cursor: not-allowed`, atributo HTML `disabled`. Igual en las siete variantes.
- **loading** — conserva el texto del botón y antepone un spinner (14px, animación de rotación continua). No cambia el color de fondo de la variante. El botón debe deshabilitarse funcionalmente durante `loading` para evitar doble envío (no forma parte del artifact visual, es requisito de comportamiento).

### Caso especial: `destructive-confirm`

Patrón de doble confirmación dentro de un mismo botón, para no introducir un modal:

1. **Estado inicial** — texto de la acción (p. ej. «Cancelar reserva»), apariencia `danger`.
2. **Primer clic (armado)** — cambia el texto a la pregunta de confirmación (p. ej. «¿Confirmar cancelación?»), aplica `data-armed="true"` (fondo `--color-error-pressed` más el anillo de foco en `--color-sky`, para hacer visible que el botón quedó armado) y arranca una ventana de 4 segundos.
3. **Segundo clic dentro de la ventana** — ejecuta la acción y desarma el botón.
4. **Sin segundo clic** — pasados los 4 segundos, el botón se desarma solo y vuelve al texto original; no ejecuta nada.

El texto de ayuda contextual (p. ej. «Doble clic requerido…») acompaña al botón como texto auxiliar, no como parte del componente `Button` en sí.

### Interacciones y accesibilidad

- El anillo de foco es visible por teclado (`:focus-visible`) en las siete variantes.
- `disabled` usa el atributo nativo, no solo estilos, para quedar fuera del orden de tabulación y ser anunciado correctamente por lectores de pantalla.
- Sin iconos: no hay contenido que dependa de `alt` o `aria-label` adicional más allá del texto visible del botón.
- El patrón `destructive-confirm` debe anunciar el cambio de estado (texto de pregunta) a tecnología asistiva — requisito de comportamiento no cubierto por el artifact visual, a resolver en la implementación (p. ej. `aria-live` sobre el texto de ayuda).

### Tokens y reglas visuales aplicables

Ver [Tokens de diseño](design-tokens.md) para los valores de color, radio (`--radius`, 12px) y sombra (`--shadow-default/hover/pressed`), y [Sistema de diseño](design-system.md) para las reglas de aplicación (sombra solo en relleno sólido, disabled siempre gris, foco siempre `sky`).

### API objetivo (React)

Forma prevista para la implementación en React + TypeScript (sin código todavía: `frontend/` no existe — ver [Implementación frontend](frontend-implementation.md)):

```
<Button variant="primary" size="md" state="default" fullWidth={false}>Reservar</Button>
```

- `variant`: `"primary" | "secondary" | "success" | "danger" | "warning" | "ghost" | "destructiveConfirm"`.
- `size`: `"sm" | "md" | "lg"`.
- `fullWidth`: `boolean`, por defecto `false`.
- `state`: prop explícita solo para los estados que dependen de lógica de la aplicación — `"disabled"` y `"loading"` (o, de forma más idiomática en React, las props nativas `disabled` y una prop `loading` aparte). Los estados `hover`, `pressed` y `focus-visible` **no** son props: son pseudoclases CSS (`:hover`, `:active`, `:focus-visible`) resueltas por el navegador, y no deben modelarse como estado de React.
- El patrón `destructive-confirm` mantiene su propio estado interno (armado / temporizador de 4s) dentro del componente; no se expone como prop.

## Otros componentes

Pendiente: especificaciones de badge de estado/rol, tarjeta de reserva y fila de usuario — visibles como contexto en el artifact de diseño, pero sin especificación propia todavía.

## Documentos relacionados

- [Tokens de diseño](design-tokens.md): valores reutilizables.
- [Sistema de diseño](design-system.md): reglas globales de uso visual.
- [Implementación frontend](frontend-implementation.md): ubicación y consumo de componentes compartidos.
