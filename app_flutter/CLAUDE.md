# app_flutter/CLAUDE.md

## Estado

Fases 0-5 completas (dashboard y auditoría — última pieza de la Fase 5 — cerrados el 2026-08-20). Restan Fase 6 (pulido multiplataforma) y Fase 6-Web (proxy real). Fase 1: listado público de espacios (`/espacios`), detalle (`/espacios/:id`, ruta empujada fuera del `ShellRoute` — ver "Rutas empujadas vs. destinos del shell" más abajo) con sus recursos activos, y disponibilidad real de un recurso. Fase 2: esa misma grilla de disponibilidad se volvió seleccionable (`SelectableSlotGrid`) para usuarios autenticados — elegir un rango de franjas libres consecutivas + formulario mínimo (asistentes, tipo opcional) crea la reserva (`POST /reservas`, solo `recurso_ids`); pantalla "Mis reservas" (`/reservas/mis-reservas`) lista, muestra estado y permite cancelar. Zonas/ensayos/acompañantes NO tienen UI de selección todavía (alcance acotado a la modalidad "equipos" — ver plan). Fase 3: campana de notificaciones con contador (`NotificationBell`, polling 30s vía `NotificacionesUnreadCountProvider`) en el `AppBar` de ambos shells, panel con lista + marcar leída/todas (`NotificacionesSheet`). Fase 4: `GestionReservasScreen` (`/admin/reservas`, gestor/admin) — aprobar/rechazar/marcar asistencia/cancelar; `ConfiguracionEspacioScreen` (`/admin/configuracion`, SOLO gestor) — ahora con editor completo `horario_atencion` día×hora (6-22, `HorarioEditor`, validación "al menos una franja") + antelación + aprobación automática; `GestionRecursosScreen`/`GestionZonasScreen`/`GestionEnsayosScreen` (`/admin/recursos|zonas|ensayos`, gestor/admin) — crear/editar/eliminar con `409` si tiene reservas/recursos/ensayos; guard por ROL vía `kNavDestinations` (admin redirigido en `/admin/configuracion`); navegación adaptativa con `Recursos|Zonas|Ensayos` en top nav + shortcuts en `InicioScreen` para móvil. Fase 5 (parcial, 2026-08-20): `GestionUsuariosScreen` (`/usuarios`, SOLO admin) — listar (`GET /usuarios`), crear (`POST`, `409` username/email duplicado, `400` gestor sin `espacio_id`), editar (`PUT`, password opcional, `409` username/email en uso, `409` último admin `proteger_administradores` con `pg_advisory_xact_lock`), eliminar (`DELETE`, oculta botón propio, `409` self y `409` último admin), validación email/username/password, `espacio` nullable; guard `kNavDestinations` admin-only (gestor → `/espacios`, `403` backend `Solo un administrador…`), todo verificado Playwright (admin_flutter crea/edita/borra, gestor 403). Fase 5 (cierre, 2026-08-20): dashboard (heatmap 7×13, gráficos fl_chart — ver "Pase de animaciones"/"Dashboard: gráficos grandes" más abajo) y `AuditoriaScreen` (`/admin/control-cambios`, SOLO admin) — solo lectura, `GET /admin/control-cambios` (`limit=200`), lista de tarjetas (no tabla: no cabe en móvil sin scroll horizontal) con ícono/color por `accion` (texto libre del backend, no enum — mapeo con fallback genérico, ver `_estiloAccion` en `auditoria_screen.dart`), agrupada bajo "Gestión ▾" en desktop y shortcut en `InicioScreen` en móvil; guard `kNavDestinations` admin-only verificado (gestor → `/espacios`). Restan Fase 6 (pulido multiplataforma) y Fase 6-Web (proxy real). `flutter analyze` No issues, `flutter test` 1/1. Ver el plan completo — vive fuera del repo en `~/.claude/plans/`.

## Usuario de prueba `gestor_flutter`

Creado en `reservas_test` durante la verificación de la Fase 4 para poder probar rutas exclusivas de `gestor` (que `admin_flutter`, usado en fases anteriores, no puede — `GET/PUT /espacios/gestion/configuracion` da 403 incluso a admin). Usuario `gestor_flutter` / clave `ClaveGestor123`, asignado al espacio "Auditorio Principal" (id 1). Vive en `reservas_test`, se pierde si se recrea el contenedor — recrear con `POST /usuarios` (`{"username":"gestor_flutter","email":"gestor_flutter@example.com","password":"ClaveGestor123","rol":"gestor","espacio_id":1}`, autenticado como admin) si hace falta.

## "Reservas" es un slot de navegación, no una ruta fija (Fase 4)

`kNavDestinations` (`core/router/nav_destinations.dart`) tiene DOS entradas con `id` distinto pero mismo `label` ("Reservas") y `rolesPermitidos` disjuntos: `mis-reservas` (`{usuario}` → `/reservas/mis-reservas`) y `gestion-reservas` (`{gestor, admin}` → `/admin/reservas`). `visibleDestinations()` solo deja pasar la que aplica al rol del usuario actual, así que cada rol ve un único ítem "Reservas" apuntando a la pantalla correcta — mismo patrón que `reservationsHref` en `frontend/src/components/Navbar.tsx`. Si se agrega un tercer rol o una tercera variante de "Reservas", seguir este mismo patrón (una `NavDestinationSpec` por variante, roles disjuntos), no intentar que un único destino resuelva su `path` dinámicamente.

## Guard por rol del router reutiliza `kNavDestinations` (Fase 4)

Hasta la Fase 3 el `redirect` de `app_router.dart` solo distinguía sesión sí/no. Ahora también busca si `state.matchedLocation` coincide con el `path` de algún `NavDestinationSpec` que tenga `rolesPermitidos` no nulo, y si el usuario actual no calza, redirige a `/espacios`. Ventaja: una sola fuente de verdad — si mañana se agrega un destino nuevo restringido por rol a `kNavDestinations`, el guard de ruta lo hereda automáticamente, no hace falta tocar `app_router.dart` en paralelo y arriesgarse a que se desincronicen.

## Dos bugs reales encontrados verificando la Fase 2 contra el backend (no solo `flutter analyze`/`flutter test`)

1. **Ningún `catch` de la app mostraba jamás el mensaje real de error del backend.** `dio.get/post/...` siempre lanza `DioException`, nunca el `ApiException` directamente — `AuthInterceptor` (`core/network/auth_interceptor.dart`) la deja en `DioException.error`, no en el objeto lanzado. Todo el código (desde la Fase 0) comparaba `e is ApiException` contra la `DioException` cruda, que siempre da `false`, así que cada error mostraba el fallback genérico ("No se pudo iniciar sesión...", etc.) en vez de la razón real. Arreglado con tres helpers nuevos en `core/network/api_exception.dart`: `apiExceptionOf(Object)`, `apiErrorMessage(Object, {required fallback})`, `apiErrorStatusCode(Object)` — **usar siempre estos, nunca `e is ApiException` sobre el error crudo de un repositorio o de un `AsyncValue.error`**.
2. **`PUT /reservas/{id}/cancelar` solo acepta reservas ya `aprobada`**, no `esperando` (`backend/app/services/reservas.py:739`, mensaje `"Solo puedes cancelar reservas aprobadas"`) — una reserva pendiente no la puede retirar el usuario, debe esperar a que gestor/admin la apruebe o rechace (no hay bug del lado backend, es la regla de negocio real). `Reserva.puedeCancelarse` (`features/reservas/domain/reserva.dart`) ahora refleja exactamente esto: solo `true` en `aprobada`. No confundir con `ESTADOS_RESERVA_BLOQUEANTES` del backend (`{esperando, aprobada}`), que es una regla distinta (qué estados bloquean solapamiento de horario al crear), no relacionada con qué se puede cancelar.

Lección: `flutter analyze`/`flutter test` no detectan ninguno de estos dos — solo aparecieron probando el flujo real contra el backend. Seguir verificando cada fase end-to-end, no solo con análisis estático.

## Fase 4b: CRUD recursos/zonas/ensayos + editor de horario (2026-08-20, verificado Playwright)

- **Modelos `@freezed`**: `Zona` (`schemas/zona.py:24`), `Ensayo` (`schemas/ensayo.py:20`) con `created_at/updated_at` como `String` crudo (mismo criterio fechas naive `America/Bogota`); `TipoRecurso` ya existía.
- **Repositorios**: `RecursosRepository` gana `listarGestion`/`listarTipos`/`crear`/`actualizar`/`eliminar` (`api/recursos.py:104`, `409` si `_recurso_tiene_reservas`); `ZonasRepository` (`api/zonas.py:39`, `PUT /zonas/{id}/recursos` reemplazo completo con validación mismo espacio + unicidad `409`); `EnsayosRepository` (`api/ensayos.py:34`).
- **Providers**: `recursosGestion`/`tiposRecursos`, `zonasGestion`, `ensayosGestion` (`@riverpod`, `build_runner` 12 outputs).
- **Editor horario**: `HorarioEditor` (`features/espacios/presentation/horario_editor.dart`, 16 franjas 06-22 igual que `frontend/src/app/admin/configuracion/page.tsx:23`, celdas verdes `Disponible` `Color(0xFF22C55E)`, `horarioFromJson`/`horarioToJson` con claves `0..6`); `ConfiguracionEspacioScreen` ahora maneja `Map<int,List<int>> _horario` mutable, validación client `Seleccioná al menos una franja` antes de `PUT /espacios/gestion/configuracion` (`schemas/espacio.py:79` `ge 0 le 8760`, `HorarioAtencion` normaliza `sorted(set)`), `409`/`422` vía `apiErrorMessage`.
- **Pantallas CRUD**: `GestionRecursosScreen`/`GestionZonasScreen`/`GestionEnsayosScreen` (`/admin/recursos|zonas|ensayos`, `rolesPermitidos:{gestor,admin}`, `primario:false` en `kNavDestinations:99` + shortcuts en `InicioScreen:47` para móvil); cada una con `FloatingActionButton Nuevo`, `_FormDialog` (`Form` + `validator`), `AlertDialog` eliminar con confirmación, `SnackBar` `apiErrorMessage` (`409` `No se puede eliminar…`).
- **Navegación**: `AppRoutes.adminZonas`/`adminEnsayos`, `app_router.dart:88` 3 `GoRoute` dentro del `ShellRoute`; guard por ROL reutiliza `kNavDestinations` (admin → `/espacios` en `/admin/configuracion`, RN-005 `GET /espacios` admin ve 6 espacios).
- **Hallazgo vivo**: `DELETE /zonas/{id}` con ensayos asociados devuelve `500` en vez de `409` (backend `api/zonas.py:130` solo bloquea `ZonaRecurso`, no `Ensayo.zona_id` FK → `IntegrityError` no capturado); en Flutter se muestra `Ha ocurrido…` vía fallback, no `detail` real. Documentado como riesgo, no bloquea: borrar ensayos primero. También `DELETE /recursos/1` con reservas `409` correcto, `DELETE /zonas/1` con recursos `409` correcto.
- **Verificación Playwright**: login `gestor_flutter`→ crear recurso `201` id 2 → editar `200` mantenimiento 10 capacidad → delete `204` → crear zona `201` → editar `200` → `PUT /zonas/1/recursos [1]` → `409` al borrar zona con recursos → vaciar recursos → borrar ensayos → borrar zona `204`; ensayo crear `201` → editar → `PUT /espacios/gestion/configuracion` horario nuevo con Dom `10,11` y Lun sin `7` → `200` verificado en UI (celda Lun 07-08 blanca, Dom 10-11 verde) + revert a original; admin login → `6` espacios, guard, notificación bell `2` unread.

## Fase 5 (parcial): Usuarios (2026-08-20, verificado Playwright)

- **Reutilización de modelo**: `AuthUser` (`features/auth/domain/auth_user.dart`) como espejo exacto de `UsuarioResponse` (`schemas/usuario.py:57`) — `id/username/email/rol/espacio:UsuarioEspacioResponse|null`, sin duplicar modelo.
- **Repositorio**: `UsuariosRepository` (`features/usuarios/data/usuarios_repository.dart`, `GET /usuarios` `200`, `POST /usuarios` `201` `409` username/email duplicado `400` gestor sin `espacio_id`, `PUT /usuarios/{id}` `200` `409` username/email en uso + `409` self/last-admin `proteger_administradores` `pg_advisory_xact_lock:38`, `DELETE` `204`/`409`/`404`, `password` omitido si vacío en `PUT` como en `frontend/src/app/usuarios/page.tsx:91`).
- **Provider**: `usuariosList` (`@riverpod`, `riverpod_generator`, `flutter pub run build_runner build` 2 outputs).
- **Pantalla**: `GestionUsuariosScreen` (`/usuarios`, `rolesPermitidos:{admin}` en `kNavDestinations`, `AppRoutes.usuarios`, `ShellRoute`, guard `admin`→`gestor` redirige a `/espacios` `403` `Solo un administrador…`); `Scaffold`+`FloatingActionButton Nuevo` + `ListView` de `_UsuarioCard` (círculo rol `shield|briefcase|user`, badge `rol.name` pill, `# ID` `Sin espacio|Auditorio`, chip `Tú` si `currentUser.id==usuario.id`, `Editar` siempre, `Eliminar` oculto si propio `frontend/src/app/usuarios/page.tsx:312`); `_UsuarioFormDialog` (`Form` `username 3..80`, `email @.`, `password 6..72` requerido en crear opcional en editar, `Dropdown rol usuario|gestor|admin`, `Dropdown espacio` solo si `gestor` con `espaciosListProvider`, validación `400` gestor sin espacio, `apiErrorMessage` `409`/`400`).
- **Navegación**: `TopNavShell` muestra `Usuarios` solo admin, `InicioScreen:47` `Wrap` con `Usuarios` button solo admin, bottom nav no satura (primario:false).
- **Verificación Playwright**: admin `admin_flutter` `GET /usuarios` `200` 3 usuarios (`beto, admin_flutter Tú sin Eliminar, gestor_flutter`), `POST /usuarios` `usuario_test_pw` `201` → edit `PUT` a gestor `200` espacio 1 → `409` username duplicado → `400` gestor sin espacio → `409` self delete `No puedes eliminar tu propia…` + self demote `No puedes cambiar…` → crear `admin2` `201` → demote `admin2` a usuario `200` deja 1 admin → delete `usuario_test_pw` + `admin2` `204` limpia → gestor login `GET /usuarios` `403` + guard redirect a `/espacios`.

## Pase de animaciones (2026-08-20, a pedido explícito del usuario — "instala lo que sea y haga falta")

Se agregó `flutter_animate` (declarativo, extensión `.animate()` sobre cualquier `Widget`) para transiciones de entrada, hover/press y feedback de éxito, más consistente que animar cada pantalla a mano. Widgets reutilizables nuevos en `core/widgets/`:

- `staggered_entrance.dart` (`Widget.staggerEntrance(index)`): fade+slideY de entrada con delay escalonado por índice (cap en 12 ítems) — aplicado a los `itemBuilder` de listas/grillas (espacios, mis-reservas, gestión de reservas/recursos/zonas/ensayos/usuarios) y a las tarjetas del dashboard.
- `hover_lift.dart` (`HoverLift`): `MouseRegion`+`AnimatedScale` (1.02x hover / 0.97x press) con sombra — envuelve `EspacioCard` y las tarjetas resumen del dashboard.
- `animated_counter.dart` (`AnimatedCounter`): cuenta ascendente (`TweenAnimationBuilder`, ~900ms `easeOutCubic`) — usado en los números del dashboard.
- `success_burst.dart` (`SuccessBurst.show(context, message: ...)`): overlay no descartable con ícono de check (escala elástica) + mensaje, se cierra solo a los 1200ms — reemplaza el `SnackBar` al crear una reserva (`recurso_disponibilidad_sheet.dart`).

`app_router.dart` ahora da una transición a **todas** las rutas (antes solo `/espacios/:id` la tenía): `FadeThroughTransition` (Material Motion) para los destinos "de pestaña" dentro del `ShellRoute` (cambiar de sección), `SharedAxisTransition` escalado para rutas empujadas (`/espacios/:id`, `/admin/configuracion`) — ver `_fadeThroughPage`/`_sharedAxisPage`.

### `flutter_animate` con `.repeat()` infinito rompe los widget tests (FakeAsync)

Un `AnimationController` que se repite para siempre (`.animate(onPlay: (c) => c.repeat())`) dentro de un widget montado en un test deja un `Timer` pendiente cuando `flutter_test` corre bajo `FakeAsync` — cualquier test que monte esa pantalla falla ("Pending timers"), aunque el comportamiento real de la app sea correcto. Pasó primero en `login_screen.dart` (blobs de fondo con `.repeat(reverse: true)`): la solución NO es un `pumpWidget(SizedBox())` al final del test (no alcanza), son dos cambios juntos:
1. Cambiar la animación a un solo tramo (sin `.repeat()`) cuando sea razonable — los blobs del login ahora son una entrada de escala+fade única, no una animación continua.
2. Si igual queda una animación finita con delay, el test debe usar `tester.pumpAndSettle()` en vez de `tester.pump()` al final, para que el reloj falso avance hasta que no queden animaciones agendadas (`pumpAndSettle` nunca termina si algo usa `.repeat()` sin fin — otra razón para evitarlo en pantallas con test).

Ver `test/features/auth/presentation/login_screen_test.dart` para el patrón exacto.

**Riesgo pendiente, no resuelto todavía**: `espacios_list_screen.dart` tiene un ícono de brújula con rotación infinita (`.animate(onPlay: (c) => c.repeat()).rotate(...)`) — hoy no rompe nada porque `EspaciosListScreen` no tiene widget test propio, pero si se agrega uno que monte esa pantalla sin `pumpAndSettle`-avoidance, va a fallar con el mismo síntoma. Si se escribe ese test, aplicar la misma lección (quitar el `.repeat()` o evitar `pumpAndSettle` sobre esa pantalla).

## Stack

Flutter 3.47.1 (canal stable), Riverpod 3.x + `riverpod_generator` (código generado, `@riverpod`), `go_router`, `dio` + `dio_cookie_manager`/`cookie_jar` (nativo) o adaptador de navegador (Web), `freezed`/`json_serializable` para modelos. SDK instalado vía `git clone https://github.com/flutter/flutter.git -b stable` en `C:\Users\<usuario>\dev\flutter` (no vía winget: no existe un paquete de Flutter SDK en winget, solo apps hechas con Flutter). Diseño: `google_fonts`, `lucide_icons_flutter`, `animations` (transiciones Material), `shimmer` (skeletons) — ver "Sistema de diseño" más abajo.

## Sistema de diseño — Fase 6 (2026-08-20, VIGENTE)

Tercer y último pase de diseño, a partir de una **revisión externa encargada a otra IA** (el prompt de contexto está en `HANDOFF_DISENO_FASE6.md`). A diferencia de los dos pases anteriores, este no fue un cambio de gusto: la revisión encontró **dos fallos de accesibilidad medibles**, y esos motivaron la reescritura de la capa de color.

### Archivos nuevos en `lib/core/theme/` (fuente de verdad)

- **`app_colors.dart`** — rampas y tokens. Reemplaza los `Color(0xFF...)` sueltos que estaban repartidos por 12 archivos.
- **`app_typography.dart`** — escala de 9 niveles + `overline` + `numerico`.
- **`app_elevation.dart`** — 5 niveles de sombra.
- `app_spacing.dart` / `app_gradients.dart` / `app_theme.dart` — actualizados.

### Los dos fallos de contraste que se corrigieron (no reintroducir)

1. **`#10B981` (esmeralda) daba 2.54:1 contra blanco.** Falla AA para texto (4.5:1) *y* el mínimo de 3:1 para componentes. Se usaba a la vez como texto de badge "Activo", relleno del botón de confirmar, y borde de slot libre — los tres usos eran inválidos.
2. **`#D97706` (ámbar) daba 3.20:1.** Falla AA como texto de badge "Esperando"/"Mantenimiento".

La corrección **no fue "elegir otro verde"**: fue que un color de estado necesita **un tono por función**. Ver `EstadoTokens` en `app_colors.dart` — `relleno`, `sobreRelleno`, `tinte`, `sobreTinte` y `borde` son valores distintos y verificados, nunca derivados con `withValues(alpha:)` sobre un tono base. Los cinco estados (`AppEstados.positivo/informativo/pendiente/negativo/neutro`) están en esa tabla.

**Regla dura**: en código nuevo usar `AppEstados.<estado>.<rol>`. `kEmerald` sigue exportado desde `app_theme.dart` solo por retrocompatibilidad de imports y **solo sirve como parada de gradiente o trazo de gráfico**, nunca como texto ni relleno de botón.

### Otros cambios estructurales

- **Fondo `#F1F5F9`** (antes `grey.shade50` = `#FAFAFA`): daba **1.04:1** contra la tarjeta blanca, imperceptible en pantallas mate o con brillo bajo. Además la tarjeta ahora lleva **borde de 1px `#E2E8F0` además de la sombra** — es lo que sostiene la lectura en Windows/Web, donde el render de sombras es más débil que en móvil.
- **Escala tipográfica de 9 niveles.** Antes había tres niveles reales para expresar hasta cinco de información por pantalla. Lo que faltaba específicamente era `AppText.overline()` (11px/700/+0.9, mayúsculas por el llamador): el nivel que separa "etiqueta de dato" de "dato" sin gastar espacio vertical.
- **`AppText.numerico()` con `FontFeature.tabularFigures()`.** Inter usa cifras proporcionales por defecto, así que los dígitos cambiaban de ancho mientras un contador animaba (el número "vibraba") y las columnas de cifras no alineaban. `AnimatedCounter` ahora fuerza esta feature aunque el estilo recibido no la traiga.
- **Radios concéntricos**: 28 (sheet/diálogo) / 20 (tarjeta) / 14 (botón, campo) / 8 (interno de tarjeta) / 4 (celda densa). Regla: radio del hijo = radio del padre − su padding. Los botones bajaron de 16 a 14 porque 20 vs 16 se leen como el mismo radio.
- **Sombras slate, no azules.** Una sombra tintada de primario al 10% sobre fondo casi blanco se percibe como un halo de color, no como profundidad.
- **`ThemeMode.light` fijado en `app.dart`.** `darkTheme` estaba activo con `ThemeMode.system`, así que cualquier dispositivo en modo oscuro renderizaba un tema derivado por `fromSeed` que nadie diseñó ni verificó. `AppTheme.dark()` hoy devuelve el tema claro; un oscuro real es trabajo pendiente explícito.
- **Gradientes por `modalidad_reserva`, no por `id`.** Antes se elegían con `id % 6`, así que el mismo espacio salía azul en una lista y naranja en otra según su posición: el gradiente no era información, era textura aleatoria. La revisión sugería atarlos al *tipo* de espacio, pero **`EspacioResponse` no tiene ese campo** y agregarlo implicaría tocar el backend; `modalidad_reserva` (`equipos`/`zonas`/`mixto`) es la señal semántica estable más cercana que ya existe. **Consecuencia práctica**: en `reservas_test` los 4 espacios son `equipos`, así que hoy todas las tarjetas salen del mismo azul — el gradiente es correcto pero no aporta variedad con estos datos.
- **Motion acotado**: `staggerEntrance` ahora tiene techo (`min(index, 6) * 35ms`) — sin él, una lista de 40 ítems tardaba 1.6s en terminar de entrar. `HoverLift` dejó de escalar en hover (Flutter rasteriza y reescala, así que el texto se desdibujaba, y en grilla densa la tarjeta se solapaba con la vecina): ahora eleva sombra + traslada 2px, y el escalado quedó solo para `press`. En Android/iOS ni siquiera monta `MouseRegion`.

### Tres bugs reales encontrados verificando este pase (ninguno lo detectó `flutter analyze`)

1. **El dashboard se renderizaba VACÍO.** Un `Row` con `CrossAxisAlignment.stretch` (para los divisores verticales entre KPIs) dentro de un `SingleChildScrollView`: la altura no está acotada, así que `stretch` deja a los hijos sin restricción vertical y toda la franja colapsa. La API respondía `200` — el fallo era puramente de layout. Solución: divisor de altura fija (`Container(width: 1, height: 44)`), no `VerticalDivider` + `stretch`.
2. **El destino activo del top nav se veía deshabilitado.** `_NavButton` hacía `onPressed: activo ? null : onPressed`; un `TextButton` con `onPressed: null` **es** un botón deshabilitado, y Material entonces ignora el `foregroundColor` del estilo y aplica el de deshabilitado. Resultado: el destino donde estabas parado se veía gris y apagado mientras los demás se veían normales — justo al revés. Ahora queda habilitado con un callback vacío.
3. **Ejes Y con fracciones en datos enteros.** `fl_chart` repartía el eje en `0, 0.5, 1, 1.5, 2, 2.5, 3` para conteos de reservas, y encima partía `"2.5"` en dos líneas porque `reservedSize: 28` no alcanzaba. Corregido con `_ejeEntero()` + `_tituloEjeY()` en `dashboard_screen.dart` (paso entero calculado, `maxY` explícito, `reservedSize: 34`).

### Segunda tanda: interacción (items 9 y 10 del checklist)

**`SlotChip` (`features/espacios/presentation/slot_chip.dart`) — nuevo, compartido.** `DisponibilidadSlotGrid` (solo lectura) y `SelectableSlotGrid` (reserva) tenían cada una su propio chip con colores distintos; ahora comparten uno. Lo importante es que **los estados se distinguen por forma, no solo por color**: `mantenimiento` lleva rayas diagonales a 45° (`CustomPainter`) además del icono, porque "ya está reservado" y "el equipo no está operativo" son cosas distintas para quien reserva y con solo tono son indistinguibles para alguien con daltonismo o en una proyección de aula (requisito 1.4.1 de WCAG). Hay `SlotLeyenda` para traducir los tres estados.

**Selección por arrastre en `SelectableSlotGrid`.** Se puede seguir tocando inicio y fin (único camino viable con lector de pantalla), y además arrastrar. Dos decisiones no obvias:
- El arrastre es **horizontal** (`onHorizontalDrag*`), no `onPan`: el widget vive dentro de un `showModalBottomSheet` scrolleable y un pan competiría con el scroll vertical del sheet en el gesture arena — el usuario intentaría desplazar la hoja y en su lugar pintaría franjas.
- **`dragStartBehavior: DragStartBehavior.down`** es obligatorio. Con el default (`.start`), Flutter reporta el inicio del arrastre en la posición donde el gesto fue *reconocido*, o sea después del umbral táctil (~18px): para entonces el dedo ya está sobre la franja siguiente, el ancla queda en la franja equivocada y la franja donde el usuario empezó nunca entra en la selección. **Lo encontró el test de arrastre, no la inspección visual.**
- Un rango que cruzaría una franja ocupada se ignora en vez de partirse en dos.

**`HorarioEditor` reescrito.** 7 días × 16 horas = 112 celdas; configurar un espacio eran 112 toques y no había forma de revertir un error. Ahora: arrastre para pintar (long-press + deslizar — *no* `onPan`, porque la tabla está en un scroll horizontal), toggle de columna en el encabezado de día, toggle de fila en la etiqueta de hora, y **"Deshacer"** en un `SnackBar` de 8s tras cada operación masiva (`ConfiguracionEspacioScreen._actualizarHorario`). Las celdas usan `GestureDetector`, no `InkWell`: en una grilla densa el ripple se desborda sobre las vecinas y durante un arrastre quedan varios solapados. Se mantuvo el **verde** para celda activa (en contra de la sugerencia de la revisión, que proponía azul de marca) porque en esta app el verde *significa* "disponible" y estas celdas son exactamente las franjas que quedarán disponibles: con azul, el editor no coincidiría con la grilla que después ve quien reserva.

**Sheet de reserva**: resumen persistente ("14:00–16:00 · 2 horas · 3 asistentes") sobre un botón de ancho completo, y cuando está deshabilitado dice por qué en vez de quedarse gris y mudo.

**Tests: de 1 a 9.** `slot_chip_test.dart` (4) cubre los tres estados y que el patrón de mantenimiento exista y `ocupado` NO lo tenga (si ambos lo tuvieran, el patrón dejaría de distinguir). `selectable_slot_grid_test.dart` (4) cubre el arrastre, incluido el caso del rango que cruza una franja ocupada.

### Tercera tanda: estructura (items 8, 11-15)

**Tres clases de ventana, no dos (`shell/app_shell.dart`).** El salto era binario en 840dp, así que un tablet a 800dp mostraba una barra inferior pensada para un teléfono con la pantalla medio vacía a los costados. Ahora sigue las *window size classes* de Material 3: `< 600` compacta (bottom nav), `600–1240` media (**`RailNavShell`**, nuevo), `≥ 1240` expandida (top nav). En el rail entran **todos** los destinos, incluidos los `primario: false`, porque la columna crece hacia abajo — no hace falta el menú "Gestión" que sí necesita el top nav.

**`ContenidoCentrado`** (en `app_shell.dart`) limita el contenido a 1280px y lo centra en las clases media y expandida. Sin esto, en un monitor de 27" la app no se ve como una aplicación de escritorio sino como una app móvil estirada.

**Dashboard**: la torta de estados pasó a **barra apilada horizontal** (`_EstadoBarraApilada`) — dos gráficos circulares en la misma pantalla compiten por el mismo rol y ninguno gana; comparar longitudes además es más preciso que comparar ángulos. El donut de ocupación se extrajo a `_OcupacionHero` y ahora comparte fila con la barra apilada en proporción 8/4 (de una rejilla de 12) en pantallas anchas, en vez de ocupar todo el ancho mientras el reparto por estado caía en la grilla secundaria.

**Auditoría: de tarjetas a filas densas.** Un log se escanea verticalmente buscando un patrón; con una tarjeta elevada por evento, cada entrada reclama la misma atención y el ojo no puede recorrerla. Ahora son filas con divisor de 1px, punto de color por tipo de acción (con cinco tipos el punto alcanza y el icono era redundante), hora alineada a la derecha en cifras tabulares, y encabezado adhesivo por día. **No se calcula "Hoy"/"Ayer"** a propósito: `created_at` llega naive en `America/Bogota` y compararlo contra la fecha local del dispositivo daría una etiqueta equivocada fuera de esa zona — un error silencioso.

**Estados vacíos y de error diferenciados.** `EmptyView` dejó de ser un icono dentro de un círculo gris (el patrón por defecto de cualquier framework) y usa geometría del propio vocabulario de la app: una grilla 4×3 de celdas vacías con el icono de dominio flotando en una cápsula. Acepta `detalle` (una línea de contexto) y `accion` (botón primario). `ErrorView` se rediseñó para **no parecerse** al vacío: panel con tinte negativo, título "No se pudo cargar" y botón de reintento — "no hay nada todavía" y "falló la carga" piden acciones distintas.

**`EspacioCardSkeleton` es isomorfo a `EspacioCard`**: misma cabecera de 72px, mismo radio, título/metadato/chips en las mismas posiciones. Si `EspacioCard` cambia de estructura, este archivo cambia con ella — un skeleton que no coincide enseña a esperar una forma que no llega.

**`MediaQuery.disableAnimationsOf` respetado** en `staggerEntrance` y `HoverLift`. Además de ser lo correcto para quien tiene trastornos vestibulares, apaga estas animaciones en los widget tests (donde `AutomatedTestWidgetsFlutterBinding` fija `disableAnimations: true`), así un test que monte una lista no queda esperando timers de `flutter_animate`. `staggerEntrance` pasó de extensión pura a envolver un `_EntradaEscalonada` para poder leer el `MediaQuery` (la extensión sobre `Widget` no tiene `BuildContext`).

### Cuarta tanda: pulido fino restante (2026-08-21, verificado backend + Flutter)

**Usuarios: de tarjetas a tabla + avatar con iniciales.** `GestionUsuariosScreen` (`gestion_usuarios_screen.dart:20-178`) ahora es responsive: `<600dp` mantiene `ListView` de `_UsuarioCard`, `≥600dp` usa `CustomScrollView` con `Card` única que contiene `_CabeceraTabla` (`AppText.overline()`) + `_FilaUsuario` por usuario con `Divider 1px AppColors.borde`. Columnas `flex 3/1/2/1/2` (`USUARIO | ROL | ESPACIO | ID | ACCIONES`), igual que auditoría pero sin sticky por día (una sola cabecera). Avatar: nuevo `_UsuarioAvatar` (`:93-122`) con iniciales (`admin_flutter → AF`, `beto → BE`) `Text titleSmall w700` sobre `primaryContainer/tertiaryContainer/surfaceContainerHighest` según `RolUsuario` — reemplaza `Icon shield/briefcase/user` tanto en tarjeta móvil como fila desktop (el icono repetía el `rol.name` pill). Verificado `flutter analyze`/`test`.

**Mis reservas agrupado por tiempo.** `mis_reservas_screen.dart:50-118` pasó de `ListView` plano `sort b.fecha` a `CustomScrollView` con `SliverMainAxisGroup` + `SliverPersistentHeader` adhesivo por bucket, igual que `auditoria_screen.dart:69`. Cuatro buckets `HOY / ESTA SEMANA / PRÓXIMAS / PASADAS` (`_GrupoReserva:243`) calculados con `_hoyBogotaStr()` (`DateTime.now().toUtc()-5h`, Bogotá no tiene verano) y `_hoyBogotaPlusDiasStr(7)` por `String.compareTo` (sin `DateTime.parse`, sigue el criterio de `created_at` naive). Orden interno: futuras ascendente, pasadas descendente. Header `_EncabezadoGrupoReserva` (`:276-317`, `min/max 36`, `AppColors.fondo / AppText.overline() + pill count numerico`). Rechazadas muestran `motivoRechazo` en `Container tinte negativo`.

**Gestión de reservas: una sola primaria por fila.** `gestion_reservas_screen.dart:152-225` antes mostraba `Outlined Rechazar + Filled Aprobar` (dos con peso) y `ChoiceChip Sí/No + Outlined Cancelar`. Ahora: `esperando → Filled Aprobar` + `PopupMenuButton ellipsisVertical` con `Rechazar` (que abre diálogo de motivo); `aprobada → ChoiceChip Sí/No` + `PopupMenu Cancelar`. Solo `Aprobar` es `FilledButton`, el resto es `PopupMenu` secundario — `AppEstados` y `AppSpacing` se mantienen. `motivo` se muestra en la misma card cuando `estado==rechazada && motivoRechazo!=null` (`Container tinte negativo`).

**Header comprimible pulido.** `espacio_detalle_screen.dart:52-81` ya era `SliverAppBar pinned expandedHeight:180`; ahora es `expandedHeight:200 collapsedHeight:56 pinned:true floating:true snap:true stretch:true scrolledUnderElevation:2 shadowColor:AppColors.sombra systemOverlayStyle:light` con `FlexibleSpaceBar expandedTitleScale:1.18 collapseMode:parallax stretchModes:[zoomBackground,fadeTitle]` y `DecoratedBox Stack + kGradientScrim` para que el título blanco no pierda contraste. `physics: BouncingScrollPhysics` para stretch visible.

**Motivo obligatorio al rechazar (backend + frontend + Flutter + auditoría).** Con autorización explícita se tocó el backend (ver `backend/app/schemas/reserva.py:75-78` + `migrations.py:453` + `models/reserva.py:36`):
- `ReservaEstadoUpdate:75` añade `motivo: str|None max_length:500` con `field_validator` + `model_validator` que exige `motivo` no vacío cuando `nuevo_estado==RECHAZADA` → `422` si falta.
- `Reserva.motivo_rechazo = Column(Text, nullable=True) :36` + `ALTER TABLE reservas ADD COLUMN IF NOT EXISTS motivo_rechazo TEXT` (idempotente).
- `ReservaResponse.motivo_rechazo: str|None`.
- `services/reservas.py:636` `cambiar_estado(..., motivo=None)` valida `400` si `RECHAZADA` sin motivo, persiste `reserva.motivo_rechazo` (limpia a `None` si no es rechazada), `Notificacion` + `registrar_cambio("... - Motivo: {motivo}")` para auditoría (`control_cambio.descripcion`), `api/notificaciones.py:33` `_mensaje` inyecta motivo en `Tu reserva de X fue rechazada: {motivo}`.
- `api/reservas.py:53` `cambiar_estado_endpoint(..., motivo=data.motivo)`.
- `openapi.snapshot.json:1254` regenerado + `tests/test_api_reservas.py:410` y `tests/test_doble_escritura:229` y `tests/test_schemas_contrato.py:233` actualizados.
- Frontend `types/reserva.ts:63` + `services/reservas.ts:19` `cambiarEstado(id, estado, motivo?)` y `admin/reservas/page.tsx:79` `prompt` + `mis-reservas/page.tsx:181` muestra motivo.
- Flutter `domain/reserva.dart:113` `String? motivoRechazo`, `data/reservas_repository.dart:75` `cambiarEstado(id, nuevo, {motivo})`, `presentation/gestion_reservas_screen.dart:78-129` diálogo `AlertDialog Form TextFormField maxLength:500 validator` + card muestra `motivoRechazo` en `Container AppEstados.negativo.tinte`, `mis_reservas_screen.dart:243` igual, `notificaciones` ya vienen con motivo en el mensaje.

**Delta KPIs (backend + Flutter).** Con autorización:
- `schemas/admin_dashboard.py:43` nuevas `PeriodoDelta, DeltaInt, DeltaFloat, DashboardDeltas{periodo_dias, periodoActual, periodoPrevio, totalReservas, ocupacionPorcentaje}` + `AdminDashboardSummary.deltas: DashboardDeltas|None`.
- `api/admin_dashboard.py:23` `_calcular_ocupacion_porcentaje` + `_construir_resumen(..., periodo_dias=None)` + cálculo de `deltas` cuando `periodo_dias` viene: ventanas `actual [hoy-periodo+1, hoy]` y `previo [actual- periodo, actual-1]` con `date.today()` y `timedelta`, `total_actual/previo` vía `count()`, `delta/pct`, y `bloque_actual/previo` para ocupación (reusa `_calcular_ocupacion_porcentaje`). Endpoints `GET /admin/dashboard/summary?periodo_dias=30` y `/gestion/dashboard/summary?periodo_dias` (`Query ge1 le365`).
- Flutter `domain/dashboard_summary.dart:74-105` espejo `PeriodoDelta/DeltaInt/DeltaFloat/DashboardDeltas` + `deltas`, `data/dashboard_repository.dart:14` `GET ...?periodo_dias=30`, `presentation/dashboard_screen.dart:121-350` `_SummaryStrip` pasa `DeltaInt` a `_StatItem` que muestra `_DeltaBadge` (`trendingUp/Down/minus` + `+delta (+pct%)` con `AppEstados.positivo/negativo/neutro`), `_OcupacionHero` muestra `_DeltaBadge` bajo el porcentaje + `vs 30 días previos`.

**P1 — CRUD Espacios admin (paridad con `frontend/src/app/admin/espacios/page.tsx:147`).** Con autorización “primero que todo quede igual”:
- `data/espacios_repository.dart:56` añade `crear({nombre,ubicacion,capacidad,correo,estado,modalidadReserva}) → POST /espacios`, `actualizar(id,{...}) → PUT /espacios/{id}` (solo campos non-null), `eliminar(id) → DELETE /espacios/{id}` (409 si tiene dependencias) — espejo de `frontend/src/services/espacios.ts:15`.
- `presentation/gestion_espacios_screen.dart` nuevo (patrón `GestionRecursosScreen:20`): `Scaffold AppBar FloatingActionButton Nuevo` + `ListView` de `_EspacioCard` (`EstadoBadge`, `Wrap capacidad/correo/modalidad`) + actions `Editar` (`_EspacioFormDialog` con validators `nombre 1-100, ubicacion 200, capacidad>0, correo @.`), `Cambiar estado` (cicla `activo→inactivo→mantenimiento→activo` vía `PUT {estado}` igual que `frontend:101`), `Eliminar` con `409` vía `apiErrorMessage`; `ref.invalidate(espaciosListProvider)` tras mutación.
- `core/router/app_routes.dart:14` ya existía `adminEspacios`, ahora registrado `app_router.dart:113` `GoRoute /admin/espacios → GestionEspaciosScreen` + `nav_destinations.dart:132` `gestion-espacios {admin} primario:false` + `shell/inicio_screen.dart:81` shortcut `Espacios` solo admin. Verificado `flutter analyze` / `flutter test` + manual `admin_test POST 201 / PUT 200 / DELETE 204 / 409 con recurso`.

### Pendiente fino (requiere toolchain, no tocado sin confirmación)

- Compilar Windows/Android: `flutter doctor` sigue `X Visual Studio not installed` + `X Android SDK` (`windows: flutter generated_plugin_registrant` warnings son CRLF, no fallo). Requiere instalar VS workload C++ + Android Studio/SDK.
- Proxy same-origin real de Fase 6-Web: `docker-compose.yml` sin `ports:` en `backend` + `env/web.json` `/api` siguen necesitando servicio `nginx/caddy` con confirmación.

## Sistema de diseño (pases 1 y 2 — histórico)

Pase de diseño explícito (a pedido del usuario, tras considerar "feo" el Material 3 por defecto de las Fases 0/1), **rehecho una segunda vez** (2026-08-20) cuando el usuario rechazó también el primer pase ("ni los colores ni el layout del dashboard me convencen") y dio una dirección concreta vía `AskUserQuestion`: paleta "tech-clean" académica (azul profundo + verde esmeralda, nada de arcoíris), esquinas muy redondeadas, sombras sutiles, y dashboard con gráficos grandes en vez de números protagonistas. Base en `lib/core/theme/`:

- `app_theme.dart`: tipografía "Plus Jakarta Sans" (titulares) + "Inter" (cuerpo) vía `google_fonts`; paleta fija (no un solo `ColorScheme.fromSeed` con semilla índigo como en el primer pase) — `kAcademicBlue = 0xFF1E3A8A` como `primary`, `kEmerald = 0xFF10B981` como `secondary`/`tertiary` **reservado para estados "disponible"/positivo**, `surface = Colors.grey.shade50` (fondo) con `surfaceContainerLow = Colors.white` (tarjetas) — contraste "tarjeta blanca sobre gris" en vez del fondo levemente teñido que da `fromSeed` por defecto. `cardTheme` usa `AppRadius.xl` (20, antes 16) + `elevation: 3` con `shadowColor` traslúcido y `surfaceTintColor: Colors.transparent` (Material 3 tiñe automáticamente las superficies elevadas con `primary`; sin anularlo las tarjetas blancas se ven azuladas). Botones/inputs subieron de `AppRadius.md` (12) a `AppRadius.lg` (16) para ir más acorde a las esquinas muy redondeadas pedidas, sin llegar al radio de tarjeta.
- `app_spacing.dart` (`AppSpacing`/`AppRadius`): escala única de espaciado/radios — usar siempre estas constantes en vez de números sueltos (`SizedBox(height: 8)` etc.) en código nuevo. `AppRadius.xl = 20.0` es nuevo (segundo pase), reservado para tarjetas y bottom sheets.
- `app_gradients.dart` (`gradientForId(int id)`): paleta de 4 gradientes para cabeceras de tarjeta (espacios), **acotada a la familia azul/slate/teal** — el primer pase tenía 6 gradientes tipo arcoíris (violeta, naranja, fucsia incluidos) que el usuario rechazó explícitamente por no encajar con el look minimalista. El verde esmeralda quedó fuera de esta paleta a propósito: es el color semántico de "disponible" (`EstadoBadge`), no un color de marca de tarjeta — mezclarlos haría perder el significado del verde en el resto de la UI.
- Colores semánticos de estado (`EstadoBadge.activo`, `EstadoReservaBadge.aprobada`, `SuccessBurst`, `NotificacionesSheet` tipo `aprobada`, `HorarioEditor` franja seleccionada, mensaje de éxito en `ConfiguracionEspacioScreen`) unificados al mismo `0xFF10B981` (antes cada uno tenía su propio verde: `0xFF22C55E`, `0xFF16A34A` sueltos) — un solo verde en toda la app, no varios tonos parecidos pero distintos.
- `core/widgets/`: `EstadoBadge` (badge de color por `EstadoEntidad`, con variante `sobreOscuro` para cabeceras de gradiente), `EmptyView`/`ErrorView` (ícono en círculo + mensaje, mismo lenguaje visual), `BrandMark` (ícono + wordmark, reutilizado en ambos shells y el login).
- Transición de lista→detalle: `CustomTransitionPage` + `SharedAxisTransition` (paquete `animations`, oficial de flutter.dev) en la ruta `/espacios/:id` de `app_router.dart`.
- Carga: `Shimmer.fromColors` (paquete `shimmer`) en vez de un spinner centrado para grillas (`EspacioCardSkeleton`) — mejor percepción de velocidad.

### Dashboard: "gráficos grandes, pocos números" (segundo pase, 2026-08-20)

El dashboard original (`dashboard_screen.dart`) tenía 4 tarjetas KPI grandes con ícono+contador compitiendo visualmente con los charts de abajo. A pedido explícito del usuario se invirtió la jerarquía:
- `_SummaryStrip`/`_StatItem` (antes `_SummaryGrid`/`_SummaryCard`): los totales ahora son una sola tarjeta con ítems en línea (ícono chico + número + etiqueta), no 4 tarjetas elevadas — mucho menos peso visual.
- "Ocupación global" se separó como *hero* a todo el ancho arriba de la grilla de charts (antes competía en la grilla 2 columnas) — donut más grande (240px, antes 180px) con el porcentaje en `displaySmall`.
- El resto de los charts (reservas por estado/fecha/espacio, recursos más reservados) subieron de 180px a 220px de alto.
- Colores de charts alineados a la paleta: azul académico como serie principal (antes índigo/cian mezclados), esmeralda para "recursos más reservados" y para el estado "aprobadas" del pie de estados, heatmap con intensidad en azul académico (antes cian).

### `phosphor_flutter` NO es compatible con este SDK — usar `lucide_icons_flutter`

Se probó primero `phosphor_flutter` (íconos duotone/fill, muy vistosos) pero `PhosphorIconData extends IconData` no compila: `IconData` es una `final class` en este SDK y no se puede extender fuera de su librería. El error solo aparece al compilar de verdad (`flutter test`/`flutter run`/`flutter build`), **no** en `flutter analyze` — no confiar en que `analyze` limpio garantice que un paquete de íconos de terceros compila. También se descartó `lucide_icons` (paquete hermano, sin `_flutter`) por el mismo motivo (`LucideIconData extends IconData`) y porque le faltan varios nombres de ícono que sí tiene `lucide_icons_flutter`. Antes de agregar cualquier paquete de íconos nuevo, verificar que declare `IconData` por composición (`const IconData(codepoint, fontFamily: ...)`), no por herencia.

### Costo conocido: `lucide_icons_flutter` pesa ~2.5MB de más en Web (aceptado)

El paquete declara 7 familias de fuente en su propio `pubspec.yaml` (`Lucide` + 6 variantes de grosor `Lucide100`..`Lucide600`); Flutter empaqueta automáticamente **todas** las fuentes que un paquete declara, sin importar cuáles use realmente la app — el tree-shaking de íconos solo reduce las glifos dentro de una fuente usada, no elimina archivos de fuente completos sin usar. Como el código solo referencia `LucideIcons.*` (familia base), las 6 variantes de peso (~2.5MB) quedan sin usar pero igual se bundlean. Se aceptó el costo porque es secundario frente a los ~37MB del motor CanvasKit del build Web (que además normalmente se sirve desde CDN en producción, no autoalojado — decisión de la Fase 6-Web). Si el tamaño del bundle Web se vuelve un problema real, opciones a futuro: forkear el paquete para declarar solo la fuente base, o migrar a otro set de íconos que no cargue variantes de peso.

## Backend intacto — nunca modificar sin aprobación aparte

Igual que `frontend/CLAUDE.md`: ningún cambio en `backend/app/schemas/`, routers de `backend/app/api/`, OpenAPI, ni en la política de cookie/CORS de `backend/app/main.py`, sin aprobación explícita separada. `app_flutter/` se adapta al contrato existente, nunca al revés.

**Excepción 2026-08-21 (autorizada en esta sesión, ver `git log` y `openapi.snapshot.json`):** con autorización explícita del usuario se tocó `backend/` solo para los dos pendientes que lo exigían: `motivo_rechazo` (`schemas/reserva.py:75`, `models/reserva.py:36`, `migrations.py:453`, `services/reservas.py:636`, `api/reservas.py:53`, `api/notificaciones.py:33`, regenerado `openapi.snapshot.json:1254`) y `deltas` (`schemas/admin_dashboard.py:43`, `api/admin_dashboard.py:23`), más `frontend/` (`types/reserva.ts:63`, `services/reservas.ts:19`, `admin/reservas/page.tsx:79`). Fuera de esto sigue vigente “frontend se adapta, no al revés”.

## Sesión: cookie HttpOnly, nunca un token en el cliente

El backend (Fase 9G) solo acepta la cookie `access_token` (`HttpOnly`, `SameSite=Lax`), fijada por `POST /auth/login`. **Nunca** leer/decodificar el JWT en Dart ni guardar sesión en `shared_preferences`/`localStorage` — sería una fuente de verdad paralela a la cookie (misma regla que ya rige para `frontend/`). Manejo de cookie condicional por plataforma en `lib/core/network/cookie_interceptor*.dart` (conditional import `dart.library.io`):
- Nativo (móvil/escritorio): `cookie_jar`/`PersistCookieJar` con `FileStorage` en disco.
- Web: sin cookie jar propio — el navegador maneja la cookie `HttpOnly` (dio solo pone `withCredentials: true`).

## Entornos vía `--dart-define-from-file`

Nunca hardcodear una URL de backend en código. Archivos en `env/`:
- `env/dev.json` → `http://localhost:8000` (desktop / Chrome local, backend expuesto al host).
- `env/dev_android.json` → `http://10.0.2.2:8000` (emulador Android).
- `env/web.json` → `/api` (ruta relativa, para cuando exista el proxy same-origin de la Fase 6-Web — **no usar todavía en producción**, ver más abajo).
- `env/prod.json` → placeholder, reemplazar `BASE_URL` antes de un build de producción real.

Ejemplo: `flutter run -d chrome --dart-define-from-file=env/dev.json`.

## `docker-compose.yml` actual NO expone el backend al host

`backend` (en `docker-compose.yml`, raíz del repo) no tiene `ports:` — solo es alcanzable desde `frontend` (Next.js) vía red interna de Docker, igual que documenta el README. Un cliente Flutter nativo corriendo en el host **no puede** llegar a `http://localhost:8000` así levantando ese stack; para eso haría falta agregar `ports: ["8000:8000"]` al servicio `backend`, cambio de `docker-compose.yml` que requiere confirmación explícita (regla ya vigente del proyecto) antes de aplicarse — no se ha hecho.

## Cómo se verificó la Fase 0 sin ese puerto expuesto (y sin tocar `reservas_db`)

Regla dura del proyecto: ninguna tarea asistida debe leer/escribir/migrar `reservas_db` (la base de `docker-compose.yml`); solo `reservas_test` (puerto 5433, `docker-compose.test.yml`) es válida. Para probar login/logout real contra un backend vivo:

1. `docker compose -f docker-compose.test.yml up -d --wait` (raíz del repo) — expone `reservas_test` en `localhost:5433`.
2. Backend corrido **localmente** (no en Docker): `backend/.venv` + `uvicorn app.main:app --host 127.0.0.1 --port 8000`, con `DATABASE_URL` apuntando a `reservas_test` y `SECRET_KEY` exportada a mano en la sesión de shell (`config.py` no llama `load_dotenv()`) — así el backend queda en `localhost:8000`, alcanzable desde el host, sin tocar `docker-compose.yml` ni `reservas_db`.
3. Para el build Web (Chrome era el único target disponible en esta máquina: sin Visual Studio ni Android SDK instalados todavía), se sirvió `flutter build web` detrás de un proxy same-origin **desechable** (script Python de un solo archivo, fuera del repo, en el scratchpad de la sesión) que reenvía `/api/*` a `http://localhost:8000` — el mismo patrón arquitectónico que se documentó para la Fase 6-Web, pero como script de verificación puntual, no como el proxy real de producción (ese se construye en la Fase 6-Web con su propio servicio en `docker-compose.yml`, confirmado aparte).

Ninguno de estos tres pasos es permanente ni forma parte del repo: son solo la forma de verificar la Fase 0 en esta máquina. Antes de retomar el trabajo hay que volver a levantarlos (o instalar Visual Studio/Android SDK para probar nativo, lo cual evita el problema del proxy Web por completo ya que los clientes nativos no están sujetos a CORS).

## Riesgos de dependencias detectados en la Fase 0 (no reabrir sin verificar de nuevo)

- **`freezed` quedó en una versión de desarrollo (`4.0.0-dev.3`), no estable.** Es la única versión de `freezed` compatible con `riverpod_generator` 4.0.8 (que requiere `analyzer ^13.0.0`; la línea estable de `freezed` tope en 3.2.0, que requiere `analyzer ^7.5.9`). Revisar `flutter pub outdated` periódicamente por si el ecosistema publica una versión estable compatible; no forzar una versión estable de `freezed` sin volver a resolver este conflicto.
- **`riverpod_lint`/`custom_lint` no se instalaron**: incompatibles con Riverpod 3.4.2 en el momento de la Fase 0 (conflicto de versiones de `analyzer`/`riverpod_analyzer_utils`). Se usa solo `flutter_lints`. Reintentar cuando el ecosistema se estabilice.
- **`AsyncValue.valueOrNull` no existe en Riverpod 3.4.2** — la API cambió a `AsyncValue.value` (ya nullable-friendly, devuelve el último valor conocido incluso en estado de error/loading). Usar `.value`, no `.valueOrNull`, en todo el código nuevo.

## Rutas empujadas vs. destinos del shell (lección de la Fase 1)

`ShellRoute` (bottom/top nav) es solo para las pantallas "raíz" de cada destino de navegación (`/espacios`, `/dashboard`, ...). Una pantalla de detalle abierta por navegación normal (`/espacios/:id`) **no** va dentro del `ShellRoute`: anidarla ahí duplica el `Scaffold`/`AppBar` (el de `BottomNavShell`/`TopNavShell` MÁS el propio de la pantalla), un bug real que se detectó visualmente en la Fase 1. Las rutas "empujadas" (con su propia `AppBar` + botón atrás, sin bottom/top nav) se registran como `GoRoute` de nivel superior en `app_router.dart`, igual que `/login`, y se navega a ellas con `context.push(...)` (preserva la pila), no `context.go(...)`.

## `build.yaml`: `json_serializable` con `field_rename: snake`

Desde la Fase 1 hay un `app_flutter/build.yaml` que configura `field_rename: snake` para todo el proyecto — evita anotar `@JsonKey(name: 'snake_case')` campo por campo en modelos con muchos campos `snake_case` (`espacio_id`, `hora_inicio`, `horario_atencion`, etc.). Los campos Dart en `camelCase` se mapean solos al JSON `snake_case` del backend. Los modelos de la Fase 0 (una sola palabra por campo: `id`, `rol`, `espacio`) no se vieron afectados, pero cualquier campo nuevo de una sola palabra en mayúsculas especiales debe verificarse contra una respuesta real del backend.

## `usePathUrlStrategy()` (Web)

`main.dart` llama `usePathUrlStrategy()` (paquete `flutter_web_plugins`, no-op fuera de Web) para que las rutas en Web sean limpias (`/espacios/3`) en vez de con `#` (`/#/espacios/3`) — necesario para que una recarga de página o un enlace compartido a `/espacios/3` funcione, siempre que el proxy same-origin (real en Fase 6-Web, desechable mientras tanto) sirva `index.html` como fallback de SPA para rutas no-archivo.

## Toolchains nativas: pendientes de instalar

`flutter doctor` reporta Web (Chrome/Edge) funcional. Windows desktop requiere Visual Studio (workload "Desktop development with C++") y Android requiere Android Studio/SDK — ninguna de las dos está instalada todavía (decisión explícita: se difirió para no bloquear la Fase 0 con descargas grandes). Sin esto, los targets Windows/Android quedan escritos pero **sin verificar en ejecución real** — solo pasan `flutter analyze`/`flutter test`.

## Comandos

```bash
flutter analyze
flutter test
flutter pub run build_runner build   # tras tocar modelos freezed/json o providers @riverpod (--delete-conflicting-outputs ya no existe en este build_runner, se ignora)
flutter run -d chrome --dart-define-from-file=env/dev.json        # nota: login chocará con CORS sin el proxy same-origin (ver arriba)
```
