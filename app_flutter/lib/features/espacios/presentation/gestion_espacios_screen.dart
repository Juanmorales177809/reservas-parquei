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
import '../../laboratorios/application/laboratorios_providers.dart';
import '../../recursos/application/recursos_providers.dart';
import '../application/espacios_providers.dart';
import '../data/espacios_repository.dart';
import '../domain/espacio.dart';

/// Búsqueda + tabla ordenable en pantalla ancha (2026-08-31) -- mismo
/// diseño que `GestionRecursosScreen`, ver el comentario ahí para el porqué
/// de usar `DataTable` nativo en vez del patrón fijo de `_UsuariosTabla`.
class GestionEspaciosScreen extends ConsumerStatefulWidget {
  const GestionEspaciosScreen({super.key});

  @override
  ConsumerState<GestionEspaciosScreen> createState() => _GestionEspaciosScreenState();
}

class _GestionEspaciosScreenState extends ConsumerState<GestionEspaciosScreen> {
  String _busqueda = '';
  int? _sortColumnIndex;
  bool _sortAscending = true;

  List<Espacio> _filtrarYOrdenar(List<Espacio> espacios, Map<int, String> nombrePorLaboratorio) {
    var resultado = espacios;
    final consulta = _busqueda.trim().toLowerCase();
    if (consulta.isNotEmpty) {
      resultado = resultado
          .where((z) =>
              z.nombre.toLowerCase().contains(consulta) ||
              (nombrePorLaboratorio[z.laboratorioId] ?? '').toLowerCase().contains(consulta))
          .toList();
    }
    if (_sortColumnIndex != null) {
      resultado = List.of(resultado)
        ..sort((a, b) {
          final cmp = switch (_sortColumnIndex) {
            0 => a.nombre.toLowerCase().compareTo(b.nombre.toLowerCase()),
            1 => (nombrePorLaboratorio[a.laboratorioId] ?? '').toLowerCase().compareTo((nombrePorLaboratorio[b.laboratorioId] ?? '').toLowerCase()),
            2 => (a.capacidad ?? -1).compareTo(b.capacidad ?? -1),
            3 => a.estado.name.compareTo(b.estado.name),
            _ => 0,
          };
          return _sortAscending ? cmp : -cmp;
        });
    }
    return resultado;
  }

  @override
  Widget build(BuildContext context) {
    final espaciosAsync = ref.watch(espaciosGestionProvider);
    final nombrePorLaboratorio = <int, String>{
      for (final e in ref.watch(laboratoriosListProvider).value ?? const []) e.id: e.nombre,
    };

    return Scaffold(
      appBar: AppBar(title: const Text('Espacios')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _mostrarCrear(context, ref),
        icon: const Icon(LucideIcons.plus, size: 18),
        label: const Text('Nueva'),
      ),
      body: espaciosAsync.when(
        loading: () => const LoadingSpinner(),
        error: (error, _) => ErrorView(
          message: apiErrorMessage(error, fallback: 'No se pudieron cargar los espacios.'),
          onRetry: () => ref.invalidate(espaciosGestionProvider),
        ),
        data: (espacios) {
          if (espacios.isEmpty) {
            return const EmptyView(icon: LucideIcons.mapPinned, message: 'No hay espacios registrados.');
          }
          final filtradas = _filtrarYOrdenar(espacios, nombrePorLaboratorio);
          final esCompacta = MediaQuery.sizeOf(context).width < kCompactBreakpoint;
          return Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(AppSpacing.lg, AppSpacing.lg, AppSpacing.lg, AppSpacing.sm),
                child: TextField(
                  decoration: const InputDecoration(
                    hintText: 'Buscar por nombre o laboratorio',
                    prefixIcon: Icon(LucideIcons.search, size: 18),
                    isDense: true,
                    border: OutlineInputBorder(),
                  ),
                  onChanged: (v) => setState(() => _busqueda = v),
                ),
              ),
              Expanded(
                child: filtradas.isEmpty
                    ? Center(
                        child: Text(
                          'No se encontraron resultados para "$_busqueda".',
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                      )
                    : esCompacta
                        ? RefreshIndicator(
                            onRefresh: () => ref.refresh(espaciosGestionProvider.future),
                            child: ListView.separated(
                              padding: const EdgeInsets.fromLTRB(AppSpacing.lg, 0, AppSpacing.lg, AppSpacing.lg),
                              itemCount: filtradas.length,
                              separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.md),
                              itemBuilder: (context, index) => _EspacioCard(
                                espacio: filtradas[index],
                                laboratorioNombre: nombrePorLaboratorio[filtradas[index].laboratorioId],
                              ).staggerEntrance(index),
                            ),
                          )
                        : RefreshIndicator(
                            onRefresh: () => ref.refresh(espaciosGestionProvider.future),
                            child: SingleChildScrollView(
                              padding: const EdgeInsets.fromLTRB(AppSpacing.lg, 0, AppSpacing.lg, AppSpacing.lg),
                              child: SingleChildScrollView(
                                scrollDirection: Axis.horizontal,
                                child: _EspaciosTabla(
                                  espacios: filtradas,
                                  nombrePorLaboratorio: nombrePorLaboratorio,
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

  void _mostrarCrear(BuildContext context, WidgetRef ref) {
    showDialog<void>(
      context: context,
      builder: (_) => _EspacioFormDialog(onSaved: () => ref.invalidate(espaciosGestionProvider)),
    );
  }
}

class _EspaciosTabla extends StatelessWidget {
  const _EspaciosTabla({
    required this.espacios,
    required this.nombrePorLaboratorio,
    required this.sortColumnIndex,
    required this.sortAscending,
    required this.onSort,
  });

  final List<Espacio> espacios;
  final Map<int, String> nombrePorLaboratorio;
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
          DataColumn(label: const Text('LABORATORIO'), onSort: onSort),
          DataColumn(label: const Text('CAPACIDAD'), numeric: true, onSort: onSort),
          DataColumn(label: const Text('ESTADO'), onSort: onSort),
          const DataColumn(label: Text('ACCIONES')),
        ],
        rows: [
          for (final z in espacios)
            DataRow(
              cells: [
                DataCell(Text(z.nombre)),
                DataCell(Text(nombrePorLaboratorio[z.laboratorioId] ?? 'Laboratorio ${z.laboratorioId}')),
                DataCell(Text(z.capacidad != null ? '${z.capacidad}' : '—')),
                DataCell(EstadoBadge(estado: z.estado)),
                DataCell(_AccionesEspacio(espacio: z)),
              ],
            ),
        ],
      ),
    );
  }
}

class _AccionesEspacio extends ConsumerStatefulWidget {
  const _AccionesEspacio({required this.espacio});

  final Espacio espacio;

  @override
  ConsumerState<_AccionesEspacio> createState() => _AccionesEspacioState();
}

class _AccionesEspacioState extends ConsumerState<_AccionesEspacio> {
  bool _eliminando = false;

  Future<void> _eliminar() async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Eliminar espacio'),
        content: Text('¿Eliminar "${widget.espacio.nombre}"?'),
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
      ref.invalidate(espaciosGestionProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Espacio eliminado.')));
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo eliminar el espacio.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _eliminando = false);
    }
  }

  void _editar() {
    showDialog<void>(
      context: context,
      builder: (_) => _EspacioFormDialog(espacio: widget.espacio, onSaved: () => ref.invalidate(espaciosGestionProvider)),
    );
  }

  void _gestionarRecursos() {
    showDialog<void>(
      context: context,
      builder: (_) => _EspacioRecursosDialog(espacio: widget.espacio, onSaved: () => ref.invalidate(espaciosGestionProvider)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        IconButton(
          onPressed: _eliminando ? null : _gestionarRecursos,
          icon: const Icon(LucideIcons.boxes, size: 16),
          tooltip: 'Recursos',
        ),
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

class _EspacioCard extends ConsumerStatefulWidget {
  const _EspacioCard({required this.espacio, this.laboratorioNombre});
  final Espacio espacio;
  final String? laboratorioNombre;
  @override
  ConsumerState<_EspacioCard> createState() => _EspacioCardState();
}

class _EspacioCardState extends ConsumerState<_EspacioCard> {
  bool _eliminando = false;

  Future<void> _eliminar() async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Eliminar espacio'),
        content: Text('¿Eliminar "${widget.espacio.nombre}"?'),
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
      ref.invalidate(espaciosGestionProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Espacio eliminado.')));
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo eliminar el espacio.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _eliminando = false);
    }
  }

  void _editar() {
    showDialog<void>(
      context: context,
      builder: (_) => _EspacioFormDialog(espacio: widget.espacio, onSaved: () => ref.invalidate(espaciosGestionProvider)),
    );
  }

  void _gestionarRecursos() {
    showDialog<void>(
      context: context,
      builder: (_) => _EspacioRecursosDialog(espacio: widget.espacio, onSaved: () => ref.invalidate(espaciosGestionProvider)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final z = widget.espacio;
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
                Expanded(child: Text(z.nombre, style: textTheme.titleMedium)),
                EstadoBadge(estado: z.estado),
              ],
            ),
            if (z.descripcion != null && z.descripcion!.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.xs),
              Text(z.descripcion!, style: textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant)),
            ],
            const SizedBox(height: AppSpacing.sm),
            Wrap(
              spacing: AppSpacing.md,
              children: [
                if (z.capacidad != null) _Info(icon: LucideIcons.users, text: 'Capacidad ${z.capacidad}'),
                _Info(icon: LucideIcons.hash, text: 'ID ${z.id} · Laboratorio ${widget.laboratorioNombre ?? z.laboratorioId}'),
              ],
            ),
            const SizedBox(height: AppSpacing.md),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                OutlinedButton.icon(
                  onPressed: _eliminando ? null : _gestionarRecursos,
                  icon: const Icon(LucideIcons.boxes, size: 14),
                  label: const Text('Recursos'),
                ),
                const SizedBox(width: AppSpacing.sm),
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
  late String _descripcion;
  int? _capacidad;
  late EstadoEntidad _estado;
  int? _laboratorioId;
  bool _guardando = false;
  String? _error;

  bool get _esEdicion => widget.espacio != null;

  @override
  void initState() {
    super.initState();
    final z = widget.espacio;
    _nombre = z?.nombre ?? '';
    _descripcion = z?.descripcion ?? '';
    _capacidad = z?.capacidad;
    _estado = z?.estado ?? EstadoEntidad.activo;
    // Al crear, un gestor no elige laboratorio: se siembra con el suyo (uno
    // solo por definición, ver tabla de roles en el CLAUDE.md raíz), y el
    // selector queda oculto más abajo. Para un admin `laboratorio` es null,
    // así que esto queda en null y el selector sí se muestra.
    _laboratorioId = z?.laboratorioId ?? ref.read(authProvider).value?.laboratorio?.id;
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
      final repo = ref.read(espaciosRepositoryProvider);
      if (_esEdicion) {
        await repo.actualizar(
          widget.espacio!.id,
          nombre: _nombre,
          descripcion: _descripcion.isEmpty ? null : _descripcion,
          capacidad: _capacidad,
          estado: _estado.name,
          laboratorioId: _laboratorioId,
        );
      } else {
        await repo.crear(
          nombre: _nombre,
          laboratorioId: _laboratorioId!,
          descripcion: _descripcion.isEmpty ? null : _descripcion,
          capacidad: _capacidad,
          estado: _estado.name,
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
    final laboratoriosAsync = ref.watch(laboratoriosListProvider);
    final auth = ref.watch(authProvider).value;
    final esAdmin = auth?.rol == RolUsuario.admin;

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
                decoration: const InputDecoration(labelText: 'Nombre *'),
                validator: (v) => (v == null || v.trim().isEmpty) ? 'Requerido' : null,
                onSaved: (v) => _nombre = v!.trim(),
              ),
              const SizedBox(height: AppSpacing.md),
              // Solo admin elige laboratorio — mismo criterio que
              // `GestionRecursosScreen`. Antes era `!_esEdicion || esAdmin`,
              // que al CREAR se lo mostraba también al gestor con la lista
              // global de laboratorios; peor aún, el `initialValue` de abajo
              // preseleccionaba `laboratorios.first` y el `onSaved` lo confirmaba
              // en el estado, así que un gestor que ni tocaba el campo
              // enviaba un laboratorio ajeno y recibía un 403 del backend.
              if (esAdmin)
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
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                initialValue: _descripcion,
                decoration: const InputDecoration(labelText: 'Descripción'),
                onSaved: (v) => _descripcion = v?.trim() ?? '',
              ),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                initialValue: _capacidad?.toString() ?? '',
                decoration: const InputDecoration(labelText: 'Capacidad (opcional)'),
                keyboardType: TextInputType.number,
                validator: (v) {
                  if (v == null || v.trim().isEmpty) return null;
                  final n = int.tryParse(v);
                  if (n == null || n <= 0) return 'Debe ser > 0';
                  return null;
                },
                onSaved: (v) => _capacidad = (v == null || v.trim().isEmpty) ? null : int.parse(v),
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

/// `PUT /espacios/{id}/recursos` es un reemplazo completo, no un agregar/quitar
/// incremental -- por eso la selección arranca precargada desde
/// `espacio.recursoIds` (ver `EspacioResponse.recurso_ids`, Fase A1): sin eso, un
/// gestor que guarde sin darse cuenta de que el diálogo abrió vacío
/// desasociaría todo lo que el espacio ya tenía.
class _EspacioRecursosDialog extends ConsumerStatefulWidget {
  const _EspacioRecursosDialog({required this.espacio, required this.onSaved});
  final Espacio espacio;
  final VoidCallback onSaved;
  @override
  ConsumerState<_EspacioRecursosDialog> createState() => _EspacioRecursosDialogState();
}

class _EspacioRecursosDialogState extends ConsumerState<_EspacioRecursosDialog> {
  late final Set<int> _seleccionados = widget.espacio.recursoIds.toSet();
  bool _guardando = false;
  String? _error;

  Future<void> _guardar() async {
    setState(() {
      _guardando = true;
      _error = null;
    });
    try {
      await ref.read(espaciosRepositoryProvider).reemplazarRecursos(widget.espacio.id, _seleccionados.toList());
      widget.onSaved();
      if (mounted) Navigator.pop(context);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Recursos del espacio actualizados.')));
      }
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(e, fallback: 'No se pudieron actualizar los recursos del espacio.'));
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final recursos = ref.watch(recursosPorLaboratorioProvider(widget.espacio.laboratorioId));

    return AlertDialog(
      title: Text('Recursos de ${widget.espacio.nombre}'),
      content: SizedBox(
        width: double.maxFinite,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (recursos.isEmpty)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: AppSpacing.md),
                  child: Text('No hay recursos en este laboratorio.'),
                ),
              ...recursos.map(
                (r) => CheckboxListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text(r.nombre),
                  subtitle: Text(r.tipo.nombre),
                  value: _seleccionados.contains(r.id),
                  onChanged: (v) => setState(() {
                    if (v == true) {
                      _seleccionados.add(r.id);
                    } else {
                      _seleccionados.remove(r.id);
                    }
                  }),
                ),
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
              : const Text('Guardar'),
        ),
      ],
    );
  }
}
