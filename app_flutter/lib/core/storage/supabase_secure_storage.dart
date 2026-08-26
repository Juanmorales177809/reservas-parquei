// Almacenamiento seguro para el token Supabase intercambiado con el backend.
//
// No implementa `LocalStorage` de supabase_flutter por ahora: supabase_flutter
// por defecto usa SharedPreferences (ver plan rechazado
// ya-tenemos-el-ci-calm-octopus.md). Para open source institucional sin
// recursos, el MVP usa el storage por defecto de supabase_flutter y este
// helper guarda el token que se envía a `POST /auth/supabase/sesion` en
// `flutter_secure_storage` (Keychain/EncryptedSharedPreferences) como
// mitigación, sin tocar todavía el LocalStorage interno de supabase_flutter.
//
// Cuando haya recursos para hardening extra, cambiar
// `Supabase.initialize(localStorage: ...)` por una implementación de
// `LocalStorage` que delegue en este mismo `_storage`.
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SupabaseSecureStorage {
  SupabaseSecureStorage({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  final FlutterSecureStorage _storage;
  static const _key = 'supabase_session_raw';

  Future<void> guardarSesion(String raw) => _storage.write(key: _key, value: raw);
  Future<String?> leerSesion() => _storage.read(key: _key);
  Future<void> borrarSesion() => _storage.delete(key: _key);
}
