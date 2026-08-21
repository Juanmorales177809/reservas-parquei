/// Escala de espaciado única — reemplaza los números mágicos (`SizedBox(height: 8)`,
/// `EdgeInsets.all(16)`, ...) repartidos por las pantallas, para que el
/// ritmo visual sea consistente en toda la app.
///
/// Los seis primeros valores (4-32) vienen de las Fases 0-5 y NO se
/// renombraron en el pase de Fase 6 (los usan cientos de líneas). Los tres
/// últimos son nuevos: la escala se cortaba justo donde empieza el
/// escritorio, así que en Web ancho las pantallas no tenían forma de
/// expresar "aire de sección" y todo quedaba con la densidad de móvil.
abstract final class AppSpacing {
  /// Separación icono–etiqueta, padding vertical de badge.
  static const xs = 4.0;

  /// Gap entre chips, padding horizontal de badge, gap de celdas de grilla densa.
  static const sm = 8.0;

  /// Gap de icono en fila, padding interno de campo compacto.
  static const md = 12.0;

  /// Padding interno de tarjeta en móvil, gap de grilla en móvil.
  static const lg = 16.0;

  /// Padding interno de tarjeta en escritorio, gap de grilla, margen lateral.
  static const xl = 24.0;

  /// Separación entre bloques dentro de una pantalla.
  static const xxl = 32.0;

  /// Margen lateral de pantalla en ≥ 840dp.
  static const xxxl = 40.0;

  /// Separación entre secciones mayores (bloques del dashboard).
  static const huge = 48.0;

  /// Aire superior de pantallas de una sola tarjeta (Login), padding de
  /// estado vacío.
  static const giant = 64.0;

  /// Ancho máximo del contenido, centrado. Por encima de esto el fondo
  /// sigue expandiéndose pero el contenido no: sin este límite, Web en un
  /// monitor de 27" no se ve como una app de escritorio sino como una app
  /// móvil estirada.
  static const anchoContenidoMaximo = 1280.0;
}

/// Radios de borde.
///
/// **Regla concéntrica**: el radio de un hijo = radio del padre − su
/// padding, con piso en [xs]. Un botón de radio 16 dentro de una tarjeta de
/// radio 20 con padding 16 produce una relación óptica errónea: el hijo se
/// ve más redondo de lo que corresponde y el padre menos. Con padding 16
/// dentro de una tarjeta de 20, los elementos internos van a 8, no a 16.
abstract final class AppRadius {
  /// Celda de heatmap, celda del editor de horario. En una grilla densa un
  /// radio mayor come área útil.
  static const xs = 4.0;

  /// Elemento interno de tarjeta: chip, slot de disponibilidad, mini-tarjeta.
  /// (20 de tarjeta − 12 de padding ≈ 8.)
  static const sm = 8.0;

  /// Contenedor de icono, banner interno.
  static const md = 12.0;

  /// Botón, campo, dropdown. Baja de 16 a 14 para que el escalón contra el
  /// radio de tarjeta (20) sea perceptible: 20 vs 16 se leen como el mismo
  /// radio.
  static const control = 14.0;

  /// Contenedor mediano (banner, tarjeta anidada).
  static const lg = 16.0;

  /// Tarjeta. Es la firma de forma del sistema.
  static const xl = 20.0;

  /// Bottom sheet, diálogo, panel lateral. Nivel superior de la jerarquía
  /// de forma.
  static const sheet = 28.0;

  /// Cápsula: badge, tag, avatar. Es lo que distingue un badge de un botón
  /// pequeño.
  static const pill = 999.0;
}
