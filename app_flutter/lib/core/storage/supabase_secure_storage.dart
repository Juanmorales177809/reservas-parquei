// `LocalStorage` real para el SDK de Supabase (antes solo un wrapper
// dormido: supabase_flutter seguía usando SharedPreferences por defecto pese
// a que este archivo existía). Ahora se pasa a
// `Supabase.initialize(localStorage: SupabaseSecureStorage())` en main.dart,
// así la sesión de Supabase (el JWT que también viaja como cookie
// `access_token` hacia nuestro backend) queda en `flutter_secure_storage`
// (Keychain / EncryptedSharedPreferences) en vez de texto plano.
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class SupabaseSecureStorage extends LocalStorage {
  const SupabaseSecureStorage({FlutterSecureStorage? storage}) : _storage = storage ?? const FlutterSecureStorage();

  final FlutterSecureStorage _storage;
  static const _key = 'supabase_session_raw';

  @override
  Future<void> initialize() async {}

  @override
  Future<String?> accessToken() => _storage.read(key: _key);

  @override
  Future<bool> hasAccessToken() async => (await _storage.containsKey(key: _key));

  @override
  Future<void> persistSession(String persistSessionString) => _storage.write(key: _key, value: persistSessionString);

  @override
  Future<void> removePersistedSession() => _storage.delete(key: _key);
}
