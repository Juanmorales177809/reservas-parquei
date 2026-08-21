# Prompt de traspaso — revisión de diseño para Fase 6

> Archivo temporal, solo para pasarle contexto a otra IA (experta en
> diseño/UI-UX) que va a proponer mejoras visuales para la Fase 6 de este
> proyecto. Se puede borrar una vez usado, no forma parte del código.

Copiá todo el bloque de abajo como primer mensaje.

---

## PROMPT

Estoy construyendo **Reservas Parquei**, un sistema de reservas de espacios institucionales para una universidad (laboratorios, auditorios, salas de estudio, salas de juntas) — lo van a usar estudiantes y personal académico real, así que la calidad visual importa, no es un prototipo descartable. El frontend se está migrando de Next.js a **Flutter** (multiplataforma: Android, iOS, Windows, macOS, Linux y Web), y ya tiene toda la funcionalidad construida. Lo que te pido es una revisión de diseño experta para elevar el nivel visual antes de la fase de pulido final ("Fase 6" en mi plan interno) — no tenés que escribir código Flutter si no querés, pero sí quiero recomendaciones concretas y accionables (colores exactos, espaciados, tipografía, jerarquía, motion), no principios genéricos de UI/UX que ya conozco.

### Quiénes lo usan

- **usuario**: consulta disponibilidad y crea/cancela sus propias reservas.
- **gestor**: administra un único espacio asignado (recursos, zonas, ensayos, horario, aprobar/rechazar reservas de ese espacio).
- **admin**: gestión global — todos los espacios, usuarios, dashboard con estadísticas, auditoría de cambios.

### Restricciones técnicas (no negociables)

- Sigue siendo **Flutter/Material 3** — cualquier recomendación tiene que poder implementarse con widgets de Flutter (temas, `BoxDecoration`, `TextTheme`, paquetes de animación como `flutter_animate`/`animations`), no asumas HTML/CSS ni otro framework.
- Todo el texto de la UI es **en español** y así se mantiene.
- No hay fotografías reales de los espacios (es un sistema institucional, no tiene banco de imágenes) — los headers de tarjeta usan gradientes/color plano + ícono, no fotos. Cualquier propuesta debe asumir "sin imágenes reales" como restricción, no como algo a resolver consiguiendo fotos de stock.
- Paquetes de íconos: usamos `lucide_icons_flutter` (no Phosphor — incompatible con este SDK de Flutter, `IconData` es `final class`). Si recomendás otro set de íconos, debe declarar `IconData` por composición, no herencia.

### Historia del diseño hasta ahora (importante para no repetir vueltas)

1. Primer estado: Material 3 por defecto (semilla índigo `#4F46E5`) — el usuario lo consideró "feo".
2. Primer rediseño: tipografía real (Plus Jakarta Sans + Inter), gradientes de marca "arcoíris" (6 colores: índigo/violeta, celeste/azul, esmeralda, naranja/ámbar, fucsia, cian) en los headers de tarjeta, animaciones de entrada/hover. **El usuario lo rechazó también**: "ni los colores ni el layout del dashboard me convencen".
3. Segundo rediseño (el actual, vigente): dirección dada explícitamente por el usuario — paleta **"tech-clean" académica**: azul académico profundo + verde esmeralda muy acotado, esquinas muy redondeadas, sombras sutiles de alta fidelidad. Esto SÍ lo convenció más, pero seguimos iterando.

**No propongas volver a un estilo "arcoíris"/multicolor por tarjeta ni a un índigo/violeta genérico de SaaS** — ya se probó y se descartó explícitamente. La dirección aprobada es la académica azul/esmeralda descrita abajo; podés refinarla, cambiar tonos, ajustar jerarquía, proponer un sistema tipográfico más rico, etc., pero partiendo de esa identidad, no reemplazándola por otra genérica.

### Sistema de diseño actual (valores exactos)

**Color** (`lib/core/theme/app_theme.dart`):
- Primario: `#1E3A8A` (azul académico profundo).
- Secundario/terciario: `#10B981` (verde esmeralda) — **reservado exclusivamente para estados "disponible/activo/aprobado/positivo"** (badges, botón confirmar), no se usa como color decorativo suelto.
- Fondo: `Colors.grey.shade50` (gris casi blanco).
- Tarjetas: blanco puro (`surfaceContainerLow`), esquinas de **20px** de radio, `elevation: 3` con sombra sutil (`shadowColor` translúcido al 10% del primario), `surfaceTintColor: transparent` (para que Material 3 no las tiña de azul automáticamente).
- Botones/inputs: radio de 16px (un escalón menos redondeado que las tarjetas).
- Colores semánticos de acción en listas (auditoría, badges de reserva): crear=esmeralda, actualizar=azul, eliminar=rojo `#DC2626`, pendiente/esperando=ámbar `#D97706`.
- Gradientes de tarjeta (`app_gradients.dart`): 4 variantes, todas dentro de la familia azul/slate/teal (`#1E3A8A→#2563EB`, `#0F172A→#334155`, `#0F766E→#14B8A6`, `#1E40AF→#3B82F6`) — nada fuera de esa gama fría.

**Tipografía**: "Plus Jakarta Sans" (`google_fonts`) para titulares (headline/title, peso 700-800, `letterSpacing` levemente negativo en headlines), "Inter" para cuerpo de texto.

**Espaciado** (`app_spacing.dart`, escala fija en todo el código): 4 / 8 / 12 / 16 / 24 / 32.

**Motion** (`flutter_animate` + paquete `animations` oficial):
- Transiciones de página: `FadeThroughTransition` (Material Motion) entre destinos de navegación de igual nivel, `SharedAxisTransition` escalado para pantallas "empujadas" (detalle, configuración).
- Entrada escalonada de listas/grillas: fade + slideY de 8%, delay de 40ms por ítem (`staggerEntrance`).
- Hover/press en tarjetas tocables: escala 1.02x al pasar el mouse, 0.97x al presionar, con sombra que aparece en hover (`HoverLift`, `lib/core/widgets/hover_lift.dart`).
- Contadores animados (cuenta ascendente) en las métricas del dashboard.
- Un "success burst" (ícono de check con escala elástica + mensaje) al confirmar una reserva, reemplazando un `SnackBar` genérico.

### Inventario de pantallas (todas ya construidas y funcionales)

- **Login**: ícono con gradiente azul→esmeralda, blobs de fondo decorativos, tarjeta centrada.
- **Espacios** (pública, sin sesión): grid de tarjetas con header de gradiente + ícono, badge de estado, capacidad/ubicación/conteo de recursos.
- **Detalle de espacio**: recursos del espacio, selector de fecha, grilla de disponibilidad horaria (slots libre/ocupado/mantenimiento).
- **Reserva**: bottom sheet con grilla seleccionable de franjas, formulario mínimo (asistentes, tipo).
- **Mis reservas** / **Gestión de reservas** (según rol): lista con badge de estado, acciones (aprobar/rechazar/asistencia/cancelar).
- **Gestión de recursos/zonas/ensayos** (gestor/admin): CRUD con diálogos de formulario.
- **Configuración de espacio** (solo gestor): editor de horario semanal día×hora (grilla de celdas toggle), antelación mínima, aprobación automática.
- **Usuarios** (solo admin): CRUD con avatar por rol (círculo con ícono), badge de rol.
- **Dashboard** (gestor/admin): franja compacta de KPIs en línea (no tarjetas grandes), un gráfico "hero" a todo el ancho (donut de ocupación global), grilla de gráficos secundarios (barras, líneas, torta de estados), heatmap 7 días × 13 horas.
- **Auditoría** (solo admin): lista de tarjetas con ícono/color por tipo de acción, solo lectura.
- **Notificaciones**: panel deslizable con lista, marcar leída/todas.

### Navegación adaptativa

Un único `AppShell` decide el layout según ancho lógico (breakpoint 840dp): **bottom nav con íconos** en móvil/tablet angosta, **top nav horizontal** en escritorio/Web ancho. Los destinos secundarios (Recursos/Zonas/Ensayos/Configuración/Usuarios/Auditoría) se agrupan en escritorio bajo un dropdown "Gestión ▾" para no saturar la barra superior; en móvil viven como accesos rápidos en la pantalla de Inicio (no hay más espacio en la bottom bar, que ya tiene 4 slots primarios: Espacios/Inicio/Reservas/Dashboard).

### Lo que te pido concretamente

Estamos por entrar en la fase de pulido final antes de compilar builds nativos reales (Windows/Android) y desplegar Web. Quiero que, con todo este contexto, propongas mejoras de diseño concretas y priorizadas para llevar esto de "bien" a "genuinamente pulido/profesional". Specifically:

1. **Crítica honesta del sistema actual** descrito arriba — qué es débil, inconsistente o se queda corto, con la razón puntual (no "podría ser más bonito", sino "el contraste X/Y no cumple AA" o "la jerarquía tipográfica solo tiene 3 niveles reales y se siente plana").
2. **Refinamientos concretos** al sistema de color/tipografía/espaciado/elevación — valores exactos (hex, tamaños, pesos), no "usá colores más vivos".
3. **Recomendaciones por pantalla** para las que consideres más débiles del inventario de arriba (decime cuáles priorizarías primero y por qué).
4. **Micro-interacciones/motion** adicionales que valgan la pena más allá de lo ya implementado (listado en "Motion" arriba) — con criterio de cuándo NO animar (ya aprendimos que una animación en loop infinito rompe los tests automatizados de Flutter, así que cualquier motion continuo debe justificarse).
5. Si tenés una opinión sobre **iconografía, ilustraciones o estados vacíos/de carga** más ricos que lo que tenemos (shimmer genérico + ícono en círculo para estados vacíos), decila.

No hace falta que generes código — priorizo dirección de diseño clara y específica que yo (u otra IA con acceso al repo) pueda traducir directamente a Flutter.
