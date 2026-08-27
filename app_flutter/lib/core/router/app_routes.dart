/// Nombres de ruta centralizados — reemplaza los `href` hoy dispersos en
/// `frontend/src/components/Navbar.tsx`. Única fuente de verdad para rutas,
/// consumida por `app_router.dart` y `nav_destinations.dart`.
abstract final class AppRoutes {
  static const login = '/login';
  static const completarCuenta = '/completar-cuenta';
  static const terminos = '/terminos';
  // No hay `inicio`: tras autenticarse se aterriza en [admin], el
  // dashboard real. La antigua `/dashboard` servía una `InicioScreen`
  // placeholder y se eliminó el 2026-08-24.
  static const espacios = '/espacios';
  static const espacioDetalleTemplate = '/espacios/:id';
  static String espacioDetalle(int id) => '/espacios/$id';
  static const misReservas = '/reservas/mis-reservas';
  static const nuevaReserva = '/reservas/nueva';
  static const admin = '/admin';
  static const adminEspacios = '/admin/espacios';
  static const adminRecursos = '/admin/recursos';
  static const adminZonas = '/admin/zonas';
  static const adminEnsayos = '/admin/ensayos';
  static const adminReservas = '/admin/reservas';
  static const adminConfiguracion = '/admin/configuracion';
  static const adminControlCambios = '/admin/control-cambios';
  static const usuarios = '/usuarios';
  static const perfil = '/perfil';

  /// Templates de ruta accesibles sin sesión (ver `frontend/CLAUDE.md`,
  /// "Rutas públicas y protegidas"), comparados contra `state.fullPath` de
  /// go_router (el template registrado, no la URL interpolada — así
  /// `/espacios/:id` cubre cualquier id sin enumerarlos).
  static const publicas = {login, completarCuenta, terminos, espacios, espacioDetalleTemplate};
}
