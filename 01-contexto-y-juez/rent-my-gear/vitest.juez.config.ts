import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

// The judge lives outside src/ so the normal suite never runs it by accident.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.tsx"],
    include: ["juez/**/*.juez.test.{ts,tsx}"],
    testTimeout: 20000,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
