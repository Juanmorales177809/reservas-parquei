import { expect, test } from "@playwright/test";
import { USUARIO } from "./cuentas";
import { entrar } from "./ayudas";

// FE-27: la sesión no muere cuando vence el acceso (15 minutos): se renueva con el refresco.
// Inicia sesión por su cuenta: la renovación rota el refresco y no debe invalidar el de otras pruebas.
test("con el acceso vencido, una acción del cliente renueva la sesión y continúa", async ({ page, context }) => {
  await entrar(page, USUARIO);
  await page.goto("/notificaciones");
  await expect(page.getByRole("heading", { name: "Notificaciones" })).toBeVisible();

  await context.clearCookies({ name: "rp_access" }); // el acceso venció
  expect((await context.cookies()).some((c) => c.name === "rp_access")).toBe(false);

  const [renovacion, lecturaRepetida] = await Promise.all([
    page.waitForResponse((r) => r.url().endsWith("/api/auth/sesiones/renovacion")),
    page.waitForResponse((r) => r.url().includes("/api/notificaciones?") && r.status() === 200),
    page.getByLabel("Estado").selectOption("false"), // GET /api/notificaciones?leida=false vence y se repite
  ]);
  expect(renovacion.status()).toBe(200);
  expect(lecturaRepetida.status()).toBe(200);
  await expect(page).toHaveURL(/\/notificaciones/);
  expect((await context.cookies()).some((c) => c.name === "rp_access")).toBe(true);
});
