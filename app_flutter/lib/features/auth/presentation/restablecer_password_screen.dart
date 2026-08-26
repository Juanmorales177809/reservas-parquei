import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/router/app_routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../data/auth_repository.dart';

/// Paso 2 de la recuperación: código de 6 dígitos + contraseña nueva,
/// `POST /auth/restablecer`. [identificadorInicial] llega desde
/// [RecuperarPasswordScreen] (vía `extra` de go_router) para no hacer
/// retipear usuario/email — sigue siendo editable por si se equivocaron.
class RestablecerPasswordScreen extends ConsumerStatefulWidget {
  const RestablecerPasswordScreen({this.identificadorInicial, super.key});

  final String? identificadorInicial;

  @override
  ConsumerState<RestablecerPasswordScreen> createState() => _RestablecerPasswordScreenState();
}

class _RestablecerPasswordScreenState extends ConsumerState<RestablecerPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  late final _identificadorController = TextEditingController(text: widget.identificadorInicial);
  final _codigoController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _enviando = false;
  String? _error;

  @override
  void dispose() {
    _identificadorController.dispose();
    _codigoController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _restablecer() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _enviando = true;
      _error = null;
    });
    try {
      await ref.read(authRepositoryProvider).restablecerPassword(
            identificador: _identificadorController.text.trim(),
            codigo: _codigoController.text.trim(),
            passwordNueva: _passwordController.text,
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Contraseña restablecida. Ya podés iniciar sesión.')),
      );
      context.go(AppRoutes.login);
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(e, fallback: 'No se pudo restablecer la contraseña.'));
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Restablecer contraseña')),
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
                    'Ingresá el código de 6 dígitos que te llegó por correo (vence en 15 minutos) y tu nueva contraseña.',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: AppSpacing.xl),
                  TextFormField(
                    controller: _identificadorController,
                    decoration: const InputDecoration(
                      labelText: 'Usuario o email',
                      prefixIcon: Icon(LucideIcons.userCircle),
                    ),
                    validator: (v) => (v == null || v.trim().isEmpty) ? 'Requerido' : null,
                  ),
                  const SizedBox(height: AppSpacing.md),
                  TextFormField(
                    controller: _codigoController,
                    decoration: const InputDecoration(
                      labelText: 'Código de 6 dígitos',
                      prefixIcon: Icon(LucideIcons.keyRound),
                    ),
                    keyboardType: TextInputType.number,
                    maxLength: 6,
                    validator: (v) {
                      if (v == null || v.trim().isEmpty) return 'Requerido';
                      if (v.trim().length != 6) return 'Debe tener 6 dígitos';
                      return null;
                    },
                  ),
                  TextFormField(
                    controller: _passwordController,
                    decoration: const InputDecoration(
                      labelText: 'Nueva contraseña',
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
                    onFieldSubmitted: (_) => _restablecer(),
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: AppSpacing.md),
                    Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                  ],
                  const SizedBox(height: AppSpacing.xl),
                  FilledButton(
                    onPressed: _enviando ? null : _restablecer,
                    child: _enviando
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                          )
                        : const Text('Restablecer contraseña'),
                  ),
                  const SizedBox(height: AppSpacing.md),
                  TextButton(
                    onPressed: () => context.go(AppRoutes.login),
                    child: const Text('Volver a iniciar sesión'),
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
