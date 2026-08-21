// `defaultTargetPlatform` vive en foundation y NO lo reexporta material.
import 'package:flutter/foundation.dart' show defaultTargetPlatform, TargetPlatform;
import 'package:flutter/material.dart';

import '../theme/app_elevation.dart';
import '../theme/app_spacing.dart';

/// Realimentación de puntero/toque para una tarjeta tocable.
///
/// **Reescrito en Fase 6.** La versión anterior escalaba la tarjeta entera
/// a 1.02x en hover, con dos problemas reales:
///
/// 1. Flutter rasteriza y luego reescala, así que el texto se desdibuja
///    durante toda la transición.
/// 2. En una grilla densa, una tarjeta 2% más grande se solapa con su
///    vecina.
///
/// Ahora el hover **no escala**: eleva la sombra (nivel 1 → nivel 2) y
/// traslada 2px hacia arriba. El escalado queda solo para el `press`, donde
/// la duración es corta y el desenfoque no llega a percibirse.
///
/// Además, en plataformas táctiles no se monta `MouseRegion` en absoluto:
/// antes se pagaba su costo en Android/iOS sin ningún beneficio, porque
/// ahí no existe el concepto de "puntero encima".
class HoverLift extends StatefulWidget {
  const HoverLift({required this.child, this.borderRadius = AppRadius.xl, super.key});

  final Widget child;

  /// Debe coincidir con el radio del hijo para que la sombra no se
  /// proyecte con una silueta distinta a la de la tarjeta.
  final double borderRadius;

  @override
  State<HoverLift> createState() => _HoverLiftState();
}

class _HoverLiftState extends State<HoverLift> {
  bool _hover = false;
  bool _presionado = false;

  static bool get _esTactil =>
      defaultTargetPlatform == TargetPlatform.android || defaultTargetPlatform == TargetPlatform.iOS;

  @override
  Widget build(BuildContext context) {
    // "Reducir movimiento" del sistema: se conserva el cambio de sombra
    // (informa sin mover nada) pero se anulan escala y traslación.
    final sinMovimiento = MediaQuery.disableAnimationsOf(context);

    final contenido = AnimatedScale(
      scale: (_presionado && !sinMovimiento) ? 0.97 : 1.0,
      // 100ms: clase "instantáneo". Un press debe responder, no animarse.
      duration: const Duration(milliseconds: 100),
      curve: Curves.easeOut,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        curve: Curves.easeOutCubic,
        transform: Matrix4.translationValues(0, (_hover && !sinMovimiento) ? -2 : 0, 0),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(widget.borderRadius),
          boxShadow: _hover ? AppElevation.hover : AppElevation.reposo,
        ),
        child: widget.child,
      ),
    );

    final conPress = Listener(
      onPointerDown: (_) => setState(() => _presionado = true),
      onPointerUp: (_) => setState(() => _presionado = false),
      onPointerCancel: (_) => setState(() => _presionado = false),
      child: contenido,
    );

    if (_esTactil) return conPress;

    return MouseRegion(
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: conPress,
    );
  }
}
