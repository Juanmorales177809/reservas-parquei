import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import 'package:flutter/services.dart';

import '../../../core/domain/enums.dart';
import '../../../core/network/api_exception.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_gradients.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/estado_badge.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../../recursos/application/recursos_providers.dart';
import '../../recursos/domain/recurso.dart';
import '../../espacios/application/espacios_providers.dart';
import '../application/laboratorios_providers.dart';
import '../domain/laboratorio.dart';
import '../../reservas/presentation/laboratorio_reserva_sheet.dart';
import '../../reservas/presentation/recurso_disponibilidad_sheet.dart';

class LaboratorioDetalleScreen extends ConsumerWidget {
  const LaboratorioDetalleScreen({required this.laboratorioId, super.key});

  final int laboratorioId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final laboratorioAsync = ref.watch(laboratorioProvider(laboratorioId));

    // Sin `Scaffold` propio (Fase 6 de
    // ~/.claude/plans/dazzling-wobbling-zebra.md — bug del navbar que
    // desaparecía): esta pantalla ahora vive DENTRO del `ShellRoute`, así
    // que ya está montada sobre el `Scaffold` del shell activo
    // (`BottomNavShell`/`RailNavShell`/`TopNavShell`). El `SliverAppBar` de
    // abajo no necesita un `Scaffold` propio para funcionar -- ya resuelve
    // `pinned`/`floating`/`snap` dentro del `CustomScrollView`, y el botón
    // "atrás" lo sigue agregando Flutter automáticamente por
    // `ModalRoute.canPop`, no por el `Scaffold`.
    return laboratorioAsync.when(
      loading: () => const LoadingSpinner(),
      error: (error, _) => ErrorView(
        message: apiErrorMessage(error, fallback: 'No se pudo cargar el laboratorio.'),
        onRetry: () => ref.invalidate(laboratorioProvider(laboratorioId)),
      ),
      data: (laboratorio) => _LaboratorioDetalleBody(laboratorio: laboratorio),
    );
  }
}

class _LaboratorioDetalleBody extends ConsumerWidget {
  const _LaboratorioDetalleBody({required this.laboratorio});

  final Laboratorio laboratorio;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final recursos = ref.watch(recursosPorLaboratorioProvider(laboratorio.id));
    final espaciosAsync = ref.watch(espaciosGestionProvider);
    final espacios = (espaciosAsync.value ?? []).where((z) => z.laboratorioId == laboratorio.id).toList();
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
          backgroundColor: kGradienteLaboratorio.colors.first,
          surfaceTintColor: Colors.transparent,
          shadowColor: AppColors.sombra,
          scrolledUnderElevation: 2,
          elevation: 0,
          systemOverlayStyle: SystemUiOverlayStyle.light,
          iconTheme: const IconThemeData(color: Colors.white),
          flexibleSpace: FlexibleSpaceBar(
            titlePadding: const EdgeInsets.only(left: 56, bottom: AppSpacing.md, right: AppSpacing.lg),
            title: Text(
              laboratorio.nombre,
              style: textTheme.titleMedium?.copyWith(color: Colors.white),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            expandedTitleScale: 1.18,
            collapseMode: CollapseMode.parallax,
            stretchModes: const [StretchMode.zoomBackground, StretchMode.fadeTitle],
            background: DecoratedBox(
              decoration: BoxDecoration(gradient: kGradienteLaboratorio),
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
                          EstadoBadge(estado: laboratorio.estado),
                        ],
                      ),
                      const SizedBox(height: AppSpacing.md),
                      _InfoRow(icon: LucideIcons.mapPin, text: laboratorio.ubicacion),
                      const SizedBox(height: AppSpacing.sm),
                      _InfoRow(
                        icon: LucideIcons.users,
                        text: laboratorio.capacidad > 0 ? '${laboratorio.capacidad} personas' : 'Capacidad sin definir',
                      ),
                      const SizedBox(height: AppSpacing.sm),
                      _InfoRow(
                        icon: LucideIcons.clock,
                        text: '${formatearHora(laboratorio.horaApertura)} – ${formatearHora(laboratorio.horaCierre)}',
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: AppSpacing.md),
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  onPressed: () => _mostrarMotivoSolicitud(context, laboratorio),
                  icon: const Icon(LucideIcons.calendarPlus, size: 18),
                  label: const Text('Nueva solicitud'),
                ),
              ),
              const SizedBox(height: AppSpacing.xl),
              // Sin ModalidadLaboratorio (removido, ver Fase 3 de
              // ~/.claude/plans/dazzling-wobbling-zebra.md): cada sección
              // se muestra si el laboratorio efectivamente tiene ese tipo de
              // dato, en vez de por una configuración explícita.
              if (recursos.isNotEmpty) ...[
                Text('Recursos', style: textTheme.titleMedium),
                const SizedBox(height: AppSpacing.sm),
                ...recursos.map(
                  (recurso) => Padding(
                    padding: const EdgeInsets.only(bottom: AppSpacing.sm),
                    child: _RecursoTile(recurso: recurso),
                  ),
                ),
              ],
              if (espacios.isNotEmpty) ...[
                const SizedBox(height: AppSpacing.lg),
                Text('Espacios', style: textTheme.titleMedium),
                const SizedBox(height: AppSpacing.sm),
                ...espacios.map((z) => Card(
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: Theme.of(context).colorScheme.tertiaryContainer,
                            child: const Icon(LucideIcons.mapPinned, size: 20),
                          ),
                          title: Text(z.nombre),
                          subtitle: Text(z.descripcion ?? ''),
                          trailing: Text('${z.capacidad ?? laboratorio.capacidad} cap.', style: Theme.of(context).textTheme.bodySmall),
                        ),
                      )),
              ],
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

/// Espejo de la pregunta 11 del formulario real de solicitud de
/// laboratorios: el motivo bifurca el resto del formulario. Motivos 1 y 2
/// abren el `LaboratorioReservaSheet` de siempre (ya denso: recursos+espacios+
/// acompañantes+disponibilidad+descripción) con `tipoSolicitud`
/// prefijado -- no vale la pena convertirlo en un formulario de 4 ramas.
/// Motivos 3 y 4 (orden de salida, mano de obra) quedan deshabilitados
/// hasta la Fase C: no encajan en el modelo de "franja horaria de un día"
/// de `Reserva` (una es un rango de días, la otra no usa ningún recurso).
void _mostrarMotivoSolicitud(BuildContext context, Laboratorio laboratorio) {
  showDialog<void>(
    context: context,
    builder: (dialogContext) => _MotivoSolicitudDialog(laboratorio: laboratorio),
  );
}

class _MotivoSolicitudDialog extends StatelessWidget {
  const _MotivoSolicitudDialog({required this.laboratorio});

  final Laboratorio laboratorio;

  void _elegir(BuildContext context, TipoSolicitud tipoSolicitud) {
    Navigator.pop(context);
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => LaboratorioReservaSheet(laboratorio: laboratorio, tipoSolicitud: tipoSolicitud),
    );
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return SimpleDialog(
      title: const Text('Motivo de la solicitud'),
      children: [
        ListTile(
          leading: const Icon(LucideIcons.building2),
          title: Text(tipoSolicitudLabel(TipoSolicitud.reservaEnLaboratorio)),
          onTap: () => _elegir(context, TipoSolicitud.reservaEnLaboratorio),
        ),
        ListTile(
          leading: const Icon(LucideIcons.mapPin),
          title: Text(tipoSolicitudLabel(TipoSolicitud.reservaFueraLaboratorio)),
          onTap: () => _elegir(context, TipoSolicitud.reservaFueraLaboratorio),
        ),
        ListTile(
          enabled: false,
          leading: Icon(LucideIcons.truck, color: scheme.onSurfaceVariant.withValues(alpha: 0.5)),
          title: const Text('Orden de salida (equipos fuera de la sede)'),
          subtitle: const Text('Próximamente'),
        ),
        ListTile(
          enabled: false,
          leading: Icon(LucideIcons.hardHat, color: scheme.onSurfaceVariant.withValues(alpha: 0.5)),
          title: const Text('Mano de obra'),
          subtitle: const Text('Próximamente'),
        ),
      ],
    );
  }
}
