import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../core/router/app_routes.dart';
import '../core/theme/app_spacing.dart';
import '../features/auth/application/auth_provider.dart';
import '../features/auth/domain/auth_user.dart';

/// Placeholder de la Fase 0 — el dashboard real (con estadísticas) llega
/// en la Fase 5. El acceso a "Configuración del espacio" (solo gestor) es
/// temporal acá: en escritorio también está en el top nav (`pushed:
/// true`), pero en móvil la bottom nav solo muestra destinos `primario`,
/// así que este es el único camino móvil hasta que exista una pantalla
/// "Más"/Perfil (ver Fase 6 del plan).
class InicioScreen extends ConsumerWidget {
  const InicioScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authProvider).value;
    final scheme = Theme.of(context).colorScheme;
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 72,
            height: 72,
            decoration: BoxDecoration(
              gradient: LinearGradient(colors: [scheme.primary, scheme.tertiary]),
              shape: BoxShape.circle,
            ),
            child: const Icon(LucideIcons.sparkles, color: Colors.white, size: 32),
          ),
          const SizedBox(height: AppSpacing.lg),
          Text(
            user == null ? 'Inicio' : 'Hola, ${user.username}',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: AppSpacing.xs),
          Text(
            user?.rol.name ?? '',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: scheme.onSurfaceVariant),
          ),
          if (user != null && (user.rol == RolUsuario.gestor || user.rol == RolUsuario.admin)) ...[
            const SizedBox(height: AppSpacing.lg),
            Wrap(
              spacing: AppSpacing.sm,
              runSpacing: AppSpacing.sm,
              alignment: WrapAlignment.center,
              children: [
                OutlinedButton.icon(
                  onPressed: () => context.go(AppRoutes.admin),
                  icon: const Icon(LucideIcons.layoutDashboard, size: 18),
                  label: const Text('Dashboard'),
                ),
                OutlinedButton.icon(
                  onPressed: () => context.go(AppRoutes.adminRecursos),
                  icon: const Icon(LucideIcons.package, size: 18),
                  label: const Text('Recursos'),
                ),
                OutlinedButton.icon(
                  onPressed: () => context.go(AppRoutes.adminZonas),
                  icon: const Icon(LucideIcons.mapPinned, size: 18),
                  label: const Text('Zonas'),
                ),
                OutlinedButton.icon(
                  onPressed: () => context.go(AppRoutes.adminEnsayos),
                  icon: const Icon(LucideIcons.flaskConical, size: 18),
                  label: const Text('Ensayos'),
                ),
                if (user.rol == RolUsuario.gestor)
                  OutlinedButton.icon(
                    onPressed: () => context.push(AppRoutes.adminConfiguracion),
                    icon: const Icon(LucideIcons.settings, size: 18),
                    label: const Text('Configuración'),
                  ),
                if (user.rol == RolUsuario.admin) ...[
                  OutlinedButton.icon(
                    onPressed: () => context.go(AppRoutes.usuarios),
                    icon: const Icon(LucideIcons.users, size: 18),
                    label: const Text('Usuarios'),
                  ),
                  OutlinedButton.icon(
                    onPressed: () => context.go(AppRoutes.adminControlCambios),
                    icon: const Icon(LucideIcons.history, size: 18),
                    label: const Text('Auditoría'),
                  ),
                ],
              ],
            ),
          ],
          const SizedBox(height: AppSpacing.xl),
          OutlinedButton.icon(
            onPressed: () => ref.read(authProvider.notifier).logout(),
            icon: const Icon(LucideIcons.logOut, size: 18),
            label: const Text('Cerrar sesión'),
          ),
        ],
      ),
    );
  }
}
