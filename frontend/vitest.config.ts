import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  resolve: {
    // Igual que tsconfig.json: "@/*" -> "./*", relativo a frontend/.
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    globals: true,
    // e2e/ son pruebas de Playwright (npm run e2e), no de Vitest.
    exclude: ["node_modules/**", "e2e/**", ".next/**"],
  },
});
