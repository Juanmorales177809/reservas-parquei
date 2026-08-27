// ignore_for_file: use_build_context_synchronously
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/domain/enums.dart';
import '../../../core/network/api_exception.dart';
import '../../../core/router/app_routes.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../../../core/widgets/staggered_entrance.dart';
import '../../espacios/domain/espacio.dart' show formatearHora;
import '../application/reservas_providers.dart';
import '../data/reservas_repository.dart';
import '../domain/reserva.dart';
import 'estado_reserva_badge.dart';

/// Espejo de la lista de "mis reservas" de `frontend/src/app/espacios/page.tsx`
/// (hoy embebida en esa página vía `GET /reservas/mis-reservas`) — acá vive
/// en su propia pantalla, coherente con el resto de la navegación de la app.
class MisReservasScreen extends ConsumerWidget {
  const MisReservasScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final reservasAsync = ref.watch(misReservasProvider);

    return reservasAsync.when(
      loading: () => const LoadingSpinner(),
      error: (error, _) => ErrorView(
        message: apiErrorMessage(error, fallback: 'No se pudieron cargar tus reservas.'),
        onRetry: () => ref.invalidate(misReservasProvider),
      ),
      data: (reservas) {
        if (reservas.isEmpty) {
          return EmptyView(
            icon: LucideIcons.calendarX,
            message: 'Todavía no tenés reservas',
            detalle: 'Elegí un espacio, mirá su disponibilidad y reservá una franja horaria.',
            accion: FilledButton.icon(
              onPressed: () => context.go(AppRoutes.espacios),
              icon: const Icon(LucideIcons.building2, size: 18),
              label: const Text('Ver espacios'),
            ),
          );
        }
        // Agrupado por tiempo con encabezado adhesivo (como auditoría por día).
        // `fecha` es `YYYY-MM-DD` naive en `America/Bogota` — el backend no
        // expone un "hoy" canónico, así que se compara contra el hoy de esa
        // zona calculado desde el reloj del dispositivo en UTC-5 (Bogotá no
        // tiene horario de verano). Comparar contra `DateTime.now()` local
        // daría una etiqueta equivocada fuera de esa zona (mismo riesgo que
        // hizo que auditoría evitara "Hoy"/"Ayer").
        final hoyStr = _hoyBogotaStr();
        final limiteSemanaStr = _hoyBogotaPlusDiasStr(7, hoyStr);
        final grupos = <_GrupoReserva, List<Reserva>>{
          _GrupoReserva.hoy: [],
          _GrupoReserva.estaSemana: [],
          _GrupoReserva.proximas: [],
          _GrupoReserva.pasadas: [],
        };
        for (final r in reservas) {
          grupos[_grupoPara(r.fecha, hoyStr, limiteSemanaStr)]!.add(r);
        }
        // Orden interno: futuras ascendente (la más próxima primero), pasadas
        // descendente (la más reciente primero) — es lo que el ojo espera en
        // cada bloque.
        for (final entry in grupos.entries) {
          entry.value.sort((a, b) {
            final cmpFecha = a.fecha.compareTo(b.fecha);
            if (cmpFecha != 0) {
              return entry.key == _GrupoReserva.pasadas ? -cmpFecha : cmpFecha;
            }
            return a.horaInicio.compareTo(b.horaInicio);
          });
        }
        final ordenGrupos = [
          _GrupoReserva.hoy,
          _GrupoReserva.estaSemana,
          _GrupoReserva.proximas,
          _GrupoReserva.pasadas,
        ];
        final gruposConDatos = ordenGrupos.where((g) => grupos[g]!.isNotEmpty).toList();

        return RefreshIndicator(
          onRefresh: () => ref.refresh(misReservasProvider.future),
          child: CustomScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            slivers: [
              for (final grupo in gruposConDatos)
                SliverMainAxisGroup(
                  slivers: [
                    SliverPersistentHeader(
                      pinned: true,
                      delegate: _EncabezadoGrupoReserva(grupo: grupo, cantidad: grupos[grupo]!.length),
                    ),
                    SliverPadding(
                      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg),
                      sliver: SliverList.separated(
                        itemCount: grupos[grupo]!.length,
                        separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.md),
                        itemBuilder: (context, index) {
                          final globalIndex = ordenGrupos.indexOf(grupo) * 100 + index;
                          return _ReservaCard(reserva: grupos[grupo]![index]).staggerEntrance(globalIndex);
                        },
                      ),
                    ),
                    const SliverToBoxAdapter(child: SizedBox(height: AppSpacing.lg)),
                  ],
                ),
            ],
          ),
        );
      },
    );
  }
}

class _ReservaCard extends ConsumerStatefulWidget {
  const _ReservaCard({required this.reserva});

  final Reserva reserva;

  @override
  ConsumerState<_ReservaCard> createState() => _ReservaCardState();
}

class _ReservaCardState extends ConsumerState<_ReservaCard> {
  bool _cancelando = false;

  Future<void> _confirmarCancelacion() async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('¿Cancelar esta reserva?'),
        content: Text(
          '${widget.reserva.espacio.nombre} · ${_formatearFecha(widget.reserva.fecha)} · '
          '${formatearHora(widget.reserva.horaInicio)}–${formatearHora(widget.reserva.horaFin)}',
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Volver')),
          FilledButton.tonal(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Cancelar reserva'),
          ),
        ],
      ),
    );
    if (confirmar != true) return;

    setState(() => _cancelando = true);
    try {
      await ref.read(reservasRepositoryProvider).cancelar(widget.reserva.id);
      ref.invalidate(misReservasProvider);
    } on Object catch (e) {
      if (mounted) {
        final mensaje = apiErrorMessage(e, fallback: 'No se pudo cancelar la reserva.');
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(mensaje)));
      }
    } finally {
      if (mounted) setState(() => _cancelando = false);
    }
  }

  Future<void> _editarReserva(BuildContext context) async {
    final formKey = GlobalKey<FormState>();
    final fecha = widget.reserva.fecha;
    final horaInicio = widget.reserva.horaInicio.substring(0, 5);
    final horaFin = widget.reserva.horaFin.substring(0, 5);
    final asistentes = widget.reserva.asistentes;
    final fechaCtrl = TextEditingController(text: fecha);
    final inicioCtrl = TextEditingController(text: horaInicio);
    final finCtrl = TextEditingController(text: horaFin);
    final asistCtrl = TextEditingController(text: '$asistentes');
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Editar reserva'),
        content: SingleChildScrollView(
          child: Form(
            key: formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  controller: fechaCtrl,
                  decoration: const InputDecoration(labelText: 'Fecha (YYYY-MM-DD)'),
                  readOnly: true,
                  onTap: () async {
                    final ini = DateTime.tryParse(fechaCtrl.text) ?? DateTime.now();
                    final picked = await showDatePicker(context: ctx, initialDate: ini, firstDate: DateTime(2020), lastDate: DateTime(2030));
                    if (picked != null) {
                      final f = '${picked.year.toString().padLeft(4, '0')}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}';
                      fechaCtrl.text = f;
                    }
                  },
                  validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null,
                ),
                const SizedBox(height: AppSpacing.md),
                TextFormField(
                  controller: inicioCtrl,
                  decoration: const InputDecoration(labelText: 'Hora inicio (HH:MM)'),
                  validator: (v) => (v == null || !RegExp(r'^\d{2}:\d{2}$').hasMatch(v)) ? 'Formato HH:MM' : null,
                ),
                const SizedBox(height: AppSpacing.md),
                TextFormField(
                  controller: finCtrl,
                  decoration: const InputDecoration(labelText: 'Hora fin (HH:MM)'),
                  validator: (v) => (v == null || !RegExp(r'^\d{2}:\d{2}$').hasMatch(v)) ? 'Formato HH:MM' : null,
                ),
                const SizedBox(height: AppSpacing.md),
                TextFormField(
                  controller: asistCtrl,
                  decoration: const InputDecoration(labelText: 'Asistentes'),
                  keyboardType: TextInputType.number,
                  validator: (v) {
                    final n = int.tryParse(v ?? '');
                    if (n == null || n <= 0) return 'Debe ser > 0';
                    return null;
                  },
                ),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => { if (formKey.currentState!.validate()) Navigator.pop(ctx, true) }, child: const Text('Guardar')),
        ],
      ),
    );
    if (ok != true) return;
    setState(() => _cancelando = true);
    try {
      final parsedFecha = DateTime.parse(fechaCtrl.text);
      await ref.read(reservasRepositoryProvider).actualizar(
            widget.reserva.id,
            fecha: parsedFecha,
            horaInicio: inicioCtrl.text,
            horaFin: finCtrl.text,
            asistentes: int.parse(asistCtrl.text),
          );
      ref.invalidate(misReservasProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Reserva actualizada.')));
    } on Object catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo actualizar la reserva.'))));
    } finally {
      if (mounted) setState(() => _cancelando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final reserva = widget.reserva;
    final textTheme = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final nombresRecursos = reserva.recursos.map((r) => r.nombre).join(', ');

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(child: Text(reserva.espacio.nombre, style: textTheme.titleMedium)),
                EstadoReservaBadge(estado: reserva.estado),
              ],
            ),
            if (nombresRecursos.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.xs),
              Text(nombresRecursos, style: textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant)),
            ],
            const SizedBox(height: AppSpacing.sm),
            Row(
              children: [
                Icon(LucideIcons.calendarDays, size: 16, color: scheme.onSurfaceVariant),
                const SizedBox(width: AppSpacing.xs),
                Text(_formatearFecha(reserva.fecha), style: textTheme.bodyMedium),
                const SizedBox(width: AppSpacing.md),
                Icon(LucideIcons.clock, size: 16, color: scheme.onSurfaceVariant),
                const SizedBox(width: AppSpacing.xs),
                Text(
                  '${formatearHora(reserva.horaInicio)}–${formatearHora(reserva.horaFin)}',
                  style: textTheme.bodyMedium,
                ),
              ],
            ),
            const SizedBox(height: AppSpacing.xs),
            Row(
              children: [
                Icon(LucideIcons.users, size: 16, color: scheme.onSurfaceVariant),
                const SizedBox(width: AppSpacing.xs),
                Text('${reserva.asistentes} asistentes', style: textTheme.bodyMedium),
              ],
            ),
            if (reserva.descripcion != null && reserva.descripcion!.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.xs),
              Text(
                reserva.descripcion!,
                style: textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant),
              ),
            ],
            if (reserva.estado == EstadoReserva.rechazada && reserva.motivoRechazo != null) ...[
              const SizedBox(height: AppSpacing.sm),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(AppSpacing.sm),
                decoration: BoxDecoration(
                  color: AppEstados.negativo.tinte,
                  borderRadius: BorderRadius.circular(AppRadius.sm),
                  border: Border.all(color: AppEstados.negativo.borde.withValues(alpha: 0.4)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(LucideIcons.info, size: 14, color: AppEstados.negativo.sobreTinte),
                    const SizedBox(width: AppSpacing.xs),
                    Expanded(
                      child: Text(
                        'Motivo: ${reserva.motivoRechazo}',
                        style: textTheme.bodySmall?.copyWith(color: AppEstados.negativo.sobreTinte),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            if (reserva.estado == EstadoReserva.esperando) ...[
              const SizedBox(height: AppSpacing.md),
              Align(
                alignment: Alignment.centerRight,
                child: OutlinedButton.icon(
                  onPressed: _cancelando ? null : () => _editarReserva(context),
                  icon: const Icon(LucideIcons.pencil, size: 16),
                  label: const Text('Editar'),
                ),
              ),
            ],
            if (reserva.puedeCancelarse) ...[
              const SizedBox(height: AppSpacing.md),
              Align(
                alignment: Alignment.centerRight,
                child: OutlinedButton.icon(
                  onPressed: _cancelando ? null : _confirmarCancelacion,
                  icon: _cancelando
                      ? const SizedBox(height: 14, width: 14, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(LucideIcons.x, size: 16),
                  label: const Text('Cancelar'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// `"YYYY-MM-DD"` -> `"DD/MM/YYYY"`, manipulación de texto pura — sin
/// pasar por `DateTime` (mismo criterio que `formatearHora`, ver riesgo de
/// fechas/horas del plan de migración).
String _formatearFecha(String fechaIso) {
  final partes = fechaIso.split('-');
  if (partes.length != 3) return fechaIso;
  return '${partes[2]}/${partes[1]}/${partes[0]}';
}

enum _GrupoReserva { hoy, estaSemana, proximas, pasadas }

String _etiquetaGrupo(_GrupoReserva g) => switch (g) {
      _GrupoReserva.hoy => 'HOY',
      _GrupoReserva.estaSemana => 'ESTA SEMANA',
      _GrupoReserva.proximas => 'PRÓXIMAS',
      _GrupoReserva.pasadas => 'PASADAS',
    };

String _hoyBogotaStr() {
  final ahoraUtc = DateTime.now().toUtc();
  final bogota = ahoraUtc.subtract(const Duration(hours: 5));
  return '${bogota.year.toString().padLeft(4, '0')}-${bogota.month.toString().padLeft(2, '0')}-${bogota.day.toString().padLeft(2, '0')}';
}

String _hoyBogotaPlusDiasStr(int dias, String hoyStr) {
  final partes = hoyStr.split('-');
  if (partes.length != 3) return hoyStr;
  final y = int.tryParse(partes[0]) ?? 2026;
  final m = int.tryParse(partes[1]) ?? 1;
  final d = int.tryParse(partes[2]) ?? 1;
  final base = DateTime.utc(y, m, d);
  final destino = base.add(Duration(days: dias));
  return '${destino.year.toString().padLeft(4, '0')}-${destino.month.toString().padLeft(2, '0')}-${destino.day.toString().padLeft(2, '0')}';
}

_GrupoReserva _grupoPara(String fecha, String hoyStr, String limiteSemanaStr) {
  if (fecha == hoyStr) return _GrupoReserva.hoy;
  if (fecha.compareTo(hoyStr) < 0) return _GrupoReserva.pasadas;
  if (fecha.compareTo(limiteSemanaStr) <= 0) return _GrupoReserva.estaSemana;
  return _GrupoReserva.proximas;
}

class _EncabezadoGrupoReserva extends SliverPersistentHeaderDelegate {
  const _EncabezadoGrupoReserva({required this.grupo, required this.cantidad});

  final _GrupoReserva grupo;
  final int cantidad;

  @override
  double get minExtent => 36;

  @override
  double get maxExtent => 36;

  @override
  Widget build(BuildContext context, double shrinkOffset, bool overlapsContent) {
    return Container(
      color: AppColors.fondo,
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg, vertical: AppSpacing.sm),
      alignment: Alignment.centerLeft,
      child: Row(
        children: [
          Text(_etiquetaGrupo(grupo), style: AppText.overline()),
          const SizedBox(width: AppSpacing.sm),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: AppColors.superficie,
              borderRadius: BorderRadius.circular(AppRadius.pill),
              border: Border.all(color: AppColors.borde),
            ),
            child: Text(
              '$cantidad',
              style: AppText.numerico(fontSize: 11, color: AppColors.textoTerciario, fontWeight: FontWeight.w700),
            ),
          ),
        ],
      ),
    );
  }

  @override
  bool shouldRebuild(covariant _EncabezadoGrupoReserva old) => old.grupo != grupo || old.cantidad != cantidad;
}
