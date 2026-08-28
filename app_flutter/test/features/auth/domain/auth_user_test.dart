import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/core/domain/enums.dart';
import 'package:app_flutter/features/auth/domain/auth_user.dart';

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

void main() {
  group('AuthUser.perfilCompleto', () {
    test('false cuando todos los campos están vacíos (usuario recién invitado)', () {
      expect(_usuario().perfilCompleto, isFalse);
    });

    test('false si falta un solo campo', () {
      final usuario = _usuario(
        documentoIdentificacion: '123',
        telefono: '3000000000',
        institucion: 'ITM',
        vinculacion: VinculacionUsuario.estudiante,
        // dependencia queda sin completar
      );
      expect(usuario.perfilCompleto, isFalse);
    });

    test('false si un campo de texto está en blanco (solo espacios)', () {
      final usuario = _usuario(
        documentoIdentificacion: '123',
        telefono: '3000000000',
        institucion: '   ',
        vinculacion: VinculacionUsuario.estudiante,
        dependencia: 'Ingeniería',
      );
      expect(usuario.perfilCompleto, isFalse);
    });

    test('true cuando los 5 campos están completos', () {
      final usuario = _usuario(
        documentoIdentificacion: '123',
        telefono: '3000000000',
        institucion: 'ITM',
        vinculacion: VinculacionUsuario.estudiante,
        dependencia: 'Ingeniería',
      );
      expect(usuario.perfilCompleto, isTrue);
    });
  });
}
