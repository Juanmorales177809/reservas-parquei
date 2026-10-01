import { expect, test } from "@playwright/test";
import { vigilar } from "./ayudas";

const PUBLICAS_AUTENTICADO = [
  "/reservas", "/reservas/nueva", "/recursos", "/espacios",
  "/investigacion/actividades", "/investigacion/perfiles", "/investigacion/proyectos", "/investigacion/vinculaciones",
  "/notificaciones", "/notificaciones/preferencias",
  "/usuarios/perfil", "/usuarios/perfil/editar", "/usuarios/perfil/perfiles", "/usuarios/perfil/vinculaciones",
  "/cambiar-contrasena",
];
const SOLO_ADMIN = [
  "/administracion/auditoria", "/administracion/cuentas/invitar", "/administracion/identidades",
  "/administracion/importaciones", "/administracion/unidades",
];

async function visitar(page: import("@playwright/test").Page, ruta: string, problemas: string[]) {
  await page.goto(ruta);
  await page.locator("h1").first().waitFor();
  await page.waitForTimeout(800); // deja terminar las cargas propias de la pantalla
  await expect(page.getByText(/Application error|Internal Server Error/i), ruta).toHaveCount(0);
  await expect(page.locator("h1").first(), `${ruta} sin título`).toBeVisible();
  expect(problemas, ruta).toEqual([]);
}

test.describe("administrador", () => {
  test.use({ storageState: "e2e/.auth/admin.json" });
  for (const ruta of [...PUBLICAS_AUTENTICADO, ...SOLO_ADMIN]) {
    test(`carga ${ruta}`, async ({ page }) => {
      const problemas = vigilar(page);
      await visitar(page, ruta, problemas);
    });
  }
});

// Decisión 2026-10-01: el usuario solo reserva; recursos, espacios e investigación no son suyos.
const SOLO_QUIEN_GESTIONA = ["/recursos", "/espacios", "/investigacion/actividades", "/investigacion/proyectos"];

test.describe("usuario sin permisos", () => {
  test.use({ storageState: "e2e/.auth/usuario.json" });
  for (const ruta of PUBLICAS_AUTENTICADO.filter(
    (r) => !r.startsWith("/reservas/nueva") && !r.startsWith("/investigacion") && r !== "/recursos" && r !== "/espacios"
  )) {
    test(`carga ${ruta}`, async ({ page }) => {
      const problemas = vigilar(page);
      await visitar(page, ruta, problemas);
    });
  }
  for (const ruta of [...SOLO_ADMIN, ...SOLO_QUIEN_GESTIONA]) {
    test(`no entra a ${ruta}`, async ({ page }) => {
      await page.goto(ruta);
      await page.waitForTimeout(1500);
      await expect(page).not.toHaveURL(new RegExp(ruta.replace(/\//g, "\/") + "$"));
    });
  }
});
