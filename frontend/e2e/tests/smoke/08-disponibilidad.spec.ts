import { expect, headersPara, crearReservaApi, primerRecurso, solo, test } from '../../fixtures/fixtures';
import { fechaFutura, proximoDomingo } from '../../data/usuarios';
import { EspaciosPage } from '../../pages/EspaciosPage';

solo(['usuario']);

test.describe('Disponibilidad y horarios', () => {
  test('no se puede reservar un slot ya ocupado', async ({ page, backend }, testInfo) => {
    const headers = await headersPara(backend, 'usuario');
    const recurso = await primerRecurso(backend);
    const creada = await crearReservaApi(backend, headers, {
      recurso_ids: [recurso.id],
      fecha: fechaFutura(13, testInfo.retry),
      hora_inicio: '10:00',
      hora_fin: '11:00',
    });
    expect(creada.ok()).toBeTruthy();

    const espacios = new EspaciosPage(page);
    await espacios.goto();
    await espacios.abrirDisponibilidad('Auditorio Principal');
    await espacios.seleccionarFecha(fechaFutura(13, testInfo.retry));

    const slotOcupado = page.getByRole('button', { name: /10:00 - 11:00 · ocupado/ });
    await expect(slotOcupado).toBeVisible();
    await expect(slotOcupado).toBeDisabled();
  });

  test('un domingo no ofrece slots disponibles', async ({ page }) => {
    const espacios = new EspaciosPage(page);
    await espacios.goto();
    await espacios.abrirDisponibilidad('Auditorio Principal');
    await espacios.seleccionarFecha(proximoDomingo());

    await expect(espacios.slotsLibres()).toHaveCount(0);
  });
});
