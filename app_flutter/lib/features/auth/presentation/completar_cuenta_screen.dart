import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import 'package:supabase_flutter/supabase_flutter.dart' hide AuthUser;

import '../../../core/network/api_exception.dart';
import '../../../core/theme/app_spacing.dart';
import '../application/auth_provider.dart';

/// Pantalla donde una persona invitada (o alguien recuperando su
/// contraseña) elige su contraseña real por primera vez.
///
/// A esta pantalla se llega SOLO desde el link del correo de Supabase:
/// `main.dart` escucha `Supabase.instance.client.auth.onAuthStateChange` y
/// redirige acá apenas Supabase detecta el token de invitación en la URL
/// (evento `passwordRecovery` -- Supabase trata invitación y recuperación
/// igual del lado del cliente) y establece una sesión temporal. Sin esa
/// sesión temporal no hay nada que hacer acá — de ahí el chequeo de
/// `currentSession` antes de mostrar el formulario.
class CompletarCuentaScreen extends ConsumerStatefulWidget {
  const CompletarCuentaScreen({super.key, bool Function()? haySesionActiva}) : _haySesionActiva = haySesionActiva ?? _sesionRealDeSupabase;

  /// Inyectable para poder testear el estado "sin sesión" sin inicializar
  /// el singleton real de Supabase (ningún test de esta suite lo hace
  /// todavía) -- en producción siempre es [_sesionRealDeSupabase].
  final bool Function() _haySesionActiva;

  static bool _sesionRealDeSupabase() => Supabase.instance.client.auth.currentSession != null;

  @override
  ConsumerState<CompletarCuentaScreen> createState() => _CompletarCuentaScreenState();
}

class _CompletarCuentaScreenState extends ConsumerState<CompletarCuentaScreen> {
  final _formKey = GlobalKey<FormState>();
  final _passwordController = TextEditingController();
  final _confirmarController = TextEditingController();
  bool _submitting = false;
  String? _errorMessage;

  @override
  void dispose() {
    _passwordController.dispose();
    _confirmarController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _submitting = true;
      _errorMessage = null;
    });
    try {
      await ref.read(authProvider.notifier).completarCuenta(password: _passwordController.text);
      // Igual que en LoginScreen: la navegación a la ruta protegida la
      // resuelve el `redirect` de go_router al detectar el cambio de
      // estado de `authProvider`, no este widget directamente.
    } on AuthException catch (e) {
      // `updateUser` (llamado dentro de `completarCuenta`) le pega directo
      // a Supabase, no a nuestro backend -- lanza `AuthException` (paquete
      // `gotrue`), no `DioException`/`ApiException`. `apiErrorMessage` solo
      // sabe desenvolver esas dos, así que sin este catch el mensaje real
      // de Supabase (ej. "New password should be different from the old
      // password") se perdía detrás del fallback genérico.
      setState(() {
        _errorMessage = e.message;
      });
    } on Object catch (e) {
      setState(() {
        _errorMessage = apiErrorMessage(e, fallback: 'No se pudo completar la cuenta. Intenta de nuevo.');
      });
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final haySesionDeInvitacion = widget._haySesionActiva();

    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppSpacing.xl),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 400),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(LucideIcons.userCheck, size: 40, color: scheme.primary),
                const SizedBox(height: AppSpacing.lg),
                Text('Completá tu cuenta', style: Theme.of(context).textTheme.headlineSmall, textAlign: TextAlign.center),
                const SizedBox(height: AppSpacing.xs),
                Text(
                  'Elegí una contraseña para terminar de crear tu cuenta.',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: scheme.onSurfaceVariant),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: AppSpacing.xxl),
                if (!haySesionDeInvitacion)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(AppSpacing.xl),
                      child: Column(
                        children: [
                          Icon(LucideIcons.circleAlert, color: scheme.error, size: 32),
                          const SizedBox(height: AppSpacing.md),
                          Text(
                            'Este link ya no es válido o expiró. Volvé a abrir el link del correo de invitación, '
                            'o pedile a un administrador que te reenvíe la invitación.',
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                  )
                else
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(AppSpacing.xl),
                      child: Form(
                        key: _formKey,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            TextFormField(
                              controller: _passwordController,
                              decoration: const InputDecoration(
                                labelText: 'Contraseña',
                                prefixIcon: Icon(LucideIcons.lockKeyhole),
                              ),
                              obscureText: true,
                              autofillHints: const [AutofillHints.newPassword],
                              validator: (value) {
                                if (value == null || value.isEmpty) return 'Requerido';
                                if (value.length < 6) return 'Mínimo 6 caracteres';
                                return null;
                              },
                            ),
                            const SizedBox(height: AppSpacing.md),
                            TextFormField(
                              controller: _confirmarController,
                              decoration: const InputDecoration(
                                labelText: 'Confirmar contraseña',
                                prefixIcon: Icon(LucideIcons.lockKeyhole),
                              ),
                              obscureText: true,
                              autofillHints: const [AutofillHints.newPassword],
                              validator: (value) {
                                if (value == null || value.isEmpty) return 'Requerido';
                                if (value != _passwordController.text) return 'Las contraseñas no coinciden';
                                return null;
                              },
                              onFieldSubmitted: (_) => _submit(),
                            ),
                            if (_errorMessage != null) ...[
                              const SizedBox(height: AppSpacing.md),
                              Text(_errorMessage!, style: TextStyle(color: scheme.error)),
                            ],
                            const SizedBox(height: AppSpacing.xl),
                            FilledButton(
                              onPressed: _submitting ? null : _submit,
                              child: _submitting
                                  ? const SizedBox(
                                      height: 20,
                                      width: 20,
                                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                    )
                                  : const Text('Crear contraseña'),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
