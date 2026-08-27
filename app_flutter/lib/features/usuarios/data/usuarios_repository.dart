import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/domain/enums.dart';
import '../../../core/network/dio_client.dart';
import '../../auth/domain/auth_user.dart';

/// Espejo de `frontend/src/services/usuarios.ts`. La mayoría de los
/// métodos son solo admin (`require_admin`) -- excepto
/// `actualizarMiPerfil` (`PUT /usuarios/me`), self-service para cualquier
/// rol autenticado (Fase A2).
class UsuariosRepository {
  UsuariosRepository(this._dio);

  final Dio _dio;

  Future<List<AuthUser>> listar() async {
    final response = await _dio.get<List<dynamic>>('/usuarios');
    return response.data!.map((json) => AuthUser.fromJson(json as Map<String, dynamic>)).toList();
  }

  /// Sin `password`: el backend invita a la persona por email vía la API de
  /// administración de Supabase (ver `AdminUsuarioCreate` y
  /// `app/services/supabase_admin.py` en el backend) — la contraseña la
  /// elige la propia persona desde el link de invitación, el admin nunca la
  /// ve ni la fija.
  Future<AuthUser> crear({
    required String username,
    required String email,
    required String rol,
    int? espacioId,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/usuarios',
      data: {
        'username': username,
        'email': email,
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
    String? rol,
    int? espacioId,
  }) async {
    final data = <String, dynamic>{};
    if (username != null) data['username'] = username;
    if (email != null) data['email'] = email;
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

  /// `PUT /usuarios/me` — self-service, cualquier usuario autenticado edita
  /// su propio perfil. A propósito NO acepta `rol`/`espacioId`/`username`/
  /// `email`: el backend (`PerfilUpdate`, `extra="forbid"`) los rechaza con
  /// 422 si llegaran -- ni siquiera existe la forma de mandarlos desde acá.
  Future<AuthUser> actualizarMiPerfil({
    String? documentoIdentificacion,
    String? telefono,
    String? institucion,
    VinculacionUsuario? vinculacion,
    String? dependencia,
  }) async {
    final vinculacionJson = vinculacion == null ? null : vinculacionUsuarioToJson(vinculacion);
    final data = <String, dynamic>{
      'documento_identificacion': ?documentoIdentificacion,
      'telefono': ?telefono,
      'institucion': ?institucion,
      'vinculacion': ?vinculacionJson,
      'dependencia': ?dependencia,
    };
    final response = await _dio.put<Map<String, dynamic>>('/usuarios/me', data: data);
    return AuthUser.fromJson(response.data!);
  }

  /// Genera un link de invitación fresco y lo encola por correo (cubre el
  /// correo original perdido en spam, o un link vencido). `link` siempre
  /// viene, aunque `correoEnviado` sea `false` (sin SMTP configurado
  /// todavía) — la pantalla se lo muestra al admin para que lo entregue a
  /// mano mientras tanto. Ver `POST /usuarios/{id}/reenviar-invitacion`.
  Future<ReenvioInvitacion> reenviarInvitacion(int usuarioId) async {
    final response = await _dio.post<Map<String, dynamic>>('/usuarios/$usuarioId/reenviar-invitacion');
    final data = response.data!;
    return ReenvioInvitacion(link: data['link'] as String, correoEnviado: data['correo_enviado'] as bool);
  }
}

class ReenvioInvitacion {
  const ReenvioInvitacion({required this.link, required this.correoEnviado});

  final String link;
  final bool correoEnviado;
}

final usuariosRepositoryProvider = Provider<UsuariosRepository>((ref) {
  return UsuariosRepository(ref.watch(dioProvider));
});
