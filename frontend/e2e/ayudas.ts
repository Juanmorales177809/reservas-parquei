import { expect, type Page } from "@playwright/test";

export async function entrar(page: Page, cuenta: { correo: string; contrasena: string }) {
  await page.goto("/login");
  await page.getByLabel("Correo electrónico").fill(cuenta.correo);
  await page.getByLabel("Contraseña").fill(cuenta.contrasena);
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await expect(page).toHaveURL(/\/(inicio|usuarios\/perfil)/);
}

/** Recoge lo que una pantalla sana no debe producir. */
export function vigilar(page: Page) {
  const problemas: string[] = [];
  page.on("pageerror", (e) => problemas.push(`pageerror: ${e.message}`));
  page.on("response", (r) => {
    if (r.url().includes("/api/") && r.status() >= 500) problemas.push(`${r.status()} ${r.request().method()} ${r.url()}`);
  });
  return problemas;
}
