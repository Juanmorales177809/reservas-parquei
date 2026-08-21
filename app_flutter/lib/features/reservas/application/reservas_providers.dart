import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../data/reservas_repository.dart';
import '../domain/reserva.dart';

part 'reservas_providers.g.dart';

@riverpod
Future<List<Reserva>> misReservas(Ref ref) {
  return ref.read(reservasRepositoryProvider).misReservas();
}

/// `GET /reservas` — gestión, gestor/admin (ver `GestionReservasScreen`).
@riverpod
Future<List<Reserva>> reservasGestion(Ref ref) {
  return ref.read(reservasRepositoryProvider).listarGestion();
}
