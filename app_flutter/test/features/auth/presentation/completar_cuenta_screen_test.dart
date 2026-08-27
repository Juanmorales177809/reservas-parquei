import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/features/auth/presentation/completar_cuenta_screen.dart';

void main() {
  testWidgets('sin sesión de invitación activa, muestra el aviso en vez del formulario', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(home: CompletarCuentaScreen(haySesionActiva: () => false)),
      ),
    );

    expect(find.text('Este link ya no es válido o expiró. Volvé a abrir el link del correo de invitación, '
        'o pedile a un administrador que te reenvíe la invitación.'), findsOneWidget);
    expect(find.byType(TextFormField), findsNothing);
  });

  testWidgets('con sesión activa, valida los campos antes de intentar completar la cuenta', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(home: CompletarCuentaScreen(haySesionActiva: () => true)),
      ),
    );

    expect(find.text('Crear contraseña'), findsOneWidget);

    await tester.tap(find.text('Crear contraseña'));
    await tester.pump();

    expect(find.text('Requerido'), findsNWidgets(2));
  });

  testWidgets('rechaza cuando las contraseñas no coinciden', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(home: CompletarCuentaScreen(haySesionActiva: () => true)),
      ),
    );

    await tester.enterText(find.byType(TextFormField).first, 'contrasenaSegura1');
    await tester.enterText(find.byType(TextFormField).last, 'otraContrasena2');
    await tester.tap(find.text('Crear contraseña'));
    await tester.pump();

    expect(find.text('Las contraseñas no coinciden'), findsOneWidget);
  });
}
