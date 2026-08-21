import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'utils/e2e_actions.dart';
import 'utils/e2e_fixtures.dart';

/// Corre nativo (Windows/macOS/Linux) — evita por completo el problema de
/// cookies cross-origin que bloquea `flutter drive` en Web (ni
/// `--use-existing-app` ni un dev-server efímero funcionan ahí, ver
/// "E2E" en `app_flutter/CLAUDE.md`). En nativo la sesión vive en un
/// `cookie_jar` en disco, no en un navegador, así que no hay origen que
/// negociar:
///
/// ```
/// flutter drive \
///   --driver=test_driver/integration_test.dart \
///   --target=integration_test/publico_y_auth_test.dart \
///   -d windows --dart-define-from-file=env/dev.json
/// ```
///
/// Requiere el backend local corriendo contra `reservas_test` en
/// `http://localhost:8000` (nunca `reservas_db` — ver
/// `app_flutter/CLAUDE.md`).
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(asegurarFixturesE2e);

  group('Público y guard de rol', () {
    testWidgets('un visitante anónimo ve /espacios sin que lo redirijan a /login', (tester) async {
      await iniciarApp(tester);
      await irA(tester, '/espacios');

      expect(find.text('Elegí un espacio para ver sus recursos y disponibilidad'), findsOneWidget);
      // Sin sesión, "Inicio" no debe verse: `NavDestinationSpec` para
      // 'inicio' no declara `requiereSesion: false`, así que por defecto
      // exige sesión — solo "Espacios" es público (ver nav_destinations.dart).
      expect(find.text('Inicio'), findsNothing);
    });

    testWidgets('un gestor no puede entrar a /usuarios (admin-only): el guard lo redirige', (tester) async {
      await iniciarApp(tester);
      await login(tester, usuario: gestorE2eUsername, clave: gestorE2ePassword);

      await irA(tester, '/usuarios');

      // `app_router.dart` redirige a /espacios cuando el rol no coincide
      // con `rolesPermitidos` del destino — la pantalla de gestión de
      // usuarios no debe llegar a mostrarse.
      expect(find.text('Elegí un espacio para ver sus recursos y disponibilidad'), findsOneWidget);

      await logout(tester);
    });
  });
}
