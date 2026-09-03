import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/domain/enums.dart';
import '../../../core/network/api_exception.dart';
import '../../../core/router/app_routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../auth/application/auth_provider.dart';
import '../../auth/domain/auth_user.dart';
import '../data/usuarios_repository.dart';

/// `PUT /usuarios/me` -- self-service, cualquier usuario autenticado edita
/// su propio perfil (Fase A2). Los campos vienen del formulario real de
/// solicitud de laboratorios del ITM (documento, teléfono, institución,
/// vinculación, dependencia) y se completan acá una sola vez, no en cada
/// reserva -- ver `LaboratorioReservaSheet`, que ya no vuelve a pedirlos.
///
/// Obligatorio para cualquier rol (2026-08-28): el guard de
/// `app_router.dart` redirige acá mientras `AuthUser.perfilCompleto` sea
/// `false`, sin importar a qué ruta se intente navegar -- por eso los 5
/// campos llevan `validator` (antes eran todos opcionales) y el `AppBar`
/// tiene su propio botón de "Cerrar sesión": si esta pantalla se llegó a
/// mostrar por el guard forzado (recién invitado, sin nada en el stack de
/// navegación para volver atrás), sin ese botón la única salida sería
/// completar el formulario ahí mismo.
class MiPerfilScreen extends ConsumerStatefulWidget {
  const MiPerfilScreen({super.key});

  @override
  ConsumerState<MiPerfilScreen> createState() => _MiPerfilScreenState();
}

class _MiPerfilScreenState extends ConsumerState<MiPerfilScreen> {
  final _formKey = GlobalKey<FormState>();
  final _documentoController = TextEditingController();
  final _telefonoController = TextEditingController();
  final _institucionController = TextEditingController();
  final _dependenciaController = TextEditingController();
  VinculacionUsuario? _vinculacion;
  bool _recibirCorreos = true;
  bool _guardando = false;
  bool _precargado = false;
  String? _error;

  /// Precarga los controllers la primera vez que `authProvider` resuelve un
  /// usuario -- no puede hacerse en `initState`: en el primer frame ese
  /// provider puede seguir en `AsyncLoading` (su `build()` es async), y
  /// `.value` daría `null` incluso con sesión real. `_precargado` evita
  /// pisar lo que la persona ya haya escrito en rebuilds posteriores.
  void _precargarSiHaceFalta(AuthUser? usuario) {
    if (_precargado || usuario == null) return;
    _documentoController.text = usuario.documentoIdentificacion ?? '';
    _telefonoController.text = usuario.telefono ?? '';
    _institucionController.text = usuario.institucion ?? '';
    _dependenciaController.text = usuario.dependencia ?? '';
    _vinculacion = usuario.vinculacion;
    _recibirCorreos = usuario.recibirCorreos;
    _precargado = true;
  }

  @override
  void dispose() {
    _documentoController.dispose();
    _telefonoController.dispose();
    _institucionController.dispose();
    _dependenciaController.dispose();
    super.dispose();
  }

  Future<void> _guardar() async {
    if (!_formKey.currentState!.validate()) return;
    // Se captura ANTES de mutar el perfil: es lo único que distingue "vine
    // acá a la fuerza porque el perfil estaba incompleto" de "entré por mi
    // cuenta desde el menú de sesión a editar un perfil que ya estaba
    // completo" -- después de guardar, `perfilCompleto` siempre da `true`
    // en ambos casos.
    final completabaAhora = !(ref.read(authProvider).value?.perfilCompleto ?? true);
    setState(() {
      _guardando = true;
      _error = null;
    });
    try {
      final user = await ref.read(usuariosRepositoryProvider).actualizarMiPerfil(
            documentoIdentificacion: _documentoController.text.trim(),
            telefono: _telefonoController.text.trim(),
            institucion: _institucionController.text.trim(),
            vinculacion: _vinculacion,
            dependencia: _dependenciaController.text.trim(),
            recibirCorreos: _recibirCorreos,
          );
      ref.read(authProvider.notifier).actualizarPerfilLocal(user);
      if (!mounted) return;
      if (completabaAhora) {
        // El guard de `app_router.dart` trajo a la fuerza hasta acá (sin
        // nada en el stack para volver atrás); quedarse mostrando solo un
        // snackbar dejaba a la persona clavada en /perfil sin ningún
        // camino de vuelta al resto de la app -- bug real reportado.
        context.go(AppRoutes.admin);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Perfil actualizado.')));
      }
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(e, fallback: 'No se pudo actualizar el perfil.'));
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final usuario = ref.watch(authProvider).value;
    _precargarSiHaceFalta(usuario);
    final obligatorio = usuario != null && !usuario.perfilCompleto;
    // Scaffold sin appBar: no duplica el chrome del shell (la ruta ya vive
    // dentro del ShellRoute, ver app_router.dart), pero sigue haciendo
    // falta como ancestro de Material (TextField lo exige) y de
    // ScaffoldMessenger (el SnackBar de "Perfil actualizado.") -- mismo
    // patrón ya usado en ConfiguracionLaboratorioScreen.
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 600),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                Row(
                  children: [
                    Expanded(child: Text('Mi perfil', style: Theme.of(context).textTheme.titleLarge)),
                    IconButton(
                      icon: const Icon(LucideIcons.logOut),
                      tooltip: 'Cerrar sesión',
                      onPressed: () => ref.read(authProvider.notifier).logout(),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.md),
                Text(
                  obligatorio
                      ? 'Antes de continuar, completá estos datos -- se guardan una sola vez y se reutilizan al hacer una solicitud.'
                      : 'Estos datos se completan una sola vez y se reutilizan al hacer una solicitud.',
                  style: Theme.of(context).textTheme.bodyMedium,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: AppSpacing.xl),
                TextFormField(
                  controller: _documentoController,
                  decoration: const InputDecoration(labelText: 'Documento de identificación'),
                  validator: (v) => (v == null || v.trim().isEmpty) ? 'Requerido' : null,
                ),
                const SizedBox(height: AppSpacing.md),
                TextFormField(
                  controller: _telefonoController,
                  decoration: const InputDecoration(labelText: 'Teléfono/celular'),
                  keyboardType: TextInputType.phone,
                  validator: (v) => (v == null || v.trim().isEmpty) ? 'Requerido' : null,
                ),
                const SizedBox(height: AppSpacing.md),
                TextFormField(
                  controller: _institucionController,
                  decoration: const InputDecoration(labelText: 'Institución a la que pertenece'),
                  validator: (v) => (v == null || v.trim().isEmpty) ? 'Requerido' : null,
                ),
                const SizedBox(height: AppSpacing.md),
                DropdownButtonFormField<VinculacionUsuario>(
                  initialValue: _vinculacion,
                  decoration: const InputDecoration(labelText: 'Vinculación'),
                  items: VinculacionUsuario.values
                      .map((v) => DropdownMenuItem(value: v, child: Text(vinculacionUsuarioLabel(v))))
                      .toList(),
                  onChanged: (v) => setState(() => _vinculacion = v),
                  validator: (v) => v == null ? 'Requerido' : null,
                ),
                const SizedBox(height: AppSpacing.md),
                TextFormField(
                  controller: _dependenciaController,
                  decoration: const InputDecoration(labelText: 'Dependencia / Facultad'),
                  validator: (v) => (v == null || v.trim().isEmpty) ? 'Requerido' : null,
                ),
                const SizedBox(height: AppSpacing.md),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Recibir notificaciones por correo'),
                  subtitle: const Text('Aprobaciones, rechazos y cambios de tus reservas.'),
                  value: _recibirCorreos,
                  onChanged: (v) => setState(() => _recibirCorreos = v),
                ),
                if (_error != null) ...[
                  const SizedBox(height: AppSpacing.md),
                  Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                ],
                const SizedBox(height: AppSpacing.xl),
                  FilledButton(
                    onPressed: _guardando ? null : _guardar,
                    child: _guardando
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                          )
                        : const Text('Guardar'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
