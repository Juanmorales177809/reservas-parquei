import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/features/auth/application/auth_provider.dart';
import 'package:app_flutter/features/auth/domain/auth_user.dart';
import 'package:app_flutter/shell/app_shell.dart';
import 'package:app_flutter/shell/session_menu.dart';

/// Estos tests existen por dos bugs reales, opuestos y del mismo origen:
/// poner algo esencial de la sesión en UN solo shell.
///
/// 1. "Cerrar sesión" vivía solo en `InicioScreen`; al eliminarla, la app se
///    quedaba sin logout en todos los anchos.
/// 2. "Iniciar sesión" se agregó solo a `TopNavShell`, así que en celular y
///    tablet un visitante anónimo no tenía por dónde entrar.
///
/// `AppShell` elige entre bottom nav (< 600dp), rail (600–1240dp) y top nav
/// (>= 1240dp), así que se verifica en los tres.
class _AuthFalsa extends Auth {
  _AuthFalsa(this._user);

  final AuthUser? _user;

  @override
  Future<AuthUser?> build() async => _user;
}

const _gestor = AuthUser(
  id: 7,
  username: 'gestor_flutter',
  email: 'gestor_flutter@example.com',
  rol: RolUsuario.gestor,
  laboratorio: LaboratorioResumen(id: 1, nombre: 'Auditorio Principal', ubicacion: 'Bloque A'),
);

/// Anchos representativos de cada `ClaseVentana`.
const _anchos = <String, double>{
  'celular (bottom nav)': 375,
  'tablet (rail)': 800,
  'escritorio (top nav)': 1400,
};

Future<void> _montar(WidgetTester tester, {required AuthUser? usuario, required double ancho}) async {
  tester.view.physicalSize = Size(ancho, 900);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.reset);

  await tester.pumpWidget(
    ProviderScope(
      overrides: [authProvider.overrideWith(() => _AuthFalsa(usuario))],
      child: const MaterialApp(
        home: AppShell(currentPath: '/laboratorios', child: SizedBox.shrink()),
      ),
    ),
  );
  await tester.pumpAndSettle();
}

void main() {
  group('SessionMenu está en los tres anchos de ventana', () {
    _anchos.forEach((nombre, ancho) {
      testWidgets('anónimo ve el acceso a login en $nombre', (tester) async {
        await _montar(tester, usuario: null, ancho: ancho);

        expect(find.byType(SessionMenu), findsOneWidget);
        // En compacto la etiqueta se acorta a "Entrar" para no desbordar la
        // AppBar junto al BrandMark; en el resto va completa.
        final etiqueta = ancho < kCompactBreakpoint ? 'Entrar' : 'Iniciar sesión';
        expect(find.text(etiqueta), findsOneWidget);
      });

      testWidgets('autenticado ve el avatar y puede cerrar sesión en $nombre', (tester) async {
        await _montar(tester, usuario: _gestor, ancho: ancho);

        expect(find.byType(SessionMenu), findsOneWidget);
        // Sin sesión iniciada no debe ofrecerse iniciar sesión de nuevo.
        expect(find.text('Iniciar sesión'), findsNothing);
        expect(find.text('Entrar'), findsNothing);
        // La inicial del usuario hace de avatar.
        expect(find.text('G'), findsOneWidget);

        await tester.tap(find.byType(SessionMenu));
        await tester.pumpAndSettle();

        expect(find.text('Cerrar sesión'), findsOneWidget);
        expect(find.text('gestor_flutter'), findsWidgets);
      });
    });
  });
}
