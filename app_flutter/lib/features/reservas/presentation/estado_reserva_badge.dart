import 'package:flutter/material.dart';

import '../../../core/domain/enums.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';

/// Badge de color por `EstadoReserva` — mismo lenguaje visual que
/// `EstadoBadge` (espacios/recursos) pero mapeando el dominio del flujo de
/// aprobación de una reserva.
///
/// Fase 6: usa los tokens verificados de [AppEstados]. El ámbar anterior
/// (`#D97706` como texto sobre blanco) daba 3.20:1 y **fallaba AA**; ahora
/// el texto de "Esperando" es `#92400E` sobre tinte `#FFFBEB` (AAA).
class EstadoReservaBadge extends StatelessWidget {
  const EstadoReservaBadge({required this.estado, super.key});

  final EstadoReserva estado;

  @override
  Widget build(BuildContext context) {
    final (tokens, etiqueta) = switch (estado) {
      EstadoReserva.esperando => (AppEstados.pendiente, 'Esperando'),
      EstadoReserva.aprobada => (AppEstados.positivo, 'Aprobada'),
      EstadoReserva.rechazada => (AppEstados.negativo, 'Rechazada'),
      EstadoReserva.cancelada => (AppEstados.neutro, 'Cancelada'),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.sm, vertical: 3),
      decoration: BoxDecoration(
        color: tokens.tinte,
        borderRadius: BorderRadius.circular(AppRadius.pill),
        border: Border.all(color: tokens.borde.withValues(alpha: 0.35)),
      ),
      child: Text(etiqueta, style: AppText.overline(color: tokens.sobreTinte)),
    );
  }
}
