import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/domain/enums.dart';
import '../../../core/network/dio_client.dart';
import '../../auth/domain/auth_user.dart';

/// Espejo de `frontend/src/services/usuarios.ts`. Desde la separación
/// `personal`/`usuarios` (2026-08-28, ver `backend/CLAUDE.md` --
/// "Autoregistro abierto" y el plan `dazzling-wobbling-zebra.md`),
/// `/usuarios` es exclusivamente rol `usuario` (sin `rol`/`laboratorio_id`,
/// que ya no aplican ahí); `/personal` es admin/gestor, con la misma
/// forma de respuesta (`AuthUser`/`UsuarioResponse` no cambió). La mayoría
/// de los métodos son solo admin (`require_admin`) -- excepto
/// `actualizarMiPerfil` (`PUT /usuarios/me`), self-service para cualquier
/// rol autenticado (Fase A2).
class UsuariosRepository {
  UsuariosRepository(this._dio);

  final Dio _dio;

  // --- /usuarios (rol usuario únicamente) ---------------------------------

  Future<List<AuthUser>> listar() async {
    final response = await _dio.get<List<dynamic>>('/usuarios');
    return response.data!.map((json) => AuthUser.fromJson(json as Map<String, dynamic>)).toList();
  }

  /// Sin `password`: el backend invita a la persona por email vía la API de
  /// administración de Supabase -- la contraseña la elige la propia
  /// persona desde el link de invitación, el admin nunca la ve ni la fija.
  Future<AuthUser> crear({required String username, required String email}) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/usuarios',
      data: {'username': username, 'email': email},
    );
    return AuthUser.fromJson(response.data!);
  }

  Future<AuthUser> actualizar(int usuarioId, {String? username, String? email}) async {
    final data = <String, dynamic>{};
    if (username != null) data['username'] = username;
    if (email != null) data['email'] = email;
    final response = await _dio.put<Map<String, dynamic>>('/usuarios/$usuarioId', data: data);
    return AuthUser.fromJson(response.data!);
  }

  Future<void> eliminar(int usuarioId) async {
    await _dio.delete<void>('/usuarios/$usuarioId');
  }

  /// `PUT /usuarios/me` — self-service, cualquier identidad autenticada
  /// (personal o usuario) edita su propio perfil. A propósito NO acepta
  /// `rol`/`laboratorioId`/`username`/`email`: el backend (`PerfilUpdate`,
  /// `extra="forbid"`) los rechaza con 422 si llegaran -- ni siquiera
  /// existe la forma de mandarlos desde acá.
  Future<AuthUser> actualizarMiPerfil({
    String? documentoIdentificacion,
    String? telefono,
    String? institucion,
    VinculacionUsuario? vinculacion,
    String? dependencia,
    bool? recibirCorreos,
  }) async {
    final vinculacionJson = vinculacion == null ? null : vinculacionUsuarioToJson(vinculacion);
    final data = <String, dynamic>{
      'documento_identificacion': ?documentoIdentificacion,
      'telefono': ?telefono,
      'institucion': ?institucion,
      'vinculacion': ?vinculacionJson,
      'dependencia': ?dependencia,
      'recibir_correos': ?recibirCorreos,
    };
    final response = await _dio.put<Map<String, dynamic>>('/usuarios/me', data: data);
    return AuthUser.fromJson(response.data!);
  }

  /// Genera un link de invitación fresco y lo encola por correo (cubre el
  /// correo original perdido en spam, o un link vencido) para una cuenta
  /// rol `usuario`. `link` siempre viene, aunque `correoEnviado` sea
  /// `false` -- la pantalla se lo muestra al admin para que lo entregue a
  /// mano mientras tanto.
  Future<ReenvioInvitacion> reenviarInvitacion(int usuarioId) async {
    final response = await _dio.post<Map<String, dynamic>>('/usuarios/$usuarioId/reenviar-invitacion');
    final data = response.data!;
    return ReenvioInvitacion(link: data['link'] as String, correoEnviado: data['correo_enviado'] as bool);
  }

  // --- /personal (admin/gestor) -------------------------------------------

  Future<List<AuthUser>> listarPersonal() async {
    final response = await _dio.get<List<dynamic>>('/personal');
    return response.data!.map((json) => AuthUser.fromJson(json as Map<String, dynamic>)).toList();
  }

  Future<AuthUser> crearPersonal({
    required String username,
    required String email,
    required String rol,
    int? laboratorioId,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/personal',
      data: {'username': username, 'email': email, 'rol': rol, 'laboratorio_id': ?laboratorioId},
    );
    return AuthUser.fromJson(response.data!);
  }

  /// `rol: 'usuario'` degrada la cuenta a `/usuarios` (mueve la fila entre
  /// tablas del lado del backend, ver `services/migrar_actor.py`) -- el id
  /// resultante puede cambiar, por eso este método siempre devuelve el
  /// `AuthUser` actualizado en vez de solo confirmar.
  Future<AuthUser> actualizarPersonal(
    int personalId, {
    String? username,
    String? email,
    String? rol,
    int? laboratorioId,
  }) async {
    final data = <String, dynamic>{};
    if (username != null) data['username'] = username;
    if (email != null) data['email'] = email;
    if (rol != null) data['rol'] = rol;
    if (laboratorioId != null) data['laboratorio_id'] = laboratorioId;
    final response = await _dio.put<Map<String, dynamic>>('/personal/$personalId', data: data);
    return AuthUser.fromJson(response.data!);
  }

  Future<void> eliminarPersonal(int personalId) async {
    await _dio.delete<void>('/personal/$personalId');
  }

  Future<ReenvioInvitacion> reenviarInvitacionPersonal(int personalId) async {
    final response = await _dio.post<Map<String, dynamic>>('/personal/$personalId/reenviar-invitacion');
    final data = response.data!;
    return ReenvioInvitacion(link: data['link'] as String, correoEnviado: data['correo_enviado'] as bool);
  }

  /// Asciende una cuenta `usuario` existente a `personal` (admin/gestor) --
  /// distinto de `crearPersonal`, que da de alta una identidad nueva desde
  /// cero. Ver `POST /personal/promover/{usuario_id}`.
  Future<AuthUser> promoverAPersonal(
    int usuarioId, {
    required String username,
    required String email,
    required String rol,
    int? laboratorioId,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/personal/promover/$usuarioId',
      data: {'username': username, 'email': email, 'rol': rol, 'laboratorio_id': ?laboratorioId},
    );
    return AuthUser.fromJson(response.data!);
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
