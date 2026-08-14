import { expect, headersPara, crearReservaApi, primerRecurso, solo, test } from '../../fixtures/fixtures';
import { fechaFutura } from '../../data/usuarios';

solo(['gestor']);

test.describe('Notificaciones', () => {
  test('el gestor recibe la notificación de una reserva pendiente', async ({ page, backend }, testInfo) => {
    const headersUsuario = await headersPara(backend, 'usuario');
    const recurso = await primerRecurso(backend);
    const creada = await crearReservaApi(backend, headersUsuario, {
      recurso_id: recurso.id,
      fecha: fechaFutura(14, testInfo.retry),
      hora_inicio: '10:00',
      hora_fin: '11:00',
    });
    expect(creada.ok()).toBeTruthy();

    await page.goto('/dashboard');
    const campana = page.getByRole('button', { name: /Notificaciones/ });
    await campana.click();
    await expect(page.getByText('Nueva reserva pendiente para Recurso E2E').first()).toBeVisible();
  });
});
