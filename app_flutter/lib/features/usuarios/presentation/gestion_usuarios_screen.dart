import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../../../core/widgets/staggered_entrance.dart';
import '../../auth/application/auth_provider.dart';
import '../../auth/domain/auth_user.dart';
import '../../espacios/application/espacios_providers.dart';
import '../application/usuarios_providers.dart';
import '../data/usuarios_repository.dart';

class GestionUsuariosScreen extends ConsumerWidget {
  const GestionUsuariosScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usuariosAsync = ref.watch(usuariosListProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Usuarios')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _mostrarCrear(context, ref),
        icon: const Icon(LucideIcons.userPlus, size: 18),
        label: const Text('Nuevo'),
      ),
      body: usuariosAsync.when(
        loading: () => const LoadingSpinner(),
        error: (error, _) => ErrorView(
          message: apiErrorMessage(error, fallback: 'No se pudieron cargar los usuarios.'),
          onRetry: () => ref.invalidate(usuariosListProvider),
        ),
        data: (usuarios) {
          if (usuarios.isEmpty) {
            return const EmptyView(icon: LucideIcons.users, message: 'No hay usuarios registrados.');
          }
          return RefreshIndicator(
            onRefresh: () => ref.refresh(usuariosListProvider.future),
            child: ListView.separated(
              padding: const EdgeInsets.all(AppSpacing.lg),
              itemCount: usuarios.length,
              separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.md),
              itemBuilder: (context, index) => _UsuarioCard(usuario: usuarios[index]).staggerEntrance(index),
            ),
          );
        },
      ),
    );
  }

  void _mostrarCrear(BuildContext context, WidgetRef ref) {
    showDialog<void>(
      context: context,
      builder: (_) => _UsuarioFormDialog(onSaved: () => ref.invalidate(usuariosListProvider)),
    );
  }
}

class _UsuarioCard extends ConsumerStatefulWidget {
  const _UsuarioCard({required this.usuario});

  final AuthUser usuario;

  @override
  ConsumerState<_UsuarioCard> createState() => _UsuarioCardState();
}

class _UsuarioCardState extends ConsumerState<_UsuarioCard> {
  bool _eliminando = false;

  Future<void> _eliminar() async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Eliminar usuario'),
        content: Text('¿Eliminar a "${widget.usuario.username}"?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Eliminar')),
        ],
      ),
    );
    if (confirmar != true || !mounted) return;
    setState(() => _eliminando = true);
    try {
      await ref.read(usuariosRepositoryProvider).eliminar(widget.usuario.id);
      ref.invalidate(usuariosListProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Usuario eliminado.')));
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo eliminar el usuario.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _eliminando = false);
    }
  }

  void _editar() {
    showDialog<void>(
      context: context,
      builder: (_) => _UsuarioFormDialog(usuario: widget.usuario, onSaved: () => ref.invalidate(usuariosListProvider)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final u = widget.usuario;
    final textTheme = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final currentUser = ref.watch(authProvider).value;
    final esPropio = currentUser?.id == u.id;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: u.rol == RolUsuario.admin
                        ? scheme.primaryContainer
                        : u.rol == RolUsuario.gestor
                            ? scheme.tertiaryContainer
                            : scheme.surfaceContainerHighest,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    u.rol == RolUsuario.admin
                        ? LucideIcons.shield
                        : u.rol == RolUsuario.gestor
                            ? LucideIcons.briefcase
                            : LucideIcons.user,
                    size: 18,
                    color: scheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(width: AppSpacing.md),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(u.username, style: textTheme.titleMedium),
                      Text(u.email, style: textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant)),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: AppSpacing.sm, vertical: 4),
                  decoration: BoxDecoration(
                    color: u.rol == RolUsuario.admin
                        ? scheme.primaryContainer
                        : u.rol == RolUsuario.gestor
                            ? scheme.tertiaryContainer
                            : scheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(AppRadius.pill),
                  ),
                  child: Text(u.rol.name, style: textTheme.labelSmall?.copyWith(fontWeight: FontWeight.w700)),
                ),
              ],
            ),
            const SizedBox(height: AppSpacing.sm),
            Row(
              children: [
                Icon(LucideIcons.hash, size: 14, color: scheme.onSurfaceVariant),
                const SizedBox(width: AppSpacing.xs),
                Text('ID ${u.id}', style: textTheme.bodySmall),
                const SizedBox(width: AppSpacing.md),
                Icon(LucideIcons.building2, size: 14, color: scheme.onSurfaceVariant),
                const SizedBox(width: AppSpacing.xs),
                Text(u.espacio?.nombre ?? 'Sin espacio', style: textTheme.bodySmall),
                if (esPropio) ...[
                  const SizedBox(width: AppSpacing.md),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: scheme.secondaryContainer,
                      borderRadius: BorderRadius.circular(AppRadius.pill),
                    ),
                    child: Text('Tú', style: textTheme.labelSmall),
                  ),
                ],
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
                if (!esPropio)
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

class _UsuarioFormDialog extends ConsumerStatefulWidget {
  const _UsuarioFormDialog({this.usuario, required this.onSaved});

  final AuthUser? usuario;
  final VoidCallback onSaved;

  @override
  ConsumerState<_UsuarioFormDialog> createState() => _UsuarioFormDialogState();
}

class _UsuarioFormDialogState extends ConsumerState<_UsuarioFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late String _username;
  late String _email;
  String _password = '';
  late RolUsuario _rol;
  int? _espacioId;
  bool _guardando = false;
  String? _error;

  bool get _esEdicion => widget.usuario != null;

  @override
  void initState() {
    super.initState();
    final u = widget.usuario;
    _username = u?.username ?? '';
    _email = u?.email ?? '';
    _rol = u?.rol ?? RolUsuario.usuario;
    _espacioId = u?.espacio?.id;
  }

  Future<void> _guardar() async {
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();
    if (_rol == RolUsuario.gestor && _espacioId == null) {
      setState(() => _error = 'Debes asignar un espacio al gestor');
      return;
    }
    setState(() {
      _guardando = true;
      _error = null;
    });
    try {
      final repo = ref.read(usuariosRepositoryProvider);
      if (_esEdicion) {
        await repo.actualizar(
          widget.usuario!.id,
          username: _username,
          email: _email,
          password: _password.isEmpty ? null : _password,
          rol: _rol.name,
          espacioId: _rol == RolUsuario.gestor ? _espacioId : null,
        );
      } else {
        if (_password.isEmpty) {
          setState(() => _error = 'La contraseña es requerida');
          setState(() => _guardando = false);
          return;
        }
        await repo.crear(
          username: _username,
          email: _email,
          password: _password,
          rol: _rol.name,
          espacioId: _rol == RolUsuario.gestor ? _espacioId : null,
        );
      }
      widget.onSaved();
      if (mounted) Navigator.pop(context);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(_esEdicion ? 'Usuario actualizado.' : 'Usuario creado.')));
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(e, fallback: _esEdicion ? 'No se pudo actualizar el usuario.' : 'No se pudo crear el usuario.'));
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final espaciosAsync = ref.watch(espaciosListProvider);

    return AlertDialog(
      title: Text(_esEdicion ? 'Editar usuario' : 'Nuevo usuario'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                initialValue: _username,
                decoration: const InputDecoration(labelText: 'Usuario *', hintText: 'Ej. juanperez'),
                validator: (v) {
                  if (v == null || v.trim().isEmpty) return 'Requerido';
                  if (v.trim().length < 3) return 'Mín. 3 caracteres';
                  if (v.trim().length > 80) return 'Máx. 80 caracteres';
                  return null;
                },
                onSaved: (v) => _username = v!.trim(),
              ),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                initialValue: _email,
                decoration: const InputDecoration(labelText: 'Email *', hintText: 'juan@example.com'),
                keyboardType: TextInputType.emailAddress,
                validator: (v) {
                  if (v == null || v.trim().isEmpty) return 'Requerido';
                  if (!v.contains('@') || !v.split('@').last.contains('.')) return 'Email inválido';
                  return null;
                },
                onSaved: (v) => _email = v!.trim(),
              ),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                initialValue: null,
                decoration: InputDecoration(labelText: _esEdicion ? 'Nueva contraseña (opcional)' : 'Contraseña *', hintText: 'Mín. 6 caracteres'),
                obscureText: true,
                validator: (v) {
                  if (!_esEdicion && (v == null || v.isEmpty)) return 'Requerido';
                  if (v != null && v.isNotEmpty && v.length < 6) return 'Mín. 6 caracteres';
                  if (v != null && v.length > 72) return 'Máx. 72 caracteres';
                  return null;
                },
                onChanged: (v) => _password = v,
                onSaved: (v) => _password = v ?? '',
              ),
              const SizedBox(height: AppSpacing.md),
              DropdownButtonFormField<RolUsuario>(
                initialValue: _rol,
                decoration: const InputDecoration(labelText: 'Rol *'),
                items: const [
                  DropdownMenuItem(value: RolUsuario.usuario, child: Text('Usuario de reservas')),
                  DropdownMenuItem(value: RolUsuario.gestor, child: Text('Gestor de recursos')),
                  DropdownMenuItem(value: RolUsuario.admin, child: Text('Administrador total')),
                ],
                onChanged: (v) => setState(() => _rol = v!),
                onSaved: (v) => _rol = v!,
              ),
              if (_rol == RolUsuario.gestor) ...[
                const SizedBox(height: AppSpacing.md),
                espaciosAsync.when(
                  loading: () => const LinearProgressIndicator(),
                  error: (e, _) => Text(apiErrorMessage(e, fallback: 'No se pudieron cargar los espacios.')),
                  data: (espacios) => DropdownButtonFormField<int>(
                    initialValue: _espacioId ?? (espacios.isNotEmpty ? espacios.first.id : null),
                    decoration: const InputDecoration(labelText: 'Espacio asignado *'),
                    items: espacios.map((e) => DropdownMenuItem(value: e.id, child: Text(e.nombre))).toList(),
                    onChanged: (v) => setState(() => _espacioId = v),
                    validator: (v) => v == null ? 'Requerido' : null,
                    onSaved: (v) => _espacioId = v,
                  ),
                ),
              ],
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
