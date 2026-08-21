import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/domain/enums.dart';
import '../../../core/network/api_exception.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/estado_badge.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../../../core/widgets/staggered_entrance.dart';
import '../application/ensayos_providers.dart';
import '../data/ensayos_repository.dart';
import '../domain/ensayo.dart';
import '../../zonas/application/zonas_providers.dart';

class GestionEnsayosScreen extends ConsumerWidget {
  const GestionEnsayosScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ensayosAsync = ref.watch(ensayosGestionProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Ensayos')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _mostrarCrear(context, ref),
        icon: const Icon(LucideIcons.plus, size: 18),
        label: const Text('Nuevo'),
      ),
      body: ensayosAsync.when(
        loading: () => const LoadingSpinner(),
        error: (error, _) => ErrorView(
          message: apiErrorMessage(error, fallback: 'No se pudieron cargar los ensayos.'),
          onRetry: () => ref.invalidate(ensayosGestionProvider),
        ),
        data: (ensayos) {
          if (ensayos.isEmpty) {
            return const EmptyView(icon: LucideIcons.flaskConical, message: 'No hay ensayos registrados.');
          }
          return RefreshIndicator(
            onRefresh: () => ref.refresh(ensayosGestionProvider.future),
            child: ListView.separated(
              padding: const EdgeInsets.all(AppSpacing.lg),
              itemCount: ensayos.length,
              separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.md),
              itemBuilder: (context, index) => _EnsayoCard(ensayo: ensayos[index]).staggerEntrance(index),
            ),
          );
        },
      ),
    );
  }

  void _mostrarCrear(BuildContext context, WidgetRef ref) {
    showDialog<void>(
      context: context,
      builder: (_) => _EnsayoFormDialog(onSaved: () => ref.invalidate(ensayosGestionProvider)),
    );
  }
}

class _EnsayoCard extends ConsumerStatefulWidget {
  const _EnsayoCard({required this.ensayo});
  final Ensayo ensayo;
  @override
  ConsumerState<_EnsayoCard> createState() => _EnsayoCardState();
}

class _EnsayoCardState extends ConsumerState<_EnsayoCard> {
  bool _eliminando = false;

  Future<void> _eliminar() async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Eliminar ensayo'),
        content: Text('¿Eliminar "${widget.ensayo.nombre}"?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Eliminar')),
        ],
      ),
    );
    if (confirmar != true || !mounted) return;
    setState(() => _eliminando = true);
    try {
      await ref.read(ensayosRepositoryProvider).eliminar(widget.ensayo.id);
      ref.invalidate(ensayosGestionProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Ensayo eliminado.')));
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo eliminar el ensayo.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _eliminando = false);
    }
  }

  void _editar() {
    showDialog<void>(
      context: context,
      builder: (_) => _EnsayoFormDialog(ensayo: widget.ensayo, onSaved: () => ref.invalidate(ensayosGestionProvider)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final e = widget.ensayo;
    final textTheme = Theme.of(context).textTheme;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(child: Text(e.nombre, style: textTheme.titleMedium)),
                EstadoBadge(estado: e.estado),
              ],
            ),
            const SizedBox(height: AppSpacing.xs),
            Text('Zona ${e.zonaId} · ID ${e.id}', style: textTheme.bodySmall?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant)),
            const SizedBox(height: AppSpacing.md),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                OutlinedButton.icon(
                  onPressed: _eliminando ? null : _editar,
                  icon: const Icon(LucideIcons.pencil, size: 14),
                  label: const Text('Editar'),
                ),
                const SizedBox(width: AppSpacing.sm),
                FilledButton.tonalIcon(
                  onPressed: _eliminando ? null : _eliminar,
                  icon: _eliminando
                      ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(LucideIcons.trash2, size: 14),
                  label: const Text('Eliminar'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _EnsayoFormDialog extends ConsumerStatefulWidget {
  const _EnsayoFormDialog({this.ensayo, required this.onSaved});
  final Ensayo? ensayo;
  final VoidCallback onSaved;
  @override
  ConsumerState<_EnsayoFormDialog> createState() => _EnsayoFormDialogState();
}

class _EnsayoFormDialogState extends ConsumerState<_EnsayoFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late String _nombre;
  late EstadoEntidad _estado;
  int? _zonaId;
  bool _guardando = false;
  String? _error;

  bool get _esEdicion => widget.ensayo != null;

  @override
  void initState() {
    super.initState();
    final en = widget.ensayo;
    _nombre = en?.nombre ?? '';
    _estado = en?.estado ?? EstadoEntidad.activo;
    _zonaId = en?.zonaId;
  }

  Future<void> _guardar() async {
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();
    if (_zonaId == null) {
      setState(() => _error = 'Seleccioná una zona.');
      return;
    }
    setState(() {
      _guardando = true;
      _error = null;
    });
    try {
      final repo = ref.read(ensayosRepositoryProvider);
      if (_esEdicion) {
        await repo.actualizar(widget.ensayo!.id, nombre: _nombre, zonaId: _zonaId, estado: _estado.name);
      } else {
        await repo.crear(nombre: _nombre, zonaId: _zonaId!, estado: _estado.name);
      }
      widget.onSaved();
      if (mounted) Navigator.pop(context);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(_esEdicion ? 'Ensayo actualizado.' : 'Ensayo creado.')));
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(e, fallback: _esEdicion ? 'No se pudo actualizar el ensayo.' : 'No se pudo crear el ensayo.'));
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final zonasAsync = ref.watch(zonasGestionProvider);

    return AlertDialog(
      title: Text(_esEdicion ? 'Editar ensayo' : 'Nuevo ensayo'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                initialValue: _nombre,
                decoration: const InputDecoration(labelText: 'Nombre *'),
                validator: (v) => (v == null || v.trim().isEmpty) ? 'Requerido' : null,
                onSaved: (v) => _nombre = v!.trim(),
              ),
              const SizedBox(height: AppSpacing.md),
              zonasAsync.when(
                loading: () => const LinearProgressIndicator(),
                error: (e, _) => Text(apiErrorMessage(e, fallback: 'No se pudieron cargar las zonas.')),
                data: (zonas) => DropdownButtonFormField<int>(
                  initialValue: _zonaId ?? (zonas.isNotEmpty ? zonas.first.id : null),
                  decoration: const InputDecoration(labelText: 'Zona *'),
                  items: zonas.map((z) => DropdownMenuItem(value: z.id, child: Text('${z.nombre} (id ${z.id})'))).toList(),
                  onChanged: (v) => setState(() => _zonaId = v),
                  validator: (v) => v == null ? 'Requerido' : null,
                  onSaved: (v) => _zonaId = v,
                ),
              ),
              const SizedBox(height: AppSpacing.md),
              DropdownButtonFormField<EstadoEntidad>(
                initialValue: _estado,
                decoration: const InputDecoration(labelText: 'Estado'),
                items: EstadoEntidad.values.map((e) => DropdownMenuItem(value: e, child: Text(e.name))).toList(),
                onChanged: (v) => setState(() => _estado = v!),
                onSaved: (v) => _estado = v!,
              ),
              if (_error != null) ...[
                const SizedBox(height: AppSpacing.sm),
                Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
              ],
            ],
          ),
        ),
      ),
      actions: [
        TextButton(onPressed: _guardando ? null : () => Navigator.pop(context), child: const Text('Cancelar')),
        FilledButton(
          onPressed: _guardando ? null : _guardar,
          child: _guardando
              ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
              : Text(_esEdicion ? 'Guardar' : 'Crear'),
        ),
      ],
    );
  }
}
