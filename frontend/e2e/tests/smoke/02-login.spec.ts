import { expect, solo, test } from '../../fixtures/fixtures';
import { USUARIOS } from '../../data/usuarios';
import { LoginPage } from '../../pages/LoginPage';

solo(['anonimo']);

test.describe('Login por UI', () => {
  test('un usuario normal inicia sesión correctamente y llega a su dashboard', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.iniciarSesion(USUARIOS.usuario.username, USUARIOS.usuario.password);

    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.getByText(new RegExp(`Hola, ${USUARIOS.usuario.username}`))).toBeVisible();
  });

  test('un login inválido muestra el mensaje de error sin redirigir la sesión', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.iniciarSesion('usuario-inexistente', 'clave-incorrecta');

    await expect(login.mensajeError()).toBeVisible();
    await expect(login.mensajeError()).toContainText('Credenciales inválidas');
    await expect(page).toHaveURL(/\/login/);
  });
});
