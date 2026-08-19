import { expect, iniciarSesionApi, crearReservaApi, primerRecurso, solo, test } from '../../fixtures/fixtures';
import { fechaFutura } from '../../data/usuarios';

solo(['gestor']);

test.describe('Notificaciones', () => {
  test('el gestor recibe la notificación de una reserva pendiente', async ({ page, backend }, testInfo) => {
    await iniciarSesionApi(backend, 'usuario');
    const recurso = await primerRecurso(backend);
    const creada = await crearReservaApi(backend, {
      recurso_ids: [recurso.id],
      // Offset 22, no 14: reserva el mismo primer recurso y el mismo horario
      // 10:00-11:00 que e2e/tests/smoke/08-disponibilidad.spec.ts (offset 13).
      // fechaFutura salta al lunes cuando el offset crudo cae domingo, así
      // que dos offsets separados por solo 1 día (13 y 14) pueden converger
      // a la misma fecha efectiva (ej.: offset 13 en domingo -> lunes, igual
      // que offset 14 sin salto) y disparar un 409 real de
      // reservas_sin_solapamiento entre specs. Un margen de al menos 2 días
      // respecto a cualquier otro offset usado en la suite (8, 9, 11, 12, 13,
      // 15, 16, 18 — ver e2e/README.md) hace imposible la colisión sin
      // importar qué día de la semana sea "hoy": el salto de domingo nunca
      // desplaza más de 1 día.
      fecha: fechaFutura(22, testInfo.retry),
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
