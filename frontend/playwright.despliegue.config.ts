import { defineConfig } from "@playwright/test";

/**
 * Configuración de la prueba de humo de un despliegue nuevo (e2e/flujo-despliegue.spec.ts). No usa la
 * preparación de la suite normal, que exige las cuentas sembradas en la copia de pruebas: aquí las cuentas las
 * pasa quien la corre, por variables de entorno.
 */
export default defineConfig({
  testDir: "./e2e",
  testMatch: /flujo-despliegue\.spec\.ts/,
  workers: 1,
  timeout: 60_000,
  reporter: [["list"]],
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3000",
    channel: process.env.E2E_CHANNEL ?? "msedge",
    launchOptions: { slowMo: Number(process.env.E2E_SLOWMO ?? 0) },
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
});
