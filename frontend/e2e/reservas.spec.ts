import { expect, test } from "@playwright/test";

// FE-28: el listado y el detalle muestran nombres, no identificadores.
test.use({ storageState: "e2e/.auth/admin.json" });

test("el listado muestra cuándo, qué, dónde y quién, y filtra por estado y tipo", async ({ page }) => {
  await page.goto("/reservas");
  const lista = page.getByRole("list", { name: "Reservas" });
  await expect(lista).toBeVisible();
  const filas = lista.getByRole("listitem");
  expect(await filas.count()).toBeGreaterThan(0);
  await expect(filas.first()).toContainText("Laboratorio de Redes");
  await expect(filas.first()).toContainText(/Admin E2E|Usuario E2E/);
  await expect(filas.first()).not.toContainText(/#\d+/);

  // Filtro por tipo: todas las filas visibles son de ese tipo.
  await page.getByLabel("Tipo").selectOption({ label: "Lista de espera" });
  await expect(async () => {
    const textos = await filas.allTextContents();
    expect(textos.length).toBeGreaterThan(0);
    for (const t of textos) expect(t).toContain("Lista de espera");
  }).toPass();
});

test("el detalle muestra unidad, solicitante, espacio y recursos por su nombre", async ({ page }) => {
  await page.goto("/reservas");
  await page.getByLabel("Tipo").selectOption({ label: "Espacio" });
  await page.getByRole("link", { name: "Ver reserva" }).first().click();
  await expect(page).toHaveURL(/\/reservas\/\d+$/);
  await expect(page.getByText("Laboratorio de Redes").first()).toBeVisible();
  await expect(page.getByText(/Admin E2E|Usuario E2E/).first()).toBeVisible(); // quien haya creado la primera
  await expect(page.getByText("Sala de Redes")).toBeVisible();
  await expect(page.getByText(/Recurso \d+/)).toHaveCount(0);
});

test("una solicitud pendiente se edita: descripción, observación y contexto (FE-31, RN-PRO-06)", async ({ page }) => {
  await page.goto("/reservas/nueva");
  await page.getByLabel("Laboratorio", { exact: true }).selectOption({ label: "Laboratorio de Redes" });
  await page.getByLabel("Tipo", { exact: true }).selectOption({ label: "Lista de espera" });
  await page.getByLabel("Descripción de la necesidad").fill("Soporte para sensor");
  await page.getByLabel("Proyecto", { exact: true }).selectOption({ label: "Proyecto E2E (E2E-1)" });
  await page.getByRole("button", { name: "Guardar solicitud" }).click();
  await expect(page).toHaveURL(/\/reservas\/\d+$/);

  await page.getByRole("button", { name: "Editar solicitud" }).click();
  const formulario = page.getByRole("form", { name: "Editar solicitud" });
  await expect(formulario.getByLabel("Descripción de la necesidad")).toHaveValue("Soporte para sensor");
  await expect(formulario.getByLabel("Proyecto", { exact: true })).toHaveValue(/\d+/); // el contexto llega precargado
  await formulario.getByLabel("Descripción de la necesidad").fill("Soporte de aluminio para sensor");
  await formulario.getByLabel("Observación (opcional)").fill("Urgente");
  await formulario.getByRole("button", { name: "Guardar cambios" }).click();
  await expect(page.getByText("La solicitud se actualizó y sigue pendiente de aprobación.")).toBeVisible();
  await expect(page.getByText("Soporte de aluminio para sensor")).toBeVisible();
  await expect(page.getByText("Urgente")).toBeVisible();
  await expect(page.getByText("Lista de espera · Solicitada")).toBeVisible();
});

test("el filtro de fechas del listado usa la fecha de uso", async ({ page }) => {
  await page.goto("/reservas");
  await page.getByLabel("Desde (fecha de uso)").fill("2099-01-01");
  await expect(page.getByText("Sin reservas.")).toBeVisible();
  await page.getByLabel("Desde (fecha de uso)").fill("2020-01-01");
  await page.getByLabel("Hasta (fecha de uso)").fill("2019-01-01");
  await expect(page.getByText(/no puede ser posterior/)).toBeVisible();
});
