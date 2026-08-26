// Supabase Auth hybrid (institucional sin recursos extra).
//
// Con SUPABASE_ENABLED=false (default) todo sigue con JWT propio
// (SECRET_KEY). Para Cloud free tier (recomendado, sin infra extra) solo
// crear proyecto en cloud.supabase.com y pasar estas vars via
// --dart-define o env/*.json (mismo patrón que BASE_URL).
//
// Ver backend/app/config.py (SUPABASE_ENABLED), backend/app/deps.py
// (_decode_token hybrid) y backend/app/api/auth.py (POST /auth/supabase/sesion).
abstract final class SupabaseConfig {
  static const enabled = bool.fromEnvironment('SUPABASE_ENABLED', defaultValue: false);
  static const url = String.fromEnvironment('SUPABASE_URL', defaultValue: '');
  static const anonKey = String.fromEnvironment('SUPABASE_ANON_KEY', defaultValue: '');

  static bool get isConfigured => enabled && url.isNotEmpty && anonKey.isNotEmpty;
}
