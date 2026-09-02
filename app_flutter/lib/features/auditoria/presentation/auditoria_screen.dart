import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/export_button.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../application/auditoria_providers.dart';
import '../data/auditoria_repository.dart';
import '../domain/control_cambio.dart';

/// Historial de operaciones administrativas (`require_admin`, solo lectura).
///
/// **Fase 6: pasó de tarjetas a filas densas.** Un log se escanea
/// verticalmente buscando un patrón; con una tarjeta elevada por evento,
/// cada entrada reclama la misma atención que las demás y el ojo no puede
/// recorrer la lista. Ahora son filas separadas por un divisor de 1px, con
/// un punto de color del tipo de acción en vez de un icono (con cinco
/// tipos, el punto alcanza y deja la fila mucho más limpia).
class AuditoriaScreen extends ConsumerWidget {
  const AuditoriaScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cambiosAsync = ref.watch(controlCambiosListProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Auditoría'),
        actions: [
          ExportButton(
            nombreArchivo: 'auditoria',
            mensajeExito: 'Auditoría exportada.',
            onExportar: (formato) => ref.read(auditoriaRepositoryProvider).exportar(formato),
          ),
        ],
      ),
      body: cambiosAsync.when(
        loading: () => const LoadingSpinner(),
        error: (error, _) => ErrorView(
          message: apiErrorMessage(error, fallback: 'No se pudo cargar el historial de cambios.'),
          onRetry: () => ref.invalidate(controlCambiosListProvider),
        ),
        data: (cambios) {
          if (cambios.isEmpty) {
            return const EmptyView(
              icon: LucideIcons.history,
              message: 'Todavía no hay cambios registrados',
              detalle: 'Acá aparecen las operaciones administrativas: altas, ediciones, '
                  'bajas y cambios de estado, con quién las hizo y cuándo.',
            );
          }

          // Agrupado por día: una lista plana de 200 eventos obliga a leer
          // cada marca temporal para ubicarse en el tiempo.
          final grupos = <String, List<ControlCambio>>{};
          for (final c in cambios) {
            grupos.putIfAbsent(_soloFecha(c.createdAt), () => []).add(c);
          }

          return RefreshIndicator(
            onRefresh: () => ref.refresh(controlCambiosListProvider.future),
            child: CustomScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              slivers: [
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(AppSpacing.xl, AppSpacing.lg, AppSpacing.xl, AppSpacing.sm),
                    child: Text(
                      'Últimas ${cambios.length} operaciones administrativas',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ),
                ),
                for (final entrada in grupos.entries)
                  SliverMainAxisGroup(
                    slivers: [
                      SliverPersistentHeader(
                        pinned: true,
                        delegate: _EncabezadoDia(fecha: entrada.key),
                      ),
                      SliverList.separated(
                        itemCount: entrada.value.length,
                        separatorBuilder: (_, _) => const Divider(height: 1, thickness: 1, color: AppColors.borde),
                        itemBuilder: (context, i) => _FilaCambio(cambio: entrada.value[i]),
                      ),
                    ],
                  ),
                const SliverToBoxAdapter(child: SizedBox(height: AppSpacing.xl)),
              ],
            ),
          );
        },
      ),
    );
  }
}

/// `"YYYY-MM-DDTHH:MM:SS.ffffff"` → `"YYYY-MM-DD"`.
String _soloFecha(String raw) => raw.split('T').first;

/// `"YYYY-MM-DD"` → `"DD/MM/YYYY"`.
///
/// No se calcula "Hoy"/"Ayer" a propósito: `created_at` llega naive en
/// `America/Bogota` (ver `services/reloj.py`) y compararlo contra la fecha
/// local del dispositivo daría una etiqueta equivocada para cualquiera que
/// no esté en esa espacio — un error silencioso, que es exactamente el riesgo
/// que documenta el plan de migración sobre fechas.
String _formatearDia(String fecha) {
  final partes = fecha.split('-');
  if (partes.length != 3) return fecha;
  return '${partes[2]}/${partes[1]}/${partes[0]}';
}

/// `"...THH:MM:SS.ffffff"` → `"HH:MM"`.
String _formatearHora(String raw) {
  final partes = raw.split('T');
  if (partes.length != 2 || partes[1].length < 5) return '';
  return partes[1].substring(0, 5);
}

Color _colorAccion(String accion) => switch (accion) {
      'crear' => AppEstados.positivo.relleno,
      'actualizar' || 'configurar' || 'reenviar_invitacion' => AppColors.accion,
      'eliminar' || 'cancelar' => AppEstados.negativo.relleno,
      'cambiar estado' => AppEstados.pendiente.relleno,
      'marcar_asistencia' => AppEstados.positivo.borde,
      _ => AppColors.textoTerciario,
    };

class _EncabezadoDia extends SliverPersistentHeaderDelegate {
  const _EncabezadoDia({required this.fecha});

  final String fecha;

  @override
  double get minExtent => 34;

  @override
  double get maxExtent => 34;

  @override
  Widget build(BuildContext context, double shrinkOffset, bool overlapsContent) {
    return Container(
      color: AppColors.fondo,
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xl, vertical: AppSpacing.sm),
      alignment: Alignment.centerLeft,
      child: Text(_formatearDia(fecha).toUpperCase(), style: AppText.overline()),
    );
  }

  @override
  bool shouldRebuild(covariant _EncabezadoDia oldDelegate) => oldDelegate.fecha != fecha;
}

class _FilaCambio extends StatelessWidget {
  const _FilaCambio({required this.cambio});

  final ControlCambio cambio;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Container(
      color: AppColors.superficie,
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xl, vertical: AppSpacing.md),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 6),
            child: Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(color: _colorAccion(cambio.accion), shape: BoxShape.circle),
            ),
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(cambio.descripcion, style: textTheme.bodyMedium),
                const SizedBox(height: 2),
                Text(
                  cambio.entidadId != null
                      ? '${cambio.usuario} · ${cambio.entidad} #${cambio.entidadId}'
                      : '${cambio.usuario} · ${cambio.entidad}',
                  style: textTheme.bodySmall,
                ),
              ],
            ),
          ),
          const SizedBox(width: AppSpacing.md),
          Text(
            _formatearHora(cambio.createdAt),
            style: AppText.numerico(
              fontSize: 12,
              color: AppColors.textoTerciario,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
