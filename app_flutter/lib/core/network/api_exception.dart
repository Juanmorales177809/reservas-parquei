import 'package:dio/dio.dart';

/// Excepción única para errores de la API, con el mensaje del backend ya
/// aplanado a texto — equivalente a `parseApiError` de
/// `frontend/src/services/api.ts`. Los repositorios la relanzan tal cual
/// para que la UI la muestre literal (mismo criterio que el frontend
/// actual: el mensaje de error del backend se muestra sin reescribirlo).
class ApiException implements Exception {
  const ApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}

/// Replica `parseApiError`: FastAPI/Pydantic devuelven `{detail: string}`
/// o `{detail: [{msg, ...}, ...]}` en los errores.
String parseApiErrorMessage(dynamic responseData, {int? statusCode}) {
  if (responseData is Map) {
    final detail = responseData['detail'];
    if (detail is String) return detail;
    if (detail is List) {
      return detail
          .map((item) => item is Map && item['msg'] != null ? item['msg'].toString() : item.toString())
          .join(', ');
    }
    if (detail != null) return detail.toString();
  }
  if (statusCode != null) return 'Error HTTP $statusCode';
  return 'Error de red inesperado.';
}

/// `dio.get/post/...` siempre lanza `DioException`, nunca el `ApiException`
/// directamente — `AuthInterceptor` la deja en `DioException.error`, no en
/// el objeto lanzado. Un `catch (e) { e is ApiException }` a secas SIEMPRE
/// da `false` y esconde el mensaje real del backend detrás de un fallback
/// genérico (bug real encontrado en la Fase 2: `PUT /reservas/{id}/cancelar`
/// mostraba "No se pudo cancelar la reserva." en vez de la razón real del
/// backend). Usar siempre estos dos helpers en los `catch`, nunca
/// `e is ApiException` sobre el error crudo de un repositorio.
ApiException? apiExceptionOf(Object error) {
  if (error is ApiException) return error;
  if (error is DioException && error.error is ApiException) return error.error as ApiException;
  return null;
}

String apiErrorMessage(Object error, {required String fallback}) => apiExceptionOf(error)?.message ?? fallback;

int? apiErrorStatusCode(Object error) => apiExceptionOf(error)?.statusCode;
