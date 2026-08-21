import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/router/nav_destinations.dart';
import '../core/theme/app_spacing.dart';
import '../features/auth/application/auth_provider.dart';
import 'bottom_nav_shell.dart';
import 'rail_nav_shell.dart';
import 'top_nav_shell.dart';

/// *Window size classes* de Material 3. Hasta la Fase 5 el salto era
/// binario en 840dp (bottom nav o top nav), lo que dejaba al tablet en
/// tierra de nadie: a 800dp se mostraba una barra inferior pensada para un
/// teléfono con la pantalla medio vacía a los costados. Material define
/// tres clases, no dos.
const kCompactBreakpoint = 600.0;
const kExpandedBreakpoint = 1240.0;

/// Ancho a partir del cual se considera "no móvil". Se conserva el nombre
/// porque otras partes del código lo referencian; hoy coincide con el
/// límite compacto.
const kNavBreakpoint = kCompactBreakpoint;

enum ClaseVentana { compacta, media, expandida }

ClaseVentana claseDeAncho(double ancho) {
  if (ancho < kCompactBreakpoint) return ClaseVentana.compacta;
  if (ancho < kExpandedBreakpoint) return ClaseVentana.media;
  return ClaseVentana.expandida;
}

/// Único shell de navegación: elige bottom nav / rail lateral / top nav
/// según el ancho de ventana. Un solo `ShellRoute` en `app_router.dart` lo
/// envuelve — no hay árboles de rutas separados por plataforma.
class AppShell extends ConsumerWidget {
  const AppShell({required this.child, required this.currentPath, super.key});

  final Widget child;
  final String currentPath;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authProvider).value;
    final clase = claseDeAncho(MediaQuery.sizeOf(context).width);

    // Solo la bottom nav está limitada a 4-5 slots. El rail crece hacia
    // abajo y el top nav agrupa el excedente en "Gestión", así que ambos
    // reciben la lista completa.
    final destinos = visibleDestinations(user, primarioOnly: clase == ClaseVentana.compacta);

    return switch (clase) {
      ClaseVentana.compacta => BottomNavShell(destinos: destinos, currentPath: currentPath, child: child),
      ClaseVentana.media => RailNavShell(
          destinos: destinos,
          currentPath: currentPath,
          child: ContenidoCentrado(child: child),
        ),
      ClaseVentana.expandida => TopNavShell(
          destinos: destinos,
          currentPath: currentPath,
          child: ContenidoCentrado(child: child),
        ),
    };
  }
}

/// Limita el contenido a [AppSpacing.anchoContenidoMaximo] y lo centra.
///
/// Sin esto, en un monitor de 27" la app no se ve como una aplicación de
/// escritorio sino como una app móvil estirada: párrafos de 160 caracteres
/// por línea y cuatro KPIs separados por 24px en 1800px de ancho. El fondo
/// sigue ocupando toda la ventana; el contenido no.
class ContenidoCentrado extends StatelessWidget {
  const ContenidoCentrado({required this.child, super.key});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.topCenter,
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: AppSpacing.anchoContenidoMaximo),
        child: child,
      ),
    );
  }
}
