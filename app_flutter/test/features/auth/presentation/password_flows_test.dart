import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

import 'package:app_flutter/core/network/api_exception.dart';
import 'package:app_flutter/core/router/app_routes.dart';
import 'package:app_flutter/features/auth/application/auth_provider.dart';
import 'package:app_flutter/features/auth/data/auth_repository.dart';
import 'package:app_flutter/features/auth/domain/auth_user.dart';
import 'package:app_flutter/features/auth/presentation/cambiar_password_temporal_screen.dart';
import 'package:app_flutter/features/auth/presentation/login_screen.dart';
import 'package:app_flutter/features/auth/presentation/recuperar_password_screen.dart';
import 'package:app_flutter/features/auth/presentation/restablecer_password_screen.dart';

/// Fake por subclase (mismo patrón que `_AuthFalsa` en
/// `test/shell/session_menu_test.dart`): estas pantallas llaman al
/// repositorio/notifier directamente, así que se sobreescribe con un doble
/// en vez de tocar la red.
class _AuthRepositoryFalso extends AuthRepository {
  _AuthRepositoryFalso() : super(Dio());

  String? ultimoIdentificadorSolicitado;
  Map<String, String>? ultimoRestablecimiento;
  Object? errorParaLanzar;

  @override
  Future<void> solicitarRecuperacion({required String identificador}) async {
    if (errorParaLanzar != null) throw errorParaLanzar!;
    ultimoIdentificadorSolicitado = identificador;
  }

  @override
  Future<void> restablecerPassword({
    required String identificador,
    required String codigo,
    required String passwordNueva,
  }) async {
    if (errorParaLanzar != null) throw errorParaLanzar!;
    ultimoRestablecimiento = {'identificador': identificador, 'codigo': codigo, 'passwordNueva': passwordNueva};
  }
}

const _usuarioAutenticado = AuthUser(
  id: 1,
  username: 'nuevo_usuario',
  email: 'nuevo@example.com',
  rol: RolUsuario.usuario,
  debeCambiarPassword: true,
);

class _AuthFalsaParaCambio extends Auth {
  _AuthFalsaParaCambio();

  Map<String, String>? ultimoCambio;
  bool logoutLlamado = false;
  Object? errorParaLanzar;

  @override
  Future<AuthUser?> build() async => _usuarioAutenticado;

  @override
  Future<void> cambiarPassword({required String passwordActual, required String passwordNueva}) async {
    if (errorParaLanzar != null) throw errorParaLanzar!;
    ultimoCambio = {'passwordActual': passwordActual, 'passwordNueva': passwordNueva};
  }

  @override
  Future<void> logout() async {
    logoutLlamado = true;
  }
}

void main() {
  group('LoginScreen', () {
    testWidgets('muestra el link a recuperar contraseña', (tester) async {
      await tester.pumpWidget(const ProviderScope(child: MaterialApp(home: LoginScreen())));
      expect(find.text('¿Olvidaste tu contraseña?'), findsOneWidget);
      await tester.pumpAndSettle();
    });
  });

  group('RecuperarPasswordScreen', () {
    Widget montar(_AuthRepositoryFalso fake) {
      final router = GoRouter(
        initialLocation: '/',
        routes: [
          GoRoute(path: '/', builder: (_, _) => const RecuperarPasswordScreen()),
          GoRoute(path: AppRoutes.restablecer, builder: (_, state) => Text('restablecer:${state.extra}')),
          GoRoute(path: AppRoutes.login, builder: (_, _) => const Text('pantalla de login')),
        ],
      );
      return ProviderScope(
        overrides: [authRepositoryProvider.overrideWithValue(fake)],
        child: MaterialApp.router(routerConfig: router),
      );
    }

    testWidgets('exige el identificador antes de enviar', (tester) async {
      final fake = _AuthRepositoryFalso();
      await tester.pumpWidget(montar(fake));
      await tester.tap(find.text('Enviar código'));
      await tester.pump();
      expect(find.text('Requerido'), findsOneWidget);
      expect(fake.ultimoIdentificadorSolicitado, isNull);
    });

    testWidgets('solicita la recuperación y navega a restablecer con el identificador', (tester) async {
      final fake = _AuthRepositoryFalso();
      await tester.pumpWidget(montar(fake));
      await tester.enterText(find.byType(TextFormField), 'ana');
      await tester.tap(find.text('Enviar código'));
      await tester.pumpAndSettle();

      expect(fake.ultimoIdentificadorSolicitado, 'ana');
      expect(find.text('restablecer:ana'), findsOneWidget);
    });

    testWidgets('muestra el error del backend si la solicitud falla', (tester) async {
      final fake = _AuthRepositoryFalso()..errorParaLanzar = const ApiException('Demasiados intentos.', statusCode: 429);
      await tester.pumpWidget(montar(fake));
      await tester.enterText(find.byType(TextFormField), 'ana');
      await tester.tap(find.text('Enviar código'));
      await tester.pumpAndSettle();

      expect(find.text('Demasiados intentos.'), findsOneWidget);
    });
  });

  group('RestablecerPasswordScreen', () {
    Widget montar(_AuthRepositoryFalso fake, {String? identificadorInicial}) {
      final router = GoRouter(
        initialLocation: '/',
        routes: [
          GoRoute(
            path: '/',
            builder: (_, _) => RestablecerPasswordScreen(identificadorInicial: identificadorInicial),
          ),
          GoRoute(path: AppRoutes.login, builder: (_, _) => const Text('pantalla de login')),
        ],
      );
      return ProviderScope(
        overrides: [authRepositoryProvider.overrideWithValue(fake)],
        child: MaterialApp.router(routerConfig: router),
      );
    }

    testWidgets('precarga el identificador recibido, sigue siendo editable', (tester) async {
      await tester.pumpWidget(montar(_AuthRepositoryFalso(), identificadorInicial: 'ana'));
      final campo = tester.widget<TextFormField>(find.byType(TextFormField).first);
      expect(campo.controller!.text, 'ana');
    });

    testWidgets('valida los tres campos y el largo del código', (tester) async {
      final fake = _AuthRepositoryFalso();
      await tester.pumpWidget(montar(fake));
      await tester.enterText(find.byType(TextFormField).at(1), '123');
      // find.text a secas es ambiguo: el AppBar y el botón comparten texto.
      await tester.tap(find.widgetWithText(FilledButton, 'Restablecer contraseña'));
      await tester.pump();

      expect(find.text('Requerido'), findsNWidgets(2)); // identificador y contraseña
      expect(find.text('Debe tener 6 dígitos'), findsOneWidget);
      expect(fake.ultimoRestablecimiento, isNull);
    });

    testWidgets('restablece y navega al login', (tester) async {
      final fake = _AuthRepositoryFalso();
      await tester.pumpWidget(montar(fake, identificadorInicial: 'ana'));
      await tester.enterText(find.byType(TextFormField).at(1), '123456');
      await tester.enterText(find.byType(TextFormField).at(2), 'nuevaClave2');
      // find.text a secas es ambiguo: el AppBar y el botón comparten texto.
      await tester.tap(find.widgetWithText(FilledButton, 'Restablecer contraseña'));
      await tester.pumpAndSettle();

      expect(fake.ultimoRestablecimiento, {
        'identificador': 'ana',
        'codigo': '123456',
        'passwordNueva': 'nuevaClave2',
      });
      expect(find.text('pantalla de login'), findsOneWidget);
    });

    testWidgets('código inválido muestra el error del backend', (tester) async {
      final fake = _AuthRepositoryFalso()..errorParaLanzar = const ApiException('Código inválido o vencido', statusCode: 400);
      await tester.pumpWidget(montar(fake, identificadorInicial: 'ana'));
      await tester.enterText(find.byType(TextFormField).at(1), '000000');
      await tester.enterText(find.byType(TextFormField).at(2), 'nuevaClave2');
      // find.text a secas es ambiguo: el AppBar y el botón comparten texto.
      await tester.tap(find.widgetWithText(FilledButton, 'Restablecer contraseña'));
      await tester.pumpAndSettle();

      expect(find.text('Código inválido o vencido'), findsOneWidget);
    });
  });

  group('CambiarPasswordTemporalScreen', () {
    Widget montar(_AuthFalsaParaCambio fake) {
      return ProviderScope(
        overrides: [authProvider.overrideWith(() => fake)],
        child: const MaterialApp(home: CambiarPasswordTemporalScreen()),
      );
    }

    testWidgets('exige los tres campos y que coincidan', (tester) async {
      final fake = _AuthFalsaParaCambio();
      await tester.pumpWidget(montar(fake));
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextFormField).at(1), 'nuevaClave2');
      await tester.enterText(find.byType(TextFormField).at(2), 'otraClave3');
      // find.text a secas es ambiguo: el AppBar y el botón comparten texto.
      await tester.tap(find.widgetWithText(FilledButton, 'Cambiar contraseña'));
      await tester.pump();

      expect(find.text('Requerido'), findsOneWidget); // contraseña temporal
      expect(find.text('No coincide'), findsOneWidget);
      expect(fake.ultimoCambio, isNull);
    });

    testWidgets('cambio exitoso llama al notifier con los valores correctos', (tester) async {
      final fake = _AuthFalsaParaCambio();
      await tester.pumpWidget(montar(fake));
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextFormField).at(0), 'temporalX1');
      await tester.enterText(find.byType(TextFormField).at(1), 'nuevaClave2');
      await tester.enterText(find.byType(TextFormField).at(2), 'nuevaClave2');
      // find.text a secas es ambiguo: el AppBar y el botón comparten texto.
      await tester.tap(find.widgetWithText(FilledButton, 'Cambiar contraseña'));
      await tester.pumpAndSettle();

      expect(fake.ultimoCambio, {'passwordActual': 'temporalX1', 'passwordNueva': 'nuevaClave2'});
    });

    testWidgets('password actual incorrecta muestra el error del backend', (tester) async {
      final fake = _AuthFalsaParaCambio()
        ..errorParaLanzar = const ApiException('La contraseña actual es incorrecta', statusCode: 401);
      await tester.pumpWidget(montar(fake));
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextFormField).at(0), 'incorrecta');
      await tester.enterText(find.byType(TextFormField).at(1), 'nuevaClave2');
      await tester.enterText(find.byType(TextFormField).at(2), 'nuevaClave2');
      // find.text a secas es ambiguo: el AppBar y el botón comparten texto.
      await tester.tap(find.widgetWithText(FilledButton, 'Cambiar contraseña'));
      await tester.pumpAndSettle();

      expect(find.text('La contraseña actual es incorrecta'), findsOneWidget);
    });

    testWidgets('el boton de cerrar sesion llama a logout', (tester) async {
      final fake = _AuthFalsaParaCambio();
      await tester.pumpWidget(montar(fake));
      await tester.pumpAndSettle();

      await tester.tap(find.text('Cerrar sesión'));
      await tester.pump();

      expect(fake.logoutLlamado, isTrue);
    });
  });
}
