import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e/tests',
  timeout: 30 * 1000,
  expect: { timeout: 5000 },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 2 : 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://127.0.0.1:8090',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: process.env.CI
    ? undefined
    : [
        {
          command: 'python -m uvicorn app.main:app --host 127.0.0.1 --port 8000',
          cwd: '../backend',
          url: 'http://127.0.0.1:8000/health',
          timeout: 30 * 1000,
          reuseExistingServer: true,
          env: {
            DATABASE_URL: process.env.TEST_DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/reservas_test',
            SECRET_KEY: process.env.TEST_SECRET_KEY || 'clave-ci-solo-proceso-minimo-32-caracteres',
          },
        },
      ],
});
