import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/core/network/api_exception.dart';
import 'package:app_flutter/features/auth/data/auth_repository.dart';
import 'package:app_flutter/features/auth/presentation/login_screen.dart';

/// Fake por subclase (mismo patrón que `_AuthRepositoryFalso` usado antes
/// en `password_flows_test.dart`, retirado junto a las pantallas de
/// recuperación clásica): `solicitarRecuperacion` llama a `POST
/// /auth/recuperar` por `Dio`, así que un test de widget necesita un doble
/// que nunca dispare esa llamada de red real.
class _AuthRepositoryFalso extends AuthRepository {
  _AuthRepositoryFalso() : super(Dio());

  String? ultimoEmailSolicitado;
  Object? errorParaLanzar;

  @override
  Future<void> solicitarRecuperacion({required String email}) async {
    if (errorParaLanzar != null) throw errorParaLanzar!;
    ultimoEmailSolicitado = email;
  }
}

void main() {
  testWidgets('LoginScreen valida campos requeridos antes de llamar a la API', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(home: LoginScreen()),
      ),
    );

    expect(find.text('Reservas Parque i'), findsOneWidget);

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

  group('Recuperar contraseña', () {
    Widget montar(_AuthRepositoryFalso fake) {
      return ProviderScope(
        overrides: [authRepositoryProvider.overrideWithValue(fake)],
        child: const MaterialApp(home: LoginScreen()),
      );
    }

    testWidgets('el diálogo precarga el email ya escrito en el login', (tester) async {
      await tester.pumpWidget(montar(_AuthRepositoryFalso()));
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextFormField).first, 'ana@example.com');
      await tester.tap(find.text('¿Olvidaste tu contraseña?'));
      await tester.pumpAndSettle();

      expect(find.text('Recuperar contraseña'), findsOneWidget);
      // Dos campos "ana@example.com": el de login (detrás del diálogo) y
      // el precargado en el diálogo.
      expect(find.text('ana@example.com'), findsNWidgets(2));
    });

    testWidgets('exige un email con formato válido antes de enviar', (tester) async {
      final fake = _AuthRepositoryFalso();
      await tester.pumpWidget(montar(fake));
      await tester.pumpAndSettle();

      await tester.tap(find.text('¿Olvidaste tu contraseña?'));
      await tester.pumpAndSettle();

      await tester.enterText(find.byKey(const Key('recuperar_password_email')), 'no-es-un-email');
      await tester.tap(find.text('Enviar'));
      await tester.pump();

      expect(find.text('Email inválido'), findsOneWidget);
      expect(fake.ultimoEmailSolicitado, isNull);
    });

    testWidgets('envía la solicitud, cierra el diálogo y muestra el mensaje genérico', (tester) async {
      final fake = _AuthRepositoryFalso();
      await tester.pumpWidget(montar(fake));
      await tester.pumpAndSettle();

      await tester.tap(find.text('¿Olvidaste tu contraseña?'));
      await tester.pumpAndSettle();

      await tester.enterText(find.byKey(const Key('recuperar_password_email')), 'ana@example.com');
      await tester.tap(find.text('Enviar'));
      await tester.pumpAndSettle();

      expect(fake.ultimoEmailSolicitado, 'ana@example.com');
      expect(find.text('Recuperar contraseña'), findsNothing);
      expect(
        find.text('Si existe una cuenta con ese email, vas a recibir un correo con instrucciones.'),
        findsOneWidget,
      );
    });

    testWidgets('muestra el error del backend si falla el envío', (tester) async {
      final fake = _AuthRepositoryFalso()..errorParaLanzar = const ApiException('Demasiados intentos.', statusCode: 429);
      await tester.pumpWidget(montar(fake));
      await tester.pumpAndSettle();

      await tester.tap(find.text('¿Olvidaste tu contraseña?'));
      await tester.pumpAndSettle();

      await tester.enterText(find.byKey(const Key('recuperar_password_email')), 'ana@example.com');
      await tester.tap(find.text('Enviar'));
      await tester.pumpAndSettle();

      expect(find.text('Demasiados intentos.'), findsOneWidget);
    });
  });
}
