import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'package:app_flutter/core/router/app_routes.dart';
import 'package:app_flutter/features/reservas/presentation/recurso_disponibilidad_sheet.dart';

import 'utils/e2e_actions.dart';
import 'utils/e2e_fixtures.dart';

/// Cubre el ciclo completo `esperando -> aprobada -> cancelada`, que es
/// exactamente donde vivía un bug real de la Fase 2: `Reserva.puedeCancelarse`
/// permitía cancelar reservas `esperando`, cuando el backend
/// (`cancelar_reserva_usuario`) solo lo permite en `aprobada` (ver
/// `app_flutter/CLAUDE.md`, sección de bugs reales de la Fase 2). Un test
/// de widget con providers mockeados no puede atrapar esa clase de error:
/// hace falta la reacción real del backend a cada transición de estado, y
/// eso es justo lo que da un E2E y no un widget test.
///
/// Corre nativo (Windows/macOS/Linux) — ver el porqué en
/// `publico_y_auth_test.dart` (misma limitación de Web, mismo motivo).
///
/// Correr con:
/// ```
/// flutter drive \
///   --driver=test_driver/integration_test.dart \
///   --target=integration_test/reserva_flujo_test.dart \
///   -d windows --dart-define-from-file=env/dev.json
/// ```
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(asegurarFixturesE2e);

  testWidgets('crear reserva (usuario) -> aprobar (gestor) -> cancelar (usuario)', (tester) async {
    await iniciarApp(tester);

    // 1) El usuario crea la reserva.
    await login(tester, usuario: usuarioE2eUsername, clave: usuarioE2ePassword);

    await irA(tester, AppRoutes.laboratorioDetalle(laboratorioE2eId));

    await tester.tap(find.text(recursoE2eNombre));
    await tester.pumpAndSettle();

    final franja = franjaLibre();
    expect(
      franja,
      findsWidgets,
      reason: 'No hay franjas libres hoy para "$recursoE2eNombre". Puede ser que una '
          'corrida anterior de este archivo haya quedado a mitad de camino (revisar '
          'reservas "esperando" en reservas_test), o que se esté corriendo después de '
          'las 19:00 (última franja del laboratorio de pruebas) — ver asegurarFixturesE2e().',
    );
    await tester.tap(franja.first);
    await tester.pumpAndSettle();

    // El botón "Reservar" del sheet de confirmación comparte texto con el
    // botón "Reservar" de la cabecera del laboratorio (flujo multi-eje) — se
    // busca específicamente dentro de `RecursoDisponibilidadSheet` para no
    // matchear ambos.
    await tester.tap(find.descendant(
      of: find.byType(RecursoDisponibilidadSheet),
      matching: find.widgetWithText(FilledButton, 'Reservar'),
    ));
    // El envío muestra un overlay de éxito (`SuccessBurst`) antes de
    // cerrarse solo — dar más margen que el pumpAndSettle por defecto.
    await tester.pumpAndSettle(const Duration(seconds: 2));

    await irA(tester, AppRoutes.misReservas);
    expect(find.text('Esperando'), findsOneWidget);
    // Esperando no se puede cancelar todavía — el botón no debe existir
    // (es exactamente la regla que antes estaba mal implementada).
    expect(find.widgetWithText(OutlinedButton, 'Cancelar'), findsNothing);

    await logout(tester);

    // 2) El gestor aprueba.
    await login(tester, usuario: gestorE2eUsername, clave: gestorE2ePassword);
    await irA(tester, AppRoutes.adminReservas);

    await tester.tap(find.widgetWithText(FilledButton, 'Aprobar').first);
    await tester.pumpAndSettle(const Duration(seconds: 1));

    await logout(tester);

    // 3) El usuario ve "Aprobada" y ahora SÍ puede cancelar.
    await login(tester, usuario: usuarioE2eUsername, clave: usuarioE2ePassword);
    await irA(tester, AppRoutes.misReservas);
    expect(find.text('Aprobada'), findsOneWidget);

    await tester.tap(find.widgetWithText(OutlinedButton, 'Cancelar'));
    await tester.pumpAndSettle();
    await tester.tap(find.widgetWithText(FilledButton, 'Cancelar reserva'));
    await tester.pumpAndSettle(const Duration(seconds: 1));

    // No `findsOneWidget`: corridas anteriores de este mismo archivo dejan
    // sus propias reservas "Cancelada" en `reservas_test` (la fixture nunca
    // las purga, igual que documenta `franjaLibre()` para las franjas
    // libres) — lo que importa es que la transición haya ocurrido, no
    // cuántas reservas canceladas acumule el historial.
    expect(find.text('Cancelada'), findsWidgets);

    await logout(tester);
  });
}
