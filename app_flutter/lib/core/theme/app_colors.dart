import 'package:flutter/material.dart';

/// Paleta completa del sistema — reemplaza los `Color(0xFF...)` sueltos que
/// estaban repartidos por las pantallas.
///
/// Origen: revisión de diseño externa para la Fase 6. Dos hallazgos de
/// accesibilidad reales motivaron la reescritura (no fue un cambio de gusto):
///
/// 1. `#10B981` (el esmeralda que usábamos como texto de badge Y relleno de
///    botón) da **2.54:1** contra blanco — falla AA para texto (4.5:1) e
///    incluso el mínimo de 3:1 para componentes de interfaz.
/// 2. `#D97706` (ámbar de "pendiente") da **3.20:1** — falla AA como texto.
///
/// La corrección NO es "usar otro verde": es que un color de estado necesita
/// **un tono por función**. Ver [EstadoTokens]: relleno, texto-sobre-relleno,
/// tinte y texto-sobre-tinte son valores distintos y verificados, nunca
/// derivados con `withOpacity()` sobre un único tono base.
abstract final class AppColors {
  // ---------------------------------------------------------------------
  // Rampa azul (marca). Antes existía un solo tono (`#1E3A8A`), lo que
  // obligaba a inventar un `withOpacity()` distinto en cada archivo para
  // chips, filas seleccionadas y estados pressed.
  // ---------------------------------------------------------------------
  static const azul50 = Color(0xFFEFF6FF);
  static const azul100 = Color(0xFFDBEAFE);
  static const azul200 = Color(0xFFBFDBFE);
  static const azul300 = Color(0xFF93C5FD);
  static const azul400 = Color(0xFF60A5FA);
  static const azul500 = Color(0xFF3B82F6);
  static const azul600 = Color(0xFF2563EB);
  static const azul800 = Color(0xFF1E40AF);
  static const azul900 = Color(0xFF1E3A8A);

  /// Color de marca. Titulares, relleno de botón primario, logotipo.
  /// 8.65:1 contra blanco (AAA).
  static const marca = azul900;

  /// Azul de *acción semántica* (enlaces, "actualizó" en auditoría, foco).
  /// Separado de [marca] a propósito: `#1E3A8A` estaba haciendo seis
  /// trabajos a la vez (marca, botón, gradiente, acción, sombra, nav
  /// activa) y cuando un color significa todo deja de significar algo.
  static const accion = azul600;

  // ---------------------------------------------------------------------
  // Neutros (slate, no gris puro: acompaña la temperatura fría del azul).
  // ---------------------------------------------------------------------
  /// Fondo de pantalla. Sube desde `grey.shade50` (`#FAFAFA`), que daba
  /// **1.04:1** contra la tarjeta blanca — imperceptible en pantallas mate
  /// o con brillo bajo. `#F1F5F9` da 1.10:1 (2.4x más separación).
  static const fondo = Color(0xFFF1F5F9);

  /// Superficie de tarjeta.
  static const superficie = Color(0xFFFFFFFF);

  /// Superficie secundaria (chip de nivel 0, celda inactiva, relleno de
  /// campo) — un escalón entre [superficie] y [fondo].
  static const superficieSutil = Color(0xFFF8FAFC);

  /// Borde por defecto de tarjeta/campo. La tarjeta ahora lleva borde
  /// ADEMÁS de sombra: es lo que sostiene la lectura en Windows y Web,
  /// donde el render de sombras es más débil que en móvil.
  static const borde = Color(0xFFE2E8F0);

  /// Borde de mayor contraste: hover, divisor fuerte, handle de sheet.
  static const bordeFuerte = Color(0xFFCBD5E1);

  /// Solo decorativo o deshabilitado — 2.56:1, nunca texto legible.
  static const textoDeshabilitado = Color(0xFF94A3B8);

  /// Metadatos (marca temporal, ayuda de campo). 4.81:1, AA justo.
  static const textoTerciario = Color(0xFF64748B);

  /// Texto secundario. 7.58:1 (AAA).
  static const textoSecundario = Color(0xFF475569);

  /// Texto principal y titulares. 17.96:1 (AAA). Casi negro con
  /// temperatura fría — evita el tinte azulado que Material 3 aplica solo
  /// si se deja derivar `onSurface` del `seed`.
  static const texto = Color(0xFF0F172A);

  /// Base de todas las sombras. Slate neutro, NO el primario: una sombra
  /// azul sobre fondo casi blanco se lee como un halo de color, no como
  /// profundidad (ver `app_elevation.dart`).
  static const sombra = texto;
}

/// Los cuatro tonos que necesita un color de estado para ser usable sin
/// romper contraste. Ningún consumidor debe derivar un tono de otro.
@immutable
class EstadoTokens {
  const EstadoTokens({
    required this.relleno,
    required this.sobreRelleno,
    required this.tinte,
    required this.sobreTinte,
    required this.borde,
  });

  /// Fondo de un botón/chip sólido de este estado.
  final Color relleno;

  /// Texto/icono sobre [relleno]. Verificado ≥ 4.5:1 contra él.
  final Color sobreRelleno;

  /// Fondo suave (badge, banner, fila resaltada).
  final Color tinte;

  /// Texto/icono sobre [tinte]. Verificado ≥ 4.5:1 contra él.
  final Color sobreTinte;

  /// Borde o indicador de 1-2px. Verificado ≥ 3:1 contra blanco.
  final Color borde;
}

/// Los cinco estados semánticos de la app. El principio original se
/// mantiene intacto — el verde SOLO significa "disponible/activo/aprobado",
/// nunca decoración — lo que cambia es que ahora hay un tono por función.
abstract final class AppEstados {
  /// Aprobada, activo, slot libre. `#047857` con blanco: 5.55:1 (AA).
  /// `#065F46` sobre `#ECFDF5`: 7.17:1 (AAA).
  static const positivo = EstadoTokens(
    relleno: Color(0xFF047857),
    sobreRelleno: Colors.white,
    tinte: Color(0xFFECFDF5),
    sobreTinte: Color(0xFF065F46),
    borde: Color(0xFF059669),
  );

  /// Informativo, "actualizó" en auditoría, chip neutro-positivo.
  static const informativo = EstadoTokens(
    relleno: AppColors.azul600,
    sobreRelleno: Colors.white,
    tinte: AppColors.azul50,
    sobreTinte: AppColors.azul800,
    borde: AppColors.azul400,
  );

  /// Esperando aprobación. El relleno sube de `#D97706` (3.20:1, fallaba)
  /// a `#B45309` (4.98:1, AA).
  static const pendiente = EstadoTokens(
    relleno: Color(0xFFB45309),
    sobreRelleno: Colors.white,
    tinte: Color(0xFFFFFBEB),
    sobreTinte: Color(0xFF92400E),
    borde: Color(0xFFD97706),
  );

  /// Rechazada, eliminada, error.
  static const negativo = EstadoTokens(
    relleno: Color(0xFFDC2626),
    sobreRelleno: Colors.white,
    tinte: Color(0xFFFEF2F2),
    sobreTinte: Color(0xFF991B1B),
    borde: Color(0xFFEF4444),
  );

  /// Cancelada, inactivo, mantenimiento. Faltaba un estado neutro con
  /// forma propia: sin contenedor, "cancelada" se veía como un fallo de
  /// render en medio de badges de color.
  static const neutro = EstadoTokens(
    relleno: AppColors.textoTerciario,
    sobreRelleno: Colors.white,
    tinte: AppColors.fondo,
    sobreTinte: AppColors.textoSecundario,
    borde: AppColors.bordeFuerte,
  );
}

/// Rampa discreta del heatmap de ocupación. Cinco escalones en vez de un
/// gradiente continuo: el ojo no compara luminosidades continuas, pero sí
/// cuenta escalones.
const kHeatmapRampa = <Color>[
  AppColors.fondo,
  AppColors.azul100,
  AppColors.azul300,
  AppColors.azul500,
  AppColors.azul900,
];
