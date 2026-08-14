import { expect, solo, test } from '../../fixtures/fixtures';

solo(['admin']);

test.describe('Secciones administrativas', () => {
  test('el control de cambios muestra el historial de operaciones', async ({ page }) => {
    await page.goto('/admin/control-cambios');
    await expect(page.getByRole('heading', { name: 'Control de cambios' })).toBeVisible();
    await expect(page.locator('tbody tr').first()).toBeVisible();
  });

  test('la administración de usuarios lista los usuarios de prueba', async ({ page }) => {
    await page.goto('/usuarios');
    await expect(page.getByRole('heading', { name: 'Administrar usuarios' })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'e2e-usuario', exact: true })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'e2e-gestor', exact: true })).toBeVisible();
  });
});
