import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/core/domain/enums.dart';
import 'package:app_flutter/features/auth/application/auth_provider.dart';
import 'package:app_flutter/features/auth/domain/auth_user.dart';
import 'package:app_flutter/features/espacios/application/espacios_providers.dart';
import 'package:app_flutter/features/espacios/domain/espacio.dart';
import 'package:app_flutter/features/zonas/application/zonas_providers.dart';
import 'package:app_flutter/features/zonas/presentation/gestion_zonas_screen.dart';

/// Sesión falsa: `Auth` es un `@riverpod class`, así que se sobreescribe
/// extendiéndolo y devolviendo el usuario ya resuelto en `build()`.
class _AuthFake extends Auth {
  _AuthFake(this._usuario);

  final AuthUser? _usuario;

  @override
  Future<AuthUser?> build() async => _usuario;
}

Espacio _espacio(int id, String nombre) => Espacio(
      id: id,
      nombre: nombre,
      ubicacion: 'Bloque $id',
      capacidad: 50,
      estado: EstadoEntidad.activo,
      diasAtencion: const [0, 1, 2, 3, 4],
      horaApertura: '08:00:00',
      horaCierre: '18:00:00',
      horarioAtencion: const {'0': [8, 9, 10]},
      horasAntelacion: 0,
      modalidadReserva: ModalidadEspacio.zonas,
    );

AuthUser _usuario(RolUsuario rol, {EspacioResumen? espacio}) => AuthUser(
      id: 1,
      username: rol.name,
      email: '${rol.name}@example.com',
      rol: rol,
      espacio: espacio,
    );

Future<void> _abrirFormularioNuevaZona(WidgetTester tester, AuthUser usuario) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        authProvider.overrideWith(() => _AuthFake(usuario)),
        // Sin zonas: el formulario es lo único bajo prueba.
        zonasGestionProvider.overrideWith((ref) async => []),
        espaciosListProvider.overrideWith(
          (ref) async => [_espacio(1, 'Auditorio Principal'), _espacio(2, 'Laboratorio')],
        ),
      ],
      child: const MaterialApp(home: GestionZonasScreen()),
    ),
  );
  await tester.pumpAndSettle();

  await tester.tap(find.text('Nueva'));
  await tester.pumpAndSettle();
}

void main() {
  group('GestionZonasScreen — selector de espacio al crear una zona', () {
    testWidgets('un gestor NO ve el selector: se usa su espacio asignado', (tester) async {
      await _abrirFormularioNuevaZona(
        tester,
        _usuario(
          RolUsuario.gestor,
          espacio: const EspacioResumen(id: 1, nombre: 'Auditorio Principal', ubicacion: 'Bloque 1'),
        ),
      );

      expect(find.text('Nueva zona'), findsOneWidget);
      // El bug original: aquí aparecía un desplegable con TODOS los
      // espacios, preseleccionado en `espacios.first` — que para un gestor
      // suele ser uno ajeno, y el backend respondía 403 al guardar.
      expect(find.text('Espacio *'), findsNothing);
      expect(find.text('Laboratorio'), findsNothing);
    });

    testWidgets('un admin SÍ ve el selector con todos los espacios', (tester) async {
      await _abrirFormularioNuevaZona(tester, _usuario(RolUsuario.admin));

      expect(find.text('Nueva zona'), findsOneWidget);
      expect(find.text('Espacio *'), findsOneWidget);
    });
  });
}
