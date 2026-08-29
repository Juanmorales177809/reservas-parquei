import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../../../core/widgets/staggered_entrance.dart';
import '../../../shell/app_shell.dart';
import '../../auth/application/auth_provider.dart';
import '../../auth/domain/auth_user.dart';
import '../../espacios/application/espacios_providers.dart';
import '../application/usuarios_providers.dart';
import '../data/usuarios_repository.dart';

/// Dos secciones desde la separación `personal`/`usuarios` (2026-08-28, ver
/// `backend/CLAUDE.md`) -- "Personal" (admin/gestor, `/personal`) y
/// "Usuarios" (rol usuario, `/usuarios`), cada una con su propio espacio de
/// IDs en el backend. `esPersonal` se hila hacia abajo por todos los
/// widgets de esta pantalla para decidir qué provider/endpoint usar y qué
/// campos mostrar en el formulario (rol/espacio solo aplican a personal).
class GestionUsuariosScreen extends ConsumerStatefulWidget {
  const GestionUsuariosScreen({super.key});

  @override
  ConsumerState<GestionUsuariosScreen> createState() => _GestionUsuariosScreenState();
}

class _GestionUsuariosScreenState extends ConsumerState<GestionUsuariosScreen> {
  bool _esPersonal = true;

  AsyncValue<List<AuthUser>> get _listaActual =>
      _esPersonal ? ref.watch(personalListProvider) : ref.watch(usuariosListProvider);

  void _invalidarListaActual() {
    ref.invalidate(_esPersonal ? personalListProvider : usuariosListProvider);
  }

  @override
  Widget build(BuildContext context) {
    final listaAsync = _listaActual;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Usuarios'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(56),
          child: Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.sm),
            child: SegmentedButton<bool>(
              segments: const [
                ButtonSegment(value: true, label: Text('Personal'), icon: Icon(LucideIcons.shield, size: 16)),
                ButtonSegment(value: false, label: Text('Usuarios'), icon: Icon(LucideIcons.user, size: 16)),
              ],
              selected: {_esPersonal},
              onSelectionChanged: (seleccion) => setState(() => _esPersonal = seleccion.first),
            ),
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _mostrarCrear(context),
        icon: const Icon(LucideIcons.userPlus, size: 18),
        label: Text(_esPersonal ? 'Nuevo' : 'Nuevo usuario'),
      ),
      body: listaAsync.when(
        loading: () => const LoadingSpinner(),
        error: (error, _) => ErrorView(
          message: apiErrorMessage(error, fallback: 'No se pudieron cargar los usuarios.'),
          onRetry: _invalidarListaActual,
        ),
        data: (usuarios) {
          if (usuarios.isEmpty) {
            return EmptyView(
              icon: LucideIcons.users,
              message: _esPersonal ? 'No hay personal registrado.' : 'No hay usuarios registrados.',
            );
          }
          final esCompacta = MediaQuery.sizeOf(context).width < kCompactBreakpoint;
          if (esCompacta) {
            return RefreshIndicator(
              onRefresh: () async => _invalidarListaActual(),
              child: ListView.separated(
                padding: const EdgeInsets.all(AppSpacing.lg),
                itemCount: usuarios.length,
                separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.md),
                itemBuilder: (context, index) =>
                    _UsuarioCard(usuario: usuarios[index], esPersonal: _esPersonal).staggerEntrance(index),
              ),
            );
          }
          return RefreshIndicator(
            onRefresh: () async => _invalidarListaActual(),
            child: CustomScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              slivers: [
                SliverPadding(
                  padding: const EdgeInsets.all(AppSpacing.lg),
                  sliver: SliverToBoxAdapter(child: _UsuariosTabla(usuarios: usuarios, esPersonal: _esPersonal)),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  void _mostrarCrear(BuildContext context) {
    showDialog<void>(
      context: context,
      builder: (_) => _UsuarioFormDialog(esPersonal: _esPersonal, onSaved: _invalidarListaActual),
    );
  }
}

String _inicialesDe(String username) {
  final v = username.trim();
  if (v.isEmpty) return '?';
  final separadores = RegExp(r'[_\.\s\-]');
  final partes = v.split(separadores).where((p) => p.isNotEmpty).toList();
  if (partes.length >= 2) {
    return (partes[0][0] + partes[1][0]).toUpperCase();
  }
  if (v.length == 1) return v.toUpperCase();
  return v.substring(0, 2).toUpperCase();
}

/// Muestra el link recién generado con un botón de copiar. Mientras el
/// SMTP del ITM sigue pendiente (`EMAIL_ENABLED=false`), `correoEnviado`
/// siempre da `false` y este diálogo es la única forma de entregar el
/// link — el día que haya SMTP configurado, el mismo endpoint ya lo manda
/// solo y este diálogo pasa a ser un respaldo, no el único camino.
void _mostrarLinkInvitacion(BuildContext context, ReenvioInvitacion resultado) {
  showDialog<void>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: const Text('Invitación reenviada'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            resultado.correoEnviado
                ? 'Se generó un nuevo link y se envió por correo.'
                : 'Se generó un nuevo link. Todavía no hay envío de correo configurado — copialo y '
                    'entregáselo a la persona por otro medio.',
          ),
          const SizedBox(height: AppSpacing.md),
          Container(
            padding: const EdgeInsets.all(AppSpacing.sm),
            decoration: BoxDecoration(
              color: AppColors.superficie,
              borderRadius: BorderRadius.circular(AppRadius.sm),
              border: Border.all(color: AppColors.borde),
            ),
            child: SelectableText(resultado.link, style: const TextStyle(fontSize: 12)),
          ),
        ],
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cerrar')),
        FilledButton.icon(
          onPressed: () {
            Clipboard.setData(ClipboardData(text: resultado.link));
            Navigator.pop(ctx);
          },
          icon: const Icon(LucideIcons.copy, size: 16),
          label: const Text('Copiar link'),
        ),
      ],
    ),
  );
}

class _UsuarioAvatar extends StatelessWidget {
  const _UsuarioAvatar({required this.username, required this.rol});

  final String username;
  final RolUsuario rol;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final bg = rol == RolUsuario.admin
        ? scheme.primaryContainer
        : rol == RolUsuario.gestor
            ? scheme.tertiaryContainer
            : scheme.surfaceContainerHighest;
    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(color: bg, shape: BoxShape.circle),
      alignment: Alignment.center,
      child: Text(
        _inicialesDe(username),
        style: Theme.of(context).textTheme.titleSmall?.copyWith(
              color: scheme.onSurfaceVariant,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.4,
            ),
      ),
    );
  }
}

class _UsuariosTabla extends StatelessWidget {
  const _UsuariosTabla({required this.usuarios, required this.esPersonal});

  final List<AuthUser> usuarios;
  final bool esPersonal;

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          _CabeceraTabla(),
          const Divider(height: 1, thickness: 1, color: AppColors.borde),
          ...List.generate(usuarios.length, (index) {
            final u = usuarios[index];
            final esUltimo = index == usuarios.length - 1;
            return Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                _FilaUsuario(usuario: u, esPersonal: esPersonal).staggerEntrance(index),
                if (!esUltimo) const Divider(height: 1, thickness: 1, color: AppColors.borde),
              ],
            );
          }),
        ],
      ),
    );
  }
}

class _CabeceraTabla extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppColors.superficie,
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg, vertical: AppSpacing.sm),
      child: Row(
        children: [
          Expanded(flex: 3, child: Text('USUARIO', style: AppText.overline())),
          Expanded(flex: 1, child: Text('ROL', style: AppText.overline())),
          Expanded(flex: 2, child: Text('ESPACIO', style: AppText.overline())),
          Expanded(flex: 1, child: Text('ID', style: AppText.overline())),
          Expanded(
            flex: 2,
            child: Align(
              alignment: Alignment.centerRight,
              child: Text('ACCIONES', style: AppText.overline()),
            ),
          ),
        ],
      ),
    );
  }
}

class _FilaUsuario extends ConsumerStatefulWidget {
  const _FilaUsuario({required this.usuario, required this.esPersonal});

  final AuthUser usuario;
  final bool esPersonal;

  @override
  ConsumerState<_FilaUsuario> createState() => _FilaUsuarioState();
}

class _FilaUsuarioState extends ConsumerState<_FilaUsuario> {
  bool _eliminando = false;
  bool _reenviando = false;

  void _invalidarLista() {
    ref.invalidate(widget.esPersonal ? personalListProvider : usuariosListProvider);
  }

  Future<void> _reenviarInvitacion() async {
    setState(() => _reenviando = true);
    try {
      final repo = ref.read(usuariosRepositoryProvider);
      final resultado = widget.esPersonal
          ? await repo.reenviarInvitacionPersonal(widget.usuario.id)
          : await repo.reenviarInvitacion(widget.usuario.id);
      if (mounted) _mostrarLinkInvitacion(context, resultado);
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo reenviar la invitación.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _reenviando = false);
    }
  }

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
      final repo = ref.read(usuariosRepositoryProvider);
      if (widget.esPersonal) {
        await repo.eliminarPersonal(widget.usuario.id);
      } else {
        await repo.eliminar(widget.usuario.id);
      }
      _invalidarLista();
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
      builder: (_) => _UsuarioFormDialog(usuario: widget.usuario, esPersonal: widget.esPersonal, onSaved: _invalidarLista),
    );
  }

  @override
  Widget build(BuildContext context) {
    final u = widget.usuario;
    final textTheme = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final currentUser = ref.watch(authProvider).value;
    // `personal` y `usuarios` tienen espacios de id independientes (ver
    // backend/CLAUDE.md) -- comparar solo por id colisionaría con una fila
    // de la OTRA tabla que casualmente comparta el mismo número.
    final currentUserEsPersonal = currentUser != null && currentUser.rol != RolUsuario.usuario;
    final esPropio = currentUserEsPersonal == widget.esPersonal && currentUser?.id == u.id;

    return Container(
      color: AppColors.superficie,
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg, vertical: AppSpacing.md),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Expanded(
            flex: 3,
            child: Row(
              children: [
                _UsuarioAvatar(username: u.username, rol: u.rol),
                const SizedBox(width: AppSpacing.md),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(u.username, style: textTheme.titleSmall, overflow: TextOverflow.ellipsis),
                      Text(u.email, style: textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant), overflow: TextOverflow.ellipsis),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            flex: 1,
            child: Align(
              alignment: Alignment.centerLeft,
              child: Container(
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
            ),
          ),
          Expanded(
            flex: 2,
            child: Row(
              children: [
                Icon(LucideIcons.building2, size: 14, color: scheme.onSurfaceVariant),
                const SizedBox(width: AppSpacing.xs),
                Expanded(child: Text(u.espacio?.nombre ?? 'Sin espacio', style: textTheme.bodySmall, overflow: TextOverflow.ellipsis)),
                if (esPropio) ...[
                  const SizedBox(width: AppSpacing.sm),
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
          ),
          Expanded(
            flex: 1,
            child: Row(
              children: [
                Icon(LucideIcons.hash, size: 14, color: scheme.onSurfaceVariant),
                const SizedBox(width: AppSpacing.xs),
                Text(
                  '${u.id}',
                  style: AppText.numerico(fontSize: 12.5, color: AppColors.textoTerciario, fontWeight: FontWeight.w500),
                ),
              ],
            ),
          ),
          Expanded(
            flex: 2,
            // "Editar"/"Eliminar" como botones anchos completos + el ícono
            // de reenviar invitación no entraban en flex:2 de una tabla de
            // 5 columnas a un ancho moderado -- overflow real encontrado
            // por `gestion_usuarios_screen_test.dart` (nunca se había
            // testeado esta fila antes). Mismo patrón ya usado en
            // `gestion_reservas_screen.dart`: una sola acción primaria
            // (acá, reenviar invitación) + el resto en un `PopupMenuButton`.
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                IconButton(
                  onPressed: _reenviando || _eliminando ? null : _reenviarInvitacion,
                  tooltip: 'Reenviar invitación',
                  icon: _reenviando
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(LucideIcons.mailPlus, size: 16),
                ),
                PopupMenuButton<String>(
                  enabled: !_eliminando,
                  tooltip: 'Más acciones',
                  icon: Icon(LucideIcons.ellipsisVertical, size: 18, color: AppColors.textoSecundario),
                  onSelected: (v) {
                    if (v == 'editar') _editar();
                    if (v == 'eliminar') _eliminar();
                  },
                  itemBuilder: (context) => [
                    const PopupMenuItem(
                      value: 'editar',
                      child: Row(children: [Icon(LucideIcons.pencil, size: 16, color: AppColors.textoSecundario), SizedBox(width: AppSpacing.sm), Text('Editar')]),
                    ),
                    if (!esPropio)
                      const PopupMenuItem(
                        value: 'eliminar',
                        child: Row(children: [Icon(LucideIcons.trash2, size: 16, color: AppColors.textoSecundario), SizedBox(width: AppSpacing.sm), Text('Eliminar')]),
                      ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _UsuarioCard extends ConsumerStatefulWidget {
  const _UsuarioCard({required this.usuario, required this.esPersonal});

  final AuthUser usuario;
  final bool esPersonal;

  @override
  ConsumerState<_UsuarioCard> createState() => _UsuarioCardState();
}

class _UsuarioCardState extends ConsumerState<_UsuarioCard> {
  bool _eliminando = false;
  bool _reenviando = false;

  void _invalidarLista() {
    ref.invalidate(widget.esPersonal ? personalListProvider : usuariosListProvider);
  }

  Future<void> _reenviarInvitacion() async {
    setState(() => _reenviando = true);
    try {
      final repo = ref.read(usuariosRepositoryProvider);
      final resultado = widget.esPersonal
          ? await repo.reenviarInvitacionPersonal(widget.usuario.id)
          : await repo.reenviarInvitacion(widget.usuario.id);
      if (mounted) _mostrarLinkInvitacion(context, resultado);
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo reenviar la invitación.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _reenviando = false);
    }
  }

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
      final repo = ref.read(usuariosRepositoryProvider);
      if (widget.esPersonal) {
        await repo.eliminarPersonal(widget.usuario.id);
      } else {
        await repo.eliminar(widget.usuario.id);
      }
      _invalidarLista();
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
      builder: (_) => _UsuarioFormDialog(usuario: widget.usuario, esPersonal: widget.esPersonal, onSaved: _invalidarLista),
    );
  }

  @override
  Widget build(BuildContext context) {
    final u = widget.usuario;
    final textTheme = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final currentUser = ref.watch(authProvider).value;
    // `personal` y `usuarios` tienen espacios de id independientes (ver
    // backend/CLAUDE.md) -- comparar solo por id colisionaría con una fila
    // de la OTRA tabla que casualmente comparta el mismo número.
    final currentUserEsPersonal = currentUser != null && currentUser.rol != RolUsuario.usuario;
    final esPropio = currentUserEsPersonal == widget.esPersonal && currentUser?.id == u.id;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                _UsuarioAvatar(username: u.username, rol: u.rol),
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
                IconButton(
                  onPressed: _reenviando || _eliminando ? null : _reenviarInvitacion,
                  tooltip: 'Reenviar invitación',
                  icon: _reenviando
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(LucideIcons.mailPlus, size: 16),
                ),
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
  const _UsuarioFormDialog({this.usuario, required this.esPersonal, required this.onSaved});

  final AuthUser? usuario;
  final bool esPersonal;
  final VoidCallback onSaved;

  @override
  ConsumerState<_UsuarioFormDialog> createState() => _UsuarioFormDialogState();
}

class _UsuarioFormDialogState extends ConsumerState<_UsuarioFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late String _username;
  late String _email;
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
    _rol = u?.rol ?? (widget.esPersonal ? RolUsuario.gestor : RolUsuario.usuario);
    _espacioId = u?.espacio?.id;
  }

  Future<void> _guardar() async {
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();
    if (widget.esPersonal && _rol == RolUsuario.gestor && _espacioId == null) {
      setState(() => _error = 'Debes asignar un espacio al gestor');
      return;
    }
    setState(() {
      _guardando = true;
      _error = null;
    });
    try {
      final repo = ref.read(usuariosRepositoryProvider);
      if (widget.esPersonal) {
        if (_esEdicion) {
          await repo.actualizarPersonal(
            widget.usuario!.id,
            username: _username,
            email: _email,
            rol: _rol.name,
            espacioId: _rol == RolUsuario.gestor ? _espacioId : null,
          );
        } else {
          await repo.crearPersonal(
            username: _username,
            email: _email,
            rol: _rol.name,
            espacioId: _rol == RolUsuario.gestor ? _espacioId : null,
          );
        }
      } else {
        if (_esEdicion) {
          await repo.actualizar(widget.usuario!.id, username: _username, email: _email);
        } else {
          // Sin contraseña: el backend invita a la persona por email vía
          // Supabase — el admin ya no la elige ni la ve.
          await repo.crear(username: _username, email: _email);
        }
      }
      widget.onSaved();
      if (mounted) Navigator.pop(context);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              _esEdicion
                  ? 'Usuario actualizado.'
                  : 'Usuario creado. Se le envió un correo de invitación para elegir su contraseña.',
            ),
          ),
        );
      }
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
      title: Text(_esEdicion ? 'Editar usuario' : (widget.esPersonal ? 'Nuevo miembro del personal' : 'Nuevo usuario')),
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
              if (widget.esPersonal) ...[
                const SizedBox(height: AppSpacing.md),
                DropdownButtonFormField<RolUsuario>(
                  initialValue: _rol,
                  decoration: const InputDecoration(labelText: 'Rol *'),
                  items: const [
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
