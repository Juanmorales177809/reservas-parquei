import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../auth/domain/auth_user.dart';
import '../data/usuarios_repository.dart';

part 'usuarios_providers.g.dart';

@riverpod
Future<List<AuthUser>> usuariosList(Ref ref) {
  return ref.read(usuariosRepositoryProvider).listar();
}
