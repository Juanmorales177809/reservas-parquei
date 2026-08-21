import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';

/// Estado vacío.
///
/// **Fase 6**: la ilustración dejó de ser un icono dentro de un círculo
/// gris — el patrón por defecto de cualquier framework, que no dice nada
/// del producto. En un sistema institucional sin banco de imágenes, una
/// ilustración vectorial genérica se ve peor que nada y envejece mal; la
/// salida es **geometría del propio vocabulario de la app**: una grilla
/// esquemática de celdas vacías, que es exactamente la forma que el usuario
/// ve cuando SÍ hay datos.
class EmptyView extends StatelessWidget {
  const EmptyView({
    required this.message,
    this.icon = LucideIcons.inbox,
    this.detalle,
    this.accion,
    super.key,
  });

  /// Título del estado vacío.
  final String message;

  /// Icono chico que acompaña la grilla — da la pista de dominio
  /// (calendario, edificio, usuarios) sin ser el protagonista.
  final IconData icon;

  /// Una línea de contexto: qué puede hacer el usuario al respecto.
  final String? detalle;

  /// Acción primaria, si la hay ("Ver espacios", "Limpiar filtros").
  final Widget? accion;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.giant),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _GrillaEsquematica(icon: icon),
            const SizedBox(height: AppSpacing.xl),
            Text(message, style: textTheme.titleLarge, textAlign: TextAlign.center),
            if (detalle != null) ...[
              const SizedBox(height: AppSpacing.sm),
              ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 360),
                child: Text(
                  detalle!,
                  style: textTheme.bodyMedium?.copyWith(color: AppColors.textoSecundario),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
            if (accion != null) ...[
              const SizedBox(height: AppSpacing.xl),
              accion!,
            ],
          ],
        ),
      ),
    );
  }
}

/// Grilla 4×3 de celdas vacías con el icono de dominio superpuesto — la
/// silueta del contenido que debería estar ahí.
class _GrillaEsquematica extends StatelessWidget {
  const _GrillaEsquematica({required this.icon});

  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 116,
      height: 92,
      child: Stack(
        alignment: Alignment.center,
        children: [
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              for (var fila = 0; fila < 3; fila++)
                Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      for (var col = 0; col < 4; col++)
                        Container(
                          width: 26,
                          height: 26,
                          margin: EdgeInsets.only(right: col < 3 ? 4 : 0),
                          decoration: BoxDecoration(
                            color: AppColors.fondo,
                            borderRadius: BorderRadius.circular(AppRadius.xs),
                            border: Border.all(color: AppColors.borde),
                          ),
                        ),
                    ],
                  ),
                ),
            ],
          ),
          // El icono flota sobre la grilla en una cápsula blanca, para que
          // se lea como "esto es lo que iría acá" y no como una celda más.
          Container(
            padding: const EdgeInsets.all(AppSpacing.md),
            decoration: BoxDecoration(
              color: AppColors.superficie,
              shape: BoxShape.circle,
              border: Border.all(color: AppColors.borde),
            ),
            child: Icon(icon, size: 22, color: AppColors.textoTerciario),
          ),
        ],
      ),
    );
  }
}
