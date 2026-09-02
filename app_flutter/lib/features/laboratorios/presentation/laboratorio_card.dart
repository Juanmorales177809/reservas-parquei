import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_gradients.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/widgets/estado_badge.dart';
import '../../../core/widgets/hover_lift.dart';
import '../../recursos/application/recursos_providers.dart';
import '../domain/laboratorio.dart';

class LaboratorioCard extends ConsumerWidget {
  const LaboratorioCard({required this.laboratorio, required this.onTap, super.key});

  final Laboratorio laboratorio;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final recursosCount = ref.watch(recursosPorLaboratorioProvider(laboratorio.id)).length;
    final textTheme = Theme.of(context).textTheme;

    return HoverLift(
      child: Card(
        child: InkWell(
          onTap: onTap,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Cabecera de gradiente en vez de una foto real. Un único
              // gradiente fijo (ver `app_gradients.dart`), consistente en
              // toda la app.
              Container(
                height: 72,
                padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
                decoration: BoxDecoration(gradient: kGradienteLaboratorio),
                child: DecoratedBox(
                  // Vela el extremo derecho para que el badge blanco no
                  // pierda definición sobre la parada clara del gradiente.
                  decoration: const BoxDecoration(gradient: kGradientScrim),
                  child: Row(
                    children: [
                      const Icon(LucideIcons.building2, color: Colors.white, size: 24),
                      const Spacer(),
                      EstadoBadge(estado: laboratorio.estado, sobreOscuro: true),
                    ],
                  ),
                ),
              ),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(AppSpacing.lg),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        laboratorio.nombre,
                        style: textTheme.titleLarge,
                        // Dos líneas: los nombres reales ("Laboratorio de
                        // Informática", "Sala de Juntas Ejecutiva") no
                        // entran en una sola a 20px en una celda de grilla.
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: AppSpacing.xs),
                      // Ubicación y capacidad en una sola línea de metadato.
                      // Antes eran tres metadatos con tres iconos en fila,
                      // que se leía como un formulario en vez de como una
                      // tarjeta.
                      Text(
                        laboratorio.capacidad > 0
                            ? '${laboratorio.ubicacion} · ${laboratorio.capacidad} personas'
                            : laboratorio.ubicacion,
                        style: textTheme.bodySmall,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const Spacer(),
                      // El conteo de recursos baja a chip de nivel 0: es
                      // información de escaneo, no de lectura. `Wrap` y no
                      // `Row`: en la celda más angosta de la grilla los dos
                      // chips no entran en una línea y un `Row` desborda.
                      Wrap(
                        spacing: AppSpacing.sm,
                        runSpacing: AppSpacing.xs,
                        children: [
                          _Chip(
                            icon: LucideIcons.package,
                            label: recursosCount == 1 ? '1 recurso' : '$recursosCount recursos',
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Chip de nivel 0 (plano, sin sombra): radio 8 = radio de tarjeta (20)
/// menos su padding, según la regla concéntrica de `AppRadius`.
class _Chip extends StatelessWidget {
  const _Chip({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.sm, vertical: AppSpacing.xs),
      decoration: BoxDecoration(
        color: AppColors.superficieSutil,
        borderRadius: BorderRadius.circular(AppRadius.sm),
        border: Border.all(color: AppColors.borde),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: AppColors.textoTerciario),
          const SizedBox(width: AppSpacing.xs),
          Text(label, style: AppText.overline()),
        ],
      ),
    );
  }
}
