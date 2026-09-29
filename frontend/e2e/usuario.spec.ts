import { expect, test } from "@playwright/test";

// Un usuario común (sin permisos administrativos) reserva y edita su solicitud. Antes solo se probaba con el
// administrador y quedó sin ver que un usuario ni siquiera podía cargar la lista de unidades.
test.use({ storageState: "e2e/.auth/usuario.json" });

function diaLaboralFuturo(): string {
  for (;;) {
    const d = new Date(Date.now() + (40 + Math.floor(Math.random() * 300)) * 86_400_000);
    if (d.getUTCDay() >= 1 && d.getUTCDay() <= 5) return d.toISOString().slice(0, 10);
  }
}

test("un usuario elige el laboratorio por nombre, reserva un espacio y edita su solicitud", async ({ page }) => {
  await page.goto("/reservas/nueva");
  await page.getByLabel("Unidad", { exact: true }).selectOption({ label: "Laboratorio de Redes" });
  await page.getByLabel("Tipo", { exact: true }).selectOption({ label: "Espacio" });
  await page.getByLabel("Espacio", { exact: true }).selectOption({ label: "Sala de Redes (cap. 20)" });
  await page.getByLabel("Fecha").fill(diaLaboralFuturo());
  const hora = 8 + Math.floor(Math.random() * 8);
  await page.getByLabel("Hora inicio").fill(`${String(hora).padStart(2, "0")}:00`);
  await page.getByLabel("Hora fin").fill(`${String(hora + 1).padStart(2, "0")}:00`);
  await page.getByLabel("Ensayo previsto").fill("Tracción");
  // Su única vinculación llega preseleccionada (RN-TIP-PE-08).
  await expect(page.getByLabel("Proyecto", { exact: true })).toHaveValue(/\d+/);
  await page.getByRole("button", { name: "Guardar solicitud" }).click();

  await expect(page).toHaveURL(/\/reservas\/\d+$/);
  await expect(page.getByText("Espacio · Solicitada")).toBeVisible();
  await expect(page.getByText("Usuario E2E").first()).toBeVisible();

  // Sin acciones de gestión: no es técnico.
  await expect(page.getByRole("button", { name: "Aprobar" })).toHaveCount(0);

  await page.getByRole("button", { name: "Editar solicitud" }).click();
  const formulario = page.getByRole("form", { name: "Editar solicitud" });
  await expect(formulario.getByLabel("Ensayo previsto")).toHaveValue("Tracción");
  await formulario.getByLabel("Ensayo previsto").fill("Compresión");
  await formulario.getByLabel("Observación (opcional)").fill("Cambio de ensayo");
  await formulario.getByRole("button", { name: "Guardar cambios" }).click();
  await expect(page.getByText("La solicitud se actualizó y sigue pendiente de aprobación.")).toBeVisible();
  await expect(page.getByText("Compresión")).toBeVisible();

  // Aparece en su propio listado, con nombres.
  await page.goto("/reservas");
  await expect(page.getByRole("table").locator("tbody tr").first()).toContainText("Sala de Redes");
});
