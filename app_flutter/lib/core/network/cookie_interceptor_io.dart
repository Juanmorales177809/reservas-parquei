import 'package:cookie_jar/cookie_jar.dart';
import 'package:dio/dio.dart';
import 'package:dio_cookie_manager/dio_cookie_manager.dart';
import 'package:path_provider/path_provider.dart';

/// Rama nativa (Android/iOS/Windows/macOS/Linux): la cookie `HttpOnly`
/// `access_token` que fija el backend se guarda en disco y se adjunta sola
/// en cada request — replica el comportamiento de la cookie de sesión de un
/// navegador, pero persistida entre reinicios de la app. El cliente nunca
/// lee ni decodifica el valor de la cookie (es opaco, igual que en un
/// navegador real).
Future<Interceptor?> createCookieInterceptor() async {
  final appDocDir = await getApplicationDocumentsDirectory();
  final cookieJar = PersistCookieJar(
    storage: FileStorage('${appDocDir.path}/.cookies/'),
    ignoreExpires: false,
  );
  return CookieManager(cookieJar);
}
