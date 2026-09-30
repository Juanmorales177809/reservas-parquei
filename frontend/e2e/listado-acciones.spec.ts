import { expect, test } from "@playwright/test";

// FE-33: las acciones de cada reserva se resuelven en un modal, sin salir del listado.
test.use({ storageState: "e2e/.auth/admin.json" });

test("rechazar una solicitud desde el listado, en un modal, y ver el listado actualizado", async ({ page }) => {
  await page.goto("/reservas");
  await page.getByRole("button", { name: "Solicitadas" }).click();
  const lista = page.getByRole("list", { name: "Reservas" });
  const tarjeta = lista.getByRole("listitem").filter({ has: page.getByRole("button", { name: "Rechazar" }) }).first();
  await expect(tarjeta).toBeVisible();
  const href = await tarjeta.getByRole("link").first().getAttribute("href");

  await tarjeta.getByRole("button", { name: "Rechazar" }).click();
  const dialogo = page.getByRole("dialog");
  await expect(dialogo).toBeVisible();
  // Solo la parte de la acción elegida, no toda la página de la reserva.
  await expect(dialogo.getByRole("heading", { name: "Revisión" })).toBeVisible();
  await expect(dialogo.getByRole("heading", { name: "Historial" })).toHaveCount(0);

  await dialogo.getByLabel("Motivo del rechazo").fill("Prueba desde el listado");
  await dialogo.getByRole("button", { name: "Rechazar" }).click();
  await expect(dialogo.getByText("Reserva rechazada.")).toBeVisible();

  await page.keyboard.press("Escape");
  await expect(dialogo).toBeHidden();
  // La solicitud ya no está entre las «Solicitadas» y el listado no se recargó desde cero.
  await expect(lista.locator(`a[href="${href}"]`)).toHaveCount(0);
  await expect(page).toHaveURL(/\/reservas$/);
});

test("el detalle abre en un modal con «Ver detalle» y enlaza a la página completa", async ({ page }) => {
  await page.goto("/reservas");
  const primera = page.getByRole("list", { name: "Reservas" }).getByRole("listitem").first();
  await primera.getByRole("button", { name: "Ver detalle" }).click();
  const dialogo = page.getByRole("dialog");
  await expect(dialogo.getByRole("heading", { name: "Historial" })).toBeVisible();
  await dialogo.getByRole("link", { name: /página completa/ }).click();
  await expect(page).toHaveURL(/\/reservas\/\d+$/);
});
