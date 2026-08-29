import 'dart:typed_data';

import 'package:file_saver/file_saver.dart';
import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../network/api_exception.dart';

/// Botón de exportar CSV/Excel reusado por dashboard/mis-reservas/auditoría
/// (2026-08-29) -- extraído de `_ExportarDashboardButton`
/// (`features/dashboard/presentation/dashboard_screen.dart`), primer punto
/// que lo necesitó.
class ExportButton extends StatefulWidget {
  const ExportButton({super.key, required this.nombreArchivo, required this.onExportar, this.mensajeExito = 'Exportado.'});

  /// Nombre base del archivo guardado (sin fecha ni extensión, se agregan
  /// automáticamente).
  final String nombreArchivo;
  final Future<List<int>> Function(String formato) onExportar;
  final String mensajeExito;

  @override
  State<ExportButton> createState() => _ExportButtonState();
}

class _ExportButtonState extends State<ExportButton> {
  bool _exportando = false;

  Future<void> _exportar(String formato) async {
    setState(() => _exportando = true);
    try {
      final bytes = await widget.onExportar(formato);
      final hoy = DateTime.now().toIso8601String().split('T').first;
      await FileSaver.instance.saveFile(
        name: '${widget.nombreArchivo}_$hoy',
        bytes: Uint8List.fromList(bytes),
        fileExtension: formato,
        mimeType: formato == 'csv' ? MimeType.csv : MimeType.microsoftExcel,
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(widget.mensajeExito)));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo exportar.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _exportando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_exportando) {
      return const Padding(
        padding: EdgeInsets.all(16),
        child: SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)),
      );
    }
    return PopupMenuButton<String>(
      icon: const Icon(LucideIcons.download),
      tooltip: 'Exportar',
      onSelected: _exportar,
      itemBuilder: (context) => const [
        PopupMenuItem(value: 'csv', child: Text('Exportar CSV')),
        PopupMenuItem(value: 'xlsx', child: Text('Exportar Excel')),
      ],
    );
  }
}
