import { expect, headersPara, crearReservaApi, primerRecurso, solo, test } from '../../fixtures/fixtures';
import { fechaFutura } from '../../data/usuarios';
import { ReservasPage } from '../../pages/ReservasPage';

solo(['usuario']);

test.describe('Cancelación', () => {
  test('un usuario cancela su reserva aprobada', async ({ page, backend }, testInfo) => {
    const headersUsuario = await headersPara(backend, 'usuario');
    const recurso = await primerRecurso(backend);
    const creada = await crearReservaApi(backend, headersUsuario, {
      recurso_id: recurso.id,
      fecha: fechaFutura(9, testInfo.retry),
      hora_inicio: '10:00',
      hora_fin: '11:00',
    });
    expect(creada.ok()).toBeTruthy();
    const reserva = (await creada.json()) as { id: number };

    const headersAdmin = await headersPara(backend, 'admin');
    const aprobada = await backend.put(`/reservas/${reserva.id}/estado`, {
      headers: headersAdmin,
      data: { nuevo_estado: 'aprobada' },
    });
    expect(aprobada.ok()).toBeTruthy();

    const pagina = new ReservasPage(page);
    await pagina.goto();
    await expect(page.getByText('Aprobada').first()).toBeVisible();
    // La cancelación usa window.confirm: aceptar el diálogo nativo.
    page.on('dialog', (dialogo) => dialogo.accept());
    await pagina.cancelarPrimeraFila();

    // Verificación dual: UI y autoridad del backend.
    await expect(page.getByText('Cancelada').first()).toBeVisible();
    const estadoApi = await backend.get('/reservas/mis-reservas', { headers: headersUsuario });
    const reservas = (await estadoApi.json()) as Array<{ id: number; estado: string }>;
    expect(reservas.find((r) => r.id === reserva.id)?.estado).toBe('cancelada');
  });
});
