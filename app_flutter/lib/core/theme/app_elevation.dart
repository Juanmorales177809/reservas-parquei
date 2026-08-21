import 'package:flutter/material.dart';

/// Cinco niveles discretos de profundidad.
///
/// Antes había uno solo (`Card(elevation: 3)`) sirviendo a la vez para
/// tarjeta en reposo, tarjeta en hover, bottom sheet, diálogo y panel de
/// notificaciones. Un sheet que flota igual que la tarjeta que lo lanzó
/// rompe la lectura de capas, y en escritorio el hover deja de informar.
///
/// Se usan `BoxShadow` explícitas en vez de `elevation:` de Material
/// porque `elevation` no permite controlar el desenfoque ni el offset por
/// separado — y porque su `surfaceTint` automático tiñe las tarjetas de
/// azul (ver `surfaceTintColor: transparent` en `app_theme.dart`).
///
/// La sombra es slate neutro (`AppColors.sombra`), no el primario: una
/// sombra azul al 10% sobre fondo casi blanco se percibe como un halo de
/// color, no como profundidad.
abstract final class AppElevation {
  /// Nivel 0 — plano. Sin sombra; la separación la da el borde.
  /// Tarjeta dentro de otra tarjeta, fila de lista, celda, chip.
  static const List<BoxShadow> plano = [];

  /// Nivel 1 — reposo. Tarjeta, campo, chip elevado.
  static const List<BoxShadow> reposo = [
    BoxShadow(
      color: Color(0x0F0F172A), // ~6%
      blurRadius: 2,
      offset: Offset(0, 1),
    ),
  ];

  /// Nivel 2 — hover. Tarjeta bajo el puntero, dropdown abierto.
  static const List<BoxShadow> hover = [
    BoxShadow(
      color: Color(0x1A0F172A), // ~10%
      blurRadius: 12,
      offset: Offset(0, 4),
    ),
  ];

  /// Nivel 3 — flotante. Bottom sheet, panel de notificaciones, menú.
  static const List<BoxShadow> flotante = [
    BoxShadow(
      color: Color(0x1F0F172A), // ~12%
      blurRadius: 24,
      offset: Offset(0, 10),
    ),
  ];

  /// Nivel 4 — modal. Diálogo de formulario, confirmación de borrado.
  static const List<BoxShadow> modal = [
    BoxShadow(
      color: Color(0x2E0F172A), // ~18%
      blurRadius: 48,
      offset: Offset(0, 20),
    ),
  ];

  /// Scrim detrás de una superficie de nivel 4.
  static const scrimModal = Color(0x6B0F172A); // ~42%
}
