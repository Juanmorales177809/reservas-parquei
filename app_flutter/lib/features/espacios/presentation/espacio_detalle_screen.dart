import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import 'package:flutter/services.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_gradients.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/estado_badge.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../../recursos/application/recursos_providers.dart';
import '../../recursos/domain/recurso.dart';
import '../application/espacios_providers.dart';
import '../domain/espacio.dart';
import '../../reservas/presentation/recurso_disponibilidad_sheet.dart';

class EspacioDetalleScreen extends ConsumerWidget {
  const EspacioDetalleScreen({required this.espacioId, super.key});

  final int espacioId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final espacioAsync = ref.watch(espacioProvider(espacioId));

    return Scaffold(
      body: espacioAsync.when(
        loading: () => const LoadingSpinner(),
        error: (error, _) => ErrorView(
          message: apiErrorMessage(error, fallback: 'No se pudo cargar el espacio.'),
          onRetry: () => ref.invalidate(espacioProvider(espacioId)),
        ),
        data: (espacio) => _EspacioDetalleBody(espacio: espacio),
      ),
    );
  }
}

class _EspacioDetalleBody extends ConsumerWidget {
  const _EspacioDetalleBody({required this.espacio});

  final Espacio espacio;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final recursos = ref.watch(recursosPorEspacioProvider(espacio.id));
    final textTheme = Theme.of(context).textTheme;

    return CustomScrollView(
      physics: const BouncingScrollPhysics(),
      slivers: [
        SliverAppBar(
          expandedHeight: 200,
          collapsedHeight: 56,
          pinned: true,
          floating: true,
          snap: true,
          stretch: true,
          backgroundColor: gradientePara(espacio.modalidadReserva).colors.first,
          surfaceTintColor: Colors.transparent,
          shadowColor: AppColors.sombra,
          scrolledUnderElevation: 2,
          elevation: 0,
          systemOverlayStyle: SystemUiOverlayStyle.light,
          iconTheme: const IconThemeData(color: Colors.white),
          flexibleSpace: FlexibleSpaceBar(
            titlePadding: const EdgeInsets.only(left: 56, bottom: AppSpacing.md, right: AppSpacing.lg),
            title: Text(
              espacio.nombre,
              style: textTheme.titleMedium?.copyWith(color: Colors.white),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            expandedTitleScale: 1.18,
            collapseMode: CollapseMode.parallax,
            stretchModes: const [StretchMode.zoomBackground, StretchMode.fadeTitle],
            background: DecoratedBox(
              decoration: BoxDecoration(gradient: gradientePara(espacio.modalidadReserva)),
              child: Stack(
                fit: StackFit.expand,
                children: [
                  Align(
                    alignment: Alignment.topRight,
                    child: Padding(
                      padding: const EdgeInsets.all(AppSpacing.lg),
                      child: Icon(
                        LucideIcons.building2,
                        color: Colors.white.withValues(alpha: 0.35),
                        size: 72,
                      ),
                    ),
                  ),
                  const DecoratedBox(
                    decoration: BoxDecoration(gradient: kGradientScrim),
                  ),
                ],
              ),
            ),
          ),
        ),
        SliverPadding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          sliver: SliverList.list(
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(AppSpacing.lg),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(child: Text('Información', style: textTheme.titleSmall)),
                          EstadoBadge(estado: espacio.estado),
                        ],
                      ),
                      const SizedBox(height: AppSpacing.md),
                      _InfoRow(icon: LucideIcons.mapPin, text: espacio.ubicacion),
                      const SizedBox(height: AppSpacing.sm),
                      _InfoRow(
                        icon: LucideIcons.users,
                        text: espacio.capacidad > 0 ? '${espacio.capacidad} personas' : 'Capacidad sin definir',
                      ),
                      const SizedBox(height: AppSpacing.sm),
                      _InfoRow(
                        icon: LucideIcons.clock,
                        text: '${formatearHora(espacio.horaApertura)} – ${formatearHora(espacio.horaCierre)}',
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: AppSpacing.xl),
              Text('Recursos', style: textTheme.titleMedium),
              const SizedBox(height: AppSpacing.sm),
              if (recursos.isEmpty)
                const EmptyView(
                  icon: LucideIcons.boxes,
                  message: 'Este espacio no tiene recursos activos.',
                )
              else
                ...recursos.map(
                  (recurso) => Padding(
                    padding: const EdgeInsets.only(bottom: AppSpacing.sm),
                    child: _RecursoTile(recurso: recurso),
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 18, color: scheme.onSurfaceVariant),
        const SizedBox(width: AppSpacing.sm),
        Expanded(child: Text(text, style: Theme.of(context).textTheme.bodyMedium)),
      ],
    );
  }
}

class _RecursoTile extends StatelessWidget {
  const _RecursoTile({required this.recurso});

  final Recurso recurso;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: scheme.secondaryContainer,
          foregroundColor: scheme.onSecondaryContainer,
          child: const Icon(LucideIcons.package, size: 20),
        ),
        title: Text(recurso.nombre),
        subtitle: Text('${recurso.tipo.nombre} · capacidad ${recurso.capacidad}'),
        trailing: const Icon(LucideIcons.chevronRight),
        onTap: () => showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          builder: (context) => RecursoDisponibilidadSheet(recurso: recurso),
        ),
      ),
    );
  }
}
