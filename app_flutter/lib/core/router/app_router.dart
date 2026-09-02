import 'package:animations/animations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/auditoria/presentation/auditoria_screen.dart';
import '../../features/auth/application/auth_provider.dart';
import '../../features/auth/presentation/completar_cuenta_screen.dart';
import '../../features/auth/presentation/login_screen.dart';
import '../../features/auth/presentation/registro_screen.dart';
import '../../features/dashboard/presentation/dashboard_screen.dart';
import '../../features/laboratorios/presentation/configuracion_laboratorio_screen.dart';
import '../../features/laboratorios/presentation/laboratorio_detalle_screen.dart';
import '../../features/laboratorios/presentation/laboratorios_list_screen.dart';
import '../../features/laboratorios/presentation/gestion_laboratorios_screen.dart';
import '../../features/legal/presentation/terminos_screen.dart';
import '../../features/recursos/presentation/gestion_recursos_screen.dart';
import '../../features/reservas/presentation/gestion_reservas_screen.dart';
import '../../features/reservas/presentation/mis_reservas_screen.dart';
import '../../features/tipos_reserva/presentation/gestion_tipos_reserva_screen.dart';
import '../../features/usuarios/presentation/gestion_usuarios_screen.dart';
import '../../features/usuarios/presentation/mi_perfil_screen.dart';
import '../../features/espacios/presentation/gestion_espacios_screen.dart';
import '../../shell/app_shell.dart';
import 'app_routes.dart';
import 'nav_destinations.dart';

/// Transición para destinos "de pestaña" dentro del `ShellRoute` (Inicio,
/// Laboratorios, Reservas, Dashboard, gestión...): "fade through" de Material
/// Motion — la que corresponde a cambiar entre destinos del mismo nivel de
/// navegación (no es un "entrar a", es un "cambiar a"). Antes de este pase
/// de diseño estas rutas no tenían transición propia (el salto entre
/// pestañas era un corte seco); ahora todo el router usa una transición
/// intencional, consistente con `laboratorioDetalleTemplate` (que ya usaba
/// shared axis desde la Fase 1).
Page<void> _fadeThroughPage(GoRouterState state, Widget child) {
  return CustomTransitionPage(
    key: state.pageKey,
    child: child,
    transitionsBuilder: (context, animation, secondaryAnimation, child) => FadeThroughTransition(
      animation: animation,
      secondaryAnimation: secondaryAnimation,
      child: child,
    ),
  );
}

/// Transición para rutas "empujadas" (drill-in, con jerarquía: vengo de A
/// y entro a B) — shared axis escalado, misma semántica que ya tenía
/// `laboratorioDetalleTemplate`.
Page<void> _sharedAxisPage(GoRouterState state, Widget child) {
  return CustomTransitionPage(
    key: state.pageKey,
    child: child,
    transitionsBuilder: (context, animation, secondaryAnimation, child) => SharedAxisTransition(
      animation: animation,
      secondaryAnimation: secondaryAnimation,
      transitionType: SharedAxisTransitionType.scaled,
      child: child,
    ),
  );
}

/// Reemplaza `ProtectedRoute.tsx`: guard centralizado una sola vez en el
/// router (no montado en cada pantalla). Misma semántica: no decidir
/// mientras `authProvider` está cargando; sin sesión en ruta protegida →
/// `/login`; con sesión en `/login` → inicio. `AppRoutes.publicas` se
/// compara contra `state.fullPath` (el template de ruta, ej.
/// `/laboratorios/:id`), no contra la URL interpolada. El guard por ROL
/// (Fase 4) reutiliza `kNavDestinations`: si la ruta actual coincide con
/// un destino de nav que tiene `rolesPermitidos`, y el usuario no cumple,
/// se redirige — una sola fuente de verdad entre "qué se ve en la barra
/// de navegación" y "qué rutas puede visitar cada rol".
final goRouterProvider = Provider<GoRouter>((ref) {
  // `refreshListenable` necesita un `Listenable` clásico; puenteamos los
  // cambios de `authProvider` (Riverpod) a un `ValueNotifier` para que
  // go_router reevalúe `redirect` en cada cambio de sesión.
  final refresh = ValueNotifier<int>(0);
  ref.listen(authProvider, (_, _) => refresh.value++);
  ref.onDispose(refresh.dispose);

  return GoRouter(
    // Laboratorios es pública: un visitante anónimo debe poder llegar ahí sin
    // chocar primero con el guard de /dashboard (que si fuera el arranque
    // lo mandaría directo a /login antes de ver la navegación).
    initialLocation: AppRoutes.laboratorios,
    refreshListenable: refresh,
    redirect: (context, state) {
      final authState = ref.read(authProvider);
      if (authState.isLoading) return null;

      final user = authState.value;
      final esRutaPublica = AppRoutes.publicas.contains(state.fullPath);

      if (user == null && !esRutaPublica) return AppRoutes.login;
      // `completarCuenta` entra acá también: una vez que se fija la
      // contraseña y se canjea la sesión (ver AuthRepository.completarCuenta),
      // el usuario ya está autenticado y no tiene sentido dejarlo en esa
      // pantalla -- mismo criterio que salir de /login tras loguearse.
      if (user != null &&
          (state.matchedLocation == AppRoutes.login ||
              state.matchedLocation == AppRoutes.registro ||
              state.matchedLocation == AppRoutes.completarCuenta)) {
        return AppRoutes.admin;
      }

      // Perfil obligatorio: cualquier rol con el perfil incompleto (los 5
      // campos de Fase A2 -- documento, teléfono, institución, vinculación,
      // dependencia) queda atrapado en /perfil hasta completarlo, sin
      // importar a qué ruta intente navegar. `MiPerfilScreen` tiene su
      // propio botón de "Cerrar sesión" para quien no quiera completarlo
      // ahora (ver mi_perfil_screen.dart) -- la única salida además de
      // llenarlo.
      if (user != null && !user.perfilCompleto && state.matchedLocation != AppRoutes.perfil) {
        return AppRoutes.perfil;
      }

      final destinosDeLaRuta = kNavDestinations.where((d) => d.path == state.matchedLocation);
      final destino = destinosDeLaRuta.isEmpty ? null : destinosDeLaRuta.first;
      if (destino != null && destino.rolesPermitidos != null && !destino.visiblePara(user)) {
        return AppRoutes.laboratorios;
      }
      return null;
    },
    routes: [
      GoRoute(path: AppRoutes.login, builder: (context, state) => const LoginScreen()),
      GoRoute(path: AppRoutes.registro, builder: (context, state) => const RegistroScreen()),
      GoRoute(path: AppRoutes.completarCuenta, builder: (context, state) => const CompletarCuentaScreen()),
      GoRoute(path: AppRoutes.terminos, builder: (context, state) => const TerminosScreen()),
      ShellRoute(
        builder: (context, state, child) => AppShell(currentPath: state.matchedLocation, child: child),
        routes: [
          GoRoute(
            path: AppRoutes.laboratorios,
            pageBuilder: (context, state) => _fadeThroughPage(state, const LaboratoriosListScreen()),
          ),
          GoRoute(
            path: AppRoutes.laboratorioDetalleTemplate,
            pageBuilder: (context, state) {
              final id = int.parse(state.pathParameters['id']!);
              return _sharedAxisPage(state, LaboratorioDetalleScreen(laboratorioId: id));
            },
          ),
          // Con guard de rol vía kNavDestinations (ver comentario de
          // `redirect` arriba): solo gestor.
          GoRoute(
            path: AppRoutes.adminConfiguracion,
            pageBuilder: (context, state) => _sharedAxisPage(state, const ConfiguracionLaboratorioScreen()),
          ),
          GoRoute(
            path: AppRoutes.misReservas,
            pageBuilder: (context, state) => _fadeThroughPage(state, const MisReservasScreen()),
          ),
          GoRoute(
            path: AppRoutes.adminReservas,
            pageBuilder: (context, state) => _fadeThroughPage(state, const GestionReservasScreen()),
          ),
          GoRoute(
            path: AppRoutes.adminLaboratorios,
            pageBuilder: (context, state) => _fadeThroughPage(state, const GestionLaboratoriosScreen()),
          ),
          GoRoute(
            path: AppRoutes.adminRecursos,
            pageBuilder: (context, state) => _fadeThroughPage(state, const GestionRecursosScreen()),
          ),
          GoRoute(
            path: AppRoutes.adminEspacios,
            pageBuilder: (context, state) => _fadeThroughPage(state, const GestionEspaciosScreen()),
          ),
          GoRoute(
            path: AppRoutes.adminTiposReserva,
            pageBuilder: (context, state) => _fadeThroughPage(state, const GestionTiposReservaScreen()),
          ),
          GoRoute(
            path: AppRoutes.usuarios,
            pageBuilder: (context, state) => _fadeThroughPage(state, const GestionUsuariosScreen()),
          ),
          GoRoute(path: AppRoutes.admin, pageBuilder: (context, state) => _fadeThroughPage(state, const DashboardScreen())),
          GoRoute(
            path: AppRoutes.adminControlCambios,
            pageBuilder: (context, state) => _fadeThroughPage(state, const AuditoriaScreen()),
          ),
          GoRoute(
            path: AppRoutes.perfil,
            pageBuilder: (context, state) => _sharedAxisPage(
              state,
              Center(
                child: SingleChildScrollView(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 600),
                      child: const MiPerfilScreen(),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    ],
  );
});
