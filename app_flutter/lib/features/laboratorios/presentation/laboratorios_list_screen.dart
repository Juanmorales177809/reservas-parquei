import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/router/app_routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/staggered_entrance.dart';
import '../application/laboratorios_providers.dart';
import 'laboratorio_card.dart';
import 'laboratorio_card_skeleton.dart';

/// `maxCrossAxisExtent` es el ancho MÁXIMO por celda, así que el número de
/// columnas es `ceil(anchoDisponible / max)`. Con 360 una pantalla de
/// ~415px caía en 2 columnas de 183px y el título de la tarjeta se
/// truncaba; con 420 esa misma pantalla da 1 columna a ancho completo, y
/// un escritorio de 1280px sigue dando 4 columnas de ~320px.
const _kGridDelegate = SliverGridDelegateWithMaxCrossAxisExtent(
  maxCrossAxisExtent: 420,
  mainAxisExtent: 232,
  crossAxisSpacing: AppSpacing.lg,
  mainAxisSpacing: AppSpacing.lg,
);

/// Espejo de `frontend/src/app/laboratorios/page.tsx` en su parte de solo
/// lectura (listado). RN-005 la aplica el backend: esta pantalla muestra
/// tal cual lo que `GET /laboratorios` devuelva.
class LaboratoriosListScreen extends ConsumerWidget {
  const LaboratoriosListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final laboratoriosAsync = ref.watch(laboratoriosListProvider);
    final scheme = Theme.of(context).colorScheme;

    return CustomScrollView(
      slivers: [
        SliverPadding(
          padding: const EdgeInsets.fromLTRB(AppSpacing.lg, AppSpacing.lg, AppSpacing.lg, 0),
          sliver: SliverToBoxAdapter(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Laboratorios', style: Theme.of(context).textTheme.headlineSmall),
                      const SizedBox(height: AppSpacing.xs),
                      Text(
                        'Elegí un laboratorio para ver sus recursos y disponibilidad',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: scheme.onSurfaceVariant),
                      ),
                    ],
                  ),
                ),
                // Sin rotación infinita (la había hasta la Fase 5): un
                // adorno que gira para siempre se percibe como plantilla,
                // no como producto, y además deja un timer pendiente que
                // hace fallar cualquier widget test que monte esta pantalla
                // bajo `FakeAsync`.
                Icon(LucideIcons.compass, size: 28, color: scheme.primary),
              ],
            ),
          ),
        ),
        laboratoriosAsync.when(
          loading: () => SliverPadding(
            padding: const EdgeInsets.all(AppSpacing.lg),
            sliver: SliverGrid(
              gridDelegate: _kGridDelegate,
              delegate: SliverChildBuilderDelegate(
                (context, index) => const LaboratorioCardSkeleton(),
                childCount: 4,
              ),
            ),
          ),
          error: (error, _) => SliverFillRemaining(
            child: ErrorView(
              message: apiErrorMessage(error, fallback: 'No se pudieron cargar los laboratorios.'),
              onRetry: () => ref.invalidate(laboratoriosListProvider),
            ),
          ),
          data: (laboratorios) {
            if (laboratorios.isEmpty) {
              return const SliverFillRemaining(
                child: EmptyView(
                  icon: LucideIcons.building2,
                  message: 'Todavía no hay laboratorios disponibles',
                  detalle: 'Cuando un administrador publique un laboratorio, va a aparecer acá '
                      'con sus recursos y su disponibilidad.',
                ),
              );
            }
            return SliverPadding(
              padding: const EdgeInsets.all(AppSpacing.lg),
              sliver: SliverGrid(
                gridDelegate: _kGridDelegate,
                delegate: SliverChildBuilderDelegate(
                  (context, index) {
                    final laboratorio = laboratorios[index];
                    return LaboratorioCard(
                      laboratorio: laboratorio,
                      onTap: () => context.push(AppRoutes.laboratorioDetalle(laboratorio.id)),
                    ).staggerEntrance(index);
                  },
                  childCount: laboratorios.length,
                ),
              ),
            );
          },
        ),
      ],
    );
  }
}
