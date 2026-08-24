import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../core/theme/app_spacing.dart';
import '../features/auth/application/auth_provider.dart';

/// Identidad de la sesión + "Cerrar sesión", en la `AppBar` de los tres
/// shells (bottom/rail/top).
///
/// Antes esto vivía en `InicioScreen`, que era **el único** lugar de la app
/// con un botón de logout. Esa pantalla se eliminó cuando el inicio pasó a
/// ser el dashboard real, así que el logout tuvo que mudarse a un lugar
/// presente en todos los anchos de ventana — si no, cerrar sesión dejaba de
/// ser posible en móvil, donde no hay top nav.
///
/// El avatar usa la inicial del usuario en vez de un ícono: además de ser
/// el patrón habitual, conserva el "quién soy" que mostraba `InicioScreen`
/// ("Hola, administrador" + rol) y que si no se perdería.
class SessionMenu extends ConsumerWidget {
  const SessionMenu({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authProvider).value;
    if (user == null) return const SizedBox.shrink();

    final scheme = Theme.of(context).colorScheme;
    final inicial = user.username.isEmpty ? '?' : user.username.substring(0, 1).toUpperCase();

    return MenuAnchor(
      alignmentOffset: const Offset(0, AppSpacing.xs),
      builder: (context, controller, child) => Tooltip(
        message: user.username,
        child: InkWell(
          onTap: () => controller.isOpen ? controller.close() : controller.open(),
          customBorder: const CircleBorder(),
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.xs),
            child: CircleAvatar(
              radius: 16,
              backgroundColor: scheme.primary,
              child: Text(
                inicial,
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: scheme.onPrimary,
                      fontWeight: FontWeight.w700,
                    ),
              ),
            ),
          ),
        ),
      ),
      menuChildren: [
        // Cabecera informativa, no accionable.
        Padding(
          padding: const EdgeInsets.fromLTRB(AppSpacing.md, AppSpacing.sm, AppSpacing.md, AppSpacing.xs),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(user.username, style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
              Text(
                user.rol.name,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant),
              ),
            ],
          ),
        ),
        const Divider(height: 1),
        MenuItemButton(
          leadingIcon: const Icon(LucideIcons.logOut, size: 18),
          onPressed: () => ref.read(authProvider.notifier).logout(),
          child: const Text('Cerrar sesión'),
        ),
      ],
    );
  }
}
