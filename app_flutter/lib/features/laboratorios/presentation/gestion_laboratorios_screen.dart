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
import '../application/laboratorios_providers.dart';
import '../data/laboratorios_repository.dart';
import '../domain/laboratorio.dart';

class GestionLaboratoriosScreen extends ConsumerWidget {
  const GestionLaboratoriosScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final laboratoriosAsync = ref.watch(laboratoriosListProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Laboratorios')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _mostrarCrear(context, ref),
        icon: const Icon(LucideIcons.plus, size: 18),
        label: const Text('Nuevo'),
      ),
      body: laboratoriosAsync.when(
        loading: () => const LoadingSpinner(),
        error: (error, _) => ErrorView(
          message: apiErrorMessage(error, fallback: 'No se pudieron cargar los laboratorios.'),
          onRetry: () => ref.invalidate(laboratoriosListProvider),
        ),
        data: (laboratorios) {
          if (laboratorios.isEmpty) {
            return const EmptyView(icon: LucideIcons.building2, message: 'No hay laboratorios registrados.');
          }
          return RefreshIndicator(
            onRefresh: () => ref.refresh(laboratoriosListProvider.future),
            child: ListView.separated(
              padding: const EdgeInsets.all(AppSpacing.lg),
              itemCount: laboratorios.length,
              separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.md),
              itemBuilder: (context, index) => _LaboratorioCard(laboratorio: laboratorios[index]).staggerEntrance(index),
            ),
          );
        },
      ),
    );
  }

  void _mostrarCrear(BuildContext context, WidgetRef ref) {
    showDialog<void>(
      context: context,
      builder: (_) => _LaboratorioFormDialog(onSaved: () => ref.invalidate(laboratoriosListProvider)),
    );
  }
}

class _LaboratorioCard extends ConsumerStatefulWidget {
  const _LaboratorioCard({required this.laboratorio});
  final Laboratorio laboratorio;
  @override
  ConsumerState<_LaboratorioCard> createState() => _LaboratorioCardState();
}

class _LaboratorioCardState extends ConsumerState<_LaboratorioCard> {
  bool _eliminando = false;
  bool _cambiandoEstado = false;

  Future<void> _eliminar() async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Eliminar laboratorio'),
        content: Text('¿Eliminar "${widget.laboratorio.nombre}"? Esta acción no se puede deshacer.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Eliminar')),
        ],
      ),
    );
    if (confirmar != true || !mounted) return;
    setState(() => _eliminando = true);
    try {
      await ref.read(laboratoriosRepositoryProvider).eliminar(widget.laboratorio.id);
      ref.invalidate(laboratoriosListProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Laboratorio eliminado.')));
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo eliminar el laboratorio.'))));
      }
    } finally {
      if (mounted) setState(() => _eliminando = false);
    }
  }

  Future<void> _toggleEstado() async {
    setState(() => _cambiandoEstado = true);
    try {
      final siguiente = switch (widget.laboratorio.estado) {
        EstadoEntidad.activo => EstadoEntidad.inactivo,
        EstadoEntidad.inactivo => EstadoEntidad.mantenimiento,
        EstadoEntidad.mantenimiento => EstadoEntidad.activo,
      };
      await ref.read(laboratoriosRepositoryProvider).actualizar(widget.laboratorio.id, estado: siguiente.name);
      ref.invalidate(laboratoriosListProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Estado cambiado a ${siguiente.name}.')));
    } on Object catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo cambiar el estado.'))));
    } finally {
      if (mounted) setState(() => _cambiandoEstado = false);
    }
  }

  void _editar() {
    showDialog<void>(
      context: context,
      builder: (_) => _LaboratorioFormDialog(laboratorio: widget.laboratorio, onSaved: () => ref.invalidate(laboratoriosListProvider)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final e = widget.laboratorio;
    final textTheme = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final ocupado = _eliminando || _cambiandoEstado;
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
            Text(e.ubicacion, style: textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant)),
            const SizedBox(height: AppSpacing.sm),
            Wrap(
              spacing: AppSpacing.md,
              runSpacing: AppSpacing.xs,
              children: [
                _Info(icon: LucideIcons.users, text: '${e.capacidad} capacidad'),
                _Info(icon: LucideIcons.mail, text: e.correo ?? 'Sin correo'),
              ],
            ),
            const SizedBox(height: AppSpacing.md),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                OutlinedButton.icon(
                  onPressed: ocupado ? null : _editar,
                  icon: const Icon(LucideIcons.pencil, size: 14),
                  label: const Text('Editar'),
                ),
                const SizedBox(width: AppSpacing.sm),
                OutlinedButton(
                  onPressed: ocupado ? null : _toggleEstado,
                  child: _cambiandoEstado
                      ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2))
                      : Text(switch (e.estado) { EstadoEntidad.activo => 'Desactivar', EstadoEntidad.inactivo => 'Mantenimiento', EstadoEntidad.mantenimiento => 'Activar' }),
                ),
                const SizedBox(width: AppSpacing.sm),
                FilledButton.tonalIcon(
                  onPressed: ocupado ? null : _eliminar,
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

class _Info extends StatelessWidget {
  const _Info({required this.icon, required this.text});
  final IconData icon;
  final String text;
  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: scheme.onSurfaceVariant),
        const SizedBox(width: AppSpacing.xs),
        Text(text, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}

class _LaboratorioFormDialog extends ConsumerStatefulWidget {
  const _LaboratorioFormDialog({this.laboratorio, required this.onSaved});
  final Laboratorio? laboratorio;
  final VoidCallback onSaved;
  @override
  ConsumerState<_LaboratorioFormDialog> createState() => _LaboratorioFormDialogState();
}

class _LaboratorioFormDialogState extends ConsumerState<_LaboratorioFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late String _nombre;
  late String _ubicacion;
  late int _capacidad;
  late String _correo;
  late EstadoEntidad _estado;
  bool _guardando = false;
  String? _error;
  bool get _esEdicion => widget.laboratorio != null;
  @override
  void initState() {
    super.initState();
    final e = widget.laboratorio;
    _nombre = e?.nombre ?? '';
    _ubicacion = e?.ubicacion ?? 'Sede Central';
    _capacidad = e?.capacidad ?? 20;
    _correo = e?.correo ?? '';
    _estado = e?.estado ?? EstadoEntidad.activo;
  }

  Future<void> _guardar() async {
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();
    setState(() {
      _guardando = true;
      _error = null;
    });
    try {
      final repo = ref.read(laboratoriosRepositoryProvider);
      if (_esEdicion) {
        await repo.actualizar(
          widget.laboratorio!.id,
          nombre: _nombre,
          ubicacion: _ubicacion,
          capacidad: _capacidad,
          estado: _estado.name,
          correo: _correo,
        );
      } else {
        await repo.crear(
          nombre: _nombre,
          ubicacion: _ubicacion,
          capacidad: _capacidad,
          correo: _correo,
          estado: _estado.name,
        );
      }
      widget.onSaved();
      if (mounted) Navigator.pop(context);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(_esEdicion ? 'Laboratorio actualizado.' : 'Laboratorio creado.')));
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(e, fallback: _esEdicion ? 'No se pudo actualizar el laboratorio.' : 'No se pudo crear el laboratorio.'));
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(_esEdicion ? 'Editar laboratorio' : 'Nuevo laboratorio'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                initialValue: _nombre,
                decoration: const InputDecoration(labelText: 'Nombre *', hintText: 'Ej. Aula 101'),
                validator: (v) {
                  if (v == null || v.trim().isEmpty) return 'Requerido';
                  if (v.trim().length > 100) return 'Máx. 100';
                  return null;
                },
                onSaved: (v) => _nombre = v!.trim(),
              ),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                initialValue: _ubicacion,
                decoration: const InputDecoration(labelText: 'Ubicación *', hintText: 'Sede Central'),
                validator: (v) {
                  if (v == null || v.trim().isEmpty) return 'Requerido';
                  if (v.trim().length > 200) return 'Máx. 200';
                  return null;
                },
                onSaved: (v) => _ubicacion = v!.trim(),
              ),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                initialValue: _capacidad.toString(),
                decoration: const InputDecoration(labelText: 'Capacidad *'),
                keyboardType: TextInputType.number,
                validator: (v) {
                  final n = int.tryParse(v ?? '');
                  if (n == null || n <= 0) return 'Debe ser > 0';
                  return null;
                },
                onSaved: (v) => _capacidad = int.parse(v!),
              ),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                initialValue: _correo,
                decoration: const InputDecoration(labelText: 'Correo *', hintText: 'laboratorio@example.com'),
                keyboardType: TextInputType.emailAddress,
                validator: (v) {
                  if (v == null || v.trim().isEmpty) return 'Requerido';
                  if (!v.contains('@') || !v.split('@').last.contains('.')) return 'Correo inválido';
                  if (v.trim().length > 255) return 'Máx. 255';
                  return null;
                },
                onSaved: (v) => _correo = v!.trim(),
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
