import { expect, iniciarSesionApi, solo, test } from '../../fixtures/fixtures';

solo(['usuario']);

test.describe('Autorización real del backend', () => {
  test('un usuario normal recibe 403 al intentar una acción administrativa', async ({ backend }) => {
    await iniciarSesionApi(backend, 'usuario');
    const respuesta = await backend.post('/usuarios', {
      data: { username: 'intruso-e2e', email: 'intruso-e2e@example.com', password: 'E2e-Intruso-123!', rol: 'admin' },
    });
    expect(respuesta.status()).toBe(403);
    const detalle = ((await respuesta.json()) as { detail: string }).detail;
    expect(detalle).toContain('Solo un administrador puede realizar esta acción');
  });

  test('un usuario normal no accede a rutas administrativas de la UI', async ({ page }) => {
    await page.goto('/admin');
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.getByRole('heading', { name: 'Panel de administración' })).not.toBeVisible();
  });
});
