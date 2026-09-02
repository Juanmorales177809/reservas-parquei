import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/router/app_routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../application/auth_provider.dart';

/// Autoregistro abierto (`POST /auth/registro`, sin aprobación de un admin
/// -- ver `backend/CLAUDE.md`, "Autoregistro abierto"): reemplaza al único
/// camino anterior de alta de cuenta (un admin invita desde
/// `GestionUsuariosScreen`, que sigue existiendo tal cual para asignar
/// roles `gestor`/`admin`). Esta pantalla siempre crea la cuenta con rol
/// `usuario`; tras crearla, `AuthRepository.registrarse` ya deja la
/// sesión iniciada -- la navegación posterior (a `/perfil`, porque el
/// perfil recién creado está incompleto) la resuelve el `redirect` de
/// go_router, igual que en `LoginScreen`, no este widget.
class RegistroScreen extends ConsumerStatefulWidget {
  const RegistroScreen({super.key});

  @override
  ConsumerState<RegistroScreen> createState() => _RegistroScreenState();
}

class _RegistroScreenState extends ConsumerState<RegistroScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmarController = TextEditingController();
  bool _submitting = false;
  String? _errorMessage;

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
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
      await ref.read(authProvider.notifier).registrarse(
            username: _usernameController.text.trim(),
            email: _emailController.text.trim(),
            password: _passwordController.text,
          );
      // Igual que en LoginScreen: la navegación post-registro la resuelve
      // el `redirect` de go_router al detectar el cambio de estado de
      // `authProvider`, no este widget.
    } on Object catch (e) {
      setState(() {
        _errorMessage = apiErrorMessage(e, fallback: 'No se pudo crear la cuenta. Intenta de nuevo.');
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
        child: Center(
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
                        BoxShadow(color: scheme.primary.withValues(alpha: 0.35), blurRadius: 24, offset: const Offset(0, 12)),
                      ],
                    ),
                    child: const Icon(LucideIcons.userPlus, color: Colors.white, size: 34),
                  ).animate().scale(begin: const Offset(0.6, 0.6), end: const Offset(1, 1), duration: 500.ms, curve: Curves.elasticOut),
                  const SizedBox(height: AppSpacing.lg),
                  Text('Crear cuenta', style: Theme.of(context).textTheme.headlineSmall)
                      .animate()
                      .fadeIn(delay: 150.ms, duration: 300.ms)
                      .slideY(begin: 0.2, end: 0),
                  const SizedBox(height: AppSpacing.xs),
                  Text(
                    'Registrate para reservar laboratorios y equipos',
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
                              controller: _usernameController,
                              decoration: const InputDecoration(
                                labelText: 'Nombre de usuario',
                                prefixIcon: Icon(LucideIcons.user),
                              ),
                              autofillHints: const [AutofillHints.username],
                              validator: (value) {
                                final v = value?.trim() ?? '';
                                if (v.isEmpty) return 'Requerido';
                                if (v.length < 3) return 'Mínimo 3 caracteres';
                                return null;
                              },
                            ),
                            const SizedBox(height: AppSpacing.md),
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
                              autofillHints: const [AutofillHints.newPassword],
                              validator: (value) {
                                if (value == null || value.isEmpty) return 'Requerido';
                                if (value.length < 8) return 'Mínimo 8 caracteres';
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
                                  : const Text('Crear cuenta'),
                            ),
                            const SizedBox(height: AppSpacing.md),
                            TextButton(
                              onPressed: _submitting ? null : () => context.go(AppRoutes.login),
                              child: const Text('¿Ya tenés cuenta? Iniciá sesión'),
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
      ),
    );
  }
}
