import { expect, iniciarSesionApi, crearReservaApi, primerRecurso, solo, test } from '../../fixtures/fixtures';
import { fechaFutura } from '../../data/usuarios';
import { AdminDashboardPage } from '../../pages/AdminDashboardPage';

solo(['admin']);

test.describe('Porcentaje global vs heatmap', () => {
  test('la UI presenta el porcentaje global sin igualarlo a las celdas del heatmap', async ({ page, backend }, testInfo) => {
    await iniciarSesionApi(backend, 'admin');
    const recurso = await primerRecurso(backend);
    const creada = await crearReservaApi(backend, {
      recurso_ids: [recurso.id],
      fecha: fechaFutura(15, testInfo.retry),
      hora_inicio: '10:00',
      hora_fin: '12:00',
    });
    expect(creada.ok()).toBeTruthy();

    const resumen = (await (await backend.get('/admin/dashboard/summary')).json()) as {
      ocupacion_global: { horas_ocupadas: number; porcentaje: number };
    };
    // La base compartida acumula reservas de otros tests: validar el mínimo
    // aportado por esta reserva (2 horas) sin exigir totales exactos.
    expect(resumen.ocupacion_global.horas_ocupadas).toBeGreaterThanOrEqual(2);
    expect(resumen.ocupacion_global.porcentaje).toBeGreaterThan(0);

    const dashboard = new AdminDashboardPage(page);
    await dashboard.goto();
    await expect(dashboard.leyendaHeatmap()).toBeVisible();
    await expect(page.getByText('ocupación', { exact: true })).toBeVisible();
    for (let hora = 7; hora <= 19; hora += 1) {
      await expect(dashboard.celdaHeatmap(`${hora}:00`)).toBeVisible();
    }
  });
});
