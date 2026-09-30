import { expect, test } from "@playwright/test";

// FE-24: cada destino del menú debe llevar a una pantalla, no a un 404.
for (const [rol, sesion] of [["administrador", "admin"], ["usuario", "usuario"]] as const) {
  test.describe(rol, () => {
    test.use({ storageState: `e2e/.auth/${sesion}.json` });

    test(`todos los destinos del menú responden`, async ({ page }) => {
      await page.goto("/reservas");
      const destinos = await page.locator("nav a").evaluateAll((as) =>
        as.map((a) => ({ href: (a as HTMLAnchorElement).getAttribute("href")!, texto: a.textContent!.trim() }))
      );
      expect(destinos.length).toBeGreaterThanOrEqual(5);
      for (const { href, texto } of destinos) {
        const respuesta = await page.goto(href);
        expect(respuesta?.status(), `${texto} (${href})`).toBeLessThan(400);
        await expect(page.locator("h1").first(), `${texto} sin título`).toBeVisible();
        await expect(page.locator("h1").first()).not.toHaveText("404");
      }
    });

    test("desde la cabecera se llega a cambiar la contraseña", async ({ page }) => {
      await page.goto("/reservas");
      await page.getByRole("link", { name: "Cambiar contraseña" }).click();
      await expect(page).toHaveURL(/\/cambiar-contrasena/);
    });
  });
}

test.describe("usuario", () => {
  test.use({ storageState: "e2e/.auth/usuario.json" });
  test("desde la cabecera se llega a Mi perfil", async ({ page }) => {
    await page.goto("/reservas");
    await page.getByRole("link", { name: "Mi perfil" }).click();
    await expect(page).toHaveURL(/\/usuarios\/perfil/);
  });
});

test.describe("administrador", () => {
  test.use({ storageState: "e2e/.auth/admin.json" });
  test("las portadas de módulo enlazan a sus pantallas", async ({ page }) => {
    for (const [ruta, enlace] of [
      ["/administracion", "Laboratorios y cargos"],
      ["/investigacion", "Actividades institucionales"],
      ["/usuarios", "Identidades e invitaciones"],
    ] as const) {
      await page.goto(ruta);
      await expect(page.getByRole("link", { name: enlace })).toBeVisible();
    }
  });
});
