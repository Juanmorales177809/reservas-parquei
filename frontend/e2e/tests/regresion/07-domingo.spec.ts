import { expect, iniciarSesionApi, primerRecurso, solo, test } from '../../fixtures/fixtures';
import { proximoDomingo } from '../../data/usuarios';

solo(['usuario']);

test.describe('Contrato de horario', () => {
  test('el backend rechaza reservas en un día sin atención', async ({ backend }) => {
    await iniciarSesionApi(backend, 'usuario');
    const recurso = await primerRecurso(backend);
    const respuesta = await backend.post('/reservas', {
      data: {
        recurso_ids: [recurso.id],
        fecha: proximoDomingo(),
        hora_inicio: '10:00',
        hora_fin: '11:00',
        asistentes: 1,
      },
    });
    expect(respuesta.status()).toBe(400);
    const detalle = ((await respuesta.json()) as { detail: string }).detail;
    expect(detalle).toContain('no está habilitado');
  });
});
