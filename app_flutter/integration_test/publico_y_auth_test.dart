import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'utils/e2e_actions.dart';
import 'utils/e2e_fixtures.dart';

/// Corre contra la app YA BUILDEADA Y SERVIDA (no contra un dev-server
/// nuevo):
///
/// ```
/// flutter drive \
///   --driver=test_driver/integration_test.dart \
///   --target=integration_test/publico_y_auth_test.dart \
///   -d chrome --use-existing-app=http://localhost:8090
/// ```
///
/// Así se prueba el artefacto real (mismo proxy same-origin que
/// producción), no una versión recompilada aparte para el test — y la
/// cookie de sesión funciona porque es genuinamente same-origin. Ver "Cómo
/// correr el E2E" en `app_flutter/CLAUDE.md`.
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(asegurarFixturesE2e);

  group('Público y guard de rol', () {
    testWidgets('un visitante anónimo ve /espacios sin que lo redirijan a /login', (tester) async {
      irA(tester, '/espacios');
      await tester.pumpAndSettle();

      expect(find.text('Elegí un espacio para ver sus recursos y disponibilidad'), findsOneWidget);
      // Sin sesión, "Inicio" no debe verse: `NavDestinationSpec` para
      // 'inicio' no declara `requiereSesion: false`, así que por defecto
      // exige sesión — solo "Espacios" es público (ver nav_destinations.dart).
      expect(find.text('Inicio'), findsNothing);
    });

    testWidgets('un gestor no puede entrar a /usuarios (admin-only): el guard lo redirige', (tester) async {
      await login(tester, usuario: gestorE2eUsername, clave: gestorE2ePassword);

      irA(tester, '/usuarios');
      await tester.pumpAndSettle();

      // `app_router.dart` redirige a /espacios cuando el rol no coincide
      // con `rolesPermitidos` del destino — la pantalla de gestión de
      // usuarios no debe llegar a mostrarse.
      expect(find.text('Elegí un espacio para ver sus recursos y disponibilidad'), findsOneWidget);

      await logout(tester);
    });
  });
}
