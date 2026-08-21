import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../features/auth/domain/auth_user.dart';
import 'app_routes.dart';

/// Fuente única de verdad de los destinos de navegación — reemplaza la
/// lógica hoy repartida en `frontend/src/components/Navbar.tsx`
/// (`homeHref`/`resourcesHref`/`reservationsHref` calculados inline).
/// Tanto el shell de bottom nav (móvil) como el de top nav (escritorio)
/// leen de la misma lista.
class NavDestinationSpec {
  const NavDestinationSpec({
    required this.id,
    required this.label,
    required this.icon,
    required this.path,
    required this.primario,
    this.rolesPermitidos,
    this.requiereSesion = true,
    this.pushed = false,
  });

  final String id;
  final String label;
  final IconData icon;
  final String path;

  /// `true` = la ruta vive fuera del `ShellRoute` (`AppBar` propia, sin
  /// bottom/top nav — ver "Rutas empujadas vs. destinos del shell" en
  /// `app_flutter/CLAUDE.md`), así que hay que navegar con `context.push`
  /// (agrega a la pila, habilita el botón "atrás" automático de
  /// go_router) en vez de `context.go` (que reemplazaría la ubicación y
  /// dejaría sin forma de volver, al desmontar el shell entero).
  final bool pushed;

  /// Roles que pueden ver este destino cuando `requiereSesion` es `true`.
  /// `null` = cualquier rol autenticado (sin restricción). Se ignora si
  /// `requiereSesion` es `false`.
  final Set<RolUsuario>? rolesPermitidos;

  /// `true` = cabe entre los 4-5 slots de la bottom nav en móvil.
  /// `false` = solo visible en el top nav de escritorio o dentro de la
  /// pantalla "Más"/Perfil en móvil.
  final bool primario;

  /// `false` = destino público (p. ej. "Espacios"): visible para anónimos
  /// y para cualquier rol, sin mirar `rolesPermitidos`.
  final bool requiereSesion;

  bool visiblePara(AuthUser? user) {
    if (!requiereSesion) return true;
    if (user == null) return false;
    if (rolesPermitidos == null) return true;
    return rolesPermitidos!.contains(user.rol);
  }
}

/// Fase 4: "Reservas" apunta a un destino distinto según el rol — mismo
/// slot de navegación, dos `NavDestinationSpec` con `rolesPermitidos`
/// disjuntos (igual criterio que `reservationsHref` en
/// `frontend/src/components/Navbar.tsx`: `usuario` ve las suyas,
/// gestor/admin ven el panel de gestión). También sirve como fuente del
/// guard por rol del router (`app_router.dart`): un destino con
/// `rolesPermitidos` es la única forma de restringir una ruta a ciertos
/// roles, no hay una lista aparte que pueda desincronizarse.
const kNavDestinations = <NavDestinationSpec>[
  NavDestinationSpec(
    id: 'espacios',
    label: 'Espacios',
    icon: LucideIcons.building2,
    path: AppRoutes.espacios,
    primario: true,
    requiereSesion: false,
  ),
  NavDestinationSpec(
    id: 'inicio',
    label: 'Inicio',
    icon: LucideIcons.house,
    path: AppRoutes.inicio,
    primario: true,
  ),
  NavDestinationSpec(
    id: 'mis-reservas',
    label: 'Reservas',
    icon: LucideIcons.calendarDays,
    path: AppRoutes.misReservas,
    primario: true,
    rolesPermitidos: {RolUsuario.usuario},
  ),
  NavDestinationSpec(
    id: 'gestion-reservas',
    label: 'Reservas',
    icon: LucideIcons.calendarDays,
    path: AppRoutes.adminReservas,
    primario: true,
    rolesPermitidos: {RolUsuario.gestor, RolUsuario.admin},
  ),
  NavDestinationSpec(
    id: 'gestion-recursos',
    label: 'Recursos',
    icon: LucideIcons.package,
    path: AppRoutes.adminRecursos,
    primario: false,
    rolesPermitidos: {RolUsuario.gestor, RolUsuario.admin},
  ),
  NavDestinationSpec(
    id: 'gestion-zonas',
    label: 'Zonas',
    icon: LucideIcons.mapPinned,
    path: AppRoutes.adminZonas,
    primario: false,
    rolesPermitidos: {RolUsuario.gestor, RolUsuario.admin},
  ),
  NavDestinationSpec(
    id: 'gestion-ensayos',
    label: 'Ensayos',
    icon: LucideIcons.flaskConical,
    path: AppRoutes.adminEnsayos,
    primario: false,
    rolesPermitidos: {RolUsuario.gestor, RolUsuario.admin},
  ),
  NavDestinationSpec(
    id: 'configuracion-espacio',
    label: 'Configuración',
    icon: LucideIcons.settings,
    path: AppRoutes.adminConfiguracion,
    primario: false,
    rolesPermitidos: {RolUsuario.gestor},
    pushed: true,
  ),
  NavDestinationSpec(
    id: 'gestion-usuarios',
    label: 'Usuarios',
    icon: LucideIcons.users,
    path: AppRoutes.usuarios,
    primario: false,
    rolesPermitidos: {RolUsuario.admin},
  ),
  NavDestinationSpec(
    id: 'dashboard',
    label: 'Dashboard',
    icon: LucideIcons.layoutDashboard,
    path: AppRoutes.admin,
    primario: true,
    rolesPermitidos: {RolUsuario.gestor, RolUsuario.admin},
  ),
  NavDestinationSpec(
    id: 'auditoria',
    label: 'Auditoría',
    icon: LucideIcons.history,
    path: AppRoutes.adminControlCambios,
    primario: false,
    rolesPermitidos: {RolUsuario.admin},
  ),
];

List<NavDestinationSpec> visibleDestinations(AuthUser? user, {required bool primarioOnly}) {
  return kNavDestinations
      .where((d) => d.visiblePara(user))
      .where((d) => !primarioOnly || d.primario)
      .toList(growable: false);
}
