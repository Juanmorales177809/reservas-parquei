import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../core/router/app_routes.dart';
import '../core/theme/app_spacing.dart';
import '../features/auth/application/auth_provider.dart';
import 'app_shell.dart';

/// Zona de sesión de la `AppBar`: "Iniciar sesión" si no hay sesión, o el
/// avatar con el menú (identidad + "Cerrar sesión") si la hay.
///
/// **Las dos mitades viven en el mismo widget a propósito.** Este archivo ya
/// nació de un error de ese tipo: el logout existía solo en `InicioScreen`,
/// y al eliminarla la app se quedaba sin forma de cerrar sesión en móvil.
/// Se movió acá... y se repitió el error en el otro sentido: el botón de
/// "Iniciar sesión" se agregó solo a `TopNavShell`, así que en celular
/// (`BottomNavShell`) y en tablet (`RailNavShell`) un visitante anónimo no
/// tenía por dónde entrar.
///
/// Mientras los tres shells monten este widget SIN condicionar por sesión,
/// ninguno de los dos caminos puede volver a faltar en un tamaño de
/// pantalla. No reintroducir un `if (autenticado)` alrededor.
class SessionMenu extends ConsumerWidget {
  const SessionMenu({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authProvider).value;
    if (user == null) return const _BotonIniciarSesion();

    final scheme = Theme.of(context).colorScheme;
    final inicial = user.username.isEmpty ? '?' : user.username.substring(0, 1).toUpperCase();

    return MenuAnchor(
      alignmentOffset: const Offset(0, AppSpacing.xs),
      builder: (context, controller, child) => Tooltip(
        message: user.username,
        child: InkWell(
          onTap: () => controller.isOpen ? controller.close() : controller.open(),
          customBorder: const CircleBorder(),
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.xs),
            child: CircleAvatar(
              radius: 16,
              backgroundColor: scheme.primary,
              child: Text(
                inicial,
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: scheme.onPrimary,
                      fontWeight: FontWeight.w700,
                    ),
              ),
            ),
          ),
        ),
      ),
      menuChildren: [
        // Cabecera informativa, no accionable. Conserva el "quién soy" que
        // mostraba la vieja `InicioScreen` ("Hola, X" + rol).
        Padding(
          padding: const EdgeInsets.fromLTRB(AppSpacing.md, AppSpacing.sm, AppSpacing.md, AppSpacing.xs),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(user.username, style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
              Text(
                user.rol.name,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant),
              ),
            ],
          ),
        ),
        const Divider(height: 1),
        MenuItemButton(
          leadingIcon: const Icon(LucideIcons.userCog, size: 18),
          onPressed: () => context.push(AppRoutes.perfil),
          child: const Text('Mi perfil'),
        ),
        MenuItemButton(
          leadingIcon: const Icon(LucideIcons.logOut, size: 18),
          onPressed: () => ref.read(authProvider.notifier).logout(),
          child: const Text('Cerrar sesión'),
        ),
      ],
    );
  }
}

class _BotonIniciarSesion extends StatelessWidget {
  const _BotonIniciarSesion();

  @override
  Widget build(BuildContext context) {
    // En pantalla compacta la `AppBar` ya lleva el `BrandMark` completo
    // ("Reservas Parque i", ~190dp): un botón con ícono + "Iniciar sesión"
    // no entra en 375dp y desborda. Se acorta a "Entrar", el mismo verbo que
    // usa el botón del formulario de login, en vez de dejarlo solo con
    // ícono — que en móvil es justo donde peor se descubre.
    final compacta = MediaQuery.sizeOf(context).width < kCompactBreakpoint;

    // `go`, no `push`: con `push` la ubicación del router sigue siendo la
    // ruta de fondo y el guard de `app_router.dart` no redirige tras
    // autenticarse. Ver la sección correspondiente en app_flutter/CLAUDE.md.
    void irALogin() => context.go(AppRoutes.login);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xs),
      child: compacta
          ? FilledButton(onPressed: irALogin, child: const Text('Entrar'))
          : FilledButton.icon(
              onPressed: irALogin,
              icon: const Icon(LucideIcons.logIn, size: 18),
              label: const Text('Iniciar sesión'),
            ),
    );
  }
}
