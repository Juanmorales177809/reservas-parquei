import { expect, test } from "@playwright/test";
import { ADMIN } from "./cuentas";
import { entrar } from "./ayudas";

test("sin sesión, una ruta protegida lleva a login", async ({ page }) => {
  await page.goto("/reservas");
  await expect(page).toHaveURL(/\/login/);
});

test("contraseña incorrecta muestra error y no entra", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Correo electrónico").fill(ADMIN.correo);
  await page.getByLabel("Contraseña").fill("una contraseña equivocada");
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await expect(page).toHaveURL(/\/login/);
  await expect(page.getByRole("alert").or(page.getByRole("status")).filter({ hasText: /.+/ }).first()).toBeVisible();
});

// Un solo inicio de sesión para las dos comprobaciones: el backend limita a 5 intentos por cuenta cada 15 min.
test("credenciales correctas entran a /inicio y la sesión viaja en cookie HttpOnly, no en localStorage", async ({ page, context }) => {
  await entrar(page, ADMIN);
  await expect(page).toHaveURL(/\/inicio/);
  const acceso = (await context.cookies()).find((c) => c.name === "rp_access");
  expect(acceso?.httpOnly).toBe(true);
  const guardado = await page.evaluate(() => JSON.stringify({ ...localStorage }));
  expect(guardado).not.toMatch(/eyJ/); // ningún JWT en localStorage
});
