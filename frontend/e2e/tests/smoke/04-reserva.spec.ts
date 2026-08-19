import { expect, iniciarSesionApi, solo, test } from '../../fixtures/fixtures';
import { fechaFutura } from '../../data/usuarios';
import { EspaciosPage } from '../../pages/EspaciosPage';

solo(['usuario']);

test.describe('Reserva por UI', () => {
  test('un usuario crea una reserva válida', async ({ page, backend }, testInfo) => {
    const espacios = new EspaciosPage(page);
    await espacios.goto();
    await espacios.abrirDisponibilidad('Auditorio Principal');
    await espacios.seleccionarFecha(fechaFutura(8, testInfo.retry));
    await espacios.seleccionarSlot('10:00');
    await espacios.irAResumen();
    await espacios.confirmarReserva();

    await expect(page.getByText(/Reserva #\d+ creada correctamente/)).toBeVisible();
    await expect(page.getByText('y pendiente de aprobación.')).toBeVisible();

    await iniciarSesionApi(backend, 'usuario');
    const respuesta = await backend.get('/reservas/mis-reservas');
    const reservas = (await respuesta.json()) as Array<{ fecha: string }>;
    expect(reservas.some((reserva) => reserva.fecha === fechaFutura(8, testInfo.retry))).toBeTruthy();
  });
});
