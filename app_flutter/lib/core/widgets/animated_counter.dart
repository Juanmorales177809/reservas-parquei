import 'package:flutter/material.dart';

/// Cuenta desde 0 hasta [value] al aparecer — usado en los KPIs del
/// dashboard para que los números se sientan "vivos" en vez de aparecer
/// estáticos. `TweenAnimationBuilder` puro, sin paquete nuevo.
///
/// **El estilo DEBE traer cifras tabulares** (`AppText.numerico`). Inter usa
/// cifras proporcionales por defecto: cada dígito tiene un ancho distinto,
/// así que mientras el contador sube el número cambia de ancho en cada
/// frame y se percibe como si "vibrara". Con `tabularFigures` todos los
/// dígitos miden lo mismo y el número crece en su lugar.
///
/// Como red de seguridad, si el estilo recibido no declara esa feature se
/// la agrega igual: es un detalle fácil de olvidar en un call site nuevo y
/// el síntoma (temblor sutil) es difícil de diagnosticar a ojo.
class AnimatedCounter extends StatelessWidget {
  const AnimatedCounter({
    required this.value,
    this.style,
    this.duration = const Duration(milliseconds: 900),
    super.key,
  });

  final int value;
  final TextStyle? style;
  final Duration duration;

  @override
  Widget build(BuildContext context) {
    final base = style ?? DefaultTextStyle.of(context).style;
    final tieneTabular = base.fontFeatures?.any((f) => f.feature == 'tnum') ?? false;
    final estilo = tieneTabular
        ? base
        : base.copyWith(fontFeatures: [...?base.fontFeatures, const FontFeature.tabularFigures()]);

    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: value.toDouble()),
      duration: duration,
      curve: Curves.easeOutCubic,
      builder: (context, valorActual, child) => Text('${valorActual.round()}', style: estilo),
    );
  }
}
