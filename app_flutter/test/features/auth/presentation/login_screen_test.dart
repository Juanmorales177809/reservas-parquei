import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/features/auth/presentation/login_screen.dart';

void main() {
  testWidgets('LoginScreen valida campos requeridos antes de llamar a la API', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(home: LoginScreen()),
      ),
    );

    expect(find.text('Reservas Parquei'), findsOneWidget);

    await tester.tap(find.text('Entrar'));
    await tester.pump();

    expect(find.text('Requerido'), findsNWidgets(2));

    // La pantalla tiene varias animaciones de entrada (`flutter_animate`:
    // ícono, textos, tarjeta, blobs de fondo) con retrasos/duraciones de
    // hasta ~1.2s reales. `pump()` avanza un solo frame sin mover el
    // reloj falso, así que esos timers quedan "pendientes" y
    // `flutter_test` falla al terminar el test (aunque el comportamiento
    // real de la app sea correcto) si no se los deja completar.
    // `pumpAndSettle` sí avanza el reloj hasta que no queda ninguna
    // animación agendada — funciona porque ninguna es infinita
    // (`.repeat()` sin fin haría que `pumpAndSettle` nunca termine).
    await tester.pumpAndSettle();
  });
}
