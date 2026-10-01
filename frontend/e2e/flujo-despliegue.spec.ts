import { expect, test, type Browser, type Page } from "@playwright/test";

/**
 * Prueba de humo de un DESPLIEGUE nuevo: el flujo completo, con tres personas distintas.
 *
 *   administrador  configura el laboratorio y registra un espacio con un equipo
 *   usuaria        pide la reserva
 *   técnico        la aprueba desde el listado (modal)
 *   usuaria        la ve aprobada
 *
 * No corre con la suite normal: necesita una base recién desplegada y cuentas que ella no trae. Se activa con
 *
 *   FLUJO_DESPLIEGUE=1 E2E_BASE_URL=http://localhost:3100 \
 *   FLUJO_ADMIN="correo:clave" FLUJO_TECNICO="correo:clave" FLUJO_USUARIA="correo:clave" \
 *   npx playwright test -c playwright.despliegue.config.ts
 *
 * El técnico debe ser personal cuyo cargo sea del laboratorio «Laboratorio de sistemas de Control y Robotica», y
 * la usuaria debe estar vinculada a un proyecto. Añada `--headed` y E2E_SLOWMO=400 para verlo.
 */
const ACTIVA = process.env.FLUJO_DESPLIEGUE === "1";
const cuenta = (variable: string) => {
  const [correo, ...resto] = (process.env[variable] ?? ":").split(":");
  return { correo, contrasena: resto.join(":") };
};

const LABORATORIO = "Laboratorio de sistemas de Control y Robotica";
const ESPACIO = `Sala de Robótica ${String(Date.now()).slice(-5)}`;

test.describe.configure({ mode: "serial" });
test.skip(!ACTIVA, "Se activa con FLUJO_DESPLIEGUE=1 contra una base recién desplegada.");

async function entrar(browser: Browser, quien: string): Promise<Page> {
  const { correo, contrasena } = cuenta(quien);
  const contexto = await browser.newContext();
  const page = await contexto.newPage();
  await page.goto("/login");
  await page.getByLabel("Correo electrónico").fill(correo);
  await page.getByLabel("Contraseña").fill(contrasena);
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await expect(page).not.toHaveURL(/\/login/);
  return page;
}

function diaHabil(): string {
  const d = new Date(Date.now() + 8 * 86_400_000);
  while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() + 1);
  return d.toISOString().slice(0, 10);
}

test("1. el administrador configura el laboratorio y registra un espacio con un equipo", async ({ browser }) => {
  const page = await entrar(browser, "FLUJO_ADMIN");

  await page.goto("/administracion/unidades");
  const fila = page.getByRole("listitem").filter({ hasText: LABORATORIO }).filter({ has: page.getByRole("link", { name: "Configurar" }) });
  await fila.getByRole("link", { name: "Configurar" }).click();
  await expect(page.getByRole("heading", { name: /^Laboratorio / })).toBeVisible();
  // Un laboratorio nuevo no trae horario: hay que fijarlo (lunes a viernes vienen marcados). Si ya está
  // configurado (la prueba se repite sobre la misma base), se sigue con lo que tiene.
  const sinConfigurar = page.getByRole("button", { name: "Configurar laboratorio" });
  await expect(page.getByRole("heading", { name: /^Laboratorio / })).toBeVisible();
  if (await sinConfigurar.waitFor({ timeout: 3000 }).then(() => true, () => false)) {
    await page.getByLabel("Apertura").fill("07:00");
    await page.getByLabel("Cierre").fill("19:00");
    await sinConfigurar.click();
  }
  await expect(page.getByText("Acepta reservas:")).toBeVisible();

  await page.getByRole("checkbox", { name: "Espacio", exact: true }).check();
  await page.getByRole("button", { name: "Guardar tipos" }).click();
  await expect(page.getByText(/Espacio/).first()).toBeVisible();

  await page.goto("/espacios");
  await page.getByRole("button", { name: "Registrar espacio" }).click();
  await page.getByLabel("Laboratorio", { exact: true }).selectOption({ label: LABORATORIO });
  await page.getByLabel("Nombre", { exact: true }).fill(ESPACIO);
  await page.getByLabel("Capacidad", { exact: true }).fill("12");
  await page.getByRole("checkbox", { name: "Pie de Rey · Equipo" }).check();
  await page.getByRole("button", { name: "Guardar espacio" }).click();
  // Un equipo solo puede estar en un espacio: si la prueba se repite sobre la misma base, el de la corrida
  // anterior sigue ocupado y el servidor lo explica; se guarda entonces sin él.
  const ocupado = await page.getByText(/ya está asociado a otro espacio/).waitFor({ timeout: 4000 }).then(() => true, () => false);
  if (ocupado) {
    await page.getByRole("checkbox", { name: "Pie de Rey · Equipo" }).uncheck();
    await page.getByRole("button", { name: "Guardar espacio" }).click();
  }
  await expect(page.getByText("Espacio creado.")).toBeVisible();
  await page.context().close();
});

test("2. la usuaria pide la reserva del espacio", async ({ browser }) => {
  const page = await entrar(browser, "FLUJO_USUARIA");
  await page.goto("/reservas/nueva");
  await page.getByLabel("Laboratorio", { exact: true }).selectOption({ label: LABORATORIO });
  await page.getByLabel("Espacio", { exact: true }).selectOption({ label: `${ESPACIO} (cap. 12)` });
  await page.getByLabel("Fecha").fill(diaHabil());
  await page.getByLabel("Hora inicio").fill("10:00");
  await page.getByLabel("Hora fin").fill("11:00");
  // Su única vinculación llega elegida; el recurso del espacio se ofrece como ficha.
  await expect(page.getByLabel("Proyecto", { exact: true })).toHaveValue(/\d+/);
  await page.getByRole("button", { name: "Guardar solicitud" }).click();

  await expect(page).toHaveURL(/\/reservas\/\d+$/);
  await expect(page.getByRole("heading", { name: /Reserva #\d+/ })).toBeVisible();
  await expect(page.getByText("Espacio · Solicitada")).toBeVisible();
  await page.context().close();
});

test("3. el técnico del laboratorio la aprueba desde el listado, en un modal", async ({ browser }) => {
  const page = await entrar(browser, "FLUJO_TECNICO");
  await page.goto("/reservas");
  await page.getByRole("button", { name: "Solicitadas" }).click();
  const tarjeta = page.getByRole("listitem").filter({ hasText: ESPACIO }).first();
  await expect(tarjeta).toBeVisible();
  await tarjeta.getByRole("button", { name: "Aprobar" }).click();

  const dialogo = page.getByRole("dialog");
  await expect(dialogo.getByRole("heading", { name: "Revisión" })).toBeVisible();
  await dialogo.getByRole("button", { name: "Aprobar" }).click();
  await expect(dialogo.getByText("Reserva aprobada.")).toBeVisible();
  await page.keyboard.press("Escape");
  // Ya no está entre las solicitadas: pasó a aprobadas, y el listado se actualizó sin recargar la página.
  await expect(page.getByRole("listitem").filter({ hasText: ESPACIO })).toHaveCount(0);
  await page.getByRole("button", { name: "Aprobadas" }).click();
  await expect(page.getByRole("listitem").filter({ hasText: ESPACIO }).first()).toContainText("Aprobada");
  await page.context().close();
});

test("4. la usuaria ve su reserva aprobada y puede agregarla a su calendario", async ({ browser }) => {
  const page = await entrar(browser, "FLUJO_USUARIA");
  await page.goto("/reservas");
  const tarjeta = page.getByRole("listitem").filter({ hasText: ESPACIO }).first();
  await expect(tarjeta).toContainText("Aprobada");
  await tarjeta.getByRole("link").first().click();
  await expect(page.getByRole("heading", { name: /Reserva #\d+/ })).toBeVisible();
  await expect(page.getByText("Agregar al calendario (.ics)")).toBeVisible();
  await page.context().close();
});
