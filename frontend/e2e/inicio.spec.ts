import { expect, test } from "@playwright/test";

// SCR-REP-04 contra el backend real. Se consulta un periodo amplio y se
// comprueba la forma de la pantalla, no cifras concretas.

test.describe("administrador", () => {
  test.use({ storageState: "e2e/.auth/admin.json" });

  test("al entrar ya muestra el mes en curso sin pulsar Consultar (FE-50)", async ({ page }) => {
    await page.goto("/inicio");
    const previo = new Date();
    previo.setDate(1);
    const esperado = `${previo.getFullYear()}-${String(previo.getMonth() + 1).padStart(2, "0")}-01`;
    await expect(page.getByLabel("Desde")).toHaveValue(esperado);
    await expect(page.getByRole("region", { name: "Resumen del periodo" })).toBeVisible();
    await expect(page.getByRole("region", { name: "Por estado" })).toBeVisible();
  });

  test("el inicio muestra indicadores, estados y mapa tras consultar", async ({ page }) => {
    await page.goto("/inicio");
    await expect(page.getByRole("heading", { name: "Inicio" })).toBeVisible();
    await page.getByLabel("Desde").fill("2020-01-01");
    await page.getByLabel("Hasta").fill("2030-12-31");
    await page.getByRole("button", { name: "Consultar" }).click();
    await expect(page.getByRole("region", { name: "Resumen del periodo" })).toBeVisible();
    await expect(page.getByRole("region", { name: "Por estado" })).toBeVisible();
    await expect(page.getByRole("region", { name: "Mapa de calor por día y hora" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Ocupación" })).toBeVisible();
  });

  test("el menú empieza en Inicio", async ({ page }) => {
    await page.goto("/reservas");
    const destinos = await page.locator("nav a").evaluateAll((as) =>
      as.map((a) => a.textContent!.trim())
    );
    expect(destinos[0]).toBe("Inicio");
  });
});

test.describe("usuario", () => {
  test.use({ storageState: "e2e/.auth/usuario.json" });

  test("ve accesos y no consulta ningún resumen", async ({ page }) => {
    await page.goto("/inicio");
    await expect(page.getByRole("heading", { name: "Inicio" })).toBeVisible();
    await expect(page.getByRole("link", { name: /Mis reservas/ })).toBeVisible();
    await expect(page.getByRole("button", { name: "Consultar" })).toHaveCount(0);
  });
});
