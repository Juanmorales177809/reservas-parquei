import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../auth/domain/auth_user.dart';
import '../data/usuarios_repository.dart';

part 'usuarios_providers.g.dart';

@riverpod
Future<List<AuthUser>> usuariosList(Ref ref) {
  return ref.read(usuariosRepositoryProvider).listar();
}

/// Personal institucional (admin/gestor) -- tabla separada de `usuarios`
/// desde 2026-08-28, ver `backend/CLAUDE.md` y
/// `usuarios_repository.dart::listarPersonal`.
@riverpod
Future<List<AuthUser>> personalList(Ref ref) {
  return ref.read(usuariosRepositoryProvider).listarPersonal();
}
