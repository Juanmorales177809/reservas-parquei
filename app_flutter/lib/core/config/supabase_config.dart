// Supabase Auth es el único mecanismo de autenticación (corte completo,
// reemplaza el login clásico username/password propio). Configuración vía
// --dart-define o env/*.json (mismo patrón que BASE_URL en app_config.dart).
//
// Ver backend/app/config.py (validate() exige estas mismas variables del
// lado backend), backend/app/deps.py (_decode_token) y
// backend/app/api/auth.py (POST /auth/supabase/sesion).
abstract final class SupabaseConfig {
  static const url = String.fromEnvironment('SUPABASE_URL', defaultValue: '');
  // Formato publishable (sb_publishable_...), preferido en Supabase Cloud.
  static const publishableKey = String.fromEnvironment('SUPABASE_PUBLISHABLE_KEY', defaultValue: '');
  // Legacy JWT anon (eyJ...), deprecado en supabase_flutter pero aún soportado.
  static const anonKey = String.fromEnvironment('SUPABASE_ANON_KEY', defaultValue: '');

  static String get effectiveKey => publishableKey.isNotEmpty ? publishableKey : anonKey;

  /// Usado solo para fallar rápido y con un mensaje claro en `main.dart` si
  /// faltó configurar el entorno — no hay ningún camino que siga
  /// funcionando sin esto, a diferencia del viejo flag hybrid.
  static bool get isConfigured => url.isNotEmpty && effectiveKey.isNotEmpty;
}
