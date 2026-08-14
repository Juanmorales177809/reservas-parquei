import type { Page } from '@playwright/test';

/** Página de reservas propias del usuario. */
export class ReservasPage {
  constructor(private readonly page: Page) {}

  async goto() {
    await this.page.goto('/reservas/mis-reservas');
  }

  filas() {
    return this.page.locator('tbody tr');
  }

  async editarPrimeraFila(asistentes: number) {
    await this.page.getByRole('button', { name: 'Editar' }).first().click();
    await this.page.getByRole('spinbutton', { name: 'Asistentes' }).fill(String(asistentes));
    await this.page.getByRole('button', { name: 'Guardar' }).first().click();
  }

  async cancelarPrimeraFila() {
    await this.page.getByRole('button', { name: 'Cancelar' }).first().click();
  }
}
