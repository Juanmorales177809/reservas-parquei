import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

import 'package:app_flutter/core/domain/enums.dart';
import 'package:app_flutter/core/network/api_exception.dart';
import 'package:app_flutter/core/router/app_routes.dart';
import 'package:app_flutter/features/auth/application/auth_provider.dart';
import 'package:app_flutter/features/auth/domain/auth_user.dart';
import 'package:app_flutter/features/usuarios/data/usuarios_repository.dart';
import 'package:app_flutter/features/usuarios/presentation/mi_perfil_screen.dart';

AuthUser _usuario({
  String? documentoIdentificacion,
  String? telefono,
  String? institucion,
  VinculacionUsuario? vinculacion,
  String? dependencia,
}) =>
    AuthUser(
      id: 1,
      username: 'ana',
      email: 'ana@example.com',
      rol: RolUsuario.usuario,
      documentoIdentificacion: documentoIdentificacion,
      telefono: telefono,
      institucion: institucion,
      vinculacion: vinculacion,
      dependencia: dependencia,
    );

class _AuthFake extends Auth {
  _AuthFake(this._usuario);
  final AuthUser? _usuario;

  @override
  Future<AuthUser?> build() async => _usuario;
}

/// Fake por subclase, mismo patrón que en otras pantallas: solo
/// `actualizarMiPerfil` está bajo prueba.
class _UsuariosRepositoryFalso extends UsuariosRepository {
  _UsuariosRepositoryFalso(this._usuario) : super(Dio());

  final AuthUser _usuario;
  Map<String, dynamic>? ultimoEnvio;
  Object? errorParaLanzar;

  @override
  Future<AuthUser> actualizarMiPerfil({
    String? documentoIdentificacion,
    String? telefono,
    String? institucion,
    VinculacionUsuario? vinculacion,
    String? dependencia,
  }) async {
    if (errorParaLanzar != null) throw errorParaLanzar!;
    ultimoEnvio = {
      'documentoIdentificacion': documentoIdentificacion,
      'telefono': telefono,
      'institucion': institucion,
      'vinculacion': vinculacion,
      'dependencia': dependencia,
    };
    return _usuario.copyWith(
      documentoIdentificacion: documentoIdentificacion,
      telefono: telefono,
      institucion: institucion,
      vinculacion: vinculacion,
      dependencia: dependencia,
    );
  }
}

void main() {
  Widget montar(AuthUser usuario, _UsuariosRepositoryFalso fake) {
    return ProviderScope(
      overrides: [
        authProvider.overrideWith(() => _AuthFake(usuario)),
        usuariosRepositoryProvider.overrideWithValue(fake),
      ],
      child: const MaterialApp(home: MiPerfilScreen()),
    );
  }

  /// Con `GoRouter` real (a diferencia de `montar`) -- necesario para los
  /// casos que ejercitan `context.go(AppRoutes.admin)` tras completar el
  /// perfil obligatorio.
  Widget montarConRouter(AuthUser usuario, _UsuariosRepositoryFalso fake) {
    final router = GoRouter(
      initialLocation: AppRoutes.perfil,
      routes: [
        GoRoute(path: AppRoutes.perfil, builder: (context, state) => const MiPerfilScreen()),
        GoRoute(path: AppRoutes.admin, builder: (context, state) => const Text('ADMIN_HOME')),
      ],
    );
    return ProviderScope(
      overrides: [
        authProvider.overrideWith(() => _AuthFake(usuario)),
        usuariosRepositoryProvider.overrideWithValue(fake),
      ],
      child: MaterialApp.router(routerConfig: router),
    );
  }

  testWidgets('precarga los campos ya guardados', (tester) async {
    final usuario = _usuario(telefono: '3053695592', vinculacion: VinculacionUsuario.estudiante);
    await tester.pumpWidget(montar(usuario, _UsuariosRepositoryFalso(usuario)));
    await tester.pumpAndSettle();

    expect(find.text('3053695592'), findsOneWidget);
    expect(find.text('Estudiante'), findsOneWidget);
  });

  Future<void> llenarCamposObligatorios(WidgetTester tester) async {
    await tester.enterText(find.widgetWithText(TextFormField, 'Documento de identificación'), '123456');
    await tester.enterText(find.widgetWithText(TextFormField, 'Teléfono/celular'), '3000000000');
    await tester.enterText(find.widgetWithText(TextFormField, 'Institución a la que pertenece'), 'ITM');
    await tester.tap(find.byType(DropdownButtonFormField<VinculacionUsuario>));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Estudiante').last);
    await tester.pumpAndSettle();
    await tester.enterText(find.widgetWithText(TextFormField, 'Dependencia / Facultad'), 'Ingeniería');
  }

  testWidgets('perfil incompleto: al guardar navega a /admin en vez de quedarse en /perfil', (tester) async {
    final usuario = _usuario();
    final fake = _UsuariosRepositoryFalso(usuario);
    await tester.pumpWidget(montarConRouter(usuario, fake));
    await tester.pumpAndSettle();

    await llenarCamposObligatorios(tester);
    await tester.tap(find.text('Guardar'));
    await tester.pumpAndSettle();

    expect(fake.ultimoEnvio?['telefono'], '3000000000');
    expect(find.text('ADMIN_HOME'), findsOneWidget);
    expect(find.byType(MiPerfilScreen), findsNothing);
  });

  testWidgets('perfil ya completo: guardar una edición muestra el snackbar y no navega', (tester) async {
    final usuario = _usuario(
      documentoIdentificacion: '111',
      telefono: '3000000000',
      institucion: 'ITM',
      vinculacion: VinculacionUsuario.estudiante,
      dependencia: 'Ingeniería',
    );
    final fake = _UsuariosRepositoryFalso(usuario);
    await tester.pumpWidget(montarConRouter(usuario, fake));
    await tester.pumpAndSettle();

    await tester.enterText(find.widgetWithText(TextFormField, 'Teléfono/celular'), '3001112222');
    await tester.tap(find.text('Guardar'));
    await tester.pumpAndSettle();

    expect(fake.ultimoEnvio?['telefono'], '3001112222');
    expect(find.text('Perfil actualizado.'), findsOneWidget);
    expect(find.text('ADMIN_HOME'), findsNothing);
  });

  testWidgets('muestra el error del backend si falla el guardado', (tester) async {
    final usuario = _usuario();
    final fake = _UsuariosRepositoryFalso(usuario)
      ..errorParaLanzar = const ApiException('No se pudo actualizar.', statusCode: 500);
    await tester.pumpWidget(montar(usuario, fake));
    await tester.pumpAndSettle();

    await llenarCamposObligatorios(tester);
    await tester.tap(find.text('Guardar'));
    await tester.pumpAndSettle();

    expect(find.text('No se pudo actualizar.'), findsOneWidget);
  });

  testWidgets('con campos vacíos, Guardar no envía nada (los 5 son obligatorios)', (tester) async {
    final usuario = _usuario();
    final fake = _UsuariosRepositoryFalso(usuario);
    await tester.pumpWidget(montar(usuario, fake));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Guardar'));
    await tester.pumpAndSettle();

    expect(fake.ultimoEnvio, isNull);
    expect(find.text('Requerido'), findsWidgets);
  });

  testWidgets('perfil incompleto muestra el texto de "antes de continuar"', (tester) async {
    final usuario = _usuario();
    await tester.pumpWidget(montar(usuario, _UsuariosRepositoryFalso(usuario)));
    await tester.pumpAndSettle();

    expect(find.textContaining('Antes de continuar'), findsOneWidget);
  });

  testWidgets('tiene un botón de Cerrar sesión como salida', (tester) async {
    final usuario = _usuario();
    await tester.pumpWidget(montar(usuario, _UsuariosRepositoryFalso(usuario)));
    await tester.pumpAndSettle();

    expect(find.byTooltip('Cerrar sesión'), findsOneWidget);
  });
}
