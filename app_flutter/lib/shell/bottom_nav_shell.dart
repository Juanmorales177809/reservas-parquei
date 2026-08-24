import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/router/nav_destinations.dart';
import '../core/widgets/brand_mark.dart';
import '../features/auth/application/auth_provider.dart';
import '../features/notificaciones/presentation/notification_bell.dart';
import 'session_menu.dart';

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
        // Solo el ícono: en celular el ancho es escaso y el título competía
        // con el botón de "Iniciar sesión" hasta desbordar. El rail y el top
        // nav sí muestran el wordmark completo.
        title: const BrandMark(compact: true),
        actions: [
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
      // no hay nada que elegir: no se muestra barra (el acceso a login vive
      // en la `AppBar`, ver `SessionMenu`).
      bottomNavigationBar: destinos.length < 2
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
