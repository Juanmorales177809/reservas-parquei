import 'package:flutter/material.dart';

import 'app_colors.dart';
import 'app_spacing.dart';
import 'app_typography.dart';

/// Alias retrocompatibles: varias pantallas importan `kAcademicBlue`/
/// `kEmerald` desde este archivo. La fuente de verdad ahora es
/// `app_colors.dart` (rampas completas + tokens de estado verificados
/// contra WCAG) — estos dos se conservan para no romper esos imports.
///
/// **En código nuevo usar `AppColors.marca` / `AppEstados.positivo`**, no
/// estos: `kEmerald` (`#10B981`) NO tiene contraste suficiente para texto
/// ni para relleno de botón (2.54:1 contra blanco), solo sirve como trazo
/// de gráfico o parada de gradiente.
const kAcademicBlue = AppColors.marca;
const kEmerald = Color(0xFF10B981);

/// Tema de la app.
///
/// Pase de Fase 6 (revisión de diseño externa): la paleta dejó de derivarse
/// de un único `seedColor` y pasa a tokens explícitos y verificados
/// (`app_colors.dart`), con escala tipográfica de 9 niveles
/// (`app_typography.dart`) y radios concéntricos (`app_spacing.dart`).
class AppTheme {
  AppTheme._();

  static ThemeData light() => _build(_lightScheme());

  /// **No hay tema oscuro diseñado todavía.** La identidad "tech-clean"
  /// académica se definió entera en claro (fondo `#F1F5F9`, tarjeta blanca,
  /// sombras slate) y un oscuro derivado automáticamente por
  /// `ColorScheme.fromSeed` invertiría esas superficies sin que nadie haya
  /// verificado el contraste de los tokens de estado sobre ellas.
  ///
  /// `app.dart` fija `ThemeMode.light` a propósito para no exponer un tema
  /// a medio hacer; esto queda como trabajo pendiente explícito de una
  /// fase futura, no como un olvido.
  static ThemeData dark() => light();

  /// `ColorScheme.fromSeed` deriva superficies levemente teñidas de azul y
  /// un `secondary`/`tertiary` violáceos por el algoritmo de Material 3.
  /// Se parte de él (para que los slots que no usamos tengan algo
  /// razonable) pero se sobrescriben todos los que la UI toca de verdad.
  static ColorScheme _lightScheme() {
    return ColorScheme.fromSeed(seedColor: AppColors.marca).copyWith(
      primary: AppColors.marca,
      onPrimary: Colors.white,
      primaryContainer: AppColors.azul50,
      onPrimaryContainer: AppColors.azul800,

      secondary: AppEstados.positivo.relleno,
      onSecondary: AppEstados.positivo.sobreRelleno,
      secondaryContainer: AppEstados.positivo.tinte,
      onSecondaryContainer: AppEstados.positivo.sobreTinte,

      tertiary: AppColors.accion,
      onTertiary: Colors.white,
      tertiaryContainer: AppColors.azul50,
      onTertiaryContainer: AppColors.azul800,

      error: AppEstados.negativo.relleno,
      onError: Colors.white,
      errorContainer: AppEstados.negativo.tinte,
      onErrorContainer: AppEstados.negativo.sobreTinte,

      surface: AppColors.fondo,
      onSurface: AppColors.texto,
      onSurfaceVariant: AppColors.textoSecundario,
      surfaceContainerLowest: AppColors.superficie,
      surfaceContainerLow: AppColors.superficie,
      surfaceContainer: AppColors.superficieSutil,
      surfaceContainerHigh: AppColors.superficieSutil,
      surfaceContainerHighest: AppColors.fondo,

      outline: AppColors.bordeFuerte,
      outlineVariant: AppColors.borde,
      shadow: AppColors.sombra,
    );
  }

  static ThemeData _build(ColorScheme scheme) {
    final base = ThemeData(useMaterial3: true, colorScheme: scheme);
    final textTheme = AppText.theme();

    return base.copyWith(
      textTheme: textTheme,
      scaffoldBackgroundColor: scheme.surface,
      // Material 3 tiñe automáticamente TODA superficie elevada con
      // `primary`. Sin anularlo, cada tarjeta, sheet y menú queda azulado
      // en vez de blanco.
      appBarTheme: AppBarTheme(
        backgroundColor: scheme.surface,
        surfaceTintColor: Colors.transparent,
        shadowColor: AppColors.sombra,
        elevation: 0,
        scrolledUnderElevation: 1,
        titleTextStyle: textTheme.headlineMedium,
        iconTheme: const IconThemeData(color: AppColors.textoSecundario, size: 20),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: AppColors.superficie,
        surfaceTintColor: Colors.transparent,
        // Contenedor tintado, no icono de color suelto: el contenedor es
        // lo que hace inequívoco dónde estás.
        indicatorColor: AppColors.azul50,
        indicatorShape: const StadiumBorder(),
        elevation: 0,
        height: 68,
        labelTextStyle: WidgetStateProperty.resolveWith(
          (states) => textTheme.labelMedium?.copyWith(
            fontWeight: states.contains(WidgetState.selected) ? FontWeight.w700 : FontWeight.w500,
            color: states.contains(WidgetState.selected) ? AppColors.marca : AppColors.textoTerciario,
          ),
        ),
        iconTheme: WidgetStateProperty.resolveWith(
          (states) => IconThemeData(
            size: 20,
            color: states.contains(WidgetState.selected) ? AppColors.marca : AppColors.textoTerciario,
          ),
        ),
      ),
      navigationRailTheme: NavigationRailThemeData(
        backgroundColor: AppColors.superficie,
        indicatorColor: AppColors.azul50,
        indicatorShape: const StadiumBorder(),
        selectedIconTheme: const IconThemeData(size: 20, color: AppColors.marca),
        unselectedIconTheme: const IconThemeData(size: 20, color: AppColors.textoTerciario),
        selectedLabelTextStyle: textTheme.labelMedium?.copyWith(
          fontWeight: FontWeight.w700,
          color: AppColors.marca,
        ),
        unselectedLabelTextStyle: textTheme.labelMedium,
      ),
      // Nivel 1 (reposo) de `app_elevation.dart`: sombra MUY suave, neutra
      // (no azul), MÁS un borde de 1px. El borde es lo que sostiene la
      // lectura en Windows y Web, donde el render de sombras es más débil
      // que en móvil — sin él la tarjeta blanca sobre fondo casi blanco
      // desaparece.
      cardTheme: CardThemeData(
        elevation: 1,
        shadowColor: AppColors.sombra,
        surfaceTintColor: Colors.transparent,
        color: AppColors.superficie,
        margin: EdgeInsets.zero,
        clipBehavior: Clip.antiAlias,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.xl),
          side: const BorderSide(color: AppColors.borde),
        ),
      ),
      chipTheme: base.chipTheme.copyWith(
        backgroundColor: AppColors.superficieSutil,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.pill),
          side: const BorderSide(color: AppColors.borde),
        ),
        side: BorderSide.none,
        labelStyle: textTheme.labelLarge,
        padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.xs),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xl, vertical: AppSpacing.lg),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.control)),
          textStyle: textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w700),
          elevation: 0,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg, vertical: AppSpacing.md),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.control)),
          side: const BorderSide(color: AppColors.bordeFuerte),
          foregroundColor: AppColors.texto,
          textStyle: textTheme.labelLarge,
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.control)),
          foregroundColor: AppColors.accion,
          textStyle: textTheme.labelLarge,
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.superficieSutil,
        contentPadding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg, vertical: AppSpacing.lg),
        hintStyle: textTheme.bodyMedium?.copyWith(color: AppColors.textoDeshabilitado),
        labelStyle: textTheme.bodyMedium?.copyWith(color: AppColors.textoTerciario),
        helperStyle: textTheme.bodySmall,
        errorStyle: textTheme.bodySmall?.copyWith(color: AppEstados.negativo.sobreTinte),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.control),
          borderSide: const BorderSide(color: AppColors.borde),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.control),
          borderSide: const BorderSide(color: AppColors.borde),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.control),
          borderSide: const BorderSide(color: AppColors.accion, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.control),
          borderSide: BorderSide(color: AppEstados.negativo.borde, width: 1.5),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.control),
          borderSide: BorderSide(color: AppEstados.negativo.relleno, width: 2),
        ),
      ),
      dividerTheme: const DividerThemeData(
        color: AppColors.borde,
        space: AppSpacing.xl,
        thickness: 1,
      ),
      listTileTheme: ListTileThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.control)),
        contentPadding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg, vertical: AppSpacing.xs),
        titleTextStyle: textTheme.titleMedium,
        subtitleTextStyle: textTheme.bodySmall,
      ),
      // Nivel 3 (flotante): un sheet no debe flotar igual que la tarjeta
      // que lo lanzó.
      bottomSheetTheme: const BottomSheetThemeData(
        backgroundColor: AppColors.superficie,
        surfaceTintColor: Colors.transparent,
        elevation: 8,
        shadowColor: AppColors.sombra,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(AppRadius.sheet)),
        ),
      ),
      // Nivel 4 (modal).
      dialogTheme: DialogThemeData(
        backgroundColor: AppColors.superficie,
        surfaceTintColor: Colors.transparent,
        elevation: 12,
        shadowColor: AppColors.sombra,
        titleTextStyle: textTheme.titleLarge,
        contentTextStyle: textTheme.bodyMedium,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.sheet)),
      ),
      menuTheme: MenuThemeData(
        style: MenuStyle(
          backgroundColor: const WidgetStatePropertyAll(AppColors.superficie),
          surfaceTintColor: const WidgetStatePropertyAll(Colors.transparent),
          shape: WidgetStatePropertyAll(
            RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(AppRadius.lg),
              side: const BorderSide(color: AppColors.borde),
            ),
          ),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: AppColors.texto,
        contentTextStyle: textTheme.bodyMedium?.copyWith(color: Colors.white),
        actionTextColor: AppColors.azul300,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.control)),
      ),
      tooltipTheme: TooltipThemeData(
        decoration: BoxDecoration(
          color: AppColors.texto,
          borderRadius: BorderRadius.circular(AppRadius.sm),
        ),
        textStyle: textTheme.bodySmall?.copyWith(color: Colors.white),
      ),
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: AppColors.marca,
        linearMinHeight: 2,
      ),
      scrollbarTheme: ScrollbarThemeData(
        thumbColor: WidgetStatePropertyAll(AppColors.bordeFuerte),
        radius: const Radius.circular(AppRadius.xs),
        thickness: const WidgetStatePropertyAll(8),
      ),
    );
  }
}
