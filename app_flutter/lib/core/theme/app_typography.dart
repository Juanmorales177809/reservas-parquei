import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'app_colors.dart';

/// Escala tipográfica del sistema.
///
/// Antes había **tres niveles reales** (titular grueso, título de tarjeta,
/// cuerpo) para expresar hasta cinco niveles de información por pantalla
/// (sección, KPI, etiqueta de KPI, valor de fila, metadato). La
/// diferenciación terminaba resolviéndose con peso y color, y todo se
/// parecía. Esta escala tiene un rol único por nivel.
///
/// **Frontera estricta entre las dos fuentes**: "Plus Jakarta Sans" solo en
/// display/headline/title; "Inter" en todo lo demás. Si Jakarta aparece en
/// un metadato, la distinción entre ambas se disuelve y deja de valer la
/// pena cargar dos familias.
abstract final class AppText {
  /// Etiqueta de dato: encabezado de columna, etiqueta de KPI, nombre de
  /// campo, encabezado adhesivo de grupo. **Se escribe en mayúsculas por
  /// el llamador** (`'Total reservas'.toUpperCase()`), no hay `textTransform`
  /// en Flutter.
  ///
  /// Este nivel es el que separa "etiqueta de dato" de "dato" sin gastar
  /// laboratorio vertical — era exactamente el que faltaba. Vive también en el
  /// slot `labelSmall` del `TextTheme` para que los widgets de Material lo
  /// hereden solos.
  static TextStyle overline({Color color = AppColors.textoTerciario}) {
    return GoogleFonts.inter(
      fontSize: 11,
      height: 14 / 11,
      fontWeight: FontWeight.w700,
      letterSpacing: 0.9,
      color: color,
    );
  }

  /// Cifras tabulares (todas del mismo ancho).
  ///
  /// Sin esto, Inter usa cifras proporcionales: los dígitos cambian de
  /// ancho mientras un contador anima, así que el número "vibra" al subir,
  /// y las columnas de cifras de una tabla no alinean verticalmente.
  /// Usar en KPIs, contadores, capacidad, conteos y celdas de heatmap.
  static TextStyle numerico({
    required double fontSize,
    Color color = AppColors.texto,
    FontWeight fontWeight = FontWeight.w600,
    double? height,
  }) {
    return GoogleFonts.inter(
      fontSize: fontSize,
      height: height,
      fontWeight: fontWeight,
      color: color,
      fontFeatures: const [FontFeature.tabularFigures()],
    );
  }

  /// Ancho máximo de una línea de texto de lectura (~68 caracteres).
  /// En Web ancho, sin este límite, una descripción se estira a 160
  /// caracteres por línea y deja de ser legible.
  static const anchoLecturaMaximo = 640.0;

  static TextTheme theme() {
    // Jakarta: display / headline / title.
    TextStyle jakarta(double size, double lineHeight, FontWeight peso, double track) {
      return GoogleFonts.plusJakartaSans(
        fontSize: size,
        height: lineHeight / size,
        fontWeight: peso,
        letterSpacing: track,
        color: AppColors.texto,
      );
    }

    // Inter: body / label.
    TextStyle inter(double size, double lineHeight, FontWeight peso, double track, Color color) {
      return GoogleFonts.inter(
        fontSize: size,
        height: lineHeight / size,
        fontWeight: peso,
        letterSpacing: track,
        color: color,
      );
    }

    return TextTheme(
      // Título de Login y KPI protagonista del dashboard.
      displayLarge: jakarta(40, 44, FontWeight.w800, -1.2),
      displayMedium: jakarta(34, 40, FontWeight.w800, -1.0),
      displaySmall: jakarta(30, 36, FontWeight.w800, -0.9),

      // Título de pantalla: Large en escritorio, Medium en móvil.
      headlineLarge: jakarta(32, 38, FontWeight.w800, -0.8),
      headlineMedium: jakarta(26, 32, FontWeight.w700, -0.6),
      headlineSmall: jakarta(22, 28, FontWeight.w700, -0.4),

      // Título de tarjeta / encabezado de diálogo / sección interna.
      titleLarge: jakarta(20, 26, FontWeight.w700, -0.3),
      titleMedium: jakarta(16, 22, FontWeight.w700, -0.1),
      titleSmall: jakarta(14, 20, FontWeight.w700, 0),

      // Texto de lectura (descripciones, cuerpo de diálogo).
      bodyLarge: inter(16, 24, FontWeight.w400, 0, AppColors.texto),
      // Cuerpo por defecto de la interfaz.
      bodyMedium: inter(14, 21, FontWeight.w400, 0, AppColors.texto),
      // Metadatos, marca temporal, ayuda de campo.
      bodySmall: inter(12.5, 18, FontWeight.w500, 0.1, AppColors.textoTerciario),

      // Etiqueta de botón.
      labelLarge: inter(14, 20, FontWeight.w600, 0.1, AppColors.texto),
      // Etiqueta de navegación.
      labelMedium: inter(12, 16, FontWeight.w600, 0.2, AppColors.textoSecundario),
      // Slot natural de Material 3 para el overline.
      labelSmall: overline(),
    );
  }
}
