import { expect, test } from "@playwright/test";

// SCR-REP-01..03 contra el backend real. Los datos dependen de lo que hayan dejado las otras pruebas,
// así que se consulta un periodo amplio y se comprueba la forma de la pantalla, no cifras concretas.

async function consultar(page: import("@playwright/test").Page) {
  await page.getByLabel("Desde").fill("2020-01-01");
  await page.getByLabel("Hasta").fill("2030-12-31");
  await page.getByRole("button", { name: "Consultar" }).click();
}

test.describe("administrador", () => {
  test.use({ storageState: "e2e/.auth/admin.json" });

  test("la portada lleva a las tres pantallas", async ({ page }) => {
    await page.goto("/reportes");
    for (const nombre of ["Ocupación", "Solicitudes", "Lista de espera"]) {
      await expect(page.getByRole("link", { name: new RegExp(nombre) })).toBeVisible();
    }
  });

  test("ocupación por laboratorio: tabla, gráfico de una sola medida y exportación", async ({ page }) => {
    await page.goto("/reportes/ocupacion");
    await expect(page.getByRole("heading", { name: "Reportes · Ocupación" })).toBeVisible();
    await expect(page.getByRole("button", { name: "CSV" })).toHaveCount(0); // no se ofrece sin consultar
    await consultar(page);
    await expect(page.getByRole("table")).toBeVisible();
    await expect(page.getByRole("columnheader", { name: "Horas disponibles" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Ocupación por laboratorio" })).toBeVisible();
    await expect(page.locator(".recharts-surface")).toBeVisible();
    await expect(page.locator(".recharts-bar-rectangle").first()).toBeVisible();

    const descarga = page.waitForEvent("download");
    await page.getByRole("button", { name: "CSV" }).click();
    expect((await descarga).suggestedFilename()).toMatch(/\.csv$/);
  });

  test("ocupación por proyecto mide en horas", async ({ page }) => {
    await page.goto("/reportes/ocupacion");
    await page.getByLabel("Dimensión").selectOption({ label: "Proyecto" });
    await consultar(page);
    await expect(page.getByRole("heading", { name: "Horas reservadas por proyecto" })).toBeVisible();
    await expect(page.getByRole("columnheader", { name: "Ocupación" })).toHaveCount(0);
  });

  test("solicitudes: una columna por estado y sin gráfico", async ({ page }) => {
    await page.goto("/reportes/solicitudes");
    await consultar(page);
    await expect(page.getByRole("columnheader", { name: "En ejecución" })).toBeVisible();
    await expect(page.locator(".recharts-surface")).toHaveCount(0);
  });

  test("lista de espera exige periodo y muestra el mensaje del servidor si falta", async ({ page }) => {
    await page.goto("/reportes/lista-espera");
    await page.getByLabel("Desde").fill("");
    await page.getByLabel("Hasta").fill("");
    await page.getByRole("button", { name: "Consultar" }).click();
    await expect(page.locator("p[role=alert]")).toBeVisible();
    await consultar(page);
    await expect(page.getByRole("heading", { name: /Reportes · Lista de espera/ })).toBeVisible();
    await expect(page.locator("p[role=alert]")).toHaveCount(0);
  });
});

test.describe("usuario sin permiso", () => {
  test.use({ storageState: "e2e/.auth/usuario.json" });

  test("si llega por otra vía, la denegación aparece en la misma pantalla", async ({ page }) => {
    await page.goto("/reportes/solicitudes");
    await page.getByRole("button", { name: "Consultar" }).click();
    await expect(page.locator("p[role=alert]")).toHaveText("No tienes acceso a los reportes.");
  });
});
