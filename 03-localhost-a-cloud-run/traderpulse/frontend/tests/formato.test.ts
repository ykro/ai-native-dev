import { describe, expect, it } from "vitest";
import { cambio, precio, puntosSparkline } from "../src/lib/formato";

describe("formato", () => {
  it("muestra el signo del cambio", () => {
    expect(cambio(1.234)).toBe("+1.23 %");
    expect(cambio(-0.5)).toBe("-0.50 %");
  });
  it("formatea dólares", () => {
    expect(precio(176.2)).toContain("176.20");
  });
  it("escala la serie al alto del SVG", () => {
    expect(puntosSparkline([10, 20, 15], 100, 10)).toBe("0.0,10.0 50.0,0.0 100.0,5.0");
    expect(puntosSparkline([5])).toBe("");
  });
});
