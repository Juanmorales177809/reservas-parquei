import 'package:flutter/material.dart';

import '../domain/enums.dart';
import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';
import '../theme/app_typography.dart';

/// Badge de color por `EstadoEntidad` — compartido entre features
/// (laboratorios, recursos, espacios).
///
/// Fase 6: los colores salen de [AppEstados], donde cada estado tiene un
/// tono distinto para relleno, texto-sobre-tinte y borde. Antes usaba un
/// único `#10B981` como texto sobre blanco (2.54:1, **fallaba AA**) y
/// `#F59E0B` para mantenimiento (también por debajo del mínimo).
class EstadoBadge extends StatelessWidget {
  const EstadoBadge({required this.estado, this.sobreOscuro = false, super.key});

  final EstadoEntidad estado;

  /// `true` cuando el badge va sobre una cabecera de gradiente.
  ///
  /// En ese caso se usa una cápsula **blanca casi opaca con el texto en el
  /// color del estado**, no un tinte translúcido: un badge de color sobre
  /// un gradiente de color es difícil de leer, mientras que uno blanco es
  /// legible sobre cualquier extremo del gradiente.
  final bool sobreOscuro;

  @override
  Widget build(BuildContext context) {
    final (tokens, etiqueta) = switch (estado) {
      EstadoEntidad.activo => (AppEstados.positivo, 'Activo'),
      EstadoEntidad.inactivo => (AppEstados.neutro, 'Inactivo'),
      EstadoEntidad.mantenimiento => (AppEstados.pendiente, 'Mantenimiento'),
    };

    final fondo = sobreOscuro ? Colors.white.withValues(alpha: 0.92) : tokens.tinte;
    final texto = tokens.sobreTinte;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.sm, vertical: 3),
      decoration: BoxDecoration(
        color: fondo,
        borderRadius: BorderRadius.circular(AppRadius.pill),
        border: sobreOscuro ? null : Border.all(color: tokens.borde.withValues(alpha: 0.35)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(color: tokens.borde, shape: BoxShape.circle),
          ),
          const SizedBox(width: AppSpacing.xs),
          Text(etiqueta, style: AppText.overline(color: texto)),
        ],
      ),
    );
  }
}
