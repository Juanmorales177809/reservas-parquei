import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/core/domain/enums.dart';
import 'package:app_flutter/core/network/api_exception.dart';
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

  testWidgets('precarga los campos ya guardados', (tester) async {
    final usuario = _usuario(telefono: '3053695592', vinculacion: VinculacionUsuario.estudiante);
    await tester.pumpWidget(montar(usuario, _UsuariosRepositoryFalso(usuario)));
    await tester.pumpAndSettle();

    expect(find.text('3053695592'), findsOneWidget);
    expect(find.text('Estudiante'), findsOneWidget);
  });

  testWidgets('guardar envía los campos actuales del formulario', (tester) async {
    final usuario = _usuario();
    final fake = _UsuariosRepositoryFalso(usuario);
    await tester.pumpWidget(montar(usuario, fake));
    await tester.pumpAndSettle();

    await tester.enterText(find.widgetWithText(TextFormField, 'Teléfono/celular'), '3000000000');
    await tester.tap(find.text('Guardar'));
    await tester.pumpAndSettle();

    expect(fake.ultimoEnvio?['telefono'], '3000000000');
    expect(find.text('Perfil actualizado.'), findsOneWidget);
  });

  testWidgets('muestra el error del backend si falla el guardado', (tester) async {
    final usuario = _usuario();
    final fake = _UsuariosRepositoryFalso(usuario)
      ..errorParaLanzar = const ApiException('No se pudo actualizar.', statusCode: 500);
    await tester.pumpWidget(montar(usuario, fake));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Guardar'));
    await tester.pumpAndSettle();

    expect(find.text('No se pudo actualizar.'), findsOneWidget);
  });
}
