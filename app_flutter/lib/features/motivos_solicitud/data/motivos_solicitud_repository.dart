import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/dio_client.dart';
import '../domain/motivo_solicitud.dart';

class MotivosSolicitudRepository {
  MotivosSolicitudRepository(this._dio);

  final Dio _dio;

  Future<List<MotivoSolicitud>> listar({required int laboratorioId}) async {
    final response = await _dio.get<List<dynamic>>(
      '/motivos-solicitud',
      queryParameters: {'laboratorio_id': laboratorioId},
    );
    return response.data!.map((json) => MotivoSolicitud.fromJson(json as Map<String, dynamic>)).toList();
  }
}

final motivosSolicitudRepositoryProvider = Provider<MotivosSolicitudRepository>((ref) {
  return MotivosSolicitudRepository(ref.watch(dioProvider));
});
