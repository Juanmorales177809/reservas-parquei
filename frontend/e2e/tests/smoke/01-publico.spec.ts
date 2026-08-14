import { expect, solo, test } from '../../fixtures/fixtures';
import { fechaFutura } from '../../data/usuarios';
import { EspaciosPage } from '../../pages/EspaciosPage';

solo(['anonimo']);

test.describe('Público', () => {
  test('un anónimo ve únicamente espacios activos en el listado', async ({ page, backend }) => {
    const espacios = new EspaciosPage(page);
    await espacios.goto();

    // Número de espacios activos según el backend (RN-005), sin hardcodear
    // el tamaño del seed.
    const activosApi = (await (await backend.get('/espacios')).json()) as Array<{
      estado: string;
    }>;
    const esperados = activosApi.filter((espacio) => espacio.estado === 'activo').length;

    const tarjetas = espacios.tarjetas();
    await expect(tarjetas.first()).toBeVisible();
    await expect(tarjetas).toHaveCount(esperados);
    for (const tarjeta of await tarjetas.all()) {
      await expect(tarjeta.getByText('Activo', { exact: true })).toBeVisible();
    }
    await expect(page.getByText('No hay espacios activos.')).not.toBeVisible();
  });

  test('un anónimo puede consultar disponibilidad de un recurso', async ({ page }) => {
    const espacios = new EspaciosPage(page);
    await espacios.goto();
    await espacios.abrirDisponibilidad('Auditorio Principal');
    // La fecha por defecto es hoy y no supera la anticipación: elegir una
    // fecha futura para que existan slots libres.
    await espacios.seleccionarFecha(fechaFutura(8));

    await expect(espacios.dialogo()).toHaveAttribute('aria-modal', 'true');
    await expect(espacios.slotsLibres().first()).toBeVisible();
  });
});
