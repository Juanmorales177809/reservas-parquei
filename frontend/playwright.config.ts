import { defineConfig } from "@playwright/test";

/**
 * Pruebas de extremo a extremo contra el backend real. Esperan la aplicación en
 * E2E_BASE_URL (por defecto http://localhost:3000; el frontend reenvía /api al
 * backend) y las cuentas sembradas de e2e/cuentas.ts. Usan el Edge/Chrome del
 * sistema para no depender de una descarga: E2E_CHANNEL lo cambia.
 */
export default defineConfig({
  testDir: "./e2e",
  workers: 1,
  timeout: 30_000,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3000",
    channel: process.env.E2E_CHANNEL ?? "msedge",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "preparacion", testMatch: /preparacion\.setup\.ts/ },
    { name: "e2e", testIgnore: /preparacion\.setup\.ts/, dependencies: ["preparacion"] },
  ],
});
