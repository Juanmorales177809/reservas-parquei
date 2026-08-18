import { expect, solo, test } from '../../fixtures/fixtures';

solo(['anonimo']);

// Fase 9F-B: la sesión ya no vive en localStorage sino en una cookie
// HttpOnly. `page.evaluate` no puede leerla ni escribirla (por diseño:
// HttpOnly es invisible para JS de página). Para simular una sesión
// inválida usamos context.addCookies(), el mecanismo equivalente a nivel
// de Playwright — igual que un atacante o un bug de servidor podría dejar
// una cookie corrupta, pero nunca algo que la propia app pueda hacer.
const COOKIE_INVALIDA = {
  name: 'access_token',
  value: 'token-invalido-e2e',
  domain: 'localhost',
  path: '/',
  httpOnly: true,
  secure: false,
  sameSite: 'Lax' as const,
};

test.describe('Sesión y redirecciones', () => {
  test('una cookie de sesión inválida redirige a /login en una ruta protegida', async ({
    page,
    context,
  }) => {
    await context.addCookies([COOKIE_INVALIDA]);

    await page.goto('/dashboard');

    await expect(page).toHaveURL(/\/login/);
    // La página de login debe renderizar de verdad, no solo la URL: si el
    // 401 de /usuarios/me disparara el interceptor global por error, el
    // navegador recargaría a mitad de un redirect ya en curso.
    await expect(page.getByRole('button', { name: 'Ingresar' })).toBeVisible();
  });

  test('un token inválido en la cookie se comporta como sesión inválida en otra ruta protegida', async ({
    page,
    context,
  }) => {
    await context.addCookies([COOKIE_INVALIDA]);

    await page.goto('/admin');

    await expect(page).toHaveURL(/\/login/);
  });

  test('sin cookie de sesión, una ruta protegida redirige a /login', async ({ page }) => {
    await page.goto('/reservas/mis-reservas');

    await expect(page).toHaveURL(/\/login/);
  });
});
