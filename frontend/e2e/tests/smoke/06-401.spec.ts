import { expect, solo, test } from '../../fixtures/fixtures';

solo(['anonimo']);

test.describe('Sesión y redirecciones', () => {
  test('un 401 limpia la sesión y redirige a /login', async ({ page }) => {
    // Sembrar el token inválido una sola vez (sin addInitScript, que se
    // re-ejecutaría en cada navegación y lo re-inyectaría tras el redirect).
    await page.goto('/espacios');
    await page.evaluate(() => {
      window.localStorage.setItem('token', 'token-invalido-e2e');
      window.localStorage.setItem(
        'user',
        JSON.stringify({ id: 1, username: 'x', email: 'x@test.com', rol: 'usuario', espacio: null }),
      );
    });

    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login/);
    const token = await page.evaluate(() => window.localStorage.getItem('token'));
    expect(token).toBeNull();
  });

  test('un token inválido se comporta como sesión inválida en rutas protegidas', async ({ page }) => {
    await page.goto('/espacios');
    await page.evaluate(() => {
      window.localStorage.setItem('token', 'token-corrupto');
      window.localStorage.setItem('user', 'no-es-json');
    });

    await page.goto('/admin');
    await expect(page).toHaveURL(/\/login/);
  });
});
