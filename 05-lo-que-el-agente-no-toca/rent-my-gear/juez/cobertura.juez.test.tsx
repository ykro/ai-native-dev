/**
 * Juez de la cobertura por daños (Judge-First).
 *
 * Se escribió antes que el código. Hoy falla; el cambio está terminado cuando pasa
 * sin tocar este archivo. Mira el sistema desde afuera: el endpoint POST /api/rental
 * y el resumen de precio que ve quien renta.
 *
 * Contrato que fija:
 *   - fotografia-video paga 20 % de cobertura; montana-camping y deportes-acuaticos, 10 %.
 *   - La cobertura se calcula sobre el subtotal en centavos enteros y se redondea al centavo,
 *     con las mitades hacia arriba.
 *   - El total es subtotal + cobertura, exacto a dos decimales.
 *   - El servidor ignora cualquier precio que mande el navegador.
 *   - La pantalla muestra la cobertura y el mismo total que confirma el servidor.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import type { GearItem } from "@/lib/validation";

const FIXTURES: Record<string, GearItem> = {
  "juez-foto": {
    id: "juez-foto",
    name: "Cámara de prueba",
    category: "fotografia-video",
    description: "Equipo ficticio del juez",
    specs: {},
    dailyRate: 150,
    imageURL: null,
  },
  "juez-montana": {
    id: "juez-montana",
    name: "Tienda de prueba",
    category: "montana-camping",
    description: "Equipo ficticio del juez",
    specs: {},
    dailyRate: 33.35,
    imageURL: null,
  },
  "juez-agua": {
    id: "juez-agua",
    name: "Kayak de prueba",
    category: "deportes-acuaticos",
    description: "Equipo ficticio del juez",
    specs: {},
    dailyRate: 89.95,
    imageURL: null,
  },
};

vi.mock("@/services/inventoryService", () => ({
  getGearById: async (id: string) => FIXTURES[id] ?? null,
}));

// Three inclusive days, far enough in the future to never be "in the past".
const START = "2030-03-01T00:00:00.000Z";
const END = "2030-03-03T00:00:00.000Z";

type Quote = {
  subtotal: number;
  coverageRate: number;
  coverageFee: number;
  totalPrice: number;
};

async function postRental(body: Record<string, unknown>): Promise<{ status: number; json: Quote }> {
  const { POST } = await import("@/app/api/rental/route");
  const { NextRequest } = await import("next/server");
  const req = new NextRequest("http://localhost/api/rental", {
    method: "POST",
    body: JSON.stringify(body),
    headers: { "content-type": "application/json" },
  });
  const res = await POST(req);
  return { status: res.status, json: (await res.json()) as Quote };
}

describe("Juez · cobertura por daños", () => {
  beforeEach(() => {
    vi.spyOn(console, "log").mockImplementation(() => {});
  });

  it("fotografía y video paga 20 % sobre el subtotal", async () => {
    const { status, json } = await postRental({ gearId: "juez-foto", startDate: START, endDate: END });
    expect(status).toBe(201);
    expect(json.subtotal).toBe(450);
    expect(json.coverageRate).toBe(0.2);
    expect(json.coverageFee).toBe(90);
    expect(json.totalPrice).toBe(540);
  });

  it("montaña redondea medio centavo hacia arriba y no arrastra error de flotantes", async () => {
    const { json } = await postRental({ gearId: "juez-montana", startDate: START, endDate: END });
    expect(json.subtotal).toBe(100.05);
    expect(json.coverageRate).toBe(0.1);
    expect(json.coverageFee).toBe(10.01);
    expect(json.totalPrice).toBe(110.06);
  });

  it("deportes acuáticos da un total exacto a dos decimales", async () => {
    const { json } = await postRental({ gearId: "juez-agua", startDate: START, endDate: END });
    expect(json.subtotal).toBe(269.85);
    expect(json.coverageRate).toBe(0.1);
    expect(json.coverageFee).toBe(26.99);
    expect(json.totalPrice).toBe(296.84);
  });

  it("el servidor ignora los precios que manda el navegador", async () => {
    const { json } = await postRental({
      gearId: "juez-foto",
      startDate: START,
      endDate: END,
      totalPrice: 1,
      coverageFee: 0,
      coverageRate: 0,
    });
    expect(json.coverageFee).toBe(90);
    expect(json.totalPrice).toBe(540);
  });

  it("la pantalla muestra la cobertura y el mismo total que el servidor", async () => {
    const { PriceSummary } = await import("@/components/features/RentalFlow/PriceSummary");
    const { formatPrice } = await import("@/lib/date-utils");
    const { json } = await postRental({ gearId: "juez-montana", startDate: START, endDate: END });

    render(
      <PriceSummary
        item={FIXTURES["juez-montana"]}
        dates={{ startDate: new Date(START), endDate: new Date(END) }}
        onConfirm={async () => {}}
        onBack={() => {}}
      />
    );

    expect(screen.getByText(/cobertura por daños/i)).toBeInTheDocument();
    expect(screen.getByText(formatPrice(json.coverageFee))).toBeInTheDocument();
    expect(screen.getAllByText(formatPrice(json.totalPrice)).length).toBeGreaterThan(0);
  });
});
