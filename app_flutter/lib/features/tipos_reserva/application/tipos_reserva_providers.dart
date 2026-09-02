import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../auth/application/auth_provider.dart';
import '../../auth/domain/auth_user.dart';
import '../data/tipos_reserva_repository.dart';
import '../domain/tipo_reserva.dart';

part 'tipos_reserva_providers.g.dart';

/// Tipos de reserva de un laboratorio puntual -- usado por el dropdown
/// dinámico del formulario de reserva (`laboratorio_reserva_sheet.dart`,
/// `recurso_disponibilidad_sheet.dart`, Fase 7).
@riverpod
Future<List<TipoReserva>> tiposReserva(Ref ref, int laboratorioId) {
  return ref.read(tiposReservaRepositoryProvider).listar(laboratorioId: laboratorioId);
}

/// Tipos de reserva para la pantalla de gestión (`GestionTiposReservaScreen`)
/// -- mismo criterio de filtro cliente-side que `espaciosGestionProvider`:
/// un gestor solo ve/gestiona los de su propio laboratorio.
@riverpod
Future<List<TipoReserva>> tiposReservaGestion(Ref ref) {
  final usuario = ref.watch(authProvider).value;
  final laboratorioId = usuario?.rol == RolUsuario.gestor ? usuario?.laboratorio?.id : null;
  return ref.read(tiposReservaRepositoryProvider).listar(laboratorioId: laboratorioId);
}
