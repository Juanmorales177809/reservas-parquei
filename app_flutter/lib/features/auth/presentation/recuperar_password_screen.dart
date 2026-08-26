import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/router/app_routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../data/auth_repository.dart';

/// Paso 1 de la recuperación: pide usuario o email, dispara
/// `POST /auth/recuperar`. La respuesta del backend es SIEMPRE 204 exista o
/// no el identificador (anti-enumeración) — este screen respeta eso: el
/// mensaje que muestra es genérico y NUNCA confirma ni desmiente que la
/// cuenta exista.
class RecuperarPasswordScreen extends ConsumerStatefulWidget {
  const RecuperarPasswordScreen({super.key});

  @override
  ConsumerState<RecuperarPasswordScreen> createState() => _RecuperarPasswordScreenState();
}

class _RecuperarPasswordScreenState extends ConsumerState<RecuperarPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _identificadorController = TextEditingController();
  bool _enviando = false;
  String? _error;

  @override
  void dispose() {
    _identificadorController.dispose();
    super.dispose();
  }

  Future<void> _enviar() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _enviando = true;
      _error = null;
    });
    final identificador = _identificadorController.text.trim();
    try {
      await ref.read(authRepositoryProvider).solicitarRecuperacion(identificador: identificador);
      if (!mounted) return;
      context.push(AppRoutes.restablecer, extra: identificador);
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(e, fallback: 'No se pudo enviar el código. Intenta de nuevo.'));
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Recuperar contraseña')),
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
                    'Ingresá tu usuario o email y te mandamos un código para restablecer tu contraseña.',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: AppSpacing.xl),
                  TextFormField(
                    controller: _identificadorController,
                    decoration: const InputDecoration(
                      labelText: 'Usuario o email',
                      prefixIcon: Icon(LucideIcons.userCircle),
                    ),
                    autofillHints: const [AutofillHints.username],
                    validator: (v) => (v == null || v.trim().isEmpty) ? 'Requerido' : null,
                    onFieldSubmitted: (_) => _enviar(),
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: AppSpacing.md),
                    Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                  ],
                  const SizedBox(height: AppSpacing.xl),
                  FilledButton(
                    onPressed: _enviando ? null : _enviar,
                    child: _enviando
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                          )
                        : const Text('Enviar código'),
                  ),
                  const SizedBox(height: AppSpacing.md),
                  // `go`, no `push`: si se llegó acá empujado desde /login
                  // (o cualquier otra ruta), go reemplaza la ubicación en
                  // vez de apilar, evitando el bug de navegación ya
                  // documentado en app_flutter/CLAUDE.md (push + guard).
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
