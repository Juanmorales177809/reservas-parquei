import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/dio_client.dart';
import '../../auth/domain/auth_user.dart';

/// Espejo de `frontend/src/services/usuarios.ts` — solo admin (`require_admin`).
class UsuariosRepository {
  UsuariosRepository(this._dio);

  final Dio _dio;

  Future<List<AuthUser>> listar() async {
    final response = await _dio.get<List<dynamic>>('/usuarios');
    return response.data!.map((json) => AuthUser.fromJson(json as Map<String, dynamic>)).toList();
  }

  Future<AuthUser> crear({
    required String username,
    required String email,
    required String password,
    required String rol,
    int? espacioId,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/usuarios',
      data: {
        'username': username,
        'email': email,
        'password': password,
        'rol': rol,
        'espacio_id': ?espacioId,
      },
    );
    return AuthUser.fromJson(response.data!);
  }

  Future<AuthUser> actualizar(
    int usuarioId, {
    String? username,
    String? email,
    String? password,
    String? rol,
    int? espacioId,
  }) async {
    final data = <String, dynamic>{};
    if (username != null) data['username'] = username;
    if (email != null) data['email'] = email;
    if (password != null && password.isNotEmpty) data['password'] = password;
    if (rol != null) data['rol'] = rol;
    if (espacioId != null) data['espacio_id'] = espacioId;
    // Si rol es gestor y no se envía espacio_id, el backend lo exige; el caller debe asegurar.
    // Si se quiere limpiar espacio_id para no-gestor, no enviar nada — el backend lo ignora.
    final response = await _dio.put<Map<String, dynamic>>('/usuarios/$usuarioId', data: data);
    return AuthUser.fromJson(response.data!);
  }

  Future<void> eliminar(int usuarioId) async {
    await _dio.delete<void>('/usuarios/$usuarioId');
  }
}

final usuariosRepositoryProvider = Provider<UsuariosRepository>((ref) {
  return UsuariosRepository(ref.watch(dioProvider));
});
