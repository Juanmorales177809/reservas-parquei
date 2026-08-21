import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/widgets/animated_counter.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/hover_lift.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../../../core/widgets/staggered_entrance.dart';
import '../../auth/application/auth_provider.dart';
import '../../auth/domain/auth_user.dart';
import '../application/dashboard_providers.dart';
import '../domain/dashboard_summary.dart';

// Nombres abreviados a propósito: la primera columna de la tabla de
// heatmap es angosta (varias horas más a la derecha) y los nombres
// completos ("Miércoles") se cortaban en 2-3 líneas dentro de la celda.
const _kDias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
const _kHoras = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19];
/// Orden: pendientes, aprobadas, rechazadas, canceladas — mismos colores
/// que `EstadoReservaBadge`, para que el gráfico y los badges de la lista
/// de reservas hablen el mismo idioma.
const _kColoresEstado = [
  Color(0xFFB45309), // pendiente
  Color(0xFF047857), // positivo
  Color(0xFFDC2626), // negativo
  Color(0xFF64748B), // neutro
];

/// Los tres gráficos de conteo (reservas por espacio, reservas por fecha,
/// recursos más reservados) miden **cantidades enteras**, pero `fl_chart`
/// reparte el eje Y en fracciones si no se le indica lo contrario: con un
/// máximo de 3 dibujaba `0, 0.5, 1, 1.5, 2, 2.5, 3` — etiquetas que no
/// significan nada ("2.5 reservas") y que además se partían en dos líneas
/// porque `reservedSize: 28` no alcanzaba para tres caracteres.
({double maxY, double intervalo}) _ejeEntero(int maxValor) {
  final tope = maxValor < 1 ? 1 : maxValor;
  // Como mucho 4 divisiones, siempre de tamaño entero.
  final paso = (tope / 4).ceil();
  final maxY = (tope / paso).ceil() * paso;
  return (maxY: maxY.toDouble(), intervalo: paso.toDouble());
}

AxisTitles _tituloEjeY(double intervalo) => AxisTitles(
      sideTitles: SideTitles(
        showTitles: true,
        reservedSize: 34,
        interval: intervalo,
        getTitlesWidget: (valor, meta) => Padding(
          padding: const EdgeInsets.only(right: AppSpacing.sm),
          child: Text(
            '${valor.toInt()}',
            style: AppText.numerico(
              fontSize: 11,
              color: AppColors.textoTerciario,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ),
    );

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final summaryAsync = ref.watch(dashboardSummaryProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Dashboard')),
      body: summaryAsync.when(
        loading: () => const LoadingSpinner(),
        error: (error, _) => ErrorView(
          message: apiErrorMessage(error, fallback: 'No se pudo cargar el dashboard.'),
          onRetry: () => ref.invalidate(dashboardSummaryProvider),
        ),
        data: (summary) {
          if (summary.totalReservas == 0 && summary.recursosActivos == 0) {
            // Permite ver gráficas vacías igualmente, pero muestra estado inicial
          }
          final user = ref.watch(authProvider).value;
          final esAdmin = user?.rol == RolUsuario.admin;
          final esGestor = user?.rol == RolUsuario.gestor;
          return RefreshIndicator(
            onRefresh: () => ref.refresh(dashboardSummaryProvider.future),
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(AppSpacing.lg),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  if (esGestor && summary.espacioNombre != null) ...[
                    Text('Espacio: ${summary.espacioNombre}', style: Theme.of(context).textTheme.titleSmall),
                    const SizedBox(height: AppSpacing.md),
                  ],
                  _SummaryStrip(summary: summary, esAdmin: esAdmin),
                  const SizedBox(height: AppSpacing.xl),
                  _AnalisisSection(summary: summary, esAdmin: esAdmin),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

/// Franja compacta de números (no una grilla de tarjetas grandes): a
/// pedido del usuario, el dashboard prioriza gráficos grandes y deja los
/// totales como referencia secundaria — una sola tarjeta con ítems en
/// línea, en vez de 4 tarjetas elevadas compitiendo visualmente con los
/// charts de abajo.
class _SummaryStrip extends StatelessWidget {
  const _SummaryStrip({required this.summary, required this.esAdmin});

  final DashboardSummary summary;
  final bool esAdmin;

  @override
  Widget build(BuildContext context) {
    final deltas = summary.deltas;
    final items = [
      _StatItem(
        icon: LucideIcons.calendarDays,
        label: 'Total reservas',
        value: summary.totalReservas,
        color: AppColors.marca,
        delta: deltas?.totalReservas,
      ),
      _StatItem(icon: LucideIcons.clock, label: 'Pendientes', value: summary.reservasPendientes, color: AppEstados.pendiente.relleno),
      _StatItem(icon: LucideIcons.package, label: 'Recursos activos', value: summary.recursosActivos, color: AppColors.accion),
      if (esAdmin) _StatItem(icon: LucideIcons.users, label: 'Usuarios', value: summary.usuarios, color: AppEstados.positivo.relleno),
    ];
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: LayoutBuilder(
          builder: (context, constraints) {
            final isNarrow = constraints.maxWidth < 520;
            if (isNarrow) {
              return Wrap(
                runSpacing: AppSpacing.xl,
                children: [
                  for (var i = 0; i < items.length; i++)
                    SizedBox(
                      width: (constraints.maxWidth - AppSpacing.lg) / 2,
                      child: items[i].staggerEntrance(i),
                    ),
                ],
              );
            }
            // Divisores verticales entre KPIs: con solo espacio, la franja
            // se lee como cuatro textos sueltos; con divisores, como un
            // instrumento de medición.
            //
            // Divisor de altura FIJA, no `VerticalDivider` con
            // `CrossAxisAlignment.stretch`: esta `Row` vive dentro de un
            // `SingleChildScrollView`, así que su altura no está acotada y
            // `stretch` deja a los hijos sin restricción vertical — el
            // resultado es que toda la franja colapsa y el dashboard se
            // renderiza vacío (regresión real detectada en la
            // verificación, no en `flutter analyze`).
            return Row(
              children: [
                for (var i = 0; i < items.length; i++) ...[
                  if (i > 0)
                    Container(
                      width: 1,
                      height: 44,
                      color: AppColors.borde,
                      margin: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
                    ),
                  Expanded(child: items[i].staggerEntrance(i)),
                ],
              ],
            );
          },
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  const _StatItem({required this.icon, required this.label, required this.value, required this.color, this.delta});

  final IconData icon;
  final String label;
  final int value;
  final Color color;
  final DeltaInt? delta;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Container(
          padding: const EdgeInsets.all(AppSpacing.sm),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(AppRadius.md),
          ),
          child: Icon(icon, size: 18, color: color),
        ),
        const SizedBox(width: AppSpacing.md),
        Flexible(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              // El valor primero y la etiqueta debajo en `overline`: es el
              // nivel tipográfico que separa "etiqueta de dato" de "dato"
              // sin gastar espacio vertical.
              AnimatedCounter(
                value: value,
                style: AppText.numerico(fontSize: 26, fontWeight: FontWeight.w700, height: 1.15),
              ),
              if (delta != null) ...[
                const SizedBox(height: 4),
                _DeltaBadge(delta: delta!.delta, pct: delta!.deltaPct),
              ],
              const SizedBox(height: 2),
              Text(
                label.toUpperCase(),
                style: AppText.overline(),
                // Dos líneas: con el rail lateral ocupando 80px, en una
                // ventana media cada KPI queda en ~170px y "RECURSOS
                // ACTIVOS" no entra en una sola línea.
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _DeltaBadge extends StatelessWidget {
  const _DeltaBadge({required this.delta, this.pct});

  final num delta;
  final double? pct;

  @override
  Widget build(BuildContext context) {
    final positivo = delta > 0;
    final negativo = delta < 0;
    final color = positivo ? AppEstados.positivo : negativo ? AppEstados.negativo : AppEstados.neutro;
    final icon = positivo ? LucideIcons.trendingUp : negativo ? LucideIcons.trendingDown : LucideIcons.minus;
    final signo = positivo ? '+' : '';
    final texto = pct == null ? '$signo$delta' : '$signo$delta (${pct! > 0 ? '+' : ''}${pct!.toStringAsFixed(1)}%)';
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.sm, vertical: 2),
      decoration: BoxDecoration(
        color: color.tinte,
        borderRadius: BorderRadius.circular(AppRadius.pill),
        border: Border.all(color: color.borde.withValues(alpha: 0.35)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color.sobreTinte),
          const SizedBox(width: 4),
          Text(texto, style: AppText.numerico(fontSize: 11, color: color.sobreTinte, fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}

/// Donut protagonista de ocupación global (solo admin).
class _OcupacionHero extends StatelessWidget {
  const _OcupacionHero({required this.summary});

  final DashboardSummary summary;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final ocupacion = summary.ocupacionGlobal;
    final libres = (ocupacion.horasDisponibles - ocupacion.horasOcupadas).clamp(0.0, double.infinity);
    final delta = summary.deltas?.ocupacionPorcentaje;

    return HoverLift(
      child: _CardContainer(
        title: 'Ocupación global',
        subtitle: 'Horas reservadas en todos los recursos y espacios.',
        child: ocupacion.horasDisponibles == 0
            ? const _EmptyChart(message: 'No hay ocupación registrada.', height: 220)
            : SizedBox(
                height: 240,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    PieChart(
                      PieChartData(
                        sections: [
                          PieChartSectionData(
                            value: ocupacion.horasOcupadas,
                            color: AppColors.marca,
                            radius: 62,
                            title: '',
                          ),
                          PieChartSectionData(
                            value: libres,
                            color: AppColors.borde,
                            radius: 62,
                            title: '',
                          ),
                        ],
                        sectionsSpace: 2,
                        centerSpaceRadius: 68,
                      ),
                    ),
                    Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          '${ocupacion.porcentaje}%',
                          style: textTheme.displaySmall?.copyWith(color: AppColors.marca),
                        ),
                        Text('ocupación', style: textTheme.bodyMedium?.copyWith(color: AppColors.textoTerciario)),
                        if (delta != null) ...[
                          const SizedBox(height: AppSpacing.sm),
                          _DeltaBadge(delta: delta.delta, pct: delta.deltaPct),
                          const SizedBox(height: 2),
                          Text(
                            'vs 30 días previos',
                            style: AppText.overline().copyWith(fontSize: 10),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
      ),
    );
  }
}

class _AnalisisSection extends StatelessWidget {
  const _AnalisisSection({required this.summary, required this.esAdmin});

  final DashboardSummary summary;
  final bool esAdmin;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final tieneEstados = summary.reservasPorEstado.pendientes + summary.reservasPorEstado.aprobadas + summary.reservasPorEstado.rechazadas + summary.reservasPorEstado.canceladas > 0;
    final maxOcupacion = summary.ocupacionPorDiaHora.map((e) => e.cantidad).fold<int>(0, (a, b) => a > b ? a : b);

    // Altura de gráfico secundario aumentada (180 -> 220): a pedido del
    // usuario, el dashboard prioriza gráficos grandes sobre números —
    // "Ocupación global" (abajo) se separa como hero a todo el ancho en
    // vez de competir en la grilla 2 columnas con el resto.
    const chartHeight = 220.0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Análisis de reservas', style: textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700)),
        const SizedBox(height: AppSpacing.lg),
        // Fila protagonista: el donut de ocupación pesa el doble que el
        // reparto por estado (≈8 y 4 columnas de una rejilla de 12). Antes
        // el donut ocupaba el ancho completo y el reparto por estado caía
        // en la grilla de abajo como un gráfico secundario más, así que la
        // pantalla no comunicaba cuál de los dos era el titular.
        LayoutBuilder(
          builder: (context, constraints) {
            final hero = esAdmin ? _OcupacionHero(summary: summary) : null;
            final estados = _CardContainer(
              title: 'Reservas por estado',
              child: !tieneEstados
                  ? const _EmptyChart(message: 'No hay reservas para representar.', height: 120)
                  : _EstadoBarraApilada(estado: summary.reservasPorEstado),
            );

            if (hero == null) return estados;
            if (constraints.maxWidth < 900) {
              return Column(
                children: [
                  hero,
                  const SizedBox(height: AppSpacing.md),
                  estados,
                ],
              );
            }
            return IntrinsicHeight(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Expanded(flex: 8, child: hero),
                  const SizedBox(width: AppSpacing.md),
                  Expanded(flex: 4, child: estados),
                ],
              ),
            );
          },
        ),
        const SizedBox(height: AppSpacing.md),
        // Grid responsive: 1 col en móvil, 2 cols en escritorio
        LayoutBuilder(
          builder: (context, constraints) {
            final isWide = constraints.maxWidth >= 900;
            final cards = <Widget>[
              if (esAdmin && summary.reservasPorEspacio.isNotEmpty)
                _CardContainer(
                  title: 'Reservas por espacio',
                  subtitle: 'Incluye las reservas de todos los recursos de cada espacio.',
                  child: SizedBox(
                    height: chartHeight,
                    child: Builder(builder: (context) {
                    final eje = _ejeEntero(
                      summary.reservasPorEspacio.map((e) => e.cantidad).fold<int>(0, (a, b) => a > b ? a : b),
                    );
                    return BarChart(
                      BarChartData(
                        maxY: eje.maxY,
                        barGroups: [
                          for (var i = 0; i < summary.reservasPorEspacio.length; i++)
                            BarChartGroupData(x: i, barRods: [
                              BarChartRodData(toY: summary.reservasPorEspacio[i].cantidad.toDouble(), color: AppColors.marca, width: 18, borderRadius: const BorderRadius.vertical(top: Radius.circular(4))),
                            ]),
                        ],
                        titlesData: FlTitlesData(
                          leftTitles: _tituloEjeY(eje.intervalo),
                          bottomTitles: AxisTitles(
                            sideTitles: SideTitles(
                              showTitles: true,
                              getTitlesWidget: (v, meta) {
                                final idx = v.toInt();
                                if (idx < 0 || idx >= summary.reservasPorEspacio.length) return const SizedBox.shrink();
                                return Padding(
                                  padding: const EdgeInsets.only(top: 4),
                                  child: Text(summary.reservasPorEspacio[idx].nombre, style: const TextStyle(fontSize: 10), overflow: TextOverflow.ellipsis),
                                );
                              },
                            ),
                          ),
                          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                        ),
                        gridData: FlGridData(
                          show: true,
                          drawVerticalLine: false,
                          horizontalInterval: eje.intervalo,
                        ),
                        borderData: FlBorderData(show: false),
                      ),
                    );
                    }),
                  ),
                ),
              // "Reservas por estado" ya NO vive acá: subió a la fila
              // protagonista, junto al donut de ocupación.
              _CardContainer(
                title: 'Reservas por fecha',
                child: summary.reservasPorFecha.isEmpty
                    ? const _EmptyChart(message: 'No hay fechas con reservas.', height: chartHeight)
                    : SizedBox(
                        height: chartHeight,
                        child: Builder(builder: (context) {
                        final eje = _ejeEntero(
                          summary.reservasPorFecha.map((e) => e.cantidad).fold<int>(0, (a, b) => a > b ? a : b),
                        );
                        return LineChart(
                          LineChartData(
                            maxY: eje.maxY,
                            minY: 0,
                            lineBarsData: [
                              LineChartBarData(
                                spots: [
                                  for (var i = 0; i < summary.reservasPorFecha.length; i++) FlSpot(i.toDouble(), summary.reservasPorFecha[i].cantidad.toDouble()),
                                ],
                                isCurved: true,
                                color: AppColors.marca,
                                barWidth: 3,
                                dotData: const FlDotData(show: true),
                              ),
                            ],
                            titlesData: FlTitlesData(
                              leftTitles: _tituloEjeY(eje.intervalo),
                              bottomTitles: AxisTitles(
                                sideTitles: SideTitles(
                                  showTitles: true,
                                  getTitlesWidget: (v, meta) {
                                    final idx = v.toInt();
                                    if (idx < 0 || idx >= summary.reservasPorFecha.length) return const SizedBox.shrink();
                                    final fecha = summary.reservasPorFecha[idx].fecha;
                                    // "YYYY-MM-DD" -> "DD/MM"
                                    final partes = fecha.split('-');
                                    final label = partes.length == 3 ? '${partes[2]}/${partes[1]}' : fecha;
                                    return Text(label, style: const TextStyle(fontSize: 10));
                                  },
                                  interval: (summary.reservasPorFecha.length / 6).ceilToDouble().clamp(1, double.infinity),
                                ),
                              ),
                              rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                              topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                            ),
                            gridData: FlGridData(
                              show: true,
                              drawVerticalLine: false,
                              horizontalInterval: eje.intervalo,
                            ),
                            borderData: FlBorderData(show: false),
                          ),
                        );
                        }),
                      ),
              ),
              _CardContainer(
                title: 'Recursos más reservados',
                child: summary.recursosMasReservados.isEmpty
                    ? const _EmptyChart(message: 'No hay recursos con reservas.', height: chartHeight)
                    : SizedBox(
                        height: chartHeight,
                        child: Builder(builder: (context) {
                        final eje = _ejeEntero(
                          summary.recursosMasReservados.map((e) => e.cantidad).fold<int>(0, (a, b) => a > b ? a : b),
                        );
                        return BarChart(
                          BarChartData(
                            maxY: eje.maxY,
                            barGroups: [
                              for (var i = 0; i < summary.recursosMasReservados.length; i++)
                                BarChartGroupData(x: i, barRods: [
                                  BarChartRodData(toY: summary.recursosMasReservados[i].cantidad.toDouble(), color: AppEstados.positivo.relleno, width: 18, borderRadius: const BorderRadius.vertical(top: Radius.circular(4))),
                                ]),
                            ],
                            titlesData: FlTitlesData(
                              leftTitles: _tituloEjeY(eje.intervalo),
                              bottomTitles: AxisTitles(
                                sideTitles: SideTitles(
                                  showTitles: true,
                                  getTitlesWidget: (v, meta) {
                                    final idx = v.toInt();
                                    if (idx < 0 || idx >= summary.recursosMasReservados.length) return const SizedBox.shrink();
                                    return Text(summary.recursosMasReservados[idx].nombre, style: const TextStyle(fontSize: 10), overflow: TextOverflow.ellipsis);
                                  },
                                ),
                              ),
                              rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                              topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                            ),
                            gridData: FlGridData(
                              show: true,
                              drawVerticalLine: false,
                              horizontalInterval: eje.intervalo,
                            ),
                            borderData: FlBorderData(show: false),
                          ),
                        );
                        }),
                      ),
              ),
            ];
            if (isWide) {
              final rows = <Widget>[];
              for (var i = 0; i < cards.length; i += 2) {
                final first = cards[i].staggerEntrance(i);
                final second = i + 1 < cards.length ? cards[i + 1].staggerEntrance(i + 1) : null;
                rows.add(
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(child: first),
                      if (second != null) ...[const SizedBox(width: AppSpacing.md), Expanded(child: second)],
                    ],
                  ),
                );
                rows.add(const SizedBox(height: AppSpacing.md));
              }
              rows.add(_HeatmapCard(summary: summary, maxOcupacion: maxOcupacion).staggerEntrance(cards.length));
              return Column(children: rows);
            }
            return Column(
              children: [
                for (var i = 0; i < cards.length; i++) ...[cards[i].staggerEntrance(i), const SizedBox(height: AppSpacing.md)],
                _HeatmapCard(summary: summary, maxOcupacion: maxOcupacion).staggerEntrance(cards.length),
              ],
            );
          },
        ),
      ],
    );
  }
}

class _CardContainer extends StatelessWidget {
  const _CardContainer({required this.title, this.subtitle, required this.child});

  final String title;
  final String? subtitle;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
            if (subtitle != null) ...[
              const SizedBox(height: AppSpacing.xs),
              Text(subtitle!, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant)),
            ],
            const SizedBox(height: AppSpacing.md),
            child,
          ],
        ),
      ),
    );
  }
}

/// Reparto de reservas por estado como **barra apilada horizontal**.
///
/// Antes era una segunda torta. El dashboard ya tiene un donut protagonista
/// ("Ocupación global"): dos gráficos circulares en la misma pantalla
/// compiten por el mismo rol y ninguno gana. Una barra apilada ocupa una
/// fracción del espacio, se lee más rápido (comparar longitudes es más
/// preciso que comparar ángulos) y deja el peso visual al hero.
class _EstadoBarraApilada extends StatelessWidget {
  const _EstadoBarraApilada({required this.estado});

  final ReservasPorEstado estado;

  static const _kEtiquetas = ['Pendientes', 'Aprobadas', 'Rechazadas', 'Canceladas'];

  @override
  Widget build(BuildContext context) {
    final valores = [estado.pendientes, estado.aprobadas, estado.rechazadas, estado.canceladas];
    final total = valores.fold<int>(0, (a, b) => a + b);
    final textTheme = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(AppRadius.xs),
          child: SizedBox(
            height: 14,
            child: Row(
              children: [
                for (var i = 0; i < valores.length; i++)
                  if (valores[i] > 0)
                    Expanded(
                      flex: valores[i],
                      child: Tooltip(
                        message: '${_kEtiquetas[i]}: ${valores[i]}',
                        child: ColoredBox(color: _kColoresEstado[i], child: const SizedBox.expand()),
                      ),
                    ),
              ],
            ),
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        // Leyenda con el valor en línea: sin ella la barra es una tira de
        // colores sin significado.
        Column(
          children: [
            for (var i = 0; i < valores.length; i++)
              Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.sm),
                child: Row(
                  children: [
                    Container(
                      width: 10,
                      height: 10,
                      decoration: BoxDecoration(
                        color: _kColoresEstado[i],
                        borderRadius: BorderRadius.circular(3),
                      ),
                    ),
                    const SizedBox(width: AppSpacing.sm),
                    Expanded(child: Text(_kEtiquetas[i], style: textTheme.bodyMedium)),
                    Text(
                      '${valores[i]}',
                      style: AppText.numerico(fontSize: 14, fontWeight: FontWeight.w700),
                    ),
                    if (total > 0) ...[
                      const SizedBox(width: AppSpacing.sm),
                      SizedBox(
                        width: 40,
                        child: Text(
                          '${(valores[i] * 100 / total).round()}%',
                          textAlign: TextAlign.right,
                          style: AppText.numerico(
                            fontSize: 12,
                            color: AppColors.textoTerciario,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
          ],
        ),
      ],
    );
  }
}

class _EmptyChart extends StatelessWidget {
  const _EmptyChart({required this.message, this.height = 180});

  final String message;
  final double height;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: height,
      child: Center(child: Text(message, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant))),
    );
  }
}

class _HeatmapCard extends StatelessWidget {
  const _HeatmapCard({required this.summary, required this.maxOcupacion});

  final DashboardSummary summary;
  final int maxOcupacion;

  /// Cinco escalones discretos en vez de una opacidad continua: el ojo no
  /// compara luminosidades continuas de forma fiable, pero sí cuenta
  /// escalones. Con la versión anterior (alpha proporcional) era imposible
  /// distinguir "3 reservas" de "4" a simple vista.
  Color _intensidad(int cantidad, int maximo) {
    if (cantidad <= 0 || maximo <= 0) return kHeatmapRampa.first;
    final proporcion = cantidad / maximo;
    // 4 tramos por encima del vacío: (0, .25], (.25, .5], (.5, .75], (.75, 1]
    final escalon = (proporcion * (kHeatmapRampa.length - 1)).ceil();
    return kHeatmapRampa[escalon.clamp(1, kHeatmapRampa.length - 1)];
  }

  /// El texto blanco solo es legible en los dos escalones más oscuros.
  Color _textoSobreIntensidad(int cantidad, int maximo) {
    if (cantidad <= 0 || maximo <= 0) return AppColors.textoDeshabilitado;
    final proporcion = cantidad / maximo;
    final escalon = (proporcion * (kHeatmapRampa.length - 1)).ceil().clamp(1, kHeatmapRampa.length - 1);
    return escalon >= 3 ? Colors.white : AppColors.texto;
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final ocupacionMap = {for (final e in summary.ocupacionPorDiaHora) '${e.diaOrden}-${e.hora}': e.cantidad};

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Ocupación por día y hora', style: textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
            const SizedBox(height: AppSpacing.xs),
            Text('Heatmap visual: 07:00–19:00. El porcentaje global considera el horario completo configurado.', style: textTheme.bodySmall?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant)),
            const SizedBox(height: AppSpacing.md),
            if (maxOcupacion == 0)
              const _EmptyChart(message: 'No hay ocupación registrada.')
            else
              LayoutBuilder(
                builder: (context, constraints) {
                  // 14 columnas (1 de día + 13 de hora): en pantallas
                  // anchas se reparte el ancho disponible entre todas en
                  // vez de quedar en un ancho fijo angosto con espacio
                  // vacío a la derecha; en pantallas chicas nunca baja de
                  // 44px (mínimo legible) y ahí sí entra en scroll
                  // horizontal.
                  final anchoColumna = (constraints.maxWidth / (_kHoras.length + 1)).clamp(44.0, 72.0);
                  return SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Table(
                      defaultColumnWidth: FixedColumnWidth(anchoColumna),
                      border: TableBorder(
                        horizontalInside: BorderSide(color: Theme.of(context).colorScheme.outlineVariant.withValues(alpha: 0.2)),
                        verticalInside: BorderSide(color: Theme.of(context).colorScheme.outlineVariant.withValues(alpha: 0.2)),
                      ),
                      children: [
                        TableRow(
                          decoration: BoxDecoration(color: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.4)),
                          children: [
                            _HeatHeader(text: 'Día', style: textTheme.labelSmall),
                            for (final h in _kHoras) _HeatHeader(text: '$h:00', style: textTheme.labelSmall),
                          ],
                        ),
                        for (var dia = 0; dia < 7; dia++)
                          TableRow(
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: AppSpacing.sm, vertical: AppSpacing.sm),
                                alignment: Alignment.centerLeft,
                                child: Text(_kDias[dia], style: textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w600)),
                              ),
                              for (final hora in _kHoras)
                                Builder(
                                  builder: (context) {
                                    final cantidad = ocupacionMap['$dia-$hora'] ?? 0;
                                    return Tooltip(
                                      message: '${_kDias[dia]} $hora:00 — '
                                          '${cantidad == 1 ? '1 reserva' : '$cantidad reservas'}',
                                      child: Container(
                                        height: 34,
                                        alignment: Alignment.center,
                                        decoration: BoxDecoration(
                                          color: _intensidad(cantidad, maxOcupacion),
                                          borderRadius: BorderRadius.circular(AppRadius.xs),
                                        ),
                                        margin: const EdgeInsets.all(2),
                                        child: Text(
                                          '$cantidad',
                                          style: AppText.numerico(
                                            fontSize: 12,
                                            color: _textoSobreIntensidad(cantidad, maxOcupacion),
                                          ),
                                        ),
                                      ),
                                    );
                                  },
                                ),
                            ],
                          ),
                      ],
                    ),
                  );
                },
              ),
            const SizedBox(height: AppSpacing.lg),
            const _HeatmapLeyenda(),
          ],
        ),
      ),
    );
  }
}

/// Sin leyenda de rampa, un heatmap es decoración: el usuario ve manchas de
/// color pero no puede traducirlas a cantidades.
class _HeatmapLeyenda extends StatelessWidget {
  const _HeatmapLeyenda();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.end,
      children: [
        Text('MENOS', style: AppText.overline()),
        const SizedBox(width: AppSpacing.sm),
        for (final color in kHeatmapRampa) ...[
          Container(
            width: 18,
            height: 12,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(AppRadius.xs),
              border: Border.all(color: AppColors.borde),
            ),
          ),
          const SizedBox(width: 3),
        ],
        const SizedBox(width: AppSpacing.xs),
        Text('MÁS', style: AppText.overline()),
      ],
    );
  }
}

class _HeatHeader extends StatelessWidget {
  const _HeatHeader({required this.text, this.style});
  final String text;
  final TextStyle? style;
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.sm, vertical: AppSpacing.sm),
      alignment: Alignment.center,
      child: Text(text, style: style?.copyWith(fontWeight: FontWeight.w700)),
    );
  }
}
