import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/router/nav_destinations.dart';
import '../core/widgets/brand_mark.dart';
import '../features/auth/application/auth_provider.dart';
import '../features/notificaciones/presentation/notification_bell.dart';

/// Navegación inferior con iconos para móvil (< 840dp). Consume la misma
/// lista de destinos que [TopNavShell] — nunca la duplica.
class BottomNavShell extends ConsumerWidget {
  const BottomNavShell({required this.destinos, required this.currentPath, required this.child, super.key});

  final List<NavDestinationSpec> destinos;
  final String currentPath;
  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedIndex = destinos.indexWhere((d) => d.path == currentPath);
    final autenticado = ref.watch(isAuthenticatedProvider);
    return Scaffold(
      appBar: AppBar(
        title: const BrandMark(),
        actions: [if (autenticado) const NotificationBell()],
      ),
      body: child,
      bottomNavigationBar: destinos.isEmpty
          ? null
          : NavigationBar(
              selectedIndex: selectedIndex < 0 ? 0 : selectedIndex,
              onDestinationSelected: (index) => context.go(destinos[index].path),
              destinations: [
                for (final d in destinos) NavigationDestination(icon: Icon(d.icon), label: d.label),
              ],
            ),
    );
  }
}
