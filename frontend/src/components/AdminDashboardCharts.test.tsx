import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import type { AdminDashboardSummary } from '@/types/admin-dashboard';
import AdminDashboardCharts from './AdminDashboardCharts';

const LEYENDA_EXACTA =
  'Heatmap visual: 07:00–19:00. El porcentaje global considera el horario completo configurado.';

function resumenBase(): AdminDashboardSummary {
  return {
    total_reservas: 1,
    reservas_pendientes: 1,
    recursos_activos: 1,
    usuarios: 1,
    espacio_nombre: null,
    reservas_por_estado: { pendientes: 1, aprobadas: 0, rechazadas: 0, canceladas: 0 },
    reservas_por_fecha: [],
    reservas_por_espacio: [],
    recursos_mas_reservados: [],
    ocupacion_por_dia_hora: [],
    ocupacion_global: { horas_ocupadas: 0, horas_disponibles: 0, porcentaje: 0 },
  };
}

function resumenConOcupacion(): AdminDashboardSummary {
  const base = resumenBase();
  base.ocupacion_por_dia_hora = Array.from({ length: 7 }, (_, dia) =>
    Array.from({ length: 13 }, (_, i) => ({
      dia: 'Lunes',
      dia_orden: dia,
      hora: i + 7,
      cantidad: dia === 0 && i === 1 ? 3 : 0,
    })),
  ).flat();
  base.ocupacion_global = { horas_ocupadas: 3, horas_disponibles: 12, porcentaje: 25 };
  return base;
}

describe('AdminDashboardCharts: heatmap', () => {
  it('muestra el grid exacto de 07:00 a 19:00', () => {
    render(<AdminDashboardCharts summary={resumenConOcupacion()} showSpaces />);
    expect(screen.getByRole('columnheader', { name: 'Día' })).toBeInTheDocument();
    for (let hora = 7; hora <= 19; hora += 1) {
      expect(screen.getByRole('columnheader', { name: `${hora}:00` })).toBeInTheDocument();
    }
    expect(screen.queryByRole('columnheader', { name: '20:00' })).not.toBeInTheDocument();
    expect(screen.queryByRole('columnheader', { name: '6:00' })).not.toBeInTheDocument();
  });

  it('muestra la leyenda exacta de cobertura parcial', () => {
    render(<AdminDashboardCharts summary={resumenConOcupacion()} showSpaces />);
    expect(screen.getByText(LEYENDA_EXACTA)).toBeInTheDocument();
  });

  it('muestra las celdas con sus cantidades e intensidad aplicada', () => {
    render(<AdminDashboardCharts summary={resumenConOcupacion()} showSpaces />);
    const celdas = screen.getAllByRole('cell');
    const conReservas = celdas.filter((celda) => celda.textContent === '3');
    expect(conReservas).toHaveLength(1);
    expect(conReservas[0]).toHaveStyle({ backgroundColor: 'rgba(8, 145, 178, 1)' });
  });

  it('muestra el porcentaje global sin confundirlo con el heatmap', () => {
    render(<AdminDashboardCharts summary={resumenConOcupacion()} showSpaces />);
    expect(screen.getByText('25%')).toBeInTheDocument();
    expect(screen.getByText('ocupación')).toBeInTheDocument();
  });

  it('muestra el estado vacío cuando no hay ocupación', () => {
    render(<AdminDashboardCharts summary={resumenBase()} showSpaces />);
    // Aparece tanto en la torta de ocupación global como en el heatmap.
    expect(screen.getAllByText('No hay ocupación registrada.').length).toBeGreaterThanOrEqual(1);
  });

  it('no renderiza celdas con valores negativos ni fuera del grid', () => {
    const resumen = resumenConOcupacion();
    resumen.ocupacion_por_dia_hora = resumen.ocupacion_por_dia_hora.filter(
      (item) => item.hora >= 7 && item.hora <= 19,
    );
    render(<AdminDashboardCharts summary={resumen} showSpaces />);
    expect(screen.getAllByRole('cell')).toHaveLength(7 * 13);
  });
});
