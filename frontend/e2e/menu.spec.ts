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
      if (rol === "usuario") {
        // Inicio para los tres roles (FE-47); el usuario solo reserva.
        expect(destinos.map((d) => d.texto)).toEqual(["Inicio", "Reservas"]);
      } else {
        expect(destinos.length).toBeGreaterThanOrEqual(5);
        expect(destinos.map((d) => d.texto)).not.toContain("Notificaciones"); // es la campanita
      }
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

// Las notificaciones son una campanita en la cabecera, con avisos abajo a la derecha al entrar.
test.describe("campanita de notificaciones", () => {
  test.use({ storageState: "e2e/.auth/usuario.json" });

  test("cuenta lo que falta por leer, avisa al entrar y abre el panel con el historial", async ({ page }) => {
    await page.goto("/reservas");
    const campana = page.getByRole("button", { name: /^Notificaciones/ });
    await expect(campana).toBeVisible();
    await expect(campana).toHaveAccessibleName(/sin leer/);
    await expect(page.locator("[aria-live=polite]").getByText(/./).first()).toBeVisible();

    await campana.click();
    const panel = page.getByRole("region", { name: "Últimas notificaciones" });
    await expect(panel).toBeVisible();
    await panel.getByRole("link", { name: "Ver todas las notificaciones" }).click();
    await expect(page).toHaveURL(/\/notificaciones$/);
  });

  test("el usuario no entra a recursos ni espacios: vuelve a sus reservas", async ({ page }) => {
    await page.goto("/recursos");
    await expect(page).toHaveURL(/\/reservas$/);
    await page.goto("/espacios");
    await expect(page).toHaveURL(/\/reservas$/);
  });
});

test.describe("formulario de reserva en modal", () => {
  test.use({ storageState: "e2e/.auth/usuario.json" });

  test("«Nueva reserva» se abre sin salir del listado y se cierra con Cancelar", async ({ page }) => {
    await page.goto("/reservas");
    await page.getByRole("button", { name: "Nueva reserva" }).click();
    const dialogo = page.getByRole("dialog", { name: "Nueva reserva" });
    await expect(dialogo.getByLabel("Laboratorio", { exact: true })).toBeVisible();
    await expect(page).toHaveURL(/\/reservas$/);
    await dialogo.getByLabel("Laboratorio", { exact: true }).selectOption({ label: "Laboratorio de Redes" });
    await dialogo.getByRole("button", { name: "Cancelar" }).click();
    await expect(dialogo).toBeHidden();
    await expect(page).toHaveURL(/\/reservas$/);
  });
});
