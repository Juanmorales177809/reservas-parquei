import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

/// Entrada escalonada para ítems de lista o grilla.
///
/// **Techo obligatorio en el índice (Fase 6).** Antes el delay era
/// `40ms * index` sin límite: aceptable para 8 tarjetas (320ms), inaceptable
/// para una lista de 40 reservas — el último ítem tardaba 1.6s en aparecer y
/// para entonces el usuario ya había hecho scroll y solo veía huecos.
/// Con el tope, una lista de 4 ítems y una de 400 terminan de entrar en el
/// mismo tiempo (~210ms + duración).
///
/// **Cuándo NO usarlo**: al re-filtrar, buscar o reordenar una lista. Ahí el
/// usuario espera un cambio inmediato, no una entrada; animar hace que la
/// interfaz se sienta lenta. El stagger es solo para el primer montaje de
/// una ruta.
extension StaggeredEntrance on Widget {
  Widget staggerEntrance(
    int index, {
    Duration itemDelay = const Duration(milliseconds: 35),
    int maxIndex = 6,
  }) {
    return _EntradaEscalonada(index: index, itemDelay: itemDelay, maxIndex: maxIndex, child: this);
  }
}

/// Envoltorio necesario para poder leer `MediaQuery` — la extensión sobre
/// `Widget` no tiene `BuildContext` propio.
class _EntradaEscalonada extends StatelessWidget {
  const _EntradaEscalonada({
    required this.index,
    required this.itemDelay,
    required this.maxIndex,
    required this.child,
  });

  final int index;
  final Duration itemDelay;
  final int maxIndex;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    // Respeta "reducir movimiento" del sistema operativo (iOS/Android/
    // Windows/macOS lo exponen; Flutter lo publica en `MediaQuery`).
    // Además de ser lo correcto para quien tiene trastornos vestibulares,
    // apaga estas animaciones en los widget tests, donde
    // `AutomatedTestWidgetsFlutterBinding` fija `disableAnimations: true`:
    // así un test que monte una lista no queda esperando timers de
    // `flutter_animate`.
    if (MediaQuery.disableAnimationsOf(context)) return child;

    final delay = itemDelay * index.clamp(0, maxIndex);
    return child
        .animate(delay: delay)
        // 350ms = clase "entrada" de la tabla de motion.
        .fadeIn(duration: 350.ms, curve: Curves.easeOutCubic)
        .slideY(begin: 0.08, end: 0, duration: 350.ms, curve: Curves.easeOutCubic);
  }
}
