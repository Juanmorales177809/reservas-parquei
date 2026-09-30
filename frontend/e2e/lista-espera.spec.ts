import { expect, test } from "@playwright/test";

// Requiere el laboratorio «Laboratorio de Redes» con los tipos Lista de espera y Recurso interno
// habilitados, y el proyecto «Proyecto E2E»: ver e2e/README.md.
test.use({ storageState: "e2e/.auth/admin.json" });

// PNG válido de 1×1 píxel: el backend valida el contenido, no solo la extensión.
const PNG_1X1 = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
  "base64"
);

test("lista de espera: sin consulta de disponibilidad, con archivo adjunto que queda en la reserva", async ({ page }) => {
  await page.goto("/reservas/nueva");
  await page.getByLabel("Laboratorio", { exact: true }).selectOption({ label: "Laboratorio de Redes" });
  await page.getByLabel("Tipo").selectOption({ label: "Lista de espera" });
  await expect(page.getByRole("button", { name: "Consultar disponibilidad" })).toHaveCount(0);
  await page.getByLabel("Descripción de la necesidad").fill("Soporte a medida para sensor");
  await page.getByLabel("Archivos técnicos (opcional)").setInputFiles({
    name: "boceto.png",
    mimeType: "image/png",
    buffer: PNG_1X1,
  });
  await page.getByLabel("Proyecto").selectOption({ label: "Proyecto E2E (E2E-1)" });
  await page.getByRole("button", { name: "Guardar solicitud" }).click();

  await expect(page).toHaveURL(/\/reservas\/\d+$/);
  await expect(page.getByRole("heading", { name: "Adjuntos" })).toBeVisible();
  await expect(page.getByRole("link", { name: "boceto.png" })).toBeVisible();
});

test("un formato no admitido se rechaza antes de enviar", async ({ page }) => {
  await page.goto("/reservas/nueva");
  await page.getByLabel("Laboratorio", { exact: true }).selectOption({ label: "Laboratorio de Redes" });
  await page.getByLabel("Tipo").selectOption({ label: "Lista de espera" });
  await page.getByLabel("Archivos técnicos (opcional)").setInputFiles({
    name: "programa.exe",
    mimeType: "application/octet-stream",
    buffer: Buffer.from("MZ"),
  });
  await expect(page.getByText(/formato no admitido/)).toBeVisible();
});

/** Un día laboral futuro al azar: las reservas de prueba no deben chocar entre corridas. */
function fechaLaboralFutura(): string {
  for (;;) {
    const d = new Date(Date.now() + (30 + Math.floor(Math.random() * 300)) * 86_400_000);
    if (d.getUTCDay() >= 1 && d.getUTCDay() <= 5) return d.toISOString().slice(0, 10);
  }
}

test("una reserva puede llevar varios recursos: uno principal y los demás adicionales", async ({ page }) => {
  await page.goto("/reservas/nueva");
  await page.getByLabel("Laboratorio", { exact: true }).selectOption({ label: "Laboratorio de Redes" });
  await page.getByLabel("Tipo").selectOption({ label: "Recurso interno" });
  await page.getByLabel("Fecha").fill(fechaLaboralFutura());
  await page.getByLabel("Hora inicio").fill("09:00");
  await page.getByLabel("Hora fin").fill("11:00");
  await page.getByLabel("Recurso principal").selectOption({ label: "Silla E2E · Mobiliario" });

  // El principal no se repite entre los adicionales.
  await expect(page.getByRole("checkbox", { name: "Silla E2E · Mobiliario" })).toHaveCount(0);
  await page.getByRole("checkbox", { name: "Mesa de soldadura · Mobiliario" }).check();
  await page.getByRole("checkbox", { name: "Lupa de banco · Mobiliario" }).check();
  await page.getByLabel("Proyecto").selectOption({ label: "Proyecto E2E (E2E-1)" });
  await page.getByRole("button", { name: "Guardar solicitud" }).click();

  await expect(page).toHaveURL(/\/reservas\/\d+$/);
  await expect(page.getByText(/Silla E2E · principal/)).toHaveCount(1);
  await expect(page.getByText(/ · adicional/)).toHaveCount(2);
});

test("un espacio pide su información obligatoria y ofrece sus recursos asociados (RN-TIP-PE-12, RN-TIP-PE-18)", async ({ page }) => {
  await page.goto("/reservas/nueva");
  await page.getByLabel("Laboratorio", { exact: true }).selectOption({ label: "Laboratorio de Redes" });
  await page.getByLabel("Tipo").selectOption({ label: "Espacio" });
  await page.getByLabel("Espacio").selectOption({ label: "Sala de Redes (cap. 20)" });
  await page.getByLabel("Fecha").fill(fechaLaboralFutura());
  await page.getByLabel("Hora inicio").fill("14:00");
  await page.getByLabel("Hora fin").fill("16:00");

  // Recursos asociados al espacio, con su disponibilidad para ese horario.
  await expect(page.getByRole("checkbox", { name: /Mesa de soldadura/ })).toBeVisible();
  await expect(page.getByText("(disponible)").first()).toBeVisible();
  await page.getByRole("checkbox", { name: /Mesa de soldadura/ }).check();
  await page.getByLabel("Proyecto").selectOption({ label: "Proyecto E2E (E2E-1)" });

  // Sin el campo obligatorio no se envía; con él, sí.
  await page.getByRole("button", { name: "Guardar solicitud" }).click();
  await expect(page.getByText(/Completa la información que pide el espacio: Ensayo previsto/)).toBeVisible();
  await page.getByLabel("Ensayo previsto").fill("Tracción");
  await page.getByRole("button", { name: "Guardar solicitud" }).click();
  await expect(page).toHaveURL(/\/reservas\/\d+$/);
});
