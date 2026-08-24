import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../theme/app_spacing.dart';

/// Marca de la app (ícono + wordmark) — reutilizada en las `AppBar` del
/// shell y en la pantalla de login para que la identidad visual se sienta
/// consistente en toda la app.
///
/// [compact] muestra solo el ícono, sin el wordmark. Lo usa la `AppBar` de
/// celular: ahí el título compite por ancho con el botón de "Iniciar
/// sesión", y con el wordmark completo el `Row` desbordaba (106px en un
/// viewport de 375dp).
class BrandMark extends StatelessWidget {
  const BrandMark({this.compact = false, super.key});

  /// Hasta 2026-08-24 este parámetro se aceptaba y el `build` lo ignoraba
  /// por completo: pasarlo no hacía nada. Ahora sí recorta al ícono.
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;

    final icono = Container(
      padding: const EdgeInsets.all(AppSpacing.xs),
      decoration: BoxDecoration(
        gradient: LinearGradient(colors: [scheme.primary, scheme.tertiary]),
        borderRadius: BorderRadius.circular(AppSpacing.sm),
      ),
      child: const Icon(LucideIcons.calendarCheck, color: Colors.white, size: 18),
    );

    if (compact) return icono;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        icono,
        const SizedBox(width: AppSpacing.sm),
        // `Flexible` + elipsis y no un `Text` suelto: el ancho disponible
        // depende de cuánto ocupen las acciones de la `AppBar` y del factor
        // de escala de texto del sistema (accesibilidad), así que un ancho
        // "que siempre entra" no existe. Antes de esto, un `Text` rígido
        // desbordaba con rayas amarillas y negras en cuanto el espacio se
        // achicaba.
        Flexible(
          child: Text(
            'Reservas Parque i',
            maxLines: 1,
            softWrap: false,
            overflow: TextOverflow.ellipsis,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
          ),
        ),
      ],
    );
  }
}
