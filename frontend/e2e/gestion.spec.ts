import { expect, test } from "@playwright/test";

// FE-29: los formularios de gestión cubren lo que piden las reglas. Cada prueba deja los datos como estaban
// (o con nombres únicos) para poder repetirse.
test.use({ storageState: "e2e/.auth/admin.json" });
const sufijo = () => String(Date.now()).slice(-7);

test("un equipo existente se edita: apoyo, operatividad y serial (RN-EQP-08, RN-EQP-09); no se registra desde aquí", async ({ page }) => {
  await page.goto("/recursos");
  // Los equipos vienen de LIA: el registro solo ofrece mobiliario y otros.
  await page.getByRole("button", { name: "Registrar recurso" }).click();
  await expect(page.getByLabel("Tipo", { exact: true }).locator("option")).toHaveText(["Mobiliario", "Otro"]);
  await page.keyboard.press("Escape");

  await page.getByRole("button", { name: "Equipos" }).click();
  await page.getByLabel("Buscar por nombre o placa").fill("Osciloscopio");
  await page.getByRole("list", { name: "Recursos" }).getByRole("link").first().click();
  await expect(page.getByRole("heading", { name: /Osciloscopio/ })).toBeVisible();
  await page.getByRole("checkbox", { name: /Exige acompañamiento técnico/ }).check();
  await page.getByLabel("Serial").fill(`SN-${sufijo()}`);
  await page.getByRole("checkbox", { name: /^Operativo/ }).check();
  await page.getByRole("button", { name: "Guardar datos" }).click();
  await expect(page.getByText("Recurso actualizado.")).toBeVisible();
  await expect(page.getByRole("checkbox", { name: /Exige acompañamiento técnico/ })).toBeChecked();
});

test("la configuración del laboratorio se ve y se guarda completa (RN-LAB-03, RN-LAB-04, RN-LAB-07)", async ({ page }) => {
  await page.goto("/administracion/unidades");
  await page.getByRole("listitem").filter({ hasText: "Laboratorio de Redes" }).getByRole("link", { name: "Configurar" }).click();
  await expect(page.getByRole("heading", { name: "Laboratorio Laboratorio de Redes" })).toBeVisible();
  await expect(page.getByText(/Lunes, Martes, Miércoles, Jueves, Viernes/)).toBeVisible();

  await page.getByRole("checkbox", { name: /Enviar avisos por correo/ }).check();
  await page.getByLabel("Recordatorio (horas antes)").fill("12");
  await page.getByRole("button", { name: "Guardar configuración" }).click();
  await expect(page.getByText("Configuración guardada.")).toBeVisible();
  await expect(page.getByText("12 h antes")).toBeVisible();
  await expect(page.getByText("Avisos por correo:").locator("..")).toContainText("sí");

  // Se deja como estaba.
  await page.getByRole("checkbox", { name: /Enviar avisos por correo/ }).uncheck();
  await page.getByLabel("Recordatorio (horas antes)").fill("24");
  await page.getByRole("button", { name: "Guardar configuración" }).click();
  await expect(page.getByText("24 h antes")).toBeVisible();
});

test("un espacio se edita y sus campos adicionales se administran (RN-ESP-01, RN-ESP-CAM-02)", async ({ page }) => {
  await page.goto("/espacios");
  await page.getByRole("link", { name: "Sala de Redes" }).click();
  await expect(page.getByRole("heading", { name: "Sala de Redes" })).toBeVisible();

  const ubicacion = `Bloque E2E ${sufijo()}`;
  await page.getByLabel("Ubicación").fill(ubicacion);
  await page.getByRole("button", { name: "Guardar datos" }).click();
  await expect(page.getByText("Datos del espacio actualizados.")).toBeVisible();
  await expect(page.getByText(new RegExp(ubicacion))).toBeVisible();

  // Campo nuevo, obligatorio; se marca opcional y se deshabilita para no afectar otras pruebas.
  const campo = `Temporal ${sufijo()}`;
  await page.getByLabel("Nombre", { exact: true }).last().fill(campo);
  await page.getByRole("checkbox", { name: "Obligatorio al reservar" }).check();
  await page.getByRole("button", { name: "Agregar campo", exact: true }).click();
  await expect(page.getByText("Campo creado.")).toBeVisible();
  const fila = page.getByRole("listitem").filter({ has: page.locator(`input[value="${campo}"]`) });
  await expect(fila.getByRole("checkbox", { name: "Obligatorio" })).toBeChecked();
  // Casilla controlada por el servidor: cambia cuando la operación termina, no al pulsarla.
  await fila.getByRole("checkbox", { name: "Obligatorio" }).click();
  await expect(page.getByText("El campo ahora es opcional.")).toBeVisible();
  await expect(fila.getByRole("checkbox", { name: "Obligatorio" })).not.toBeChecked();
  await fila.getByRole("button", { name: "Deshabilitar" }).click();
  await expect(fila.getByRole("button", { name: "Habilitar" })).toBeVisible();
});

test("las personas se consultan y se editan; el correo de quien tiene cuenta no cambia", async ({ page }) => {
  await page.goto("/administracion/personas");
  await page.getByLabel("Buscar por nombre, documento o correo").fill("usuario-e2e");
  const fila = page.getByRole("listitem").filter({ hasText: "usuario-e2e@itm.edu.co" });
  await expect(fila).toContainText("con cuenta");
  await fila.getByRole("button", { name: "Editar" }).click();
  const formulario = page.getByRole("form", { name: "Editar persona" });
  await expect(formulario.getByLabel("Correo")).toBeDisabled();
  await formulario.getByLabel("Dependencia").fill("Facultad E2E");
  await formulario.getByRole("button", { name: "Guardar cambios" }).click();
  await expect(page.getByText("Datos actualizados.")).toBeVisible();
  await expect(fila).toContainText("Facultad E2E");
  // Se deja como estaba.
  await fila.getByRole("button", { name: "Editar" }).click();
  await formulario.getByLabel("Dependencia").fill("Facultad");
  await formulario.getByRole("button", { name: "Guardar cambios" }).click();
  await expect(fila).toContainText("· Facultad ·");
});

test("un espacio se registra con sus equipos asociados en el mismo paso (FE-38)", async ({ page }) => {
  const nombre = `Sala E2E ${sufijo()}`;
  await page.goto("/espacios");
  await page.getByRole("button", { name: "Registrar espacio" }).click();
  await page.getByLabel("Laboratorio", { exact: true }).selectOption({ label: "Laboratorio de sistemas de Control y Robotica" });
  await page.getByLabel("Nombre", { exact: true }).fill(nombre);
  await page.getByLabel("Capacidad", { exact: true }).fill("6");
  // Los equipos de LIA ya cargados en ese laboratorio se ofrecen como fichas.
  await page.getByRole("checkbox", { name: "Cámara Climática Constante · Equipo" }).check();
  await page.getByRole("button", { name: "Guardar espacio" }).click();
  await expect(page.getByText("Espacio creado.")).toBeVisible();

  await page.getByRole("link", { name: new RegExp(nombre) }).click();
  const fila = page.getByRole("listitem").filter({ hasText: "Cámara Climática Constante" });
  await expect(fila).toBeVisible();
  // Deja el equipo libre para repetir la prueba.
  await fila.getByRole("button", { name: "Retirar" }).click();
  await expect(page.getByRole("listitem").filter({ hasText: "Cámara Climática Constante" }).getByRole("button", { name: "Retirar" })).toHaveCount(0);
});
