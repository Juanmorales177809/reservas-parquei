import type { Page } from '@playwright/test';

/** Listado público de espacios y modal de reserva. */
export class EspaciosPage {
  constructor(private readonly page: Page) {}

  async goto() {
    await this.page.goto('/espacios');
  }

  tarjetas() {
    return this.page.locator('article.card');
  }

  mensajeVacio() {
    return this.page.getByText('No hay espacios activos.');
  }

  async abrirDisponibilidad(nombreEspacio: string) {
    const tarjeta = this.page.locator('article.card', { hasText: nombreEspacio });
    await tarjeta.getByRole('button', { name: 'Disponibilidad' }).click();
    await this.page.getByRole('dialog').waitFor();
  }

  dialogo() {
    return this.page.getByRole('dialog');
  }

  async seleccionarFecha(fecha: string) {
    await this.page.getByLabel('Fecha').fill(fecha);
  }

  async seleccionarSlot(inicio: string) {
    await this.page.getByRole('button', { name: new RegExp(`${inicio} · libre`) }).click();
  }

  slotsLibres() {
    return this.page.getByRole('button', { name: /· libre/ });
  }

  async irAResumen() {
    await this.page.getByRole('button', { name: 'Reservar recurso' }).click();
  }

  async confirmarReserva() {
    await this.page.getByRole('checkbox').check();
    await this.page.getByRole('button', { name: 'Aceptar y reservar' }).click();
  }
}
