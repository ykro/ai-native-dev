/** Juez de la tarea `api`: POST /api/ai-plan con duración y presupuesto. Mockea @google/genai, sin red. */
import { describe, it, expect, vi, beforeEach } from "vitest";

const generateContent = vi.fn();

vi.mock("@google/genai", () => ({
  GoogleGenAI: class {
    models = { generateContent };
  },
}));

function planWith(n: number, extra: Record<string, unknown> = {}, cost: unknown = 20) {
  return {
    intro: "Intro",
    days: Array.from({ length: n }, (_, i) => ({
      day: i + 1,
      title: `Día ${i + 1}`,
      activities: ["Algo"],
      costUsd: cost,
    })),
    hiddenGem: { title: "g", description: "d" },
    localFood: { dish: "p", description: "d" },
    ...extra,
  };
}

async function post(modelPlan: unknown, body: unknown = { destination: "Antigua" }) {
  generateContent.mockResolvedValue({ text: JSON.stringify(modelPlan) });
  const { POST } = await import("@/app/api/ai-plan/route");
  const res = await POST(
    new Request("http://localhost/api/ai-plan", { method: "POST", body: JSON.stringify(body) })
  );
  return { status: res.status, json: await res.json() };
}

describe("Juez · duración y presupuesto en el API", () => {
  beforeEach(() => {
    generateContent.mockReset();
    process.env.GOOGLE_GENAI_API_KEY = "test-key";
    vi.spyOn(console, "error").mockImplementation(() => {});
    vi.spyOn(console, "log").mockImplementation(() => {});
  });

  it("sin days sigue siendo un plan de 3 días", async () => {
    const { status, json } = await post(planWith(3));
    expect(status).toBe(200);
    expect(json.plan.days).toHaveLength(3);
  });

  it.each([2, 5, 7])("days=%i devuelve exactamente ese número de días", async (n) => {
    const { status, json } = await post(planWith(n), { destination: "Antigua", days: n });
    expect(status).toBe(200);
    expect(json.plan.days).toHaveLength(n);
  });

  it("si el modelo trae otro número de días responde 502 invalid_plan", async () => {
    const { status, json } = await post(planWith(4), { destination: "Antigua", days: 5 });
    expect(status).toBe(502);
    expect(json).toEqual({ error: "invalid_plan" });
  });

  it("el prompt al modelo pide el número de días elegido", async () => {
    await post(planWith(6), { destination: "Antigua", days: 6 });
    const prompt = JSON.stringify(generateContent.mock.calls[0][0]);
    expect(prompt).toMatch(/\b6[- ]?(d[ií]as?|days?)\b/i);
    expect(prompt).not.toMatch(/\b3[- ]?(d[ií]as?|days?)\b/i);
  });

  it.each([1, 8, 3.5, "5", null])("days=%j fuera de rango responde 400", async (d) => {
    const { status } = await post(planWith(3), { destination: "Antigua", days: d });
    expect(status).toBe(400);
  });

  it("el total del plan es la suma de los días aunque el modelo se equivoque", async () => {
    const { status, json } = await post(planWith(3, { totalUsd: 1 }, 30));
    expect(status).toBe(200);
    expect(json.plan.totalUsd).toBe(90);
    expect(json.plan.days.every((d: { costUsd: number }) => d.costUsd === 30)).toBe(true);
  });

  it.each([-1, 10.5, "20"])("costo de día %j responde 502 invalid_plan", async (c) => {
    const { status, json } = await post(planWith(3, {}, c));
    expect(status).toBe(502);
    expect(json).toEqual({ error: "invalid_plan" });
  });
});
