import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../core/router/nav_destinations.dart';
import '../core/theme/app_spacing.dart';
import '../core/widgets/brand_mark.dart';
import '../features/auth/application/auth_provider.dart';
import '../features/notificaciones/presentation/notification_bell.dart';
import 'session_menu.dart';

/// Navegación para móvil (< 600dp). Consume la misma lista de destinos que
/// [TopNavShell] — nunca la duplica.
///
/// Recibe **todos** los destinos visibles y hace el reparto acá: los
/// `primario` van a la barra inferior (que solo tiene 4-5 ranuras) y el
/// resto —Recursos/Zonas/Ensayos/Usuarios/Configuración/Auditoría, o sea
/// gestión, no navegación diaria— a un menú "Gestión" en la `AppBar`, igual
/// que hace [TopNavShell].
///
/// Antes este shell recibía solo los `primario` y los de gestión **no eran
/// alcanzables en celular**: el único camino era la vieja `InicioScreen`,
/// una pantalla de atajos que se eliminó al pasar el inicio a ser el
/// dashboard. Un admin en el teléfono se quedaba sin la mitad de la app.
class BottomNavShell extends ConsumerWidget {
  const BottomNavShell({required this.destinos, required this.currentPath, required this.child, super.key});

  final List<NavDestinationSpec> destinos;
  final String currentPath;
  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final autenticado = ref.watch(isAuthenticatedProvider);
    final primarios = destinos.where((d) => d.primario).toList(growable: false);
    final secundarios = destinos.where((d) => !d.primario).toList(growable: false);
    final selectedIndex = primarios.indexWhere((d) => d.path == currentPath);

    void navegar(NavDestinationSpec d) => d.pushed ? context.push(d.path) : context.go(d.path);

    return Scaffold(
      appBar: AppBar(
        // Solo el ícono: en celular el ancho es escaso y el título competía
        // con el botón de "Iniciar sesión" hasta desbordar. El rail y el top
        // nav sí muestran el wordmark completo.
        title: const BrandMark(compact: true),
        actions: [
          if (secundarios.isNotEmpty)
            MenuAnchor(
              alignmentOffset: const Offset(0, AppSpacing.xs),
              builder: (context, controller, child) => IconButton(
                onPressed: () => controller.isOpen ? controller.close() : controller.open(),
                icon: const Icon(LucideIcons.settings2, size: 20),
                tooltip: 'Gestión',
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
          if (autenticado) const NotificationBell(),
          // SIN `if (autenticado)`: ver el comentario en `SessionMenu`.
          // Condicionarlo dejaba a este shell (celular) sin botón de
          // "Iniciar sesión" para un visitante anónimo.
          const SessionMenu(),
        ],
      ),
      body: child,
      // `NavigationBar` de Material exige `destinations.length >= 2` (assert
      // en navigation_bar.dart). La guarda anterior era `destinos.isEmpty`,
      // que solo cubría el cero — y el caso de UNO es perfectamente
      // alcanzable: un visitante anónimo ve un único destino, porque
      // "Espacios" es el único con `requiereSesion: false`. En release el
      // assert no corre, así que esto no se veía como pantalla roja, pero la
      // barra quedaba en un estado no soportado. Con menos de dos destinos
      // no hay nada que elegir: no se muestra barra.
      bottomNavigationBar: primarios.length < 2
          ? null
          : NavigationBar(
              selectedIndex: selectedIndex < 0 ? 0 : selectedIndex,
              onDestinationSelected: (index) => navegar(primarios[index]),
              destinations: [
                for (final d in primarios) NavigationDestination(icon: Icon(d.icon), label: d.label),
              ],
            ),
    );
  }
}
