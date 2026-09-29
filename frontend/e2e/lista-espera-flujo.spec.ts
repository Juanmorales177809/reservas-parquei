import { expect, test } from "@playwright/test";

// FE-26: la lista de espera se puede recorrer entera. La cuenta de administrador es a la vez la
// reservista y quien gestiona la unidad, así que ve las dos caras del flujo.
test.use({ storageState: "e2e/.auth/admin.json" });

test("lista de espera: viabilidad, formulario por partes, aprobación con recepción, ejecución y horas", async ({ page }) => {
  await page.goto("/reservas/nueva");
  await page.getByLabel("Unidad").selectOption({ label: "Laboratorio de Redes" });
  await page.getByLabel("Tipo").selectOption({ label: "Lista de espera" });
  await page.getByLabel("Descripción de la necesidad").fill("Soporte mecanizado para un sensor");
  await page.getByLabel("Proyecto").selectOption({ label: "Proyecto E2E (E2E-1)" });
  await page.getByRole("button", { name: "Guardar solicitud" }).click();
  await expect(page).toHaveURL(/\/reservas\/\d+$/);

  // Aprobar antes de tiempo: el botón está bloqueado y dice qué falta.
  await expect(page.getByRole("button", { name: "Registrar recepción y aprobar" })).toBeDisabled();
  await expect(page.getByText(/Falta: la viabilidad positiva/)).toBeVisible();

  await page.getByRole("button", { name: "Es viable", exact: true }).click();
  await expect(page.getByText(/^Viable · evaluada el/)).toBeVisible();

  // Parte del reservista.
  await page.getByLabel("Campo").first().fill("Material");
  await page.getByLabel("Valor").first().fill("Aluminio 6061");
  await page.getByRole("button", { name: "Guardar parte del reservista" }).click();
  await expect(page.getByText("Tu parte del formulario quedó guardada.")).toBeVisible();

  // Parte técnica (requiere la del reservista).
  await page.getByLabel("Campo").last().fill("Proceso");
  await page.getByLabel("Valor").last().fill("Corte CNC");
  await page.getByRole("button", { name: "Guardar parte técnica" }).click();
  await expect(page.getByText("La parte técnica quedó guardada.")).toBeVisible();
  await expect(page.getByText(/Revisado por el técnico el/)).toBeVisible();

  // Aprobación con confirmación de la recepción del material.
  const aprobar = page.getByRole("button", { name: "Registrar recepción y aprobar" });
  await expect(aprobar).toBeDisabled();
  await page.getByRole("checkbox", { name: "Confirmo que el material fue recibido" }).check();
  await aprobar.click();
  await expect(page.getByText("Reserva aprobada y material recibido.")).toBeVisible();
  await expect(page.getByText("Lista de espera · Aprobada")).toBeVisible();

  // Ejecución y cierre con horas.
  await page.getByRole("button", { name: "Iniciar fabricación o prestación" }).click();
  await expect(page.getByText("Lista de espera · En ejecución")).toBeVisible();
  await page.getByLabel("Horas de ejecución").fill("3.5");
  await page.getByRole("button", { name: "Finalizar", exact: true }).click();
  await expect(page.getByText("Lista de espera · Finalizada")).toBeVisible();
  await expect(page.getByText("Horas de ejecución registradas: 3.5.")).toBeVisible();
});
