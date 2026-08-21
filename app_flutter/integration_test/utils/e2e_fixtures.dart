import 'package:dio/dio.dart';
import 'package:dio_cookie_manager/dio_cookie_manager.dart';
import 'package:cookie_jar/cookie_jar.dart';

/// Fixtures de datos para las pruebas E2E, vía llamadas HTTP directas al
/// backend — NO comparten sesión con la app que conduce `WidgetTester`.
/// Esa app usa la cookie del navegador real que `flutter drive` está
/// controlando; esta jar es propia y efímera, solo para dejar el backend
/// en un estado conocido antes de que la UI entre en juego (mismo patrón
/// que "arrange" en cualquier suite E2E: preparar datos por API, probar
/// comportamiento por UI).
///
/// Apunta siempre a `reservas_test` — nunca a la base de desarrollo o
/// producción (regla dura del `CLAUDE.md` raíz). El backend detrás de
/// [backendUrl] debe estar corriendo contra esa base; esto no lo levanta,
/// solo asume que ya está arriba (ver "Cómo correr el E2E" en
/// `app_flutter/CLAUDE.md`).
const backendUrl = String.fromEnvironment('E2E_BACKEND_URL', defaultValue: 'http://127.0.0.1:8000');

/// Admin "de arranque" para poder crear el resto de fixtures por API. En
/// local se asume el mismo usuario que ya se usa en el resto del proyecto
/// para verificación manual (`admin_flutter`, ver `app_flutter/CLAUDE.md`);
/// en otro entorno (CI, por ejemplo) se sobreescribe con
/// `--dart-define=E2E_ADMIN_USERNAME=...` apuntando al admin que ese
/// entorno haya sembrado con `INITIAL_ADMIN_*`.
const _adminUsername = String.fromEnvironment('E2E_ADMIN_USERNAME', defaultValue: 'admin_flutter');
const _adminPassword = String.fromEnvironment('E2E_ADMIN_PASSWORD', defaultValue: 'ClaveFase0Temp123');

const usuarioE2eUsername = 'usuario_e2e';
const usuarioE2ePassword = 'ClaveUsuario123';
const gestorE2eUsername = 'gestor_flutter';
const gestorE2ePassword = 'ClaveGestor123';
const espacioE2eId = 1;
const recursoE2eNombre = 'Proyector E2E';

Dio _dioConCookies() {
  final dio = Dio(BaseOptions(baseUrl: backendUrl, validateStatus: (_) => true));
  dio.interceptors.add(CookieManager(CookieJar()));
  return dio;
}

/// Idempotente: crea o ajusta lo que falte, nunca falla porque algo "ya
/// existe". Pensado para correr una vez por archivo de prueba
/// (`setUpAll`) — cada `integration_test/*.dart` es un proceso de
/// `flutter drive` separado, así que no hay forma de compartir estado en
/// memoria entre archivos.
Future<void> asegurarFixturesE2e() async {
  final admin = _dioConCookies();
  final loginAdmin = await admin.post<dynamic>(
    '/auth/login',
    data: {'username': _adminUsername, 'password': _adminPassword},
  );
  if (loginAdmin.statusCode != 200) {
    throw StateError(
      'No se pudo iniciar sesión como admin de fixtures ("$_adminUsername") en $backendUrl '
      '(status ${loginAdmin.statusCode}). ¿Está el backend corriendo contra reservas_test '
      'con ese usuario ya sembrado (INITIAL_ADMIN_*)? Ver "Cómo correr el E2E" en '
      'app_flutter/CLAUDE.md.',
    );
  }

  await _asegurarUsuario(
    admin,
    username: gestorE2eUsername,
    email: '$gestorE2eUsername@example.com',
    password: gestorE2ePassword,
    rol: 'gestor',
    espacioId: espacioE2eId,
  );
  await _asegurarUsuario(
    admin,
    username: usuarioE2eUsername,
    email: '$usuarioE2eUsername@example.com',
    password: usuarioE2ePassword,
    rol: 'usuario',
  );

  final gestor = _dioConCookies();
  await gestor.post<dynamic>(
    '/auth/login',
    data: {'username': gestorE2eUsername, 'password': gestorE2ePassword},
  );

  // Antelación 0 en el espacio de pruebas: sin esto, "hoy" casi nunca
  // tiene franjas reservables (el espacio real pide 24h) y el flujo de
  // reserva tendría que manejar el selector de fecha de Material —
  // bastante más frágil de automatizar de forma determinista que asumir
  // esta config conocida. `aprobacion_automatica` se deja en `false` a
  // propósito: el flujo de reserva prueba justamente la transición
  // esperando -> aprobada -> cancelada.
  final config = await gestor.get<dynamic>('/espacios/gestion/configuracion');
  if (config.statusCode == 200 &&
      (config.data['horas_antelacion'] != 0 || config.data['aprobacion_automatica'] != false)) {
    await gestor.put<dynamic>('/espacios/gestion/configuracion', data: {
      'horario_atencion': config.data['horario_atencion'],
      'horas_antelacion': 0,
      'aprobacion_automatica': false,
    });
  }

  await _asegurarRecurso(gestor);
}

Future<void> _asegurarUsuario(
  Dio admin, {
  required String username,
  required String email,
  required String password,
  required String rol,
  int? espacioId,
}) async {
  final existentes = await admin.get<List<dynamic>>('/usuarios');
  final yaExiste = (existentes.data ?? const []).any((u) => (u as Map)['username'] == username);
  if (yaExiste) return;
  final resp = await admin.post<dynamic>('/usuarios', data: {
    'username': username,
    'email': email,
    'password': password,
    'rol': rol,
    // `?'espacio_id': espacioId` (la forma que sugiere el linter) no
    // compila en este SDK (`invalid_null_aware_operator`) — el `if`
    // explícito es más verboso pero es el que sí funciona.
    // ignore: use_null_aware_elements
    if (espacioId != null) 'espacio_id': espacioId,
  });
  if (resp.statusCode != 201) {
    throw StateError('No se pudo crear el usuario de fixtures "$username" (${resp.statusCode}): ${resp.data}');
  }
}

Future<void> _asegurarRecurso(Dio gestor) async {
  final existentes = await gestor.get<List<dynamic>>(
    '/recursos',
    queryParameters: {'espacio_id': espacioE2eId},
  );
  final yaExiste = (existentes.data ?? const []).any((r) => (r as Map)['nombre'] == recursoE2eNombre);
  if (yaExiste) return;
  final resp = await gestor.post<dynamic>('/recursos', data: {
    'nombre': recursoE2eNombre,
    'tipo_recurso_id': 1,
    'capacidad': 1,
    'estado': 'activo',
    'espacio_id': espacioE2eId,
    'es_prestacion_servicio': false,
  });
  if (resp.statusCode != 201) {
    throw StateError('No se pudo crear el recurso de fixtures "$recursoE2eNombre" (${resp.statusCode}): ${resp.data}');
  }
}
