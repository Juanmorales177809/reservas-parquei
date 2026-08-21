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
import '../application/espacios_providers.dart';
import '../data/espacios_repository.dart';
import '../domain/espacio.dart';

class GestionEspaciosScreen extends ConsumerWidget {
  const GestionEspaciosScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final espaciosAsync = ref.watch(espaciosListProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Espacios')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _mostrarCrear(context, ref),
        icon: const Icon(LucideIcons.plus, size: 18),
        label: const Text('Nuevo'),
      ),
      body: espaciosAsync.when(
        loading: () => const LoadingSpinner(),
        error: (error, _) => ErrorView(
          message: apiErrorMessage(error, fallback: 'No se pudieron cargar los espacios.'),
          onRetry: () => ref.invalidate(espaciosListProvider),
        ),
        data: (espacios) {
          if (espacios.isEmpty) {
            return const EmptyView(icon: LucideIcons.building2, message: 'No hay espacios registrados.');
          }
          return RefreshIndicator(
            onRefresh: () => ref.refresh(espaciosListProvider.future),
            child: ListView.separated(
              padding: const EdgeInsets.all(AppSpacing.lg),
              itemCount: espacios.length,
              separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.md),
              itemBuilder: (context, index) => _EspacioCard(espacio: espacios[index]).staggerEntrance(index),
            ),
          );
        },
      ),
    );
  }

  void _mostrarCrear(BuildContext context, WidgetRef ref) {
    showDialog<void>(
      context: context,
      builder: (_) => _EspacioFormDialog(onSaved: () => ref.invalidate(espaciosListProvider)),
    );
  }
}

class _EspacioCard extends ConsumerStatefulWidget {
  const _EspacioCard({required this.espacio});
  final Espacio espacio;
  @override
  ConsumerState<_EspacioCard> createState() => _EspacioCardState();
}

class _EspacioCardState extends ConsumerState<_EspacioCard> {
  bool _eliminando = false;
  bool _cambiandoEstado = false;

  Future<void> _eliminar() async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Eliminar espacio'),
        content: Text('¿Eliminar "${widget.espacio.nombre}"? Esta acción no se puede deshacer.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Eliminar')),
        ],
      ),
    );
    if (confirmar != true || !mounted) return;
    setState(() => _eliminando = true);
    try {
      await ref.read(espaciosRepositoryProvider).eliminar(widget.espacio.id);
      ref.invalidate(espaciosListProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Espacio eliminado.')));
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo eliminar el espacio.'))));
      }
    } finally {
      if (mounted) setState(() => _eliminando = false);
    }
  }

  Future<void> _toggleEstado() async {
    setState(() => _cambiandoEstado = true);
    try {
      final siguiente = switch (widget.espacio.estado) {
        EstadoEntidad.activo => EstadoEntidad.inactivo,
        EstadoEntidad.inactivo => EstadoEntidad.mantenimiento,
        EstadoEntidad.mantenimiento => EstadoEntidad.activo,
      };
      await ref.read(espaciosRepositoryProvider).actualizar(widget.espacio.id, estado: siguiente.name);
      ref.invalidate(espaciosListProvider);
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
      builder: (_) => _EspacioFormDialog(espacio: widget.espacio, onSaved: () => ref.invalidate(espaciosListProvider)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final e = widget.espacio;
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
                _Info(icon: LucideIcons.layers, text: e.modalidadReserva.name),
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

class _EspacioFormDialog extends ConsumerStatefulWidget {
  const _EspacioFormDialog({this.espacio, required this.onSaved});
  final Espacio? espacio;
  final VoidCallback onSaved;
  @override
  ConsumerState<_EspacioFormDialog> createState() => _EspacioFormDialogState();
}

class _EspacioFormDialogState extends ConsumerState<_EspacioFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late String _nombre;
  late String _ubicacion;
  late int _capacidad;
  late String _correo;
  late EstadoEntidad _estado;
  late ModalidadEspacio _modalidad;
  bool _guardando = false;
  String? _error;
  bool get _esEdicion => widget.espacio != null;
  @override
  void initState() {
    super.initState();
    final e = widget.espacio;
    _nombre = e?.nombre ?? '';
    _ubicacion = e?.ubicacion ?? 'Sede Central';
    _capacidad = e?.capacidad ?? 20;
    _correo = e?.correo ?? '';
    _estado = e?.estado ?? EstadoEntidad.activo;
    _modalidad = e?.modalidadReserva ?? ModalidadEspacio.equipos;
  }

  Future<void> _guardar() async {
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();
    setState(() {
      _guardando = true;
      _error = null;
    });
    try {
      final repo = ref.read(espaciosRepositoryProvider);
      if (_esEdicion) {
        await repo.actualizar(
          widget.espacio!.id,
          nombre: _nombre,
          ubicacion: _ubicacion,
          capacidad: _capacidad,
          estado: _estado.name,
          correo: _correo,
          modalidadReserva: _modalidad.name,
        );
      } else {
        await repo.crear(
          nombre: _nombre,
          ubicacion: _ubicacion,
          capacidad: _capacidad,
          correo: _correo,
          estado: _estado.name,
          modalidadReserva: _modalidad.name,
        );
      }
      widget.onSaved();
      if (mounted) Navigator.pop(context);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(_esEdicion ? 'Espacio actualizado.' : 'Espacio creado.')));
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(e, fallback: _esEdicion ? 'No se pudo actualizar el espacio.' : 'No se pudo crear el espacio.'));
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(_esEdicion ? 'Editar espacio' : 'Nuevo espacio'),
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
                decoration: const InputDecoration(labelText: 'Correo *', hintText: 'espacio@example.com'),
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
              const SizedBox(height: AppSpacing.md),
              DropdownButtonFormField<ModalidadEspacio>(
                initialValue: _modalidad,
                decoration: const InputDecoration(labelText: 'Modalidad'),
                items: ModalidadEspacio.values.map((e) => DropdownMenuItem(value: e, child: Text(e.name))).toList(),
                onChanged: (v) => setState(() => _modalidad = v!),
                onSaved: (v) => _modalidad = v!,
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
