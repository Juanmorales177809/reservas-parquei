import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

import 'package:app_flutter/core/domain/enums.dart';
import 'package:app_flutter/core/router/app_routes.dart';
import 'package:app_flutter/features/espacios/presentation/slot_chip.dart';

/// Navega directo por ruta usando el `GoRouter` de la app ya montada.
///
/// Más robusto que encadenar taps por 3-4 pantallas solo para llegar a un
/// punto de partida conocido — y el guard de rol/sesión de
/// `app_router.dart` sigue aplicando igual (esto no lo esquiva, solo evita
/// tener que simular cada tap intermedio). Las interacciones que
/// realmente importa probar (login, elegir franja, aprobar, cancelar...)
/// se hacen con taps reales sobre widgets reales, nunca con esto.
void irA(WidgetTester tester, String path) {
  final context = tester.element(find.byType(MaterialApp));
  GoRouter.of(context).go(path);
}

/// Login real: escribe usuario/clave y toca "Entrar", como haría una
/// persona. `AppRoutes.login` está fuera del `ShellRoute`, así que
/// funciona sin importar qué pantalla estaba abierta antes.
Future<void> login(WidgetTester tester, {required String usuario, required String clave}) async {
  irA(tester, AppRoutes.login);
  await tester.pumpAndSettle();

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

/// `InicioScreen` es el único lugar de la app con un botón de logout
/// visible en todos los roles (ver `shell/inicio_screen.dart`).
Future<void> logout(WidgetTester tester) async {
  irA(tester, AppRoutes.inicio);
  await tester.pumpAndSettle();
  await tester.tap(find.widgetWithText(OutlinedButton, 'Cerrar sesión'));
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
