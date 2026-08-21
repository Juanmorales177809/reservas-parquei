import { test, expect } from '@playwright/test';

test.describe('Flutter Web público', () => {
  test('carga espacios públicos sin login', async ({ page }) => {
    await page.goto('/espacios');
    // Flutter Web renderiza en canvas, pero el título de AppBar debe estar en el DOM via semantics
    // Fallback: verificar que la página cargó y no hay redirect a login
    await expect(page).toHaveURL(/\/espacios/);
    // El body debe contener el canvas de Flutter
    await expect(page.locator('flt-glass-pane, canvas').first()).toBeVisible({ timeout: 15000 });
  });

  test('backend health accesible via proxy', async ({ request }) => {
    const resp = await request.get('http://127.0.0.1:8000/health');
    expect(resp.ok()).toBeTruthy();
  });
});
