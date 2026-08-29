import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/features/auth/presentation/registro_screen.dart';

/// Mismo alcance que `login_screen_test.dart`: solo valida las reglas del
/// formulario del lado del cliente, no un envío exitoso -- eso requeriría
/// mockear `Supabase.instance.client.auth.signInWithPassword` (llamado
/// dentro de `AuthRepository.registrarse` vía `login`), que no es
/// inyectable en este nivel, mismo motivo por el que `LoginScreen` tampoco
/// tiene un test de éxito real.
void main() {
  Future<void> montar(WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(home: RegistroScreen()),
      ),
    );
    await tester.pumpAndSettle();
  }

  testWidgets('valida los 4 campos requeridos antes de llamar a la API', (tester) async {
    await montar(tester);

    await tester.tap(find.widgetWithText(FilledButton, 'Crear cuenta'));
    await tester.pump();

    expect(find.text('Requerido'), findsNWidgets(4));
  });

  testWidgets('exige un nombre de usuario de al menos 3 caracteres', (tester) async {
    await montar(tester);

    await tester.enterText(find.widgetWithText(TextFormField, 'Nombre de usuario'), 'ab');
    await tester.enterText(find.widgetWithText(TextFormField, 'Email'), 'ana@example.com');
    await tester.enterText(find.widgetWithText(TextFormField, 'Contraseña'), 'clave1234');
    await tester.enterText(find.widgetWithText(TextFormField, 'Confirmar contraseña'), 'clave1234');

    await tester.tap(find.widgetWithText(FilledButton, 'Crear cuenta'));
    await tester.pump();

    expect(find.text('Mínimo 3 caracteres'), findsOneWidget);
  });

  testWidgets('exige un email con formato válido', (tester) async {
    await montar(tester);

    await tester.enterText(find.widgetWithText(TextFormField, 'Nombre de usuario'), 'ana');
    await tester.enterText(find.widgetWithText(TextFormField, 'Email'), 'no-es-un-email');
    await tester.enterText(find.widgetWithText(TextFormField, 'Contraseña'), 'clave1234');
    await tester.enterText(find.widgetWithText(TextFormField, 'Confirmar contraseña'), 'clave1234');

    await tester.tap(find.widgetWithText(FilledButton, 'Crear cuenta'));
    await tester.pump();

    expect(find.text('Email inválido'), findsOneWidget);
  });

  testWidgets('exige contraseña de al menos 8 caracteres', (tester) async {
    await montar(tester);

    await tester.enterText(find.widgetWithText(TextFormField, 'Nombre de usuario'), 'ana');
    await tester.enterText(find.widgetWithText(TextFormField, 'Email'), 'ana@example.com');
    await tester.enterText(find.widgetWithText(TextFormField, 'Contraseña'), 'corta');
    await tester.enterText(find.widgetWithText(TextFormField, 'Confirmar contraseña'), 'corta');

    await tester.tap(find.widgetWithText(FilledButton, 'Crear cuenta'));
    await tester.pump();

    expect(find.text('Mínimo 8 caracteres'), findsOneWidget);
  });

  testWidgets('exige que las contraseñas coincidan', (tester) async {
    await montar(tester);

    await tester.enterText(find.widgetWithText(TextFormField, 'Nombre de usuario'), 'ana');
    await tester.enterText(find.widgetWithText(TextFormField, 'Email'), 'ana@example.com');
    await tester.enterText(find.widgetWithText(TextFormField, 'Contraseña'), 'clave1234');
    await tester.enterText(find.widgetWithText(TextFormField, 'Confirmar contraseña'), 'otraClave1234');

    await tester.tap(find.widgetWithText(FilledButton, 'Crear cuenta'));
    await tester.pump();

    expect(find.text('Las contraseñas no coinciden'), findsOneWidget);
  });
}
