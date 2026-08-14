import type { Page } from '@playwright/test';

/** Panel de administración/gestión con dashboard y heatmap. */
export class AdminDashboardPage {
  constructor(private readonly page: Page) {}

  async goto() {
    await this.page.goto('/admin');
  }

  seccionAnalisis() {
    return this.page.getByRole('heading', { name: 'Análisis de reservas' });
  }

  leyendaHeatmap() {
    return this.page.getByText(
      'Heatmap visual: 07:00–19:00. El porcentaje global considera el horario completo configurado.',
    );
  }

  celdaHeatmap(hora: string) {
    return this.page.getByRole('columnheader', { name: hora, exact: true });
  }

  tituloOcupacionGlobal() {
    return this.page.getByRole('heading', { name: 'Ocupación global' });
  }
}
