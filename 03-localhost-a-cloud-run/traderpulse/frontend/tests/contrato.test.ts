import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

// El tipo del panel sale del contrato; si el BFF cambia un campo, tsc falla aquí y en la página.
import type { components } from "../src/lib/api-schema";

type Cotizacion = components["schemas"]["Cotizacion"];

describe("contrato compartido", () => {
  it("los números viajan como números", () => {
    const c: Cotizacion = {
      simbolo: "NVDA",
      nombre: "NVIDIA",
      precio: 176.2,
      cambio_pct: 1.5,
      volumen: 10,
      fecha: "2026-10-30",
    };
    expect(typeof c.precio).toBe("number");
  });
  it("los tipos se generaron desde el contrato publicado", () => {
    const contrato = JSON.parse(readFileSync("../contrato/openapi.json", "utf8"));
    const tipos = readFileSync("src/lib/api-schema.d.ts", "utf8");
    for (const nombre of Object.keys(contrato.components.schemas)) {
      expect(tipos).toContain(`${nombre}: {`);
    }
  });
});
