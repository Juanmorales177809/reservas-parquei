import { expect, iniciarSesionApi, crearReservaApi, primerRecurso, solo, test } from '../../fixtures/fixtures';
import { fechaFutura } from '../../data/usuarios';
import { ReservasPage } from '../../pages/ReservasPage';

solo(['usuario']);

test.describe('Modificación de reserva pendiente', () => {
  test('un usuario modifica los asistentes de una reserva esperando', async ({ page, backend }, testInfo) => {
    await iniciarSesionApi(backend, 'usuario');
    const recurso = await primerRecurso(backend);
    const creada = await crearReservaApi(backend, {
      recurso_ids: [recurso.id],
      fecha: fechaFutura(18, testInfo.retry),
      hora_inicio: '12:00',
      hora_fin: '13:00',
      asistentes: 1,
    });
    expect(creada.ok()).toBeTruthy();

    const pagina = new ReservasPage(page);
    await pagina.goto();
    await pagina.editarPrimeraFila(3);
    await expect(page.getByRole('spinbutton', { name: 'Asistentes' })).not.toBeVisible();
    await expect(page.locator('tbody tr').first()).toContainText('3');
  });
});
