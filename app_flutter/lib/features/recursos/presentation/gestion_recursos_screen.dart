import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/domain/enums.dart';
import '../../../core/network/api_exception.dart';
import '../../auth/domain/auth_user.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/estado_badge.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../../../core/widgets/staggered_entrance.dart';
import '../../../shell/app_shell.dart';
import '../../auth/application/auth_provider.dart';
import '../../espacios/application/espacios_providers.dart';
import '../application/recursos_providers.dart';
import '../data/recursos_repository.dart';
import '../domain/recurso.dart';

/// Búsqueda + tabla ordenable en pantalla ancha (2026-08-31, a pedido
/// explícito del usuario) -- mismo breakpoint que `GestionUsuariosScreen`
/// (`kCompactBreakpoint`), pero acá la tabla es un `DataTable` nativo (con
/// columnas ordenables de verdad) en vez de replicar el patrón de
/// `_UsuariosTabla` (fijo, sin orden). Búsqueda y orden 100% client-side
/// sobre lo que ya devuelve `recursosGestionProvider` -- sin tocar el
/// backend, sin query params nuevos.
class GestionRecursosScreen extends ConsumerStatefulWidget {
  const GestionRecursosScreen({super.key});

  @override
  ConsumerState<GestionRecursosScreen> createState() => _GestionRecursosScreenState();
}

class _GestionRecursosScreenState extends ConsumerState<GestionRecursosScreen> {
  String _busqueda = '';
  int? _sortColumnIndex;
  bool _sortAscending = true;

  List<Recurso> _filtrarYOrdenar(List<Recurso> recursos) {
    var resultado = recursos;
    final consulta = _busqueda.trim().toLowerCase();
    if (consulta.isNotEmpty) {
      resultado = resultado
          .where((r) =>
              r.nombre.toLowerCase().contains(consulta) ||
              r.tipo.nombre.toLowerCase().contains(consulta) ||
              r.espacio.nombre.toLowerCase().contains(consulta))
          .toList();
    }
    if (_sortColumnIndex != null) {
      resultado = List.of(resultado)
        ..sort((a, b) {
          final cmp = switch (_sortColumnIndex) {
            0 => a.nombre.toLowerCase().compareTo(b.nombre.toLowerCase()),
            1 => a.tipo.nombre.toLowerCase().compareTo(b.tipo.nombre.toLowerCase()),
            2 => a.espacio.nombre.toLowerCase().compareTo(b.espacio.nombre.toLowerCase()),
            3 => a.capacidad.compareTo(b.capacidad),
            4 => a.estado.name.compareTo(b.estado.name),
            _ => 0,
          };
          return _sortAscending ? cmp : -cmp;
        });
    }
    return resultado;
  }

  @override
  Widget build(BuildContext context) {
    final recursosAsync = ref.watch(recursosGestionProvider);
    final tiposAsync = ref.watch(tiposRecursosProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Recursos')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: tiposAsync.value == null
            ? null
            : () => _mostrarDialogoCrear(context, ref),
        icon: const Icon(LucideIcons.plus, size: 18),
        label: const Text('Nuevo'),
      ),
      body: recursosAsync.when(
        loading: () => const LoadingSpinner(),
        error: (error, _) => ErrorView(
          message: apiErrorMessage(error, fallback: 'No se pudieron cargar los recursos.'),
          onRetry: () => ref.invalidate(recursosGestionProvider),
        ),
        data: (recursos) {
          if (recursos.isEmpty) {
            return const EmptyView(icon: LucideIcons.package, message: 'No hay recursos registrados.');
          }
          final filtrados = _filtrarYOrdenar(recursos);
          final esCompacta = MediaQuery.sizeOf(context).width < kCompactBreakpoint;
          return Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(AppSpacing.lg, AppSpacing.lg, AppSpacing.lg, AppSpacing.sm),
                child: TextField(
                  decoration: const InputDecoration(
                    hintText: 'Buscar por nombre, tipo o espacio',
                    prefixIcon: Icon(LucideIcons.search, size: 18),
                    isDense: true,
                    border: OutlineInputBorder(),
                  ),
                  onChanged: (v) => setState(() => _busqueda = v),
                ),
              ),
              Expanded(
                child: filtrados.isEmpty
                    ? Center(
                        child: Text(
                          'No se encontraron resultados para "$_busqueda".',
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                      )
                    : esCompacta
                        ? RefreshIndicator(
                            onRefresh: () => ref.refresh(recursosGestionProvider.future),
                            child: ListView.separated(
                              padding: const EdgeInsets.fromLTRB(AppSpacing.lg, 0, AppSpacing.lg, AppSpacing.lg),
                              itemCount: filtrados.length,
                              separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.md),
                              itemBuilder: (context, index) => _RecursoCard(recurso: filtrados[index]).staggerEntrance(index),
                            ),
                          )
                        : RefreshIndicator(
                            onRefresh: () => ref.refresh(recursosGestionProvider.future),
                            child: SingleChildScrollView(
                              padding: const EdgeInsets.fromLTRB(AppSpacing.lg, 0, AppSpacing.lg, AppSpacing.lg),
                              child: SingleChildScrollView(
                                scrollDirection: Axis.horizontal,
                                child: _RecursosTabla(
                                  recursos: filtrados,
                                  sortColumnIndex: _sortColumnIndex,
                                  sortAscending: _sortAscending,
                                  onSort: (indice, asc) => setState(() {
                                    _sortColumnIndex = indice;
                                    _sortAscending = asc;
                                  }),
                                ),
                              ),
                            ),
                          ),
              ),
            ],
          );
        },
      ),
    );
  }

  void _mostrarDialogoCrear(BuildContext context, WidgetRef ref) {
    showDialog<void>(
      context: context,
      builder: (_) => _RecursoFormDialog(onSaved: () => ref.invalidate(recursosGestionProvider)),
    );
  }
}

class _RecursosTabla extends StatelessWidget {
  const _RecursosTabla({
    required this.recursos,
    required this.sortColumnIndex,
    required this.sortAscending,
    required this.onSort,
  });

  final List<Recurso> recursos;
  final int? sortColumnIndex;
  final bool sortAscending;
  final void Function(int columnIndex, bool ascending) onSort;

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: DataTable(
        sortColumnIndex: sortColumnIndex,
        sortAscending: sortAscending,
        columns: [
          DataColumn(label: const Text('NOMBRE'), onSort: onSort),
          DataColumn(label: const Text('TIPO'), onSort: onSort),
          DataColumn(label: const Text('ESPACIO'), onSort: onSort),
          DataColumn(label: const Text('CAPACIDAD'), numeric: true, onSort: onSort),
          DataColumn(label: const Text('ESTADO'), onSort: onSort),
          const DataColumn(label: Text('ACCIONES')),
        ],
        rows: [
          for (final r in recursos)
            DataRow(
              cells: [
                DataCell(Text(r.nombre)),
                DataCell(Text(r.tipo.nombre)),
                DataCell(Text(r.espacio.nombre)),
                DataCell(Text('${r.capacidad}')),
                DataCell(EstadoBadge(estado: r.estado)),
                DataCell(_AccionesRecurso(recurso: r)),
              ],
            ),
        ],
      ),
    );
  }
}

class _AccionesRecurso extends ConsumerStatefulWidget {
  const _AccionesRecurso({required this.recurso});

  final Recurso recurso;

  @override
  ConsumerState<_AccionesRecurso> createState() => _AccionesRecursoState();
}

class _AccionesRecursoState extends ConsumerState<_AccionesRecurso> {
  bool _eliminando = false;

  Future<void> _eliminar() async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Eliminar recurso'),
        content: Text('¿Eliminar "${widget.recurso.nombre}"? Esta acción no se puede deshacer.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Eliminar')),
        ],
      ),
    );
    if (confirmar != true || !mounted) return;
    setState(() => _eliminando = true);
    try {
      await ref.read(recursosRepositoryProvider).eliminar(widget.recurso.id);
      ref.invalidate(recursosGestionProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Recurso eliminado.')));
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo eliminar el recurso.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _eliminando = false);
    }
  }

  void _editar() {
    showDialog<void>(
      context: context,
      builder: (_) => _RecursoFormDialog(recurso: widget.recurso, onSaved: () => ref.invalidate(recursosGestionProvider)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        IconButton(
          onPressed: _eliminando ? null : _editar,
          icon: const Icon(LucideIcons.pencil, size: 16),
          tooltip: 'Editar',
        ),
        IconButton(
          onPressed: _eliminando ? null : _eliminar,
          icon: _eliminando
              ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
              : const Icon(LucideIcons.trash2, size: 16),
          tooltip: 'Eliminar',
        ),
      ],
    );
  }
}

class _RecursoCard extends ConsumerStatefulWidget {
  const _RecursoCard({required this.recurso});

  final Recurso recurso;

  @override
  ConsumerState<_RecursoCard> createState() => _RecursoCardState();
}

class _RecursoCardState extends ConsumerState<_RecursoCard> {
  bool _eliminando = false;

  Future<void> _eliminar() async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Eliminar recurso'),
        content: Text('¿Eliminar "${widget.recurso.nombre}"? Esta acción no se puede deshacer.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Eliminar')),
        ],
      ),
    );
    if (confirmar != true || !mounted) return;
    setState(() => _eliminando = true);
    try {
      await ref.read(recursosRepositoryProvider).eliminar(widget.recurso.id);
      ref.invalidate(recursosGestionProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Recurso eliminado.')));
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo eliminar el recurso.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _eliminando = false);
    }
  }

  void _editar() {
    showDialog<void>(
      context: context,
      builder: (_) => _RecursoFormDialog(recurso: widget.recurso, onSaved: () => ref.invalidate(recursosGestionProvider)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final r = widget.recurso;
    final textTheme = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(child: Text(r.nombre, style: textTheme.titleMedium)),
                EstadoBadge(estado: r.estado),
              ],
            ),
            if (r.descripcion != null && r.descripcion!.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.xs),
              Text(r.descripcion!, style: textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant)),
            ],
            const SizedBox(height: AppSpacing.sm),
            Wrap(
              spacing: AppSpacing.md,
              runSpacing: AppSpacing.xs,
              children: [
                _Info(icon: LucideIcons.tag, text: r.tipo.nombre),
                _Info(icon: LucideIcons.building2, text: r.espacio.nombre),
                _Info(icon: LucideIcons.users, text: '${r.capacidad} capacidad'),
                if (r.esPrestacionServicio) const _Info(icon: LucideIcons.wrench, text: 'Prestación de servicio'),
              ],
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

class _RecursoFormDialog extends ConsumerStatefulWidget {
  const _RecursoFormDialog({this.recurso, required this.onSaved});

  final Recurso? recurso;
  final VoidCallback onSaved;

  @override
  ConsumerState<_RecursoFormDialog> createState() => _RecursoFormDialogState();
}

class _RecursoFormDialogState extends ConsumerState<_RecursoFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late String _nombre;
  late String _descripcion;
  late int _capacidad;
  late EstadoEntidad _estado;
  int? _tipoRecursoId;
  int? _espacioId;
  bool _esPrestacion = false;
  bool _guardando = false;
  String? _error;

  bool get _esEdicion => widget.recurso != null;

  @override
  void initState() {
    super.initState();
    final r = widget.recurso;
    _nombre = r?.nombre ?? '';
    _descripcion = r?.descripcion ?? '';
    _capacidad = r?.capacidad ?? 1;
    _estado = r?.estado ?? EstadoEntidad.activo;
    _tipoRecursoId = r?.tipoRecursoId;
    _espacioId = r?.espacioId;
    _esPrestacion = r?.esPrestacionServicio ?? false;
  }

  Future<void> _guardar() async {
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();
    if (_tipoRecursoId == null) {
      setState(() => _error = 'Seleccioná un tipo de recurso.');
      return;
    }
    setState(() {
      _guardando = true;
      _error = null;
    });
    try {
      final repo = ref.read(recursosRepositoryProvider);
      if (_esEdicion) {
        await repo.actualizar(
          widget.recurso!.id,
          nombre: _nombre,
          tipoRecursoId: _tipoRecursoId,
          descripcion: _descripcion.isEmpty ? null : _descripcion,
          capacidad: _capacidad,
          estado: _estado.name,
          espacioId: _espacioId,
          esPrestacionServicio: _esPrestacion,
        );
      } else {
        await repo.crear(
          nombre: _nombre,
          tipoRecursoId: _tipoRecursoId!,
          descripcion: _descripcion.isEmpty ? null : _descripcion,
          capacidad: _capacidad,
          estado: _estado.name,
          espacioId: _espacioId,
          esPrestacionServicio: _esPrestacion,
        );
      }
      widget.onSaved();
      if (mounted) Navigator.pop(context);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(_esEdicion ? 'Recurso actualizado.' : 'Recurso creado.')));
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(e, fallback: _esEdicion ? 'No se pudo actualizar el recurso.' : 'No se pudo crear el recurso.'));
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final tiposAsync = ref.watch(tiposRecursosProvider);
    final espaciosAsync = ref.watch(espaciosListProvider);
    final auth = ref.watch(authProvider).value;
    final esAdmin = auth?.rol == RolUsuario.admin;

    return AlertDialog(
      title: Text(_esEdicion ? 'Editar recurso' : 'Nuevo recurso'),
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
              tiposAsync.when(
                loading: () => const LinearProgressIndicator(),
                error: (e, _) => Text(apiErrorMessage(e, fallback: 'No se pudieron cargar los tipos.')),
                data: (tipos) => DropdownButtonFormField<int>(
                  initialValue: _tipoRecursoId ?? (tipos.isNotEmpty ? tipos.first.id : null),
                  decoration: const InputDecoration(labelText: 'Tipo *'),
                  items: tipos.map((t) => DropdownMenuItem(value: t.id, child: Text(t.nombre))).toList(),
                  onChanged: (v) => setState(() => _tipoRecursoId = v),
                  validator: (v) => v == null ? 'Requerido' : null,
                  onSaved: (v) => _tipoRecursoId = v,
                ),
              ),
              if (esAdmin) ...[
                const SizedBox(height: AppSpacing.md),
                espaciosAsync.when(
                  loading: () => const LinearProgressIndicator(),
                  error: (e, _) => Text(apiErrorMessage(e, fallback: 'No se pudieron cargar los espacios.')),
                  data: (espacios) => DropdownButtonFormField<int>(
                  initialValue: _espacioId ?? (espacios.isNotEmpty ? espacios.first.id : null),
                    decoration: const InputDecoration(labelText: 'Espacio'),
                    items: espacios.map((e) => DropdownMenuItem(value: e.id, child: Text(e.nombre))).toList(),
                    onChanged: (v) => setState(() => _espacioId = v),
                    onSaved: (v) => _espacioId = v,
                  ),
                ),
              ],
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
                initialValue: _descripcion,
                decoration: const InputDecoration(labelText: 'Descripción'),
                maxLines: 2,
                onSaved: (v) => _descripcion = v?.trim() ?? '',
              ),
              const SizedBox(height: AppSpacing.md),
              DropdownButtonFormField<EstadoEntidad>(
                initialValue: _estado,
                decoration: const InputDecoration(labelText: 'Estado'),
                items: EstadoEntidad.values.map((e) => DropdownMenuItem(value: e, child: Text(e.name))).toList(),
                onChanged: (v) => setState(() => _estado = v!),
                onSaved: (v) => _estado = v!,
              ),
              const SizedBox(height: AppSpacing.sm),
              CheckboxListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Prestación de servicio'),
                subtitle: const Text('Solo visible para gestor/admin'),
                value: _esPrestacion,
                onChanged: (v) => setState(() => _esPrestacion = v ?? false),
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
