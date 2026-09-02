import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../../auth/application/auth_provider.dart';
import '../../auth/domain/auth_user.dart';
import '../../laboratorios/application/laboratorios_providers.dart';
import '../application/tipos_reserva_providers.dart';
import '../data/tipos_reserva_repository.dart';
import '../domain/tipo_reserva.dart';

/// Gestión simple (lista + alta/edición/baja) del catálogo `tipos_reserva`
/// por laboratorio (Fase 7 -- reemplaza el enum fijo `TipoReserva`). Sin
/// búsqueda/tabla ordenable a propósito: la cantidad de tipos por
/// laboratorio es chica (unos pocos), a diferencia de recursos/espacios.
class GestionTiposReservaScreen extends ConsumerWidget {
  const GestionTiposReservaScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tiposAsync = ref.watch(tiposReservaGestionProvider);
    final nombrePorLaboratorio = <int, String>{
      for (final e in ref.watch(laboratoriosListProvider).value ?? const []) e.id: e.nombre,
    };

    return Scaffold(
      appBar: AppBar(title: const Text('Tipos de reserva')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _mostrarCrear(context, ref),
        icon: const Icon(LucideIcons.plus, size: 18),
        label: const Text('Nuevo'),
      ),
      body: tiposAsync.when(
        loading: () => const LoadingSpinner(),
        error: (error, _) => ErrorView(
          message: apiErrorMessage(error, fallback: 'No se pudieron cargar los tipos de reserva.'),
          onRetry: () => ref.invalidate(tiposReservaGestionProvider),
        ),
        data: (tipos) {
          if (tipos.isEmpty) {
            return const EmptyView(icon: LucideIcons.tag, message: 'No hay tipos de reserva registrados.');
          }
          return RefreshIndicator(
            onRefresh: () => ref.refresh(tiposReservaGestionProvider.future),
            child: ListView.separated(
              padding: const EdgeInsets.all(AppSpacing.lg),
              itemCount: tipos.length,
              separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.md),
              itemBuilder: (context, index) => _TipoReservaCard(
                tipo: tipos[index],
                laboratorioNombre: nombrePorLaboratorio[tipos[index].laboratorioId],
              ),
            ),
          );
        },
      ),
    );
  }

  void _mostrarCrear(BuildContext context, WidgetRef ref) {
    showDialog<void>(
      context: context,
      builder: (_) => _TipoReservaFormDialog(onSaved: () => ref.invalidate(tiposReservaGestionProvider)),
    );
  }
}

class _TipoReservaCard extends ConsumerStatefulWidget {
  const _TipoReservaCard({required this.tipo, this.laboratorioNombre});

  final TipoReserva tipo;
  final String? laboratorioNombre;

  @override
  ConsumerState<_TipoReservaCard> createState() => _TipoReservaCardState();
}

class _TipoReservaCardState extends ConsumerState<_TipoReservaCard> {
  bool _eliminando = false;

  Future<void> _eliminar() async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Eliminar tipo de reserva'),
        content: Text('¿Eliminar "${widget.tipo.nombre}"?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Eliminar')),
        ],
      ),
    );
    if (confirmar != true || !mounted) return;
    setState(() => _eliminando = true);
    try {
      await ref.read(tiposReservaRepositoryProvider).eliminar(widget.tipo.id);
      ref.invalidate(tiposReservaGestionProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Tipo de reserva eliminado.')));
      }
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo eliminar el tipo de reserva.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _eliminando = false);
    }
  }

  void _editar() {
    showDialog<void>(
      context: context,
      builder: (_) => _TipoReservaFormDialog(tipo: widget.tipo, onSaved: () => ref.invalidate(tiposReservaGestionProvider)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final t = widget.tipo;
    final textTheme = Theme.of(context).textTheme;
    final activo = t.estado == 'activo';
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(child: Text(t.nombre, style: textTheme.titleMedium)),
                Chip(
                  label: Text(activo ? 'Activo' : 'Inactivo'),
                  visualDensity: VisualDensity.compact,
                  backgroundColor: activo ? Colors.green.withValues(alpha: 0.12) : Colors.grey.withValues(alpha: 0.15),
                ),
              ],
            ),
            const SizedBox(height: AppSpacing.xs),
            Text(
              'Laboratorio ${widget.laboratorioNombre ?? t.laboratorioId}',
              style: textTheme.bodySmall?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant),
            ),
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

class _TipoReservaFormDialog extends ConsumerStatefulWidget {
  const _TipoReservaFormDialog({this.tipo, required this.onSaved});

  final TipoReserva? tipo;
  final VoidCallback onSaved;

  @override
  ConsumerState<_TipoReservaFormDialog> createState() => _TipoReservaFormDialogState();
}

class _TipoReservaFormDialogState extends ConsumerState<_TipoReservaFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late String _nombre;
  late String _estado;
  int? _laboratorioId;
  bool _guardando = false;
  String? _error;

  bool get _esEdicion => widget.tipo != null;

  @override
  void initState() {
    super.initState();
    final t = widget.tipo;
    _nombre = t?.nombre ?? '';
    _estado = t?.estado ?? 'activo';
    // Mismo criterio que GestionEspaciosScreen: al crear, un gestor no
    // elige laboratorio (tiene uno solo), se siembra con el suyo.
    _laboratorioId = t?.laboratorioId ?? ref.read(authProvider).value?.laboratorio?.id;
  }

  Future<void> _guardar() async {
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();
    if (!_esEdicion && _laboratorioId == null) {
      setState(() => _error = 'Seleccioná un laboratorio.');
      return;
    }
    setState(() {
      _guardando = true;
      _error = null;
    });
    try {
      final repo = ref.read(tiposReservaRepositoryProvider);
      if (_esEdicion) {
        await repo.actualizar(widget.tipo!.id, nombre: _nombre, estado: _estado);
      } else {
        await repo.crear(nombre: _nombre, laboratorioId: _laboratorioId!, estado: _estado);
      }
      widget.onSaved();
      if (mounted) Navigator.pop(context);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(_esEdicion ? 'Tipo de reserva actualizado.' : 'Tipo de reserva creado.')),
        );
      }
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(
            e,
            fallback: _esEdicion ? 'No se pudo actualizar el tipo de reserva.' : 'No se pudo crear el tipo de reserva.',
          ));
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final laboratoriosAsync = ref.watch(laboratoriosListProvider);
    final auth = ref.watch(authProvider).value;
    final esAdmin = auth?.rol == RolUsuario.admin;

    return AlertDialog(
      title: Text(_esEdicion ? 'Editar tipo de reserva' : 'Nuevo tipo de reserva'),
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
              if (!_esEdicion && esAdmin)
                laboratoriosAsync.when(
                  loading: () => const LinearProgressIndicator(),
                  error: (e, _) => Text(apiErrorMessage(e, fallback: 'No se pudieron cargar los laboratorios.')),
                  data: (laboratorios) => DropdownButtonFormField<int>(
                    initialValue: _laboratorioId ?? (laboratorios.isNotEmpty ? laboratorios.first.id : null),
                    decoration: const InputDecoration(labelText: 'Laboratorio *'),
                    items: laboratorios.map((e) => DropdownMenuItem(value: e.id, child: Text(e.nombre))).toList(),
                    onChanged: (v) => setState(() => _laboratorioId = v),
                    validator: (v) => v == null ? 'Requerido' : null,
                    onSaved: (v) => _laboratorioId = v,
                  ),
                ),
              if (!_esEdicion && esAdmin) const SizedBox(height: AppSpacing.md),
              DropdownButtonFormField<String>(
                initialValue: _estado,
                decoration: const InputDecoration(labelText: 'Estado'),
                items: const [
                  DropdownMenuItem(value: 'activo', child: Text('Activo')),
                  DropdownMenuItem(value: 'inactivo', child: Text('Inactivo')),
                ],
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
