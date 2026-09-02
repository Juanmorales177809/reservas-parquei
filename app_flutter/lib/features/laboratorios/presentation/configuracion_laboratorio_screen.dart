import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../application/laboratorios_providers.dart';
import '../data/laboratorios_repository.dart';
import '../domain/configuracion_laboratorio.dart';
import '../domain/laboratorio.dart' show formatearHora;
import 'horario_editor.dart';

/// `GET/PUT /laboratorios/gestion/configuracion` — solo gestor. Fase 4b:
/// editor completo de `horario_atencion` (grilla día×hora) + antelación y
/// aprobación automática — espejo de `frontend/src/app/admin/configuracion/page.tsx`.
///
/// Sin `AppBar` propio (Fase 6 de
/// ~/.claude/plans/dazzling-wobbling-zebra.md — bug del navbar que
/// desaparecía): esta pantalla ahora vive DENTRO del `ShellRoute`, montada
/// sobre el `Scaffold` del shell activo. El título + botón "atrás" se
/// resuelven con un encabezado liviano (`_EncabezadoEmpujado`) en vez de un
/// segundo `AppBar` apilado. Conserva su propio `Scaffold` (sin `appBar:`,
/// así que no duplica nada visible) porque `_ConfiguracionFormState` usa
/// `ScaffoldMessenger.of(context)` para el `SnackBar` de "Deshacer" -- sin
/// un `Scaffold` en este subárbol, ese `SnackBar` no tiene dónde anclarse
/// cuando la pantalla se monta sola (como en
/// `configuracion_laboratorio_screen_test.dart`).
class ConfiguracionLaboratorioScreen extends ConsumerWidget {
  const ConfiguracionLaboratorioScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final configAsync = ref.watch(configuracionLaboratorioGestionProvider);

    return Scaffold(
      body: Column(
        children: [
          const _EncabezadoEmpujado(titulo: 'Configuración del laboratorio'),
          Expanded(
            child: configAsync.when(
              loading: () => const LoadingSpinner(),
              error: (error, _) => ErrorView(
                message: apiErrorMessage(error, fallback: 'No se pudo cargar la configuración.'),
                onRetry: () => ref.invalidate(configuracionLaboratorioGestionProvider),
              ),
              data: (config) => _ConfiguracionForm(config: config),
            ),
          ),
        ],
      ),
    );
  }
}

/// Encabezado mínimo para una ruta "empujada" (con botón atrás, sin
/// bottom/top nav propio) que vive dentro del `ShellRoute` — evita apilar
/// un segundo `AppBar` completo debajo del `AppBar` del shell activo.
class _EncabezadoEmpujado extends StatelessWidget {
  const _EncabezadoEmpujado({required this.titulo});

  final String titulo;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      bottom: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(AppSpacing.xs, AppSpacing.xs, AppSpacing.lg, AppSpacing.xs),
        child: Row(
          children: [
            const BackButton(),
            const SizedBox(width: AppSpacing.xs),
            Expanded(child: Text(titulo, style: Theme.of(context).textTheme.titleLarge)),
          ],
        ),
      ),
    );
  }
}

class _ConfiguracionForm extends ConsumerStatefulWidget {
  const _ConfiguracionForm({required this.config});

  final ConfiguracionLaboratorio config;

  @override
  ConsumerState<_ConfiguracionForm> createState() => _ConfiguracionFormState();
}

class _ConfiguracionFormState extends ConsumerState<_ConfiguracionForm> {
  late int _horasAntelacion;
  late bool _aprobacionAutomatica;
  late Map<int, List<int>> _horario;
  bool _guardando = false;
  String? _error;
  String? _success;

  @override
  void initState() {
    super.initState();
    _horasAntelacion = widget.config.horasAntelacion;
    _aprobacionAutomatica = widget.config.aprobacionAutomatica;
    _horario = horarioFromJson(widget.config.horarioAtencion);
  }

  /// Aplica un cambio del editor de horario.
  ///
  /// Cuando el cambio fue masivo (fila completa, columna completa o un
  /// arrastre), ofrece **Deshacer**: la grilla tiene 112 celdas y un toque
  /// accidental en un encabezado puede borrar la configuración de un día
  /// entero. Sin esta red, el único camino de vuelta era salir sin guardar
  /// y volver a entrar, perdiendo también el resto de los cambios.
  void _actualizarHorario(Map<int, List<int>> nuevo, {String? operacionMasiva}) {
    final anterior = _horario;
    setState(() {
      _horario = nuevo;
      // Cualquier edición invalida el "guardado con éxito" anterior: dejarlo
      // en pantalla haría creer que los cambios nuevos ya están guardados.
      _success = null;
    });
    if (operacionMasiva == null || !mounted) return;
    // `removeCurrentSnackBar()` (no `hideCurrentSnackBar()`) para que el
    // reemplazo sea inmediato: acá siempre estamos sustituyendo un aviso por
    // otro, no vale la pena animar la salida del anterior.
    ScaffoldMessenger.of(context)
      ..removeCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(operacionMasiva),
          duration: const Duration(seconds: 8),
          // `persist: false` es OBLIGATORIO acá, no un ajuste de gusto: un
          // `SnackBar` con `action` toma `persist = true` por defecto
          // (`snack_bar.dart`: `persist = persist ?? action != null`), y un
          // snackbar que persiste NO se auto-cierra nunca — el timer de
          // `duration` se dispara, ve `persist`, y retorna sin cerrarlo
          // (`scaffold.dart`, arranque de `_snackBarTimer`). El resultado es
          // el "Deshacer" clavado en pantalla para siempre. `duration` sola
          // no alcanza: sin esto, se ignora por completo. Bug real reportado
          // en producción.
          persist: false,
          action: SnackBarAction(
            label: 'Deshacer',
            onPressed: () => setState(() => _horario = anterior),
          ),
        ),
      );
  }

  Future<void> _guardar() async {
    final tieneAlgunSlot = _horario.values.any((h) => h.isNotEmpty);
    if (!tieneAlgunSlot) {
      setState(() => _error = 'Seleccioná al menos una franja de atención.');
      return;
    }
    setState(() {
      _guardando = true;
      _error = null;
      _success = null;
    });
    try {
      final horarioJson = horarioToJson(_horario);
      await ref.read(laboratoriosRepositoryProvider).actualizarConfiguracionGestion(
            horarioAtencion: horarioJson,
            horasAntelacion: _horasAntelacion,
            aprobacionAutomatica: _aprobacionAutomatica,
          );
      ref.invalidate(configuracionLaboratorioGestionProvider);
      if (mounted) {
        setState(() => _success = 'La configuración de atención fue actualizada.');
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Configuración guardada.')));
      }
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(e, fallback: 'No se pudo guardar la configuración.'));
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final config = widget.config;
    final textTheme = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;

    return ListView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      children: [
        Text(config.laboratorioNombre, style: textTheme.titleLarge),
        const SizedBox(height: AppSpacing.xs),
        Row(
          children: [
            Icon(LucideIcons.clock, size: 16, color: scheme.onSurfaceVariant),
            const SizedBox(width: AppSpacing.xs),
            Text(
              'Horario: ${formatearHora(config.horaApertura)} – ${formatearHora(config.horaCierre)}',
              style: textTheme.bodyMedium,
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.md),
        if (_success != null) ...[
          Container(
            padding: const EdgeInsets.all(AppSpacing.md),
            decoration: BoxDecoration(
              color: const Color(0xFF10B981).withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(AppRadius.md),
              border: Border.all(color: const Color(0xFF10B981).withValues(alpha: 0.3)),
            ),
            child: Row(
              children: [
                const Icon(LucideIcons.check, size: 16, color: Color(0xFF10B981)),
                const SizedBox(width: AppSpacing.sm),
                Expanded(child: Text(_success!, style: textTheme.bodySmall?.copyWith(color: const Color(0xFF10B981)))),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.md),
        ],
        Card(
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: HorarioEditor(
              horario: _horario,
              onChanged: _actualizarHorario,
            ),
          ),
        ),
        const SizedBox(height: AppSpacing.xl),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Antelación mínima', style: textTheme.titleSmall),
                const SizedBox(height: AppSpacing.xs),
                Text(
                  'Horas de anticipación requeridas para crear una reserva.',
                  style: textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant),
                ),
                const SizedBox(height: AppSpacing.md),
                Row(
                  children: [
                    IconButton.filledTonal(
                      onPressed: _horasAntelacion > 0 ? () => setState(() => _horasAntelacion--) : null,
                      icon: const Icon(LucideIcons.minus, size: 16),
                    ),
                    SizedBox(
                      width: 56,
                      child: Text(
                        '$_horasAntelacion h',
                        textAlign: TextAlign.center,
                        style: textTheme.titleMedium,
                      ),
                    ),
                    IconButton.filledTonal(
                      onPressed: _horasAntelacion < 8760 ? () => setState(() => _horasAntelacion++) : null,
                      icon: const Icon(LucideIcons.plus, size: 16),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: AppSpacing.md),
        Card(
          child: SwitchListTile(
            title: const Text('Aprobación automática'),
            subtitle: const Text('Las reservas nuevas quedan aprobadas sin revisión manual.'),
            value: _aprobacionAutomatica,
            onChanged: (v) => setState(() => _aprobacionAutomatica = v),
          ),
        ),
        if (_error != null) ...[
          const SizedBox(height: AppSpacing.md),
          Text(_error!, style: TextStyle(color: scheme.error)),
        ],
        const SizedBox(height: AppSpacing.xl),
        FilledButton(
          onPressed: _guardando ? null : _guardar,
          child: _guardando
              ? const SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                )
              : const Text('Guardar'),
        ),
      ],
    );
  }
}
