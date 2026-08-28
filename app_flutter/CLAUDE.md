# app_flutter/CLAUDE.md

## Estado (2026-08-21)

**Funcionalmente completo.** Fases 0-5 (auth, espacios/recursos públicos, reservas de usuario, notificaciones, gestión reservas/recursos/zonas/ensayos/horario, usuarios, dashboard, auditoría) + Fase 7 (cutover: `frontend/` Next.js **retirado del repo**, Flutter es la única UI) + trabajo adicional de paridad que no estaba en el plan original (P1: CRUD de espacios para admin; P2: reserva multi-eje — recursos+zonas+ensayos+acompañantes en un solo flujo, `EspacioReservaSheet`; P3: términos, edición/eliminación de reservas, dashboard también para rol `usuario`). El pase de diseño de Fase 6 (revisión externa + ejecución) está cerrado — ver "Sistema de diseño — Fase 6" más abajo y su "Cuarta tanda" para el detalle punto por punto de qué se cerró.

**Lo que realmente falta** (detalle en cada sección referenciada):
- **Build nativo Windows verificado; Android sigue pendiente**: Visual Studio (workload C++) se instaló y `flutter build windows`/`flutter drive -d windows` compilan y corren de verdad — ver "Toolchains nativas" más abajo. Android SDK sigue sin instalar.
- **E2E ya corrió de punta a punta en nativo Windows** (2026-08-21) — los dos archivos (`publico_y_auth_test.dart`, `reserva_flujo_test.dart`) pasan completos contra un backend real sobre `reservas_test`. El gap de Web (CORS/`--use-existing-app`) sigue vigente, no bloqueante para nativo — ver sección "E2E" más abajo.
- **CI sigue sin ejecutar el E2E real** — el job `e2e` de `ci.yml` corre en `ubuntu-latest` sin Visual Studio; wiring pendiente, requeriría un runner Windows.
- Zonas/ensayos: la UI de selección **si existe ya** (contradice lo que decía esta misma línea en versiones anteriores del documento) vía `EspacioReservaSheet` — la limitación de "solo modalidad equipos" quedó superada por el P2 de arriba.

`flutter analyze`: "No issues found!". `flutter test`: 22/22. Plan completo fuera del repo en `~/.claude/plans/` (histórico — ya no refleja el trabajo posterior a la Fase 5, que solo vive en este archivo y en los mensajes de commit).

### Cambios del 2026-08-24 (primer despliegue en servidor real)

Primera vez que la app se levanta en un host que no es la máquina de desarrollo (bastion Ubuntu 24.04). Tres cosas salieron de ahí, cada una detallada en su sección:

- **Puerto del `flutter_proxy`: 8090 → 8091** — el 8090 estaba ocupado por otro proyecto en ese host.
- **Botón "Iniciar sesión" en la nav superior** (`top_nav_shell.dart`): no existía **ningún** punto de entrada a `/login` en el shell; un visitante anónimo solo llegaba al login por redirección del guard o por los CTAs dentro de las hojas de reserva.
- **Bug real de navegación post-login (`push` vs `go`)** — encontrado por el usuario usando ese botón nuevo, afectaba también a tres CTAs preexistentes.
- **El gestor veía espacios y zonas ajenos** en las pantallas de gestión — ver la sección siguiente.
- **El shell adaptativo perdió funciones enteras en móvil** al eliminar `InicioScreen` — ver "Lo que se rompe al tocar el shell adaptativo" más abajo. **Queda un cambio sin verificar; leer esa sección antes de seguir.**

## ⚠️ Lo que se rompe al tocar el shell adaptativo (2026-08-24)

`AppShell` elige entre tres shells según el ancho: `BottomNavShell` (< 600dp), `RailNavShell` (600–1240dp) y `TopNavShell` (≥ 1240dp). **Todo lo que sea esencial tiene que existir en los tres.** En un mismo día se violó esa regla tres veces, en tres direcciones distintas:

1. **El logout vivía solo en `InicioScreen`.** Al eliminar esa pantalla, la app se quedaba sin forma de cerrar sesión en cualquier ancho. Se creó `SessionMenu` (avatar + identidad + "Cerrar sesión") y se montó en los tres.
2. **El botón "Iniciar sesión" se agregó solo a `TopNavShell`.** En celular y tablet un visitante anónimo no tenía por dónde entrar. Ahora `SessionMenu` resuelve **los dos** estados de sesión y los tres shells lo montan **sin** `if (autenticado)` alrededor — no reintroducir esa condición.
3. **Los destinos de gestión quedaron inalcanzables en celular.** `AppShell` filtraba con `primarioOnly` para el caso compacto, así que la bottom nav solo veía Espacios/Reservas/Dashboard; Recursos, Zonas, Ensayos, Usuarios, Configuración y Auditoría **no tenían ningún camino**. Funcionaban antes porque `InicioScreen` era una pantalla de atajos — su propio docstring lo advertía ("en móvil la bottom nav solo muestra destinos `primario`, así que este es el único camino móvil") y se pasó por alto al borrarla. Un admin en el teléfono se quedaba sin la mitad de la app.

**Estado del arreglo de (3):** `AppShell` ahora pasa la lista completa a los tres shells y `BottomNavShell` hace el reparto él mismo (primarios a la barra, resto a un menú "Gestión" con ícono de engranaje en la `AppBar`, igual que `TopNavShell`). **Este cambio se pusheó SIN pasar `flutter analyze`/`flutter test` en local** — la corrida se interrumpió. El CI es el gate y el agente de CD solo despliega commits verdes, así que si falló no llegó al servidor: verificar el estado del workflow antes de seguir.

### Dos bugs preexistentes que destapó el test de anchos

Ninguno lo había visto nadie; los encontró `test/shell/session_menu_test.dart` al montar `AppShell` a 375dp, algo que ninguna prueba hacía antes.

- **`NavigationBar` exige `destinations.length >= 2`** (assert en `navigation_bar.dart`). `BottomNavShell` protegía con `destinos.isEmpty`, que solo cubre el cero — y el caso de UNO es alcanzable: un visitante anónimo ve un único destino, porque "Espacios" es el único con `requiereSesion: false`. En release los `assert` no corren, por eso nunca se vio como pantalla roja.
- **`BrandMark` desbordaba 106px en 375dp.** Aceptaba un parámetro `compact` **desde siempre que su `build` ignoraba por completo**: alguien previó el problema, dejó la puerta y no la conectó. Ahora recorta al ícono, y en el caso normal el wordmark va en `Flexible` con elipsis — el ancho disponible depende de las acciones de la `AppBar` **y del factor de escala de texto de accesibilidad**, así que un ancho "que siempre entra" no existe.

## ⚠️ El alcance del gestor NO viene filtrado en los listados: hay que aplicarlo en el cliente (2026-08-24)

Regla a recordar, porque es contraintuitiva y ya causó dos defectos:

> El backend **sí** impone el alcance del gestor en las **escrituras** (403, o sobrescritura silenciosa del `espacio_id`), pero los **listados de lectura devuelven todo**. `GET /espacios` solo filtra por estado (`api/espacios.py:50-53`, RN-005) y `GET /zonas` tampoco acota al espacio gestionado (`api/zonas.py:31-36`): gestor y admin reciben los de todos los espacios. **Si una pantalla de gestión muestra una lista o un selector, el filtro por espacio es responsabilidad del cliente.**

El dato para filtrar ya está en memoria y no hace falta pedir nada: `AuthUser.espacio` (`features/auth/domain/auth_user.dart`) es un `EspacioResumen{id, nombre, ubicacion}` que `GET /usuarios/me` y `POST /auth/supabase/sesion` devuelven poblado para el gestor (`null` para admin y para rol `usuario`).

Lo que estaba mal, reportado por el usuario contra el despliegue real:

1. **Formulario de zonas** (`gestion_zonas_screen.dart`): la condición del selector de espacio era `if (!_esEdicion || esAdmin)`, así que **al crear** se le mostraba también al gestor, con la lista global. El agravante no era el ruido visual sino la trampa: el `DropdownButtonFormField` preseleccionaba `espacios.first` vía `initialValue` y su `onSaved` confirmaba ese valor en el estado durante `_formKey.currentState!.save()` — un gestor que ni tocaba el campo enviaba un espacio ajeno y se comía un 403 incomprensible. Arreglado a `if (esAdmin)`, con `_espacioId` sembrado en `initState` desde `AuthUser.espacio`.
2. **`zonasGestionProvider`** (`zonas/application/zonas_providers.dart`): tenía un comentario afirmando *"Para gestor, el backend ya filtra al espacio gestionado"*. **Era falso.** Por eso el gestor veía en `GestionZonasScreen` las zonas de todos los espacios, y el desplegable de zona de `GestionEnsayosScreen` —alimentado por el mismo provider— le ofrecía zonas ajenas que el backend luego rechazaba. `ZonasRepository.listar({int? espacioId})` ya aceptaba el filtro; nunca se le pasaba. Ahora el provider conmuta por rol, igual que `dashboard_providers.dart:14`.

`GestionRecursosScreen` ya lo hacía bien desde antes (envuelve el selector en `if (esAdmin)` y deja que el backend complete el espacio) — **ese es el patrón a copiar** para cualquier pantalla de gestión nueva. `GestionUsuariosScreen` y `GestionEspaciosScreen` sí deben listar todos los espacios: son exclusivas de admin.

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

## ⚠️ Un `SnackBar` con `action` NO se auto-cierra: hay que pasarle `persist: false`

Bug real reportado en producción (2026-08-25): el aviso "Se vació el Dom" del editor de horario (`ConfiguracionEspacioScreen._actualizarHorario`) quedaba clavado en pantalla para siempre, sin importar el `duration: 8s`.

La causa está en el framework, no en la app — `snack_bar.dart`:

```dart
persist = persist ?? action != null;
```

**Cualquier `SnackBar` que lleve `action` toma `persist: true` por defecto**, y un snackbar que persiste no se cierra solo nunca: el timer de `duration` se dispara, ve `persist`, y retorna sin cerrarlo (`scaffold.dart`, donde se arma `_snackBarTimer`). La documentación del campo lo dice explícitamente: *"If not provided, but the snackbar action is not null, the snackbar will persist as well."*

**Regla**: todo `SnackBar` con `action` que deba desaparecer solo necesita `persist: false` explícito. Ajustar `duration` no sirve de nada — se ignora por completo.

Dos intentos previos fallaron antes de encontrar esto, y vale la pena saber por qué para no repetirlos: no es un problema de cómo se reemplaza el snackbar anterior (`hideCurrentSnackBar` vs `removeCurrentSnackBar` es irrelevante acá), ni una carrera entre dos operaciones masivas seguidas. Cubierto por `test/features/espacios/presentation/configuracion_espacio_screen_test.dart`, verificado en ambos sentidos: el test falla si se quita el `persist: false`.

### El font de prueba desborda layouts que en la app real entran bien

Al escribir ese test apareció un `RenderFlex overflowed by 47 pixels` en `horario_editor.dart` (`_EtiquetaHora`) que **no existe en producción**: `flutter test` no carga fuentes reales y usa una de reemplazo donde cada glifo mide exactamente el tamaño de fuente, así que `"06:00–07:00"` ocupa ~121px donde Inter ocupa ~60 y revienta la columna de 112px. Antes de "arreglar" un overflow que solo aparece en un widget test, comprobar si el ancho del texto es el culpable — la salida a mano es compensar el escalado en el harness del test (`MediaQuery` con `textScaler` reducido, ver ese archivo), nunca deformar el widget de producción para complacer al test. **Ojo**: esto NO aplica al overflow de `EmptyView` documentado en la sección de E2E — ese era real y se veía en la app.

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

**P2 — Reserva multi-eje (paridad A2).** `data/reservas_repository.dart:22` `crear({recursoIds, zonaIds, ensayoIds, acompanantes, fecha, horaInicio/Fin, asistentes, tipo})` ya no hardcodea `[]`; `presentation/espacio_reserva_sheet.dart` nuevo (sheet anclado a `Espacio`, no a `Recurso`): `CheckboxListTile` Recursos si `modalidad != zonas` + Zonas si `modalidad != equipos` + Ensayos por zona + Acompañantes dinámico `nombre/correo` + `Tipo` dropdown + `SelectableSlotGrid` con `capacidadMax = min(espacio, zonas, recursos)` y `recargarSlots` (si `recursoIds[0]` → `recursoDisponibilidadProvider`, else si `zonaIds` → `fakeSlots` desde horario). `presentation/espacio_detalle_screen.dart:50` ahora muestra `Recursos` y `Zonas` del espacio y botón `FilledButton Reservar` que abre el nuevo sheet (mantiene `_RecursoTile` legacy para single). Verificado `flutter analyze` sin issues.

**P3 — Términos, edición reservas y dashboard usuario (paridad A3-A6).**
- `legal/presentation/terminos_screen.dart` nuevo + `app_router.dart:102` `GoRoute /terminos` (pública) para que `context.push(AppRoutes.terminos)` no caiga en guard.
- `data/reservas_repository.dart:86` `actualizar(id,{fecha,horaInicio,horaFin,asistentes}) → PATCH /reservas/{id}` + `eliminar(id) → DELETE`; `presentation/mis_reservas_screen.dart:135` `OutlinedButton Editar` si `esperando` abre `AlertDialog Form` con `showDatePicker` + `Hora` + `Asistentes` → `actualizar` + `ref.invalidate(misReservasProvider)`; `presentation/gestion_reservas_screen.dart:94` `PopupMenu` ahora tiene `Editar/Eliminar` además de `Rechazar/Cancelar` (ambos con `actualizar/eliminar` + `apiErrorMessage`).
- `presentation/dashboard_screen.dart:68` `DashboardScreen` ahora detecta `rol==usuario` → `_UsuarioDashboard` (usa `misReservasProvider` para `total/pendientes/aprobadas/próximas` con `_StatItem` + quick actions `Ver espacios/Mis reservas`); `nav_destinations.dart:140` `dashboard` ahora sin `rolesPermitidos` (visible para todo autenticado). Verificado `flutter analyze`/`test`.

### Pendiente fino (requiere toolchain, no tocado sin confirmación)

- Compilar Windows/Android: `flutter doctor` sigue `X Visual Studio not installed` + `X Android SDK` (`windows: flutter generated_plugin_registrant` warnings son CRLF, no fallo). Requiere instalar VS workload C++ + Android Studio/SDK. Confirmado de nuevo el 2026-08-21 (`flutter drive -d windows` → `Unable to find suitable Visual Studio toolchain`).
- ~~Proxy same-origin real de Fase 6-Web~~ — **ya no está pendiente.** Nota obsoleta: quedó escrita antes de la Fase 7 (`chore: retira frontend Next.js y promueve Flutter como unica UI`), que agregó el servicio `flutter_proxy` (`nginx:alpine`) a `docker-compose.yml` — ver "`docker-compose.yml` — backend sin `ports:`, Flutter Web vía `flutter_proxy`" más abajo. Verificado de nuevo el 2026-08-21 por HTTP contra un proxy equivalente propio apuntado a `reservas_test` (no contra `:8090`, ver advertencia sobre `reservas_db` más abajo): cookie `HttpOnly; Path=/; SameSite=lax` sin `Domain` se fija correctamente en el login, `/admin/reservas` (ruta protegida, recarga directa) devuelve el mismo `index.html` que `/` byte a byte (fallback SPA real, no 404), `/api/health` responde a través del proxy con el prefijo recortado, `main.dart.js` es el bundle minificado de un build release (~3.5MB, sin nombres de variable Dart legibles).

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

## Migración a Supabase Auth (corte total, 2026-08-26)

Reemplaza por completo la sección anterior de este documento ("Correo saliente: alta de usuario y recuperación de contraseña"): esos 3 endpoints/pantallas nacieron el mismo día y se retiraron el mismo día, a pedido del profesor de la materia de usar Supabase Auth para todo el flujo de login. Nada de ese trabajo llegó a verificarse manualmente en producción — el diseño quedó documentado en el historial de commits, no acá.

**Antecedente que motivó el diseño**: un intento previo (otra sesión de IA, "OpenCode", con acceso al mismo repo) implementó Supabase Auth como híbrido y lo dejó roto en producción real: una heurística (`username.contains('@')`) mandaba cualquier cuenta clásica por el camino de Supabase sin que existiera ahí, y el endpoint de intercambio de sesión auto-vinculaba o auto-creaba cuentas por email sin ningún control — un hueco de seguridad real, sin un solo test. Se apagó ese código (commit `9e7ff02`) para restaurar el login clásico mientras se diseñaba este reemplazo correcto.

- **Corte completo, no híbrido**: no hay flag `SUPABASE_ENABLED`. `SupabaseConfig.isConfigured` (`core/config/supabase_config.dart`) solo sirve para que `main.dart` falle rápido y con mensaje claro si falta `SUPABASE_URL`/la clave — no hay ningún camino que siga funcionando sin Supabase configurado.
- **`main.dart`**: `Supabase.initialize` ya no es condicional, y pasa `localStorage: SupabaseSecureStorage()` — `SupabaseSecureStorage` (`core/storage/supabase_secure_storage.dart`) ahora implementa de verdad la interfaz `LocalStorage` del SDK (antes era un wrapper dormido; supabase_flutter seguía usando `SharedPreferences` por defecto pese a que el archivo existía). La sesión de Supabase queda en `flutter_secure_storage` (Keychain/EncryptedSharedPreferences), no en texto plano.
- **Un solo `AuthRepository`** (`features/auth/data/auth_repository.dart`): `login(email, password)` hace `signInWithPassword` contra Supabase y el intercambio con `POST /auth/supabase/sesion` en un solo método. Se eliminó `SupabaseAuthRepository` y la heurística `username.contains('@')` de `auth_provider.dart` que causó el incidente de OpenCode — ya no hay dos repositorios ni una decisión de "cuál usar" en tiempo de login.
- **`LoginScreen`**: el campo pasa de "Usuario" a "Email" (Supabase autentica por email, no por username) — mismo criterio de validación de formato que `UsuarioCreate.validate_email` del backend. El link "¿Olvidaste tu contraseña?" se retiró junto con `RecuperarPasswordScreen`/`RestablecerPasswordScreen` (ver más abajo) y volvió el 2026-08-27 como diálogo, ver "Recuperación de contraseña self-service" más abajo.
- **Se retiraron `CambiarPasswordTemporalScreen`, `RecuperarPasswordScreen`, `RestablecerPasswordScreen`** y sus rutas (`/cambiar-password-temporal`, `/recuperar`, `/restablecer` fuera de `app_routes.dart`) — Supabase resuelve el primer cambio y la recuperación con sus propios correos/links. `AuthUser.debeCambiarPassword` se eliminó del modelo (regenerado `auth_user.freezed.dart`/`.g.dart`) y con él el guard correspondiente en `app_router.dart`.
- **Alta de usuario**: `gestion_usuarios_screen.dart` no pide contraseña ni al crear ni al editar (el campo "Nueva contraseña (opcional)" de edición también se retiró, ya que `UsuarioUpdate.password` no existe más en el backend) — Supabase invita por email, la persona elige su contraseña desde ese link.
- **`kRutasSinRedirect401`** (`auth_interceptor.dart`) cambió `/auth/login` por `/auth/supabase/sesion` (mismo motivo: un 401 ahí es parte de un intento de login en curso, no una sesión que expiró) y se retiró la entrada de `/auth/cambiar-password` (endpoint retirado).
- **`env/*.json`** ahora llevan `SUPABASE_URL`/`SUPABASE_PUBLISHABLE_KEY` en los cuatro archivos (antes solo `web.json`, y solo brevemente) — son las claves públicas del proyecto Supabase Cloud (`ijktwqnkknemjrokwcdn.supabase.co`), seguras de commitear igual que cualquier `anonKey`/`publishableKey`. La `SUPABASE_SERVICE_ROLE_KEY` (secreta, backend-only) nunca va acá — vive solo en el `.env` del backend.
- **Verificación manual real hecha el 2026-08-27** (crear usuario real en Supabase vía Admin API → login real → canjear el JWT en el backend → `GET /usuarios/me`), y encontró dos bugs reales que ni `flutter analyze` ni `pytest` atrapaban:
  1. **El backend rechazaba TODO login real con 401.** Un proyecto de Supabase real firma sus JWT con ES256 (clave asimétrica), no HS256 (secreto compartido) — `deps.py`/`api/auth.py` solo sabían verificar HS256. Corregido con verificación vía JWKS público de Supabase (`backend/app/services/supabase_jwks.py`); ver `backend/CLAUDE.md`.
  2. **El link de invitación no llevaba a ningún lado.** La migración implementó `login()` pero nunca la pantalla donde una persona invitada fija su contraseña — el correo de Supabase (`type=invite`) apuntaba a una URL sin ningún handler. Corregido: `CompletarCuentaScreen` (`features/auth/presentation/completar_cuenta_screen.dart`, ruta pública `/completar-cuenta`) + un listener de `Supabase.instance.client.auth.onAuthStateChange` en `main.dart` que redirige ahí apenas Supabase detecta el token de invitación en la URL (evento `passwordRecovery` — Supabase trata invitación y recuperación de contraseña igual del lado del cliente). `AuthRepository.completarCuenta` llama `updateUser` y reusa el mismo canje de sesión que `login`.

  **Ya resuelto en el dashboard de Supabase** (`Authentication → URL Configuration`): `Site URL` apunta a la URL real del servidor, verificado el mismo día contra un `generate_link` real que devolvió el `redirect_to` correcto.

- **Borrar usuario y reenviar invitación** (2026-08-27, mismo día): `gestion_usuarios_screen.dart` gana un botón "Reenviar invitación" (ícono `mailPlus` junto a Editar/Eliminar, en la fila de escritorio y la tarjeta móvil) que llama `POST /usuarios/{id}/reenviar-invitacion` y muestra el link en un diálogo con botón de copiar (`_mostrarLinkInvitacion`) — necesario mientras el SMTP del ITM sigue pendiente (ver memoria de sesión `smtp_itm_pendiente`), ya que Supabase no manda el correo por su cuenta para este endpoint. `UsuariosRepository.reenviarInvitacion` + el tipo `ReenvioInvitacion` (`link`, `correoEnviado`). Motivado por otro bug real encontrado en producción el mismo día: borrar un usuario nunca borraba su identidad de Supabase (solo `DELETE /usuarios/{id}` del lado backend, ver `backend/CLAUDE.md`), así que reinvitar el mismo email después fallaba con `email_exists`.

### Recuperación de contraseña self-service (2026-08-27)

Sin backend nuevo — reusa por completo el mecanismo que `CompletarCuentaScreen` ya resolvió para invitaciones (Supabase trata invitación y recuperación como el mismo evento `passwordRecovery` del lado del cliente, ver más arriba). Lo único que faltaba era el disparador: un link "¿Olvidaste tu contraseña?" en `LoginScreen`.

- **`AuthRepository.solicitarRecuperacion(email)`**: una sola llamada, `Supabase.instance.client.auth.resetPasswordForEmail(email)`, directo contra Supabase Cloud — no pasa por nuestro backend ni por el outbox de correo. La respuesta es la misma exista o no una cuenta con ese email (Supabase no distingue del lado del cliente); `_RecuperarPasswordDialog` (privado a `login_screen.dart`) muestra siempre el mismo mensaje genérico de éxito, para no filtrar qué emails están registrados.
- **UI**: diálogo, no una pantalla aparte (a diferencia de la vieja `RecuperarPasswordScreen`/`RestablecerPasswordScreen` de dos pasos) — un solo campo de email, precargado con lo que la persona ya haya escrito en el campo de login. Se abre desde el link debajo del campo de contraseña en `LoginScreen`.
- **Completar la recuperación**: es exactamente `CompletarCuentaScreen` — el link del correo establece la sesión temporal, `main.dart` la detecta (`passwordRecovery`) y redirige ahí; la persona fija su contraseña con el mismo formulario que usa una invitación nueva. No hay una pantalla "Restablecer contraseña" separada.
- **Tests**: `login_screen_test.dart` (grupo "Recuperar contraseña") — precarga del email, validación de formato, envío exitoso con mensaje genérico, y error del backend propagado. El campo del diálogo usa `Key('recuperar_password_email')` para no depender del orden de widgets en el árbol (el campo de login de fondo sigue montado detrás del diálogo).

## Fase A — perfil de usuario, recursos por zona, descripción de reserva (2026-08-27)

Primera fase de un plan más grande (formulario real de solicitud de laboratorios del ITM + Excel de inventario, ver `~/.claude/plans/ya-tenemos-el-ci-calm-octopus.md` para las fases B/C/D todavía no implementadas — 4 "motivos de solicitud", tabla `solicitudes_especiales`, import masivo). Esta fase es la parte aditiva y de bajo riesgo.

- **A1 — "Recursos" en `GestionZonasScreen`**: gap real que ya existía en el código — `PUT /zonas/{id}/recursos` y `ZonasRepository.reemplazarRecursos` (desde la Fase 12C-3) nunca tenían una pantalla que los llamara. Ahora cada `_ZonaCard` tiene un tercer botón "Recursos" que abre `_ZonaRecursosDialog`: lista los recursos del mismo `espacio_id` de la zona (`recursosPorEspacioProvider`), preseleccionados desde `Zona.recursoIds` (nuevo campo, viene de `ZonaResponse.recurso_ids` — cambio de contrato pequeño y aditivo, necesario porque el diálogo es un reemplazo completo y sin la selección actual un gestor podría vaciar por accidente una asociación que no podía ver).
- **A2 — perfil de usuario** (`/perfil`, `MiPerfilScreen`): datos del formulario real (documento, teléfono, institución, vinculación, dependencia) que hoy no existían en ningún lado — se completan una vez, no en cada reserva. `AuthUser` gana los 5 campos nullable. Nuevo `UsuariosRepository.actualizarMiPerfil` → `PUT /usuarios/me` (self-service, cualquier rol — a diferencia del resto de `UsuariosRepository`, que es admin-only). `Auth.actualizarPerfilLocal(user)` actualiza el estado en memoria con lo que ya devolvió el backend, mismo criterio que `login`/`completarCuenta` (sin volver a pedir `/usuarios/me`).
  - **Ruta empujada, no destino del shell**: `/perfil` se registra fuera del `ShellRoute` (mismo patrón que `/admin/configuracion`) porque no es un destino de navegación persistente — se llega ahí desde `SessionMenu` (nuevo ítem "Mi perfil", antes de "Cerrar sesión"), que ya se monta en los tres shells por diseño (ver la lección de 2026-08-24 sobre puntos de entrada faltantes en un solo shell).
  - `AppRoutes.perfil` ya estaba declarado desde hace tiempo y nunca se usaba — quedó esperando exactamente esto.
- **A3 — `Reserva.descripcion`**: texto libre opcional ("Actividad a realizar" del formulario real). Campo nuevo en `EspacioReservaSheet` (antes del bloque de disponibilidad), se muestra en `MisReservasScreen`/`GestionReservasScreen` si no es null. `ReservasRepository.crear`/`actualizar` lo pasan tal cual.
- **Tests**: `gestion_zonas_screen_test.dart` (grupo "recursos de una zona" — precarga, guardado, sin recursos, error del backend) y `mi_perfil_screen_test.dart` (nuevo — precarga, guardado, error del backend). `EspacioReservaSheet` sigue sin test dedicado (ya lo estaba antes de esta fase, complejidad documentada).

## Fase B — motivo de la solicitud (2026-08-27)

Segunda fase del mismo plan: agrega las 2 ramas del formulario real que sí encajan en el modelo actual de `Reserva` (franja horaria de un día). Las otras 2 (orden de salida, mano de obra) quedan visibles pero deshabilitadas hasta la Fase C.

- **`TipoSolicitud`** (`core/domain/enums.dart`), espejo del enum del backend: `reservaEnLaboratorio` (default), `reservaFueraLaboratorio`, `ordenSalida` (existe en el enum pero nunca se manda — el backend lo rechaza con 422 si llegara).
- **El botón "Reservar" de `EspacioDetalleScreen` pasa a "Nueva solicitud"** y abre primero `_MotivoSolicitudDialog` (texto de la pregunta 11 del formulario real): 2 opciones habilitadas (reserva dentro/fuera del laboratorio) + 2 deshabilitadas con rótulo "Próximamente" (orden de salida, mano de obra). Elegir un motivo cierra el diálogo y abre el `EspacioReservaSheet` de siempre, con `tipoSolicitud` prefijado por parámetro — **no se convirtió el sheet en un formulario de 4 ramas** (ya es denso: recursos+zonas+ensayos+acompañantes+disponibilidad+descripción).
- **`EspacioReservaSheet` gana 2 elementos condicionales al motivo**: si es `reservaFueraLaboratorio`, un `TextField` "¿Dónde se va a usar el equipo?" (`ubicacion_uso`, validado como requerido del lado cliente antes de enviar — si está vacío, el sheet muestra un error y no llama al repositorio). El `SwitchListTile` "¿Requiere apoyo del auxiliar del laboratorio?" aparece para ambos motivos habilitados.
- **`Reserva`/`ReservasRepository`**: `tipoSolicitud` (default `reservaEnLaboratorio`), `ubicacionUso`, `requiereApoyoAuxiliar` — `crear`/`actualizar` los pasan tal cual, mismo patrón que `descripcion` en A3.
- **`GestionReservasScreen`/`MisReservasScreen`** muestran el motivo (chip o línea, según el layout de cada tarjeta) solo cuando no es el default, más `ubicacion_uso` si tiene valor y un chip "Requiere auxiliar" cuando aplica.
- **Sin test dedicado nuevo**: ni `_MotivoSolicitudDialog` (widget privado, solo alcanzable desde `EspacioDetalleScreen`, que depende de varios providers pesados para montar) ni `EspacioReservaSheet` (ya sin test desde antes de esta fase) — mismo criterio ya documentado en A3, verificado con `flutter analyze`/`flutter test` global más revisión manual del flujo.

## Equipos adicionales en una reserva (2026-08-27)

Dos features chicas fuera del plan de fases, implementadas por OpenCode a partir de `HANDOFF-opencode-equipos-reserva.md` (raíz del repo) y revisadas/corregidas por Claude Code antes de aprobarlas — ver el detalle de diseño en `backend/CLAUDE.md`, sección "Equipos adicionales en una reserva".

- **Feature A — `EspacioReservaSheet` agrupa visualmente "Zonas (incluye sus equipos)" vs "Equipos adicionales de este laboratorio"**, en vez de mostrar `Recursos`/`Zonas` como dos listas planas sin relación. Un recurso ya cubierto por una zona marcada aparece tildado, deshabilitado (`onChanged: null`) y con la etiqueta "Incluido en zona X" — no sugiere marcarlo dos veces. Sin cambios de backend: `recurso_ids`/`zona_ids` seguían siendo ejes independientes desde la Fase 12C-6, el gap era 100% de presentación. 7 tests nuevos en `test/features/reservas/presentation/espacio_reserva_sheet_test.dart` (agrupación por modalidad, subtítulo de zona con/sin equipos, recurso cubierto por una o varias zonas, toggle de zona actualiza el estado "Incluido" en vivo).
- **Feature B — `GestionReservasScreen._editarReserva` gana selección de recursos/zonas**: el diálogo de edición (antes solo fecha/hora/asistentes) ahora es `_EditarReservaDialog`, con el mismo patrón visual de agrupación de la Feature A, precargado desde `Reserva.recursoIds`/`zonaIds`. Al guardar, llama `ReservasRepository.actualizar(..., recursoIds:, zonaIds:)` (el backend ya aceptaba estos campos en el `PATCH`, ver `backend/CLAUDE.md`) — si el gestor agregó algo nuevo, el dueño de la reserva recibe una notificación tipo `TipoNotificacion.actualizada` (ícono `LucideIcons.boxes`, color `AppColors.marca`, nuevo caso en el switch exhaustivo de `_NotificacionTile` en `notificaciones_sheet.dart`).
- **Corregido durante la revisión** (no estaba en la implementación original de OpenCode): 3 `curly_braces_in_flow_control_structures` (`if`/`else` de una línea sin llaves) en los nuevos `onChanged` de `_EditarReservaDialog`; y dos parámetros sin usar (`ensayoIds`/`acompanantes`) que se habían agregado a `ReservasRepository.actualizar` sin que ningún caller los pasara — se quitaron, ningún caller real los necesitaba.
- **Verificado**: `flutter analyze` limpio, `flutter test` 40/40 (33 previos + 7 nuevos de Feature A). **Sin verificación manual interactiva** contra un backend real corriendo — mismo gap ya documentado para el E2E Web (CORS/`--use-existing-app`), no se montó el harness nativo Windows solo para esto en esta sesión. Riesgo residual conocido: la cobertura es de tests automatizados (bastante específica, un caso por interacción visual), no del flujo real en un navegador.

## Perfil obligatorio para cualquier rol (2026-08-28)

A pedido explícito: los 5 campos de perfil de la Fase A2 (documento, teléfono, institución, vinculación, dependencia) pasan de opcionales a **obligatorios** para poder usar el resto de la app — no solo para usuarios recién invitados.

- **`AuthUser.perfilCompleto`** (`features/auth/domain/auth_user.dart`): `true` solo si los 5 campos están presentes y no son texto en blanco. Sin columna nueva en el backend — se deriva de los mismos 5 campos nullable que ya devuelve `UsuarioResponse`.
- **Guard nuevo en `app_router.dart`**: cualquier usuario autenticado con `!perfilCompleto` se redirige a `/perfil` sin importar a qué ruta intente navegar (mismo mecanismo que el guard de rol ya existente, ver "Guard por rol del router reutiliza `kNavDestinations`" más arriba) — se evalúa antes que ese guard de rol, así que ni siquiera llega a chequear permisos de destino.
- **Sin forma de distinguir "recién invitado" de "cuenta vieja que nunca lo llenó"** sin agregar una columna nueva (deliberadamente no se agregó una) — la regla es general: **toda cuenta existente con el perfil incompleto también queda atrapada la próxima vez que entre**, no solo las nuevas. Esto incluye cuentas de prueba ya creadas antes de este cambio.
- **`MiPerfilScreen` gana los 5 `validator`** (antes ningún campo era obligatorio, `_formKey.currentState!.validate()` pasaba trivialmente vacío) y un botón "Cerrar sesión" en el `AppBar` — necesario porque si el guard forzó la navegación acá (recién invitado, nada en el stack para volver atrás con el botón "atrás" normal), sin ese botón la única salida sería completar el formulario ahí mismo. El texto introductorio cambia ("Antes de continuar, completá estos datos...") cuando `!perfilCompleto`.
- Tests: `test/features/auth/domain/auth_user_test.dart` (nuevo, `perfilCompleto` con 0/4/5 campos y texto en blanco), `mi_perfil_screen_test.dart` extendido (Guardar con campos vacíos no envía nada y muestra "Requerido", texto de "antes de continuar" cuando incompleto, botón de Cerrar sesión presente). **Sin test de router** para el guard en sí — mismo criterio ya establecido para el guard de rol existente (`app_router.dart`), que tampoco tiene test dedicado; se apoya en verificación manual/E2E.

## Sesión: cookie HttpOnly, nunca un token en el cliente

El backend solo acepta la cookie `access_token` (`HttpOnly`, `SameSite=Lax`), fijada por `POST /auth/supabase/sesion` con el JWT de Supabase tal cual. **Nunca** leer/decodificar el JWT en Dart ni guardar sesión en `shared_preferences`/`localStorage` — sería una fuente de verdad paralela a la cookie (misma regla que ya rige para `frontend/`). Manejo de cookie condicional por plataforma en `lib/core/network/cookie_interceptor*.dart` (conditional import `dart.library.io`):
- Nativo (móvil/escritorio): `cookie_jar`/`PersistCookieJar` con `FileStorage` en disco.
- Web: sin cookie jar propio — el navegador maneja la cookie `HttpOnly` (dio solo pone `withCredentials: true`).

## Entornos vía `--dart-define-from-file`

Nunca hardcodear una URL de backend en código. Archivos en `env/`:
- `env/dev.json` → `http://localhost:8000` (desktop / Chrome local, backend expuesto al host).
- `env/dev_android.json` → `http://10.0.2.2:8000` (emulador Android).
- `env/web.json` → `/api` (ruta relativa, para cuando exista el proxy same-origin de la Fase 6-Web — **no usar todavía en producción**, ver más abajo).
- `env/prod.json` → placeholder, reemplazar `BASE_URL` antes de un build de producción real.

Ejemplo: `flutter run -d chrome --dart-define-from-file=env/dev.json`.

## `docker-compose.yml` — backend sin `ports:`, Flutter Web vía `flutter_proxy`

`backend` (en `docker-compose.yml`, raíz del repo) **sigue sin `ports:`** — solo es alcanzable vía red interna `application_network` (antes desde `frontend:3000`, ahora desde `flutter_proxy:8090`). Un cliente nativo corriendo en el host **tampoco** llega a `http://localhost:8000` con ese stack. `flutter_proxy` (`nginx:alpine`, `8090:80`, `volumes: nginx.conf:ro + build/web:ro`, `depends_on: backend:healthy`) es el que expone la Web al host y proxea `/api/` → `http://backend:8000/` (strip con `proxy_pass ...8000/` + `try_files /index.html` para SPA). Verificado 2026-08-21: `curl -i http://127.0.0.1:8090/` `200` html, `curl http://127.0.0.1:8090/api/health` `200 {"status":"ok"}`, `curl /espacios/3` `200` fallback — `SECRET_KEY` seteada en la shell del `up` (`clave-de-prueba...` 32+).

## Cómo se verificó la Fase 0 sin ese puerto expuesto (y sin tocar `reservas_db`)

Regla dura del proyecto: ninguna tarea asistida debe leer/escribir/migrar `reservas_db` (la base de `docker-compose.yml`); solo `reservas_test` (puerto 5433, `docker-compose.test.yml`) es válida. Para probar login/logout real contra un backend vivo:

1. `docker compose -f docker-compose.test.yml up -d --wait` (raíz del repo) — expone `reservas_test` en `localhost:5433`.
2. Backend corrido **localmente** (no en Docker): `backend/.venv` + `uvicorn app.main:app --host 127.0.0.1 --port 8000`, con `DATABASE_URL` apuntando a `reservas_test` y `SECRET_KEY` exportada a mano en la sesión de shell (`config.py` no llama `load_dotenv()`) — así el backend queda en `localhost:8000`, alcanzable desde el host, sin tocar `docker-compose.yml` ni `reservas_db`.
3. Para el build Web (Chrome era el único target disponible en esta máquina: sin Visual Studio ni Android SDK instalados todavía), se sirvió `flutter build web` detrás de un proxy same-origin **desechable** (script Python de un solo archivo, fuera del repo, en el scratchpad de la sesión) que reenvía `/api/*` a `http://localhost:8000` — el mismo patrón arquitectónico que se documentó para la Fase 6-Web, pero como script de verificación puntual, no como el proxy real de producción (ese se construye en la Fase 6-Web con su propio servicio en `docker-compose.yml`, confirmado aparte).

Ninguno de estos tres pasos es permanente ni forma parte del repo: son solo la forma de verificar la Fase 0 en esta máquina. Antes de retomar el trabajo hay que volver a levantarlos (o instalar Visual Studio/Android SDK para probar nativo, lo cual evita el problema del proxy Web por completo ya que los clientes nativos no están sujetos a CORS).

**Verificación Fase 6-Web real (2026-08-21):** con `frontend/` ya borrado, `SECRET_KEY=dummy...` + `docker compose up -d --build flutter_proxy --wait` (usa `app_flutter/nginx.conf` y `build/web` montados) + `flutter build web --dart-define-from-file=env/web.json` (`161s`, `√ Built build/web`). `curl -i http://127.0.0.1:8090/` `200` `text/html` `flutter_bootstrap.js`, `curl http://127.0.0.1:8090/api/health` `200 {"status":"ok"}` (proxy strip `proxy_pass http://backend:8000/`), `curl /espacios/3` `200` fallback `try_files` — sin exponer `backend:8000` al host.

## Riesgos de dependencias detectados en la Fase 0 (no reabrir sin verificar de nuevo)

- **`freezed` quedó en una versión de desarrollo (`4.0.0-dev.3`), no estable.** Es la única versión de `freezed` compatible con `riverpod_generator` 4.0.8 (que requiere `analyzer ^13.0.0`; la línea estable de `freezed` tope en 3.2.0, que requiere `analyzer ^7.5.9`). Revisar `flutter pub outdated` periódicamente por si el ecosistema publica una versión estable compatible; no forzar una versión estable de `freezed` sin volver a resolver este conflicto.
- **`riverpod_lint`/`custom_lint` no se instalaron**: incompatibles con Riverpod 3.4.2 en el momento de la Fase 0 (conflicto de versiones de `analyzer`/`riverpod_analyzer_utils`). Se usa solo `flutter_lints`. Reintentar cuando el ecosistema se estabilice.
- **`AsyncValue.valueOrNull` no existe en Riverpod 3.4.2** — la API cambió a `AsyncValue.value` (ya nullable-friendly, devuelve el último valor conocido incluso en estado de error/loading). Usar `.value`, no `.valueOrNull`, en todo el código nuevo.

## Rutas empujadas vs. destinos del shell (lección de la Fase 1)

`ShellRoute` (bottom/top nav) es solo para las pantallas "raíz" de cada destino de navegación (`/espacios`, `/dashboard`, ...). Una pantalla de detalle abierta por navegación normal (`/espacios/:id`) **no** va dentro del `ShellRoute`: anidarla ahí duplica el `Scaffold`/`AppBar` (el de `BottomNavShell`/`TopNavShell` MÁS el propio de la pantalla), un bug real que se detectó visualmente en la Fase 1. Las rutas "empujadas" (con su propia `AppBar` + botón atrás, sin bottom/top nav) se registran como `GoRoute` de nivel superior en `app_router.dart` y se navega a ellas con `context.push(...)` (preserva la pila), no `context.go(...)`.

**`/login` es la excepción: se registra igual (nivel superior) pero se navega con `go`, nunca con `push`** — ver la sección siguiente. Esta advertencia se agregó el 2026-08-24 justo porque esta misma sección decía antes "igual que `/login`" y esa frase indujo el bug.

## ⚠️ A `/login` se navega con `go`, NUNCA con `push` (bug real, 2026-08-24)

Síntoma reportado por el usuario, contra el despliegue real: se ingresaban credenciales válidas, el backend respondía `POST /auth/login 200 OK`, y la app **se quedaba mostrando el formulario de login**. Recargando la página aparecía la sesión ya iniciada. Parecía un 401 intermitente y no lo era.

Causa: `context.push(AppRoutes.login)`. En `go_router`, `push` agrega un `ImperativeRouteMatch` **encima** de la `RouteMatchList` actual sin cambiar el `uri` de esa lista — la barra de direcciones seguía marcando `/espacios` mientras se veía la pantalla de login (así se detectó, por captura del navegador). El guard de `app_router.dart` decide la navegación post-login con:

```dart
if (user != null && state.matchedLocation == AppRoutes.login) return AppRoutes.inicio;
```

Como `matchedLocation` valía `/espacios` y no `/login`, la condición nunca se cumplía: el login se completaba de verdad (cookie fijada, de ahí que recargar funcionara), pero nadie desapilaba el formulario. Con `go`, `/login` pasa a ser la ubicación real, el `refreshListenable` reevalúa el `redirect` al cambiar `authProvider` y la redirección a `/dashboard` ocurre sola.

Afectaba a los cuatro accesos a login que existen: el botón "Iniciar sesión" de `top_nav_shell.dart` (agregado ese mismo día) y los tres CTAs "Iniciá sesión para reservar" de `recurso_disponibilidad_sheet.dart` y `espacio_reserva_sheet.dart` — estos últimos rotos desde antes, nunca detectados porque el E2E que existe corre sobre nativo Windows y su helper `login()` navega con `irA()`/`GoRouter.go`, no tocando estos botones.

Cuarta repetición de la misma lección del proyecto: `flutter analyze` en "No issues found!" y `flutter test` en verde no dicen nada sobre si el flujo real funciona.

## `build.yaml`: `json_serializable` con `field_rename: snake`

Desde la Fase 1 hay un `app_flutter/build.yaml` que configura `field_rename: snake` para todo el proyecto — evita anotar `@JsonKey(name: 'snake_case')` campo por campo en modelos con muchos campos `snake_case` (`espacio_id`, `hora_inicio`, `horario_atencion`, etc.). Los campos Dart en `camelCase` se mapean solos al JSON `snake_case` del backend. Los modelos de la Fase 0 (una sola palabra por campo: `id`, `rol`, `espacio`) no se vieron afectados, pero cualquier campo nuevo de una sola palabra en mayúsculas especiales debe verificarse contra una respuesta real del backend.

## `usePathUrlStrategy()` (Web)

`main.dart` llama `usePathUrlStrategy()` (paquete `flutter_web_plugins`, no-op fuera de Web) para que las rutas en Web sean limpias (`/espacios/3`) en vez de con `#` (`/#/espacios/3`) — necesario para que una recarga de página o un enlace compartido a `/espacios/3` funcione, siempre que el proxy same-origin (real en Fase 6-Web, desechable mientras tanto) sirva `index.html` como fallback de SPA para rutas no-archivo.

## Toolchains nativas

**Windows: instalado y verificado (2026-08-21).** Visual Studio Build Tools 2022 (workload "Desktop development with C++" + Windows 11 SDK 10.0.26100.7705), instalado en `D:\VisualStudio` (no en `C:\`, a pedido explícito). `flutter doctor -v` reporta `[√] Visual Studio - develop Windows apps`. `flutter build windows --debug` compila y `flutter drive -d windows` corre de punta a punta contra un backend real — ver sección "E2E" más abajo. Instalación no trivial: requirió elevación UAC manual (`vs_installer.exe modify` sin admin falla en silencio), un ID de componente inválido para el SDK (`Windows10SDK.20348` no existe en el catálogo actual, usar el genérico `Windows10SDK` y dejar que el instalador resuelva a la versión 11 vigente), y seleccionar el **workload completo** "Desktop development with C++" desde la pestaña Workloads del instalador gráfico en vez de componentes individuales (una selección manual por componentes individuales dejó fuera el compilador MSVC y CMake).

**Android: sigue sin instalar** (Android Studio/SDK, decisión explícita, se difiere para no bloquear con descargas grandes). El target queda escrito pero sin verificar en ejecución real — solo pasa `flutter analyze`/`flutter test`.

## ⚠️ `http://localhost:8091` (el `flutter_proxy` de `docker-compose.yml`) apunta a `reservas_db`, NO a `reservas_test`

**El puerto por defecto pasó de 8090 a 8091 el 2026-08-24** (`FLUTTER_PROXY_PORT` en `docker-compose.yml`, junto con el default de `BACKEND_CORS_ORIGINS`): en el host de despliegue el 8090 ya estaba tomado por otro proyecto sin relación y `docker compose up` fallaba con `Bind for 0.0.0.0:8090 failed: port is already allocated`. Sigue siendo configurable por `FLUTTER_PROXY_PORT`; las menciones a `:8090` en las secciones históricas más arriba (verificaciones de Fase 6-Web, fechadas 2026-08-21) se dejaron como estaban porque describen lo que se corrió ese día.

Trampa real, fácil de pisar porque *parece* el mismo patrón same-origin usado para verificación manual en toda la Fase 0-6: `app_flutter/nginx.conf` hace `proxy_pass http://backend:8000/`, y ese `backend` es el servicio de `docker-compose.yml` cuyo `DATABASE_URL` por defecto es `reservas_db` (ver la línea `POSTGRES_DB: ${POSTGRES_DB:-reservas_db}` / `DATABASE_URL: ...db:5432/reservas_db`), **la base de desarrollo**. Nunca usar ese puerto para nada que escriba datos de prueba (fixtures, E2E, exploración con mutaciones) — es exactamente lo que la regla dura del proyecto prohíbe ("ninguna tarea asistida debe leer/escribir/migrar `reservas_db`"). Confirmado el 2026-08-21: navegar el proxy mostraba recursos ("Recurso Auditorio 1/2") que no existían en absoluto en `reservas_test` — eran datos reales de `reservas_db`.

Para cualquier verificación/E2E, usar el proxy desechable propio apuntado al backend local (ver "Cómo se verificó la Fase 0" arriba), en un puerto **distinto** al del `flutter_proxy` si el stack de Docker ya está arriba (por ejemplo 8095) para no confundir cuál es cuál.

## E2E: `integration_test` de Flutter (2026-08-21) — corrido de punta a punta en nativo Windows, ambos archivos pasan

Antes había un esqueleto de Playwright (`playwright.config.ts` + `e2e/tests/smoke/01-publico.spec.ts`) agregado por otra sesión: sin `package.json`/`node_modules` en ningún lado (no corría), con solo 2 chequeos superficiales, y el propio `ci.yml` admitía en un comentario que el job `e2e` no lo ejecutaba ("E2E Playwright de Next.js retirado..."). Se **eliminó** (`playwright.config.ts`, `e2e/`) a favor del paquete oficial `integration_test` — decisión explícita del usuario entre las dos opciones, alineada con lo que ya decía el plan de migración original antes de que apareciera el esqueleto de Playwright.

### Qué hay

- `integration_test/utils/e2e_fixtures.dart` — fixtures **por API** (login como admin de arranque + `dio`/`cookie_jar` propio, sin compartir sesión con la app que conduce el test): crea `gestor_flutter`/`usuario_e2e` si faltan, pone `horas_antelacion: 0` + `aprobacion_automatica: false` en el espacio 1 (para que "hoy" tenga franjas reservables sin tener que automatizar el `DatePicker` de Material, mucho más frágil), crea el recurso "Proyector E2E". Idempotente — no falla si ya existe.
- `integration_test/utils/e2e_actions.dart` — `irA()` (navega directo por `GoRouter.of(context).go(path)`, para llegar a un punto de partida conocido sin encadenar taps por 3-4 pantallas), `login()`/`logout()` (taps reales sobre el form), `franjaLibre()` (encuentra un `SlotChip` con `estado: libre` por **predicado del widget**, nunca por texto de hora exacto — qué franjas están libres depende de qué haya dejado ocupado una corrida anterior).
- `integration_test/publico_y_auth_test.dart` — anónimo ve `/espacios` sin sesión y sin ver "Inicio" en el nav; gestor intentando `/usuarios` (admin-only) es redirigido por el guard.
- `integration_test/reserva_flujo_test.dart` — el test insignia: `esperando -> aprobada -> cancelada` completo (usuario crea, gestor aprueba, usuario cancela). Es exactamente el ciclo donde vivía el bug real de la Fase 2 (`Reserva.puedeCancelarse` permitía cancelar `esperando`, cuando el backend solo lo permite en `aprobada`) — un widget test con providers mockeados no puede atrapar esa clase de error, hace falta la reacción real del backend a cada transición.
- `test_driver/integration_test.dart` — puente estándar para `flutter drive`.

`flutter analyze` (paquete completo, incluido `integration_test/`) queda en "No issues found!".

### Cómo correr (verificado, nativo Windows)

```bash
flutter drive \
  --driver=test_driver/integration_test.dart \
  --target=integration_test/reserva_flujo_test.dart \
  -d windows --dart-define-from-file=env/dev.json
```

Requiere el backend local corriendo contra `reservas_test` en `http://localhost:8000` (nunca `reservas_db`, ver advertencia arriba) y `reservas_test` levantada (`docker compose -f docker-compose.test.yml up -d --wait`). `E2E_BACKEND_URL`/`E2E_ADMIN_USERNAME`/`E2E_ADMIN_PASSWORD` son configurables por `--dart-define` si el admin de arranque no es `admin_flutter`/`ClaveFase0Temp123` (el que usa el resto de este documento).

**Resultado 2026-08-21**: `publico_y_auth_test.dart` (2/2, ~13s) y `reserva_flujo_test.dart` (1/1, ~38s, ciclo completo `esperando → aprobada → cancelada`) pasan enteros contra Visual Studio Build Tools 2022 recién instalado (workload "Desktop development with C++" + Windows 11 SDK) — primera ejecución automatizada real de esta suite en la historia del proyecto.

### El gap de Web sigue vigente (no bloqueante — nativo cubre el harness)

`flutter drive` para Web no soporta `--use-existing-app` (confirmado 2026-08-21: `--use-existing-app is not supported with flutter web driver`). Solo sabe lanzar su propio dev-server efímero, en un origen distinto al build real servido por un proxy same-origin, y ese dev-server efímero no sirve: el backend tiene `allow_credentials=False` en `CORSMiddleware` **a propósito** (`backend/app/main.py`, comentario explícito: "el backend nunca autoriza credenciales cross-origin de navegador") — sin eso, ninguna llamada con cookie sobrevive el CORS del navegador contra un origen distinto. No es negociable tocar esa política sin aprobación aparte — no se tocó, y no hace falta: nativo (Windows, y en teoría macOS/Linux) no está sujeto a este problema en absoluto (usa `cookie_jar` propio, no navegador), y ya es el harness que corre en esta máquina.

### Cinco bugs reales que encontró la corrida (ninguno lo atrapó `flutter analyze`/`flutter test`)

1. **`flutter drive --target=integration_test/x.dart` reemplaza el entrypoint entero.** El `main()` de `lib/main.dart` nunca se ejecutaba solo — hacía falta un helper `iniciarApp(tester)` en `e2e_actions.dart` que importa y llama al `main()` real (`app_main.main()`) al principio de cada `testWidgets`. Sin esto, `find.byType(MaterialApp)` fallaba con `Bad state: No element` porque el árbol de widgets estaba genuinamente vacío.
2. **`GoRouter.of(context)` no funciona con el contexto de `MaterialApp`.** Con `MaterialApp.router`, el `InheritedGoRouter` que expone `GoRouter.of` lo inserta el `Router` interno **por debajo** de `MaterialApp` en el árbol — buscar `.of(context)` desde el propio elemento de `MaterialApp` mira hacia arriba, nunca hacia abajo, y falla con `No GoRouter found in context`. `irA()` ahora toma el contexto de `find.byType(Scaffold).first` (toda pantalla de la app tiene un `Scaffold`).
3. **`EmptyView`/`_GrillaEsquematica` (`core/widgets/empty_view.dart:94`) tenía un overflow real de 4px.** 4 columnas de 26px con `margin: right 4` en las **cuatro** (no solo entre ellas) suman 120px dentro de un `SizedBox` de 116px — el ancho correcto para 4 celdas con 3 separaciones intermedias, no 4. `flutter analyze`/`flutter test` nunca lo vieron porque ningún widget test monta `EmptyView` con ancho acotado; el E2E lo disparó apenas arrancó la app (estado vacío transitorio de alguna lista mientras carga). Fix: sin margen en la última columna (`margin: EdgeInsets.only(right: col < 3 ? 4 : 0)`).
4. **Una corrida interrumpida deja la sesión colgada para la siguiente.** En nativo la sesión vive en un `cookie_jar` en disco — si una corrida anterior falla en un `expect` ANTES de llegar a su propio `logout()` final, la sesión de ese usuario sigue viva. La siguiente corrida entonces arranca ya autenticada, el guard del router redirige lejos de `/login`, y `login()` no encontraba ningún `TextFormField`. Fix en `e2e_actions.dart`: `login()` detecta la ausencia de campos, llama a `logout()` primero, y reintenta — la suite se recupera sola en vez de arrastrar el problema a corridas siguientes.
5. **`expect(find.text('Cancelada'), findsOneWidget)` no es idempotente entre corridas.** La fixture nunca purga reservas de corridas anteriores (mismo principio ya documentado para `franjaLibre()`), así que tras varias ejecuciones hay varias reservas "Cancelada" en pantalla, no una sola. Cambiado a `findsWidgets` — lo que importa es que la transición haya ocurrido, no cuántas acumule el historial.

Lección repetida (ya van tres veces en este proyecto — Fase 2, Fase 6, y ahora E2E): `flutter analyze` limpio y `flutter test` en verde no garantizan que el flujo real funcione. Solo correr la app de verdad contra un backend real lo confirma.

### Pendiente

- Un cuarto archivo con CRUD real de recursos vía UI (crear/editar/eliminar en `GestionRecursosScreen`) quedó fuera de este pase por presupuesto de tiempo, no por dificultad — el patrón para escribirlo ya está establecido en los archivos existentes.
- Wiring de CI (`ci.yml`) para ejecutar esto de verdad — hoy el job `e2e` solo hace un smoke de que `build/web/index.html` exista. Bloqueado por infraestructura, no por el test: CI corre en `ubuntu-latest`, sin Visual Studio, y el harness que funciona hoy es nativo Windows — requeriría cambiar (o añadir) un runner Windows en `ci.yml`.
- macOS/Linux nativos no se probaron (sin esas plataformas disponibles en esta máquina) — en teoría corren igual que Windows (mismo `cookie_jar`, sin navegador de por medio), pero no está confirmado.

## Comandos

```bash
flutter analyze
flutter test
flutter pub run build_runner build   # tras tocar modelos freezed/json o providers @riverpod (--delete-conflicting-outputs ya no existe en este build_runner, se ignora)
flutter run -d chrome --dart-define-from-file=env/dev.json        # nota: login chocará con CORS sin el proxy same-origin (ver arriba)
flutter drive --driver=test_driver/integration_test.dart --target=integration_test/reserva_flujo_test.dart -d windows --dart-define-from-file=env/dev.json   # verificado, ver sección E2E arriba
```

### Buildear la Web en un host SIN Flutter instalado (servidor de despliegue)

`flutter_proxy` sirve `build/web` como volumen: si esa carpeta no existe, nginx responde **403 Forbidden** (no 404) y parece un problema de permisos del proxy cuando en realidad no hay nada que servir. El servidor de despliegue no tiene el SDK, así que el build se hace en un contenedor descartable con el SDK oficial:

```bash
docker run --rm -v "$PWD:/app" -w /app ubuntu:24.04 bash -c '
set -e
apt-get update -qq
apt-get install -y -qq curl xz-utils git ca-certificates > /dev/null
curl -sSL --retry 5 --retry-delay 3 --speed-time 20 --speed-limit 5000 \
  https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.47.1-stable.tar.xz -o /tmp/flutter.tar.xz
tar -xJf /tmp/flutter.tar.xz -C /opt
export PATH="$PATH:/opt/flutter/bin"
git config --global --add safe.directory /opt/flutter
git config --global --add safe.directory /app
flutter config --no-analytics --no-cli-animations
flutter build web --dart-define-from-file=env/web.json
'
```

Detalles que costaron tiempo la primera vez (2026-08-24):

- **No usar `ghcr.io/cirruslabs/flutter`**: no publica un tag `3.47.1`, y su `latest` traía Dart 3.12.0 mientras `pubspec.yaml` exige `^3.13.1` → "version solving failed". El SDK oficial versionado evita depender de que un tag de terceros esté al día.
- **Los flags `--retry`/`--speed-time`/`--speed-limit` del `curl` no son decorativos**: sin ellos, una descarga estancada (pasó: se cortó en 257MB de ~1GB y quedó colgada indefinidamente, con el enlace del host a 37MB/s) deja el contenedor esperando para siempre sin imprimir nada. Toda la fase previa a `flutter config` es silenciosa, así que "no pasa nada en pantalla" es indistinguible de un cuelgue — diagnóstico: `docker exec <id> ls -la /tmp/flutter.tar.xz` dos veces y ver si el tamaño crece.
- **Desde Git Bash en Windows** hay que anteponer `MSYS_NO_PATHCONV=1`, o convierte `/app` a una ruta de Windows y `docker run` falla con "working directory ... is invalid".
- **Efecto colateral en Windows**: correr esto sobre un checkout Windows reescribe `*/flutter/generated_plugin_registrant.*` y `generated_plugins.cmake` con fin de línea LF. El diff es solo de line-endings; descartarlo (`git checkout --`) antes de commitear.
