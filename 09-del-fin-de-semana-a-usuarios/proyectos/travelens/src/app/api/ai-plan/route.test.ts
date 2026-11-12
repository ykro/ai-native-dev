import { describe, it, expect, vi } from "vitest";
import type { TravelPlan } from "@/services/schemas";
import { VALID_ITINERARY_FIXTURE } from "@/services/__fixtures__/itinerary.fixture";

const generateTravelPlan = vi.fn<
  (destination: string, context?: string) => Promise<TravelPlan | null>
>(async () => VALID_ITINERARY_FIXTURE);

vi.mock("@/services/gemini", () => ({
  GeminiService: { generateTravelPlan },
}));

async function post(body: unknown) {
  const { POST } = await import("./route");
  return POST(new Request("http://localhost/api/ai-plan", { method: "POST", body: JSON.stringify(body) }));
}

describe("POST /api/ai-plan", () => {
  it("responde 400 sin destino", async () => {
    const res = await post({});
    expect(res.status).toBe(400);
  });

  it("devuelve el plan del servicio con 200", async () => {
    generateTravelPlan.mockResolvedValueOnce(VALID_ITINERARY_FIXTURE);
    const res = await post({ destination: "Antigua" });
    expect(res.status).toBe(200);
    expect((await res.json()).plan.days).toHaveLength(3);
  });

  it("responde 502 cuando el servicio no devuelve un plan válido", async () => {
    generateTravelPlan.mockResolvedValueOnce(null);
    const res = await post({ destination: "Antigua" });
    expect(res.status).toBe(502);
    expect(await res.json()).toEqual({ error: "invalid_plan" });
  });
});
