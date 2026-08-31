import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/features/auth/application/auth_provider.dart';
import 'package:app_flutter/features/auth/domain/auth_user.dart';
import 'package:app_flutter/features/espacios/application/espacios_providers.dart';
import 'package:app_flutter/features/usuarios/application/usuarios_providers.dart';
import 'package:app_flutter/features/usuarios/presentation/gestion_usuarios_screen.dart';

/// Cubre la separación en dos secciones ("Personal" / "Usuarios") desde la
/// división `personal`/`usuarios` en el backend (2026-08-28, ver
/// `backend/CLAUDE.md`) -- cada sección lista de un endpoint distinto y el
/// formulario de alta muestra rol/espacio solo para personal.
void main() {
  final admin = AuthUser(id: 1, username: 'admin_flutter', email: 'admin@example.com', rol: RolUsuario.admin);
  final gestor = AuthUser(id: 2, username: 'gestor_flutter', email: 'gestor@example.com', rol: RolUsuario.gestor);
  final usuario = AuthUser(id: 7, username: 'usuario_flutter', email: 'usuario@example.com', rol: RolUsuario.usuario);

  // `find.text('Usuarios')` es ambiguo: el AppBar también se llama
  // "Usuarios" (título fijo para las dos secciones) -- hay que acotar la
  // búsqueda al SegmentedButton para tocar el segmento correcto.
  Finder segmentoUsuarios() => find.descendant(
        of: find.byType(SegmentedButton<bool>),
        matching: find.text('Usuarios'),
      );

  Widget montar() {
    return ProviderScope(
      overrides: [
        authProvider.overrideWith(() => _AuthFake(admin)),
        personalListProvider.overrideWith((ref) async => [admin, gestor]),
        usuariosListProvider.overrideWith((ref) async => [usuario]),
        espaciosListProvider.overrideWith((ref) async => []),
      ],
      child: const MaterialApp(home: GestionUsuariosScreen()),
    );
  }

  testWidgets('arranca en la sección Personal y lista admin/gestor', (tester) async {
    await tester.pumpWidget(montar());
    await tester.pumpAndSettle();

    expect(find.text('admin_flutter'), findsOneWidget);
    expect(find.text('gestor_flutter'), findsOneWidget);
    expect(find.text('usuario_flutter'), findsNothing);
  });

  testWidgets('cambiar a la sección Usuarios lista rol usuario', (tester) async {
    await tester.pumpWidget(montar());
    await tester.pumpAndSettle();

    await tester.tap(segmentoUsuarios());
    await tester.pumpAndSettle();

    expect(find.text('usuario_flutter'), findsOneWidget);
    expect(find.text('admin_flutter'), findsNothing);
    expect(find.text('gestor_flutter'), findsNothing);
  });

  testWidgets('Nuevo en Personal abre el diálogo con selector de rol', (tester) async {
    await tester.pumpWidget(montar());
    await tester.pumpAndSettle();

    await tester.tap(find.text('Nuevo'));
    await tester.pumpAndSettle();

    expect(find.text('Nuevo miembro del personal'), findsOneWidget);
    expect(find.text('Rol *'), findsOneWidget);
  });

  testWidgets('Nuevo usuario en la sección Usuarios abre el diálogo sin selector de rol', (tester) async {
    await tester.pumpWidget(montar());
    await tester.pumpAndSettle();

    await tester.tap(segmentoUsuarios());
    await tester.pumpAndSettle();
    await tester.tap(find.text('Nuevo usuario'));
    await tester.pumpAndSettle();

    expect(find.text('Nuevo usuario'), findsWidgets);
    expect(find.text('Rol *'), findsNothing);
  });

  group('GestionUsuariosScreen — búsqueda y orden (2026-08-31)', () {
    testWidgets('buscar por usuario filtra la lista', (tester) async {
      await tester.pumpWidget(montar());
      await tester.pumpAndSettle();

      expect(find.text('admin_flutter'), findsOneWidget);
      expect(find.text('gestor_flutter'), findsOneWidget);

      // "gestor_flu" (no el nombre completo): si se buscara el texto exacto
      // del usuario, el propio TextField con ese valor también matchearía
      // find.text('gestor_flutter'), dando un falso "2 widgets encontrados".
      await tester.enterText(find.byType(TextField), 'gestor_flu');
      await tester.pumpAndSettle();

      expect(find.text('gestor_flutter'), findsOneWidget);
      expect(find.text('admin_flutter'), findsNothing);
    });

    testWidgets('buscar algo que no matchea nada muestra el mensaje de sin resultados', (tester) async {
      await tester.pumpWidget(montar());
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextField), 'inexistente');
      await tester.pumpAndSettle();

      expect(find.textContaining('No se encontraron resultados'), findsOneWidget);
      expect(find.text('admin_flutter'), findsNothing);
    });

    testWidgets('tocar el header de una columna reordena las filas', (tester) async {
      await tester.pumpWidget(montar());
      await tester.pumpAndSettle();

      // Orden inicial (tal cual llega de personalListProvider): admin antes
      // que gestor.
      final adminAntes = tester.getTopLeft(find.text('admin_flutter')).dy;
      final gestorAntes = tester.getTopLeft(find.text('gestor_flutter')).dy;
      expect(adminAntes, lessThan(gestorAntes));

      await tester.tap(find.text('USUARIO'));
      await tester.pumpAndSettle();

      // Orden ascendente por username: "admin_flutter" < "gestor_flutter"
      // alfabéticamente, así que el orden visual no cambia con este dataset
      // -- tocar de nuevo invierte a descendente y sí se nota el cambio.
      await tester.tap(find.text('USUARIO'));
      await tester.pumpAndSettle();

      final adminDespues = tester.getTopLeft(find.text('admin_flutter')).dy;
      final gestorDespues = tester.getTopLeft(find.text('gestor_flutter')).dy;
      expect(gestorDespues, lessThan(adminDespues));
    });
  });
}

class _AuthFake extends Auth {
  _AuthFake(this._usuario);
  final AuthUser? _usuario;

  @override
  Future<AuthUser?> build() async => _usuario;
}
