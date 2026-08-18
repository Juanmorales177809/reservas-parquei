import { expect, headersPara, crearReservaApi, primerRecurso, solo, test } from '../../fixtures/fixtures';
import { fechaFutura } from '../../data/usuarios';
import { AdminDashboardPage } from '../../pages/AdminDashboardPage';

solo(['admin']);

test.describe('Dashboard y heatmap', () => {
  test('el heatmap muestra el grid 07:00–19:00 y la leyenda exacta', async ({ page, backend }, testInfo) => {
    // El heatmap solo pinta el grid con ocupación: crear una reserva previa.
    const headers = await headersPara(backend, 'admin');
    const recurso = await primerRecurso(backend);
    const creada = await crearReservaApi(backend, headers, {
      recurso_ids: [recurso.id],
      fecha: fechaFutura(16, testInfo.retry),
      hora_inicio: '10:00',
      hora_fin: '11:00',
    });
    expect(creada.ok()).toBeTruthy();

    const dashboard = new AdminDashboardPage(page);
    await dashboard.goto();

    await expect(dashboard.seccionAnalisis()).toBeVisible();
    await expect(dashboard.leyendaHeatmap()).toBeVisible();
    for (let hora = 7; hora <= 19; hora += 1) {
      await expect(dashboard.celdaHeatmap(`${hora}:00`)).toBeVisible();
    }
  });

  test('una reserva dentro del horario incrementa la ocupación global', async ({ page, backend }, testInfo) => {
    const headers = await headersPara(backend, 'admin');
    const recurso = await primerRecurso(backend);
    // Offset 20, no 12: los offsets 12 y 13 pueden converger a la misma
    // fecha efectiva cuando el día+12 cae en domingo (fechaFutura salta al
    // lunes), colisionando con smoke/08-disponibilidad.spec.ts (mismo
    // recurso y 10:00-11:00) en un 409 real de reservas_sin_solapamiento
    // entre proyectos. El 20 mantiene margen de al menos 2 días respecto a
    // todos los demás offsets (ver regresion/05-notificaciones.spec.ts).
    const creada = await crearReservaApi(backend, headers, {
      recurso_ids: [recurso.id],
      fecha: fechaFutura(20, testInfo.retry),
      hora_inicio: '10:00',
      hora_fin: '11:00',
    });
    expect(creada.ok()).toBeTruthy();

    const resumen = await (await backend.get('/admin/dashboard/summary', { headers })).json();
    const ocupacion = resumen as { ocupacion_global: { horas_ocupadas: number; porcentaje: number } };
    expect(ocupacion.ocupacion_global.horas_ocupadas).toBeGreaterThan(0);
    expect(ocupacion.ocupacion_global.porcentaje).toBeGreaterThan(0);

    const dashboard = new AdminDashboardPage(page);
    await dashboard.goto();
    await expect(dashboard.tituloOcupacionGlobal()).toBeVisible();
    await expect(page.getByText(/%$/).first()).toBeVisible();
  });
});
