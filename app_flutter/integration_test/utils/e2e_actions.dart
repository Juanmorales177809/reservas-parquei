import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

import 'package:app_flutter/core/domain/enums.dart';
import 'package:app_flutter/core/router/app_routes.dart';
import 'package:app_flutter/features/laboratorios/presentation/slot_chip.dart';
import 'package:app_flutter/main.dart' as app_main;
import 'package:app_flutter/shell/session_menu.dart';

/// Arranca la app real.
///
/// `flutter drive --target=integration_test/x_test.dart` **reemplaza el
/// entrypoint entero**: el `main()` de `lib/main.dart` nunca se ejecuta
/// solo, no hay "la app ya corriendo en paralelo" — el `main()` de este
/// archivo de test literalmente ES el entrypoint del proceso. Sin llamar
/// al `main()` real acá, `runApp(ReservasApp())` nunca se invoca y el
/// árbol de widgets queda vacío: `find.byType(MaterialApp)` falla con
/// `Bad state: No element`, no por un problema de timing sino porque
/// nunca hubo nada que encontrar. Encontrado corriendo esto de verdad
/// contra Windows nativo por primera vez — `flutter analyze` no lo
/// atrapa, porque el código compila perfectamente.
///
/// Llamar una vez al principio de cada `testWidgets` (no una sola vez
/// para todo el archivo): cada llamada rearma `AppConfig`/`Dio`/
/// `ProviderContainer` desde cero, tal como un reinicio real de la app —
/// la sesión persiste entre esos "reinicios" porque en nativo la cookie
/// vive en un `cookie_jar` en disco, no en memoria.
Future<void> iniciarApp(WidgetTester tester) async {
  await app_main.main();
  await tester.pumpAndSettle();
}

/// Navega directo por ruta usando el `GoRouter` de la app ya montada.
///
/// Más robusto que encadenar taps por 3-4 pantallas solo para llegar a un
/// punto de partida conocido — y el guard de rol/sesión de
/// `app_router.dart` sigue aplicando igual (esto no lo esquiva, solo evita
/// tener que simular cada tap intermedio). Las interacciones que
/// realmente importa probar (login, elegir franja, aprobar, cancelar...)
/// se hacen con taps reales sobre widgets reales, nunca con esto.
///
/// Requiere que [iniciarApp] ya se haya llamado en este test.
///
/// El contexto se toma de un `Scaffold`, no de `MaterialApp`: con
/// `MaterialApp.router`, el `InheritedGoRouter` que expone `GoRouter.of`
/// lo inserta el `Router` **por debajo** de `MaterialApp` en el árbol —
/// buscar `.of(context)` desde el propio elemento de `MaterialApp` mira
/// hacia arriba, nunca hacia abajo, y falla con "No GoRouter found in
/// context". Cada pantalla de esta app (login, o cualquier destino
/// envuelto por un shell) siempre tiene un `Scaffold`, así que sirve como
/// punto de entrada estable sin importar la ruta actual.
Future<void> irA(WidgetTester tester, String path) async {
  final context = tester.element(find.byType(Scaffold).first);
  GoRouter.of(context).go(path);
  await tester.pumpAndSettle();
}

/// Login real: escribe usuario/clave y toca "Entrar", como haría una
/// persona. `AppRoutes.login` está fuera del `ShellRoute`, así que
/// funciona sin importar qué pantalla estaba abierta antes.
///
/// Si una corrida anterior de la suite quedó interrumpida ANTES de su
/// propio `logout()` (por ejemplo, un `expect` que falló a mitad de
/// camino), la sesión sigue viva en el `cookie_jar` nativo en disco — ver
/// [iniciarApp]. Esta app entonces arranca ya autenticada y el guard de
/// `app_router.dart` redirige lejos de `/login` en vez de mostrar el
/// formulario, así que no hay `TextFormField` que encontrar. Se detecta
/// ese caso y se cierra esa sesión colgada antes de reintentar, para que
/// la suite se recupere sola en vez de arrastrar el problema a todos los
/// tests siguientes.
Future<void> login(WidgetTester tester, {required String usuario, required String clave}) async {
  await irA(tester, AppRoutes.login);

  if (find.byType(TextFormField).evaluate().isEmpty) {
    await logout(tester);
    await irA(tester, AppRoutes.login);
  }

  final campos = find.byType(TextFormField);
  expect(campos, findsNWidgets(2), reason: 'LoginScreen debería tener exactamente 2 campos (usuario, contraseña).');
  await tester.enterText(campos.at(0), usuario);
  await tester.enterText(campos.at(1), clave);
  await tester.pumpAndSettle();

  await tester.tap(find.widgetWithText(FilledButton, 'Entrar'));
  // El login real hace un roundtrip HTTP + la redirección de go_router;
  // 2s da margen sin depender de un número exacto de frames.
  await tester.pumpAndSettle(const Duration(seconds: 2));
}

/// El logout vive en el [SessionMenu] de la `AppBar`, que montan los tres
/// shells (bottom/rail/top), así que sirve en cualquier ancho de ventana y
/// desde cualquier pantalla con shell — no hace falta navegar antes.
///
/// Hasta 2026-08-24 estaba en `InicioScreen`, que era el único lugar de la
/// app con botón de logout; esa pantalla se eliminó cuando el inicio pasó a
/// ser el dashboard.
Future<void> logout(WidgetTester tester) async {
  await tester.tap(find.byType(SessionMenu));
  await tester.pumpAndSettle();
  await tester.tap(find.widgetWithText(MenuItemButton, 'Cerrar sesión'));
  await tester.pumpAndSettle(const Duration(seconds: 1));
}

/// Primer chip de franja horaria realmente reservable (`estado: libre` y
/// con `onTap` — `SlotChip` no monta `InkWell` cuando no es tocable).
///
/// Nunca por texto de hora exacto ("07:00–08:00"): qué franjas están
/// libres depende de qué haya dejado ocupado una corrida anterior de este
/// mismo archivo, así que el texto exacto no es estable entre corridas.
Finder franjaLibre() {
  return find.byWidgetPredicate((w) => w is SlotChip && w.estado == EstadoSlot.libre && w.onTap != null);
}
