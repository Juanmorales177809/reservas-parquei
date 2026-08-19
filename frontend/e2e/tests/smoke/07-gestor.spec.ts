import { expect, iniciarSesionApi, solo, test } from '../../fixtures/fixtures';
import { AdminDashboardPage } from '../../pages/AdminDashboardPage';

solo(['gestor']);

test.describe('Gestor', () => {
  test('el gestor accede a su panel de gestión', async ({ page }) => {
    const dashboard = new AdminDashboardPage(page);
    await dashboard.goto();
    await expect(page.getByRole('heading', { name: 'Panel de gestión' })).toBeVisible();
  });

  test('el gestor solo opera recursos de su espacio asignado', async ({ page, backend }) => {
    await iniciarSesionApi(backend, 'gestor');
    const me = await (await backend.get('/usuarios/me')).json();
    const espacioAsignado = (me as { espacio: { id: number } | null }).espacio?.id;
    expect(espacioAsignado).toBeDefined();

    const recursos = (await (await backend.get('/recursos/gestion')).json()) as Array<{
      espacio_id: number;
    }>;
    expect(recursos.length).toBeGreaterThan(0);
    for (const recurso of recursos) {
      expect(recurso.espacio_id).toBe(espacioAsignado);
    }

    await page.goto('/admin/configuracion');
    await expect(page.getByRole('heading', { name: 'Configuración' })).toBeVisible();
  });
});
