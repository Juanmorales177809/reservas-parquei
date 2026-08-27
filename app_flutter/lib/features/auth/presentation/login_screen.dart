import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/theme/app_spacing.dart';
import '../application/auth_provider.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _submitting = false;
  String? _errorMessage;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _submitting = true;
      _errorMessage = null;
    });
    try {
      await ref.read(authProvider.notifier).login(
            email: _emailController.text.trim(),
            password: _passwordController.text,
          );
      // La navegación a la ruta protegida la resuelve el `redirect` de
      // go_router al detectar el cambio de estado de `authProvider`, no
      // este widget directamente.
    } on Object catch (e) {
      setState(() {
        _errorMessage = apiErrorMessage(e, fallback: 'No se pudo iniciar sesión. Intenta de nuevo.');
      });
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;

    return Scaffold(
      body: DecoratedBox(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [scheme.primaryContainer.withValues(alpha: 0.6), scheme.surface],
          ),
        ),
        child: Stack(
          children: [
            Positioned(
              top: -60,
              right: -60,
              child: _blob(scheme.tertiary.withValues(alpha: 0.25), 220),
            ),
            Positioned(
              bottom: -80,
              left: -80,
              child: _blob(scheme.primary.withValues(alpha: 0.2), 260),
            ),
            Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(AppSpacing.xl),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 400),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        width: 72,
                        height: 72,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(colors: [scheme.primary, scheme.tertiary]),
                          borderRadius: BorderRadius.circular(AppRadius.lg),
                          boxShadow: [
                            BoxShadow(
                              color: scheme.primary.withValues(alpha: 0.35),
                              blurRadius: 24,
                              offset: const Offset(0, 12),
                            ),
                          ],
                        ),
                        child: const Icon(LucideIcons.calendarCheck, color: Colors.white, size: 34),
                      ).animate().scale(begin: const Offset(0.6, 0.6), end: const Offset(1, 1), duration: 500.ms, curve: Curves.elasticOut),
                      const SizedBox(height: AppSpacing.lg),
                      Text('Reservas Parque i', style: Theme.of(context).textTheme.headlineSmall)
                          .animate()
                          .fadeIn(delay: 150.ms, duration: 300.ms)
                          .slideY(begin: 0.2, end: 0),
                      const SizedBox(height: AppSpacing.xs),
                      Text(
                        'Iniciá sesión para gestionar tus reservas',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: scheme.onSurfaceVariant),
                        textAlign: TextAlign.center,
                      ).animate().fadeIn(delay: 220.ms, duration: 300.ms),
                      const SizedBox(height: AppSpacing.xxl),
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(AppSpacing.xl),
                          child: Form(
                            key: _formKey,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                TextFormField(
                                  controller: _emailController,
                                  decoration: const InputDecoration(
                                    labelText: 'Email',
                                    prefixIcon: Icon(LucideIcons.mail),
                                  ),
                                  keyboardType: TextInputType.emailAddress,
                                  autofillHints: const [AutofillHints.email],
                                  validator: (value) {
                                    if (value == null || value.trim().isEmpty) return 'Requerido';
                                    if (!value.contains('@') || !value.split('@').last.contains('.')) {
                                      return 'Email inválido';
                                    }
                                    return null;
                                  },
                                ),
                                const SizedBox(height: AppSpacing.md),
                                TextFormField(
                                  controller: _passwordController,
                                  decoration: const InputDecoration(
                                    labelText: 'Contraseña',
                                    prefixIcon: Icon(LucideIcons.lockKeyhole),
                                  ),
                                  obscureText: true,
                                  autofillHints: const [AutofillHints.password],
                                  validator: (value) => (value == null || value.isEmpty) ? 'Requerido' : null,
                                  onFieldSubmitted: (_) => _submit(),
                                ),
                                Align(
                                  alignment: Alignment.centerRight,
                                  child: TextButton(
                                    onPressed: () => _mostrarRecuperarPassword(context, _emailController.text),
                                    child: const Text('¿Olvidaste tu contraseña?'),
                                  ),
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
                                      : const Text('Entrar'),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ).animate().fadeIn(delay: 280.ms, duration: 350.ms).slideY(begin: 0.15, end: 0),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _blob(Color color, double size) {
    // Una sola pasada (sin `repeat`) a propósito: un `AnimationController`
    // que se repite para siempre deja un timer "pendiente" cuando
    // `flutter_test` corre bajo `FakeAsync` y hace fallar cualquier test
    // que monte esta pantalla (encontrado al agregar esta animación) —
    // ver `test/features/auth/presentation/login_screen_test.dart`.
    return IgnorePointer(
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(color: color, shape: BoxShape.circle),
      ).animate().scale(
            begin: const Offset(0.85, 0.85),
            end: const Offset(1, 1),
            duration: 900.ms,
            curve: Curves.easeOut,
          ).fadeIn(duration: 700.ms),
    );
  }
}

void _mostrarRecuperarPassword(BuildContext context, String emailPrecargado) {
  showDialog<void>(
    context: context,
    builder: (_) => _RecuperarPasswordDialog(emailInicial: emailPrecargado),
  );
}

/// El mensaje de éxito es SIEMPRE el mismo, exista o no una cuenta con ese
/// email -- `AuthRepository.solicitarRecuperacion` no distingue del lado
/// del cliente (Supabase no expone esa información), así que mostrar algo
/// distinto acá filtraría qué emails están registrados.
class _RecuperarPasswordDialog extends ConsumerStatefulWidget {
  const _RecuperarPasswordDialog({required this.emailInicial});

  final String emailInicial;

  @override
  ConsumerState<_RecuperarPasswordDialog> createState() => _RecuperarPasswordDialogState();
}

class _RecuperarPasswordDialogState extends ConsumerState<_RecuperarPasswordDialog> {
  final _formKey = GlobalKey<FormState>();
  late final _emailController = TextEditingController(text: widget.emailInicial);
  bool _enviando = false;
  String? _error;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _enviar() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _enviando = true;
      _error = null;
    });
    try {
      await ref.read(authProvider.notifier).solicitarRecuperacion(email: _emailController.text.trim());
      if (mounted) Navigator.pop(context);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Si existe una cuenta con ese email, vas a recibir un correo con instrucciones.'),
          ),
        );
      }
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(e, fallback: 'No se pudo enviar el correo. Intenta de nuevo.'));
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Recuperar contraseña'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Ingresá tu email y te mandamos un link para elegir una contraseña nueva.'),
            const SizedBox(height: AppSpacing.md),
            TextFormField(
              key: const Key('recuperar_password_email'),
              controller: _emailController,
              decoration: const InputDecoration(labelText: 'Email'),
              keyboardType: TextInputType.emailAddress,
              autofillHints: const [AutofillHints.email],
              validator: (value) {
                if (value == null || value.trim().isEmpty) return 'Requerido';
                if (!value.contains('@') || !value.split('@').last.contains('.')) return 'Email inválido';
                return null;
              },
              onFieldSubmitted: (_) => _enviar(),
            ),
            if (_error != null) ...[
              const SizedBox(height: AppSpacing.sm),
              Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: _enviando ? null : () => Navigator.pop(context), child: const Text('Cancelar')),
        FilledButton(
          onPressed: _enviando ? null : _enviar,
          child: _enviando
              ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
              : const Text('Enviar'),
        ),
      ],
    );
  }
}
