import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';

/// Placeholder animado mientras `laboratoriosListProvider` carga.
///
/// **Tiene que ser isomorfo a `LaboratorioCard`**: misma altura de cabecera,
/// mismo radio, mismos bloques en las mismas posiciones. Un skeleton
/// genérico (un rectángulo donde después aparece otra cosa) enseña al
/// usuario a esperar una forma que no llega, y el salto al contenido real
/// se percibe como un parpadeo. Si `LaboratorioCard` cambia de estructura, este
/// archivo cambia con ella.
class LaboratorioCardSkeleton extends StatelessWidget {
  const LaboratorioCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Shimmer.fromColors(
      baseColor: AppColors.borde,
      highlightColor: AppColors.fondo,
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.superficie,
          borderRadius: BorderRadius.circular(AppRadius.xl),
          border: Border.all(color: AppColors.borde),
        ),
        clipBehavior: Clip.antiAlias,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Cabecera de gradiente: 72px, igual que la tarjeta real.
            Container(height: 72, color: Colors.white),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(AppSpacing.lg),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Título (titleLarge, ~26px de alto).
                    Container(height: 20, width: 150, color: Colors.white),
                    const SizedBox(height: AppSpacing.sm),
                    // Línea de metadato (ubicación · capacidad).
                    Container(height: 12, width: 190, color: Colors.white),
                    const Spacer(),
                    // Los dos chips de nivel 0 del pie de la tarjeta.
                    Row(
                      children: [
                        Container(
                          height: 22,
                          width: 84,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(AppRadius.sm),
                          ),
                        ),
                        const SizedBox(width: AppSpacing.sm),
                        Container(
                          height: 22,
                          width: 68,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(AppRadius.sm),
                          ),
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
    );
  }
}
