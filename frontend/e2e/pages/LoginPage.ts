import type { Page } from '@playwright/test';

/** Flujo de login por UI (usado en el smoke de autenticación). */
export class LoginPage {
  constructor(private readonly page: Page) {}

  async goto() {
    await this.page.goto('/login');
  }

  async iniciarSesion(username: string, password: string) {
    await this.page.getByLabel('Usuario').fill(username);
    await this.page.getByLabel('Contraseña').fill(password);
    await this.page.getByRole('button', { name: 'Ingresar' }).click();
  }

  mensajeError() {
    return this.page.locator('.message-error');
  }
}
