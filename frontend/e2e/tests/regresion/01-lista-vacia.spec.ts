import { expect, headersPara, solo, test } from '../../fixtures/fixtures';
import { EspaciosPage } from '../../pages/EspaciosPage';

solo(['anonimo']);

test.describe('Listado público vacío', () => {
  test('sin espacios activos se muestra el mensaje de lista vacía', async ({ page, backend }) => {
    const headers = await headersPara(backend, 'admin');
    const espacios = (await (await backend.get('/espacios', { headers })).json()) as Array<{
      id: number;
      estado: string;
    }>;
    expect(espacios.length).toBeGreaterThan(0);
    const estadosOriginales = new Map(espacios.map((espacio) => [espacio.id, espacio.estado]));

    try {
      for (const espacio of espacios) {
        const actualizado = await backend.put(`/espacios/${espacio.id}`, {
          headers,
          data: { estado: 'inactivo' },
        });
        expect(actualizado.ok()).toBeTruthy();
      }

      const pagina = new EspaciosPage(page);
      await pagina.goto();
      await expect(pagina.mensajeVacio()).toBeVisible();
      await expect(pagina.tarjetas()).toHaveCount(0);
    } finally {
      // Restaurar el estado original de cada espacio (no solo 'activo'):
      // el seed incluye espacios inactivo/mantenimiento que deben conservarse.
      for (const espacio of espacios) {
        await backend.put(`/espacios/${espacio.id}`, {
          headers,
          data: { estado: estadosOriginales.get(espacio.id) },
        });
      }
    }
  });
});
