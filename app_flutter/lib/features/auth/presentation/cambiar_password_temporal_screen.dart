import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/theme/app_spacing.dart';
import '../application/auth_provider.dart';

/// Pantalla forzada por el guard de `app_router.dart` cuando
/// `AuthUser.debeCambiarPassword` es true (alta de usuario con contraseña
/// temporal, o recuperación). No tiene forma de "cancelar" ni volver atrás
/// a propósito: es obligatoria. Al completarse, el propio cambio de estado
/// de `authProvider` hace que el guard deje de redirigir acá — no hay
/// navegación explícita en este archivo, mismo criterio que `LoginScreen`.
class CambiarPasswordTemporalScreen extends ConsumerStatefulWidget {
  const CambiarPasswordTemporalScreen({super.key});

  @override
  ConsumerState<CambiarPasswordTemporalScreen> createState() => _CambiarPasswordTemporalScreenState();
}

class _CambiarPasswordTemporalScreenState extends ConsumerState<CambiarPasswordTemporalScreen> {
  final _formKey = GlobalKey<FormState>();
  final _actualController = TextEditingController();
  final _nuevaController = TextEditingController();
  final _confirmarController = TextEditingController();
  bool _guardando = false;
  String? _error;

  @override
  void dispose() {
    _actualController.dispose();
    _nuevaController.dispose();
    _confirmarController.dispose();
    super.dispose();
  }

  Future<void> _guardar() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _guardando = true;
      _error = null;
    });
    try {
      await ref.read(authProvider.notifier).cambiarPassword(
            passwordActual: _actualController.text,
            passwordNueva: _nuevaController.text,
          );
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(e, fallback: 'No se pudo cambiar la contraseña.'));
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Cambiar contraseña'),
        automaticallyImplyLeading: false,
        // Único punto de salida de esta pantalla forzada: si alguien no
        // recuerda ni siquiera la temporal, cerrar sesión es preferible a
        // dejarlo sin ninguna acción posible en la UI.
        actions: [
          TextButton.icon(
            onPressed: () => ref.read(authProvider.notifier).logout(),
            icon: const Icon(LucideIcons.logOut, size: 18),
            label: const Text('Cerrar sesión'),
          ),
        ],
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppSpacing.xl),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 400),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Tu contraseña actual es temporal. Por seguridad, tenés que cambiarla antes de continuar.',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: AppSpacing.xl),
                  TextFormField(
                    controller: _actualController,
                    decoration: const InputDecoration(
                      labelText: 'Contraseña temporal',
                      prefixIcon: Icon(LucideIcons.lockKeyhole),
                    ),
                    obscureText: true,
                    autofillHints: const [AutofillHints.password],
                    validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null,
                  ),
                  const SizedBox(height: AppSpacing.md),
                  TextFormField(
                    controller: _nuevaController,
                    decoration: const InputDecoration(
                      labelText: 'Contraseña nueva',
                      prefixIcon: Icon(LucideIcons.lockKeyhole),
                      hintText: 'Mín. 6 caracteres',
                    ),
                    obscureText: true,
                    autofillHints: const [AutofillHints.newPassword],
                    validator: (v) {
                      if (v == null || v.isEmpty) return 'Requerido';
                      if (v.length < 6) return 'Mín. 6 caracteres';
                      if (v.length > 72) return 'Máx. 72 caracteres';
                      return null;
                    },
                  ),
                  const SizedBox(height: AppSpacing.md),
                  TextFormField(
                    controller: _confirmarController,
                    decoration: const InputDecoration(
                      labelText: 'Confirmar contraseña nueva',
                      prefixIcon: Icon(LucideIcons.lockKeyhole),
                    ),
                    obscureText: true,
                    validator: (v) => v != _nuevaController.text ? 'No coincide' : null,
                    onFieldSubmitted: (_) => _guardar(),
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
                        : const Text('Cambiar contraseña'),
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
