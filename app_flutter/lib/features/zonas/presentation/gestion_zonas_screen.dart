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
import '../../recursos/application/recursos_providers.dart';
import '../application/zonas_providers.dart';
import '../data/zonas_repository.dart';
import '../domain/zona.dart';

/// Búsqueda + tabla ordenable en pantalla ancha (2026-08-31) -- mismo
/// diseño que `GestionRecursosScreen`, ver el comentario ahí para el porqué
/// de usar `DataTable` nativo en vez del patrón fijo de `_UsuariosTabla`.
class GestionZonasScreen extends ConsumerStatefulWidget {
  const GestionZonasScreen({super.key});

  @override
  ConsumerState<GestionZonasScreen> createState() => _GestionZonasScreenState();
}

class _GestionZonasScreenState extends ConsumerState<GestionZonasScreen> {
  String _busqueda = '';
  int? _sortColumnIndex;
  bool _sortAscending = true;

  List<Zona> _filtrarYOrdenar(List<Zona> zonas, Map<int, String> nombrePorEspacio) {
    var resultado = zonas;
    final consulta = _busqueda.trim().toLowerCase();
    if (consulta.isNotEmpty) {
      resultado = resultado
          .where((z) =>
              z.nombre.toLowerCase().contains(consulta) ||
              (nombrePorEspacio[z.espacioId] ?? '').toLowerCase().contains(consulta))
          .toList();
    }
    if (_sortColumnIndex != null) {
      resultado = List.of(resultado)
        ..sort((a, b) {
          final cmp = switch (_sortColumnIndex) {
            0 => a.nombre.toLowerCase().compareTo(b.nombre.toLowerCase()),
            1 => (nombrePorEspacio[a.espacioId] ?? '').toLowerCase().compareTo((nombrePorEspacio[b.espacioId] ?? '').toLowerCase()),
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
    final zonasAsync = ref.watch(zonasGestionProvider);
    final nombrePorEspacio = <int, String>{
      for (final e in ref.watch(espaciosListProvider).value ?? const []) e.id: e.nombre,
    };

    return Scaffold(
      appBar: AppBar(title: const Text('Zonas')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _mostrarCrear(context, ref),
        icon: const Icon(LucideIcons.plus, size: 18),
        label: const Text('Nueva'),
      ),
      body: zonasAsync.when(
        loading: () => const LoadingSpinner(),
        error: (error, _) => ErrorView(
          message: apiErrorMessage(error, fallback: 'No se pudieron cargar las zonas.'),
          onRetry: () => ref.invalidate(zonasGestionProvider),
        ),
        data: (zonas) {
          if (zonas.isEmpty) {
            return const EmptyView(icon: LucideIcons.mapPinned, message: 'No hay zonas registradas.');
          }
          final filtradas = _filtrarYOrdenar(zonas, nombrePorEspacio);
          final esCompacta = MediaQuery.sizeOf(context).width < kCompactBreakpoint;
          return Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(AppSpacing.lg, AppSpacing.lg, AppSpacing.lg, AppSpacing.sm),
                child: TextField(
                  decoration: const InputDecoration(
                    hintText: 'Buscar por nombre o espacio',
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
                            onRefresh: () => ref.refresh(zonasGestionProvider.future),
                            child: ListView.separated(
                              padding: const EdgeInsets.fromLTRB(AppSpacing.lg, 0, AppSpacing.lg, AppSpacing.lg),
                              itemCount: filtradas.length,
                              separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.md),
                              itemBuilder: (context, index) => _ZonaCard(
                                zona: filtradas[index],
                                espacioNombre: nombrePorEspacio[filtradas[index].espacioId],
                              ).staggerEntrance(index),
                            ),
                          )
                        : RefreshIndicator(
                            onRefresh: () => ref.refresh(zonasGestionProvider.future),
                            child: SingleChildScrollView(
                              padding: const EdgeInsets.fromLTRB(AppSpacing.lg, 0, AppSpacing.lg, AppSpacing.lg),
                              child: SingleChildScrollView(
                                scrollDirection: Axis.horizontal,
                                child: _ZonasTabla(
                                  zonas: filtradas,
                                  nombrePorEspacio: nombrePorEspacio,
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
      builder: (_) => _ZonaFormDialog(onSaved: () => ref.invalidate(zonasGestionProvider)),
    );
  }
}

class _ZonasTabla extends StatelessWidget {
  const _ZonasTabla({
    required this.zonas,
    required this.nombrePorEspacio,
    required this.sortColumnIndex,
    required this.sortAscending,
    required this.onSort,
  });

  final List<Zona> zonas;
  final Map<int, String> nombrePorEspacio;
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
          DataColumn(label: const Text('ESPACIO'), onSort: onSort),
          DataColumn(label: const Text('CAPACIDAD'), numeric: true, onSort: onSort),
          DataColumn(label: const Text('ESTADO'), onSort: onSort),
          const DataColumn(label: Text('ACCIONES')),
        ],
        rows: [
          for (final z in zonas)
            DataRow(
              cells: [
                DataCell(Text(z.nombre)),
                DataCell(Text(nombrePorEspacio[z.espacioId] ?? 'Espacio ${z.espacioId}')),
                DataCell(Text(z.capacidad != null ? '${z.capacidad}' : '—')),
                DataCell(EstadoBadge(estado: z.estado)),
                DataCell(_AccionesZona(zona: z)),
              ],
            ),
        ],
      ),
    );
  }
}

class _AccionesZona extends ConsumerStatefulWidget {
  const _AccionesZona({required this.zona});

  final Zona zona;

  @override
  ConsumerState<_AccionesZona> createState() => _AccionesZonaState();
}

class _AccionesZonaState extends ConsumerState<_AccionesZona> {
  bool _eliminando = false;

  Future<void> _eliminar() async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Eliminar zona'),
        content: Text('¿Eliminar "${widget.zona.nombre}"?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Eliminar')),
        ],
      ),
    );
    if (confirmar != true || !mounted) return;
    setState(() => _eliminando = true);
    try {
      await ref.read(zonasRepositoryProvider).eliminar(widget.zona.id);
      ref.invalidate(zonasGestionProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Zona eliminada.')));
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo eliminar la zona.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _eliminando = false);
    }
  }

  void _editar() {
    showDialog<void>(
      context: context,
      builder: (_) => _ZonaFormDialog(zona: widget.zona, onSaved: () => ref.invalidate(zonasGestionProvider)),
    );
  }

  void _gestionarRecursos() {
    showDialog<void>(
      context: context,
      builder: (_) => _ZonaRecursosDialog(zona: widget.zona, onSaved: () => ref.invalidate(zonasGestionProvider)),
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

class _ZonaCard extends ConsumerStatefulWidget {
  const _ZonaCard({required this.zona, this.espacioNombre});
  final Zona zona;
  final String? espacioNombre;
  @override
  ConsumerState<_ZonaCard> createState() => _ZonaCardState();
}

class _ZonaCardState extends ConsumerState<_ZonaCard> {
  bool _eliminando = false;

  Future<void> _eliminar() async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Eliminar zona'),
        content: Text('¿Eliminar "${widget.zona.nombre}"?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Eliminar')),
        ],
      ),
    );
    if (confirmar != true || !mounted) return;
    setState(() => _eliminando = true);
    try {
      await ref.read(zonasRepositoryProvider).eliminar(widget.zona.id);
      ref.invalidate(zonasGestionProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Zona eliminada.')));
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo eliminar la zona.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _eliminando = false);
    }
  }

  void _editar() {
    showDialog<void>(
      context: context,
      builder: (_) => _ZonaFormDialog(zona: widget.zona, onSaved: () => ref.invalidate(zonasGestionProvider)),
    );
  }

  void _gestionarRecursos() {
    showDialog<void>(
      context: context,
      builder: (_) => _ZonaRecursosDialog(zona: widget.zona, onSaved: () => ref.invalidate(zonasGestionProvider)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final z = widget.zona;
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
                _Info(icon: LucideIcons.hash, text: 'ID ${z.id} · Espacio ${widget.espacioNombre ?? z.espacioId}'),
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

class _ZonaFormDialog extends ConsumerStatefulWidget {
  const _ZonaFormDialog({this.zona, required this.onSaved});
  final Zona? zona;
  final VoidCallback onSaved;
  @override
  ConsumerState<_ZonaFormDialog> createState() => _ZonaFormDialogState();
}

class _ZonaFormDialogState extends ConsumerState<_ZonaFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late String _nombre;
  late String _descripcion;
  int? _capacidad;
  late EstadoEntidad _estado;
  int? _espacioId;
  bool _guardando = false;
  String? _error;

  bool get _esEdicion => widget.zona != null;

  @override
  void initState() {
    super.initState();
    final z = widget.zona;
    _nombre = z?.nombre ?? '';
    _descripcion = z?.descripcion ?? '';
    _capacidad = z?.capacidad;
    _estado = z?.estado ?? EstadoEntidad.activo;
    // Al crear, un gestor no elige espacio: se siembra con el suyo (uno
    // solo por definición, ver tabla de roles en el CLAUDE.md raíz), y el
    // selector queda oculto más abajo. Para un admin `espacio` es null,
    // así que esto queda en null y el selector sí se muestra.
    _espacioId = z?.espacioId ?? ref.read(authProvider).value?.espacio?.id;
  }

  Future<void> _guardar() async {
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();
    if (!_esEdicion && _espacioId == null) {
      setState(() => _error = 'Seleccioná un espacio.');
      return;
    }
    setState(() {
      _guardando = true;
      _error = null;
    });
    try {
      final repo = ref.read(zonasRepositoryProvider);
      if (_esEdicion) {
        await repo.actualizar(
          widget.zona!.id,
          nombre: _nombre,
          descripcion: _descripcion.isEmpty ? null : _descripcion,
          capacidad: _capacidad,
          estado: _estado.name,
          espacioId: _espacioId,
        );
      } else {
        await repo.crear(
          nombre: _nombre,
          espacioId: _espacioId!,
          descripcion: _descripcion.isEmpty ? null : _descripcion,
          capacidad: _capacidad,
          estado: _estado.name,
        );
      }
      widget.onSaved();
      if (mounted) Navigator.pop(context);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(_esEdicion ? 'Zona actualizada.' : 'Zona creada.')));
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(e, fallback: _esEdicion ? 'No se pudo actualizar la zona.' : 'No se pudo crear la zona.'));
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final espaciosAsync = ref.watch(espaciosListProvider);
    final auth = ref.watch(authProvider).value;
    final esAdmin = auth?.rol == RolUsuario.admin;

    return AlertDialog(
      title: Text(_esEdicion ? 'Editar zona' : 'Nueva zona'),
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
              // Solo admin elige espacio — mismo criterio que
              // `GestionRecursosScreen`. Antes era `!_esEdicion || esAdmin`,
              // que al CREAR se lo mostraba también al gestor con la lista
              // global de espacios; peor aún, el `initialValue` de abajo
              // preseleccionaba `espacios.first` y el `onSaved` lo confirmaba
              // en el estado, así que un gestor que ni tocaba el campo
              // enviaba un espacio ajeno y recibía un 403 del backend.
              if (esAdmin)
                espaciosAsync.when(
                  loading: () => const LinearProgressIndicator(),
                  error: (e, _) => Text(apiErrorMessage(e, fallback: 'No se pudieron cargar los espacios.')),
                  data: (espacios) => DropdownButtonFormField<int>(
                  initialValue: _espacioId ?? (espacios.isNotEmpty ? espacios.first.id : null),
                    decoration: const InputDecoration(labelText: 'Espacio *'),
                    items: espacios.map((e) => DropdownMenuItem(value: e.id, child: Text(e.nombre))).toList(),
                    onChanged: (v) => setState(() => _espacioId = v),
                    validator: (v) => v == null ? 'Requerido' : null,
                    onSaved: (v) => _espacioId = v,
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

/// `PUT /zonas/{id}/recursos` es un reemplazo completo, no un agregar/quitar
/// incremental -- por eso la selección arranca precargada desde
/// `zona.recursoIds` (ver `ZonaResponse.recurso_ids`, Fase A1): sin eso, un
/// gestor que guarde sin darse cuenta de que el diálogo abrió vacío
/// desasociaría todo lo que la zona ya tenía.
class _ZonaRecursosDialog extends ConsumerStatefulWidget {
  const _ZonaRecursosDialog({required this.zona, required this.onSaved});
  final Zona zona;
  final VoidCallback onSaved;
  @override
  ConsumerState<_ZonaRecursosDialog> createState() => _ZonaRecursosDialogState();
}

class _ZonaRecursosDialogState extends ConsumerState<_ZonaRecursosDialog> {
  late final Set<int> _seleccionados = widget.zona.recursoIds.toSet();
  bool _guardando = false;
  String? _error;

  Future<void> _guardar() async {
    setState(() {
      _guardando = true;
      _error = null;
    });
    try {
      await ref.read(zonasRepositoryProvider).reemplazarRecursos(widget.zona.id, _seleccionados.toList());
      widget.onSaved();
      if (mounted) Navigator.pop(context);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Recursos de la zona actualizados.')));
      }
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(e, fallback: 'No se pudieron actualizar los recursos de la zona.'));
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final recursos = ref.watch(recursosPorEspacioProvider(widget.zona.espacioId));

    return AlertDialog(
      title: Text('Recursos de ${widget.zona.nombre}'),
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
                  child: Text('No hay recursos en este espacio.'),
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
