import { defineConfig } from '@playwright/test';

// Credenciales FICTICIAS exclusivas para las pruebas E2E locales.
// Nunca usar en desarrollo ni producción.
const BACKEND_URL = 'http://localhost:8000';
const DATABASE_URL = 'postgresql://postgres:postgres@localhost:5433/reservas_test';
const SECRET_KEY = 'clave-e2e-solo-proceso-minimo-32-caracteres';
const ADMIN_USERNAME = 'e2e-admin';
const ADMIN_EMAIL = 'e2e-admin@test.com';
const ADMIN_PASSWORD = 'E2e-Admin-123!';

export default defineConfig({
  testDir: './e2e/tests',
  outputDir: './test-results',
  timeout: 30_000,
  expect: { timeout: 10_000 },
  retries: process.env.CI ? 2 : 1,
  // Base de pruebas compartida: ejecución secuencial determinista.
  workers: 1,
  reporter: [
    ['list'],
    ['html', { open: 'never' }],
  ],
  globalSetup: './e2e/global-setup.ts',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'off',
  },
  projects: [
    { name: 'anonimo', use: { storageState: { cookies: [], origins: [] } } },
    { name: 'usuario', use: { storageState: './e2e/.auth/usuario.json' } },
    { name: 'gestor', use: { storageState: './e2e/.auth/gestor.json' } },
    { name: 'admin', use: { storageState: './e2e/.auth/admin.json' } },
  ],
  // Local (Windows, sin CI): Playwright arranca backend y frontend, igual
  // que siempre. El comando del backend usa el intérprete del venv de
  // Windows y por eso solo tiene sentido fuera de CI.
  //
  // CI (Ubuntu, process.env.CI definido por GitHub Actions): el workflow
  // arranca el backend explícitamente en un paso previo (Python del
  // runner, sin depender de un .venv con ruta fija de Windows) y espera
  // su /health antes de invocar Playwright. Aquí Playwright solo arranca
  // y espera el frontend.
  webServer: process.env.CI
    ? [
        {
          // El workflow de CI arranca el frontend (`npm run dev`) como paso
          // explícito y espera http://127.0.0.1:3000 antes de invocar
          // Playwright. `reuseExistingServer: true` (fijo, no
          // `!process.env.CI`) es intencional aquí: si se dejara en
          // `false`, Playwright fallaría de inmediato con "already used,
          // set reuseExistingServer:true" al encontrar el puerto 3000 ya
          // ocupado por el proceso que arrancó el workflow. El comando se
          // deja como respaldo por si este entry se usara sin ese paso
          // previo, pero en el flujo de CI normal no se llega a invocar.
          command: 'npm run dev',
          url: 'http://localhost:3000',
          reuseExistingServer: true,
          timeout: 120_000,
          env: { BACKEND_URL },
        },
      ]
    : [
        {
          command:
            '..\\backend\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000',
          cwd: '../backend',
          url: 'http://localhost:8000/health',
          reuseExistingServer: !process.env.CI,
          timeout: 120_000,
          env: {
            DATABASE_URL,
            SECRET_KEY,
            INITIAL_ADMIN_USERNAME: ADMIN_USERNAME,
            INITIAL_ADMIN_EMAIL: ADMIN_EMAIL,
            INITIAL_ADMIN_PASSWORD: ADMIN_PASSWORD,
          },
        },
        {
          command: 'npm run dev',
          url: 'http://localhost:3000',
          reuseExistingServer: !process.env.CI,
          timeout: 120_000,
          env: { BACKEND_URL },
        },
      ],
});
