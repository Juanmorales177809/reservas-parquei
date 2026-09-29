import { test as setup } from "@playwright/test";
import { ADMIN, USUARIO } from "./cuentas";
import { entrar } from "./ayudas";

// Un solo login por cuenta: el backend limita los intentos de inicio de sesión.
setup("sesión de administrador", async ({ page }) => {
  await entrar(page, ADMIN);
  await page.context().storageState({ path: "e2e/.auth/admin.json" });
});

setup("sesión de usuario", async ({ page }) => {
  await entrar(page, USUARIO);
  await page.context().storageState({ path: "e2e/.auth/usuario.json" });
});
