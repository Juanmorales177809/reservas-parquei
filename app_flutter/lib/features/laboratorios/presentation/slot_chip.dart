import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/domain/enums.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';

/// Chip de una franja horaria, compartido por la grilla de solo lectura
/// (`DisponibilidadSlotGrid`) y la seleccionable (`SelectableSlotGrid`)
/// para que ambas hablen exactamente el mismo idioma visual.
///
/// **Los tres estados se distinguen por forma, no solo por color.** Antes
/// "ocupado" y "mantenimiento" eran dos rellenos de distinto tono y nada
/// más: para alguien con daltonismo (o en una proyección de aula con
/// colores lavados) eran indistinguibles, y son cosas muy distintas para
/// quien reserva ("ya lo tomó alguien" vs "el equipo no está operativo").
/// Ahora mantenimiento lleva rayas diagonales además del icono — requisito
/// 1.4.1 de WCAG (no transmitir información solo por color).
class SlotChip extends StatelessWidget {
  const SlotChip({
    required this.estado,
    required this.etiqueta,
    this.seleccionado = false,
    this.onTap,
    super.key,
  });

  final EstadoSlot estado;
  final String etiqueta;
  final bool seleccionado;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final (fondo, texto, borde, icono) = switch (estado) {
      EstadoSlot.libre => (
          AppEstados.positivo.tinte,
          AppEstados.positivo.sobreTinte,
          AppEstados.positivo.borde,
          LucideIcons.check,
        ),
      EstadoSlot.ocupado => (
          AppColors.fondo,
          AppColors.textoDeshabilitado,
          Colors.transparent,
          LucideIcons.x,
        ),
      EstadoSlot.mantenimiento => (
          AppColors.fondo,
          AppColors.textoSecundario,
          AppColors.bordeFuerte,
          LucideIcons.wrench,
        ),
    };

    final fondoFinal = seleccionado ? AppColors.marca : fondo;
    final textoFinal = seleccionado ? Colors.white : texto;
    final bordeFinal = seleccionado ? AppColors.marca : borde;

    Widget contenido = Container(
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.sm),
      decoration: BoxDecoration(
        color: fondoFinal,
        borderRadius: BorderRadius.circular(AppRadius.sm),
        border: Border.all(color: bordeFinal, width: seleccionado ? 2 : 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(seleccionado ? LucideIcons.check : icono, size: 13, color: textoFinal),
          const SizedBox(width: AppSpacing.xs),
          Text(etiqueta, style: AppText.numerico(fontSize: 12, color: textoFinal)),
        ],
      ),
    );

    if (estado == EstadoSlot.mantenimiento && !seleccionado) {
      contenido = ClipRRect(
        borderRadius: BorderRadius.circular(AppRadius.sm),
        child: CustomPaint(painter: const _RayasDiagonales(), child: contenido),
      );
    }

    if (onTap == null) return contenido;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(AppRadius.sm),
      child: contenido,
    );
  }
}

/// Rayas a 45° detrás del contenido — la marca visual de "no disponible por
/// mantenimiento", que no depende del color para leerse.
class _RayasDiagonales extends CustomPainter {
  const _RayasDiagonales();

  @override
  void paint(Canvas canvas, Size size) {
    final pincel = Paint()
      ..color = AppColors.bordeFuerte.withValues(alpha: 0.55)
      ..strokeWidth = 1.5;
    const paso = 7.0;
    // Se dibuja desde -alto hasta ancho para que las diagonales cubran todo
    // el rectángulo, incluidas las esquinas.
    for (var x = -size.height; x < size.width; x += paso) {
      canvas.drawLine(Offset(x, size.height), Offset(x + size.height, 0), pincel);
    }
  }

  @override
  bool shouldRepaint(covariant _RayasDiagonales oldDelegate) => false;
}

/// Leyenda de los tres estados. Una grilla de colores sin leyenda obliga a
/// deducir qué significa cada uno.
class SlotLeyenda extends StatelessWidget {
  const SlotLeyenda({super.key});

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: AppSpacing.lg,
      runSpacing: AppSpacing.xs,
      children: [
        for (final (estado, etiqueta) in const [
          (EstadoSlot.libre, 'Disponible'),
          (EstadoSlot.ocupado, 'Reservado'),
          (EstadoSlot.mantenimiento, 'Mantenimiento'),
        ])
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              SlotChip(estado: estado, etiqueta: '  '),
              const SizedBox(width: AppSpacing.xs),
              Text(etiqueta, style: AppText.overline()),
            ],
          ),
      ],
    );
  }
}
