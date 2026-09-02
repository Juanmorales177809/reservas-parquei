import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../core/router/nav_destinations.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_spacing.dart';
import '../core/widgets/brand_mark.dart';
import '../features/auth/application/auth_provider.dart';
import '../features/notificaciones/presentation/notification_bell.dart';
import 'session_menu.dart';

/// Navegación superior para PC/pantallas grandes (≥ 840dp). Consume la
/// misma lista de destinos que [BottomNavShell] — nunca la duplica.
///
/// Los destinos `primario: true` (los mismos que caben en la bottom nav
/// móvil) van como botón directo; el resto (Recursos/Espacios/
/// Usuarios/Configuración — gestión, no navegación diaria) se agrupan en
/// un único menú "Gestión" para no abarrotar la barra — antes de esto,
/// cada destino nuevo de la Fase 4b/5 se agregaba como botón suelto y la
/// barra terminó con 8 botones de texto en fila.
class TopNavShell extends ConsumerWidget {
  const TopNavShell({required this.destinos, required this.currentPath, required this.child, super.key});

  final List<NavDestinationSpec> destinos;
  final String currentPath;
  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final autenticado = ref.watch(isAuthenticatedProvider);
    final principales = destinos.where((d) => d.primario).toList(growable: false);
    final secundarios = destinos.where((d) => !d.primario).toList(growable: false);
    final secundarioActivo = secundarios.any((d) => d.path == currentPath);

    void navegar(NavDestinationSpec d) => d.pushed ? context.push(d.path) : context.go(d.path);

    return Scaffold(
      appBar: AppBar(
        title: const BrandMark(),
        actions: [
          for (final d in principales)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xs),
              child: _NavButton(
                destino: d,
                activo: currentPath == d.path,
                onPressed: () => navegar(d),
              ),
            ),
          if (secundarios.isNotEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xs),
              child: MenuAnchor(
                builder: (context, controller, child) => TextButton.icon(
                  onPressed: () => controller.isOpen ? controller.close() : controller.open(),
                  style: TextButton.styleFrom(
                    foregroundColor: secundarioActivo ? AppColors.marca : AppColors.textoTerciario,
                    backgroundColor: secundarioActivo ? AppColors.azul50 : null,
                    padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.sm),
                    textStyle: Theme.of(context)
                        .textTheme
                        .labelLarge
                        ?.copyWith(fontWeight: secundarioActivo ? FontWeight.w700 : FontWeight.w600),
                  ),
                  icon: const Icon(LucideIcons.settings2, size: 18),
                  label: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [Text('Gestión'), Icon(LucideIcons.chevronDown, size: 14)],
                  ),
                ),
                menuChildren: [
                  for (final d in secundarios)
                    MenuItemButton(
                      leadingIcon: Icon(d.icon, size: 18),
                      onPressed: currentPath == d.path ? null : () => navegar(d),
                      child: Text(d.label),
                    ),
                ],
              ),
            ),
          const SizedBox(width: AppSpacing.sm),
          if (autenticado) const NotificationBell(),
          // SIN `if (autenticado)`: `SessionMenu` resuelve los dos casos
          // (botón de "Iniciar sesión" si no hay sesión, avatar + logout si
          // la hay). Condicionarlo acá fue exactamente el bug que dejó a
          // móvil y tablet sin forma de iniciar sesión.
          const SessionMenu(),
          const SizedBox(width: AppSpacing.md),
        ],
      ),
      body: child,
    );
  }
}

class _NavButton extends StatelessWidget {
  const _NavButton({required this.destino, required this.activo, required this.onPressed});

  final NavDestinationSpec destino;
  final bool activo;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return TextButton.icon(
      // El destino activo NO se deshabilita (antes: `activo ? null : ...`).
      // Un `TextButton` con `onPressed: null` es un botón deshabilitado, y
      // Material entonces ignora el `foregroundColor` del estilo y aplica
      // el color de deshabilitado — así que el destino en el que estabas
      // parado se veía gris y apagado mientras los demás se veían
      // normales: exactamente al revés de lo que debe comunicar.
      // Ahora queda habilitado y volver a tocarlo simplemente no navega.
      onPressed: activo ? () {} : onPressed,
      style: TextButton.styleFrom(
        foregroundColor: activo ? AppColors.marca : AppColors.textoTerciario,
        backgroundColor: activo ? AppColors.azul50 : null,
        padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.sm),
        textStyle: Theme.of(context)
            .textTheme
            .labelLarge
            ?.copyWith(fontWeight: activo ? FontWeight.w700 : FontWeight.w600),
      ),
      icon: Icon(destino.icon, size: 18),
      label: Text(destino.label),
    );
  }
}
