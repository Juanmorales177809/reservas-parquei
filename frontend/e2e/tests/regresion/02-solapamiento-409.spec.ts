import { expect, headersPara, crearReservaApi, primerRecurso, solo, test } from '../../fixtures/fixtures';
import { fechaFutura } from '../../data/usuarios';
import { EspaciosPage } from '../../pages/EspaciosPage';

solo(['usuario']);

test.describe('Solapamiento', () => {
  test('una reserva solapada devuelve 409 y el slot queda ocupado en la UI', async ({ page, backend }, testInfo) => {
    const headers = await headersPara(backend, 'usuario');
    const recurso = await primerRecurso(backend);
    const fecha = fechaFutura(11, testInfo.retry);

    // Primera reserva por API (determinista): la creación por UI ya está
    // cubierta por el smoke 04-reserva.
    const primera = await crearReservaApi(backend, headers, {
      recurso_ids: [recurso.id],
      fecha,
      hora_inicio: '10:00',
      hora_fin: '11:00',
    });
    expect(primera.ok()).toBeTruthy();

    // Duplicado por API: el backend es la autoridad del 409.
    const duplicada = await crearReservaApi(backend, headers, {
      recurso_ids: [recurso.id],
      fecha,
      hora_inicio: '10:00',
      hora_fin: '11:00',
    });
    expect(duplicada.status()).toBe(409);
    const detalle = ((await duplicada.json()) as { detail: string }).detail;
    expect(detalle).toContain('ya tiene una reserva en ese horario');

    // La UI muestra el slot como ocupado y deshabilitado.
    const espacios = new EspaciosPage(page);
    await espacios.goto();
    await espacios.abrirDisponibilidad('Auditorio Principal');
    await espacios.seleccionarFecha(fecha);
    await expect(
      page.getByRole('button', { name: /10:00 - 11:00 · ocupado/ }),
    ).toBeDisabled();
  });
});
