/// <reference types="vitest/config" />

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    tsconfigPaths: true,
  },
  test: {
    environment: "jsdom",
    setupFiles: [
      "./src/test/setup.ts",
    ],
    clearMocks: true,
    mockReset: true,
    restoreMocks: true,
    coverage: {
      provider: "v8",
      reporter: [
        "text",
        "json-summary",
        "html",
      ],
      reportsDirectory: "./coverage",
      include: [
        "src/**/*.{ts,tsx}",
      ],
      exclude: [
        "src/**/*.d.ts",
        "src/main.tsx",
        "src/test/**",
      ],
    },
  },
});