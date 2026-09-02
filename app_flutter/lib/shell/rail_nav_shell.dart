import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/router/nav_destinations.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_spacing.dart';
import '../core/widgets/brand_mark.dart';
import '../features/auth/application/auth_provider.dart';
import '../features/notificaciones/presentation/notification_bell.dart';
import 'session_menu.dart';

/// Navegación lateral para el tamaño **medio** (600–1240dp): tablets,
/// ventanas a media pantalla en escritorio, Web sin maximizar.
///
/// Antes el salto era binario en 840dp — bottom nav o top nav — y eso
/// dejaba al tablet en tierra de nadie: a 800dp mostraba una barra inferior
/// pensada para un teléfono, con el resto de la pantalla vacío a los
/// costados. Material 3 define tres *window size classes*, no dos, y el
/// rail es exactamente la del medio.
///
/// A diferencia del top nav, acá **todos** los destinos entran (incluidos
/// los `primario: false`), porque la columna crece hacia abajo: no hace
/// falta esconderlos tras un menú "Gestión".
class RailNavShell extends ConsumerWidget {
  const RailNavShell({
    required this.destinos,
    required this.currentPath,
    required this.child,
    super.key,
  });

  final List<NavDestinationSpec> destinos;
  final String currentPath;
  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final autenticado = ref.watch(isAuthenticatedProvider);
    final indiceActual = destinos.indexWhere((d) => d.path == currentPath);

    return Scaffold(
      appBar: AppBar(
        title: const BrandMark(),
        actions: [
          if (autenticado) const NotificationBell(),
          // SIN `if (autenticado)`: ver el comentario en `SessionMenu`.
          const SessionMenu(),
          const SizedBox(width: AppSpacing.md),
        ],
      ),
      body: Row(
        children: [
          if (destinos.isNotEmpty)
            NavigationRail(
              // `selectedIndex` no admite un índice fuera de rango; en una
              // ruta empujada (p. ej. el detalle de un laboratorio) ningún
              // destino coincide, y en ese caso no debe marcarse ninguno.
              selectedIndex: indiceActual < 0 ? null : indiceActual,
              labelType: NavigationRailLabelType.all,
              backgroundColor: AppColors.superficie,
              onDestinationSelected: (i) {
                final destino = destinos[i];
                destino.pushed ? context.push(destino.path) : context.go(destino.path);
              },
              destinations: [
                for (final d in destinos)
                  NavigationRailDestination(
                    icon: Icon(d.icon),
                    selectedIcon: Icon(d.icon),
                    label: Text(d.label),
                  ),
              ],
            ),
          const VerticalDivider(width: 1, thickness: 1, color: AppColors.borde),
          Expanded(child: child),
        ],
      ),
    );
  }
}
