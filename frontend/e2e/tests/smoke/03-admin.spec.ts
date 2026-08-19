import { expect, iniciarSesionApi, solo, test } from '../../fixtures/fixtures';
import { sufijoUnico } from '../../data/usuarios';

solo(['admin']);

test.describe('Admin y RN-005', () => {
  test('el admin ve espacios activos e inactivos en la gestión', async ({ page, backend }) => {
    await iniciarSesionApi(backend, 'admin');
    const nombre = `Sala Inactiva ${sufijoUnico()}`;
    const creado = await backend.post('/espacios', {
      data: { nombre, ubicacion: 'E2E', capacidad: 5, estado: 'inactivo', correo: 'espacio.e2e@example.com' },
    });
    expect(creado.ok()).toBeTruthy();

    await page.goto('/admin/espacios');
    await expect(page.getByRole('heading', { name: 'Administrar espacios' })).toBeVisible();
    await expect(page.getByText(nombre)).toBeVisible();
  });

  test('el admin accede al dashboard y ve la sección de análisis', async ({ page }) => {
    await page.goto('/admin');
    await expect(page.getByRole('heading', { name: 'Panel de administración' })).toBeVisible();
  });
});
