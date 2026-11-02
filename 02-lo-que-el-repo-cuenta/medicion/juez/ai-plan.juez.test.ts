/**
 * Juez oculto de la medición del tema 02.
 *
 * El agente no lo ve durante la sesión. Se copia al repo cuando la sesión termina y
 * decide si la tarea quedó bien hecha. Mockea el SDK de Gemini, así que no usa red.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";

const generateContent = vi.fn();

vi.mock("@google/genai", () => ({
  GoogleGenAI: class {
    models = { generateContent };
  },
}));

const PLAN = {
  intro: "Tres días en Antigua",
  days: [
    { day: 1, title: "Centro", activities: ["Arco de Santa Catalina"] },
    { day: 2, title: "Volcanes", activities: ["Pacaya"] },
    { day: 3, title: "Café", activities: ["Finca en San Miguel Escobar"] },
  ],
  hiddenGem: { title: "Cerro de la Cruz", description: "Vista al Volcán de Agua" },
  localFood: { dish: "Pepián", description: "Recado de semillas tostadas" },
};

async function postWithModelText(text: string, body: unknown = { destination: "Antigua" }) {
  generateContent.mockResolvedValue({ text });
  const { POST } = await import("@/app/api/ai-plan/route");
  const res = await POST(
    new Request("http://localhost/api/ai-plan", { method: "POST", body: JSON.stringify(body) })
  );
  return { status: res.status, json: await res.json() };
}

describe("Juez · plan de viaje válido o 502", () => {
  beforeEach(() => {
    generateContent.mockReset();
    process.env.GOOGLE_GENAI_API_KEY = "test-key";
    vi.spyOn(console, "error").mockImplementation(() => {});
    vi.spyOn(console, "log").mockImplementation(() => {});
  });

  it("un plan completo llega con 200", async () => {
    const { status, json } = await postWithModelText(JSON.stringify(PLAN));
    expect(status).toBe(200);
    expect(json.plan.days).toHaveLength(3);
  });

  it("acepta el JSON envuelto en un bloque ```json", async () => {
    const { status, json } = await postWithModelText("```json\n" + JSON.stringify(PLAN) + "\n```");
    expect(status).toBe(200);
    expect(json.plan.localFood.dish).toBe("Pepián");
  });

  it("sin localFood responde 502 invalid_plan", async () => {
    const rest = { intro: PLAN.intro, days: PLAN.days, hiddenGem: PLAN.hiddenGem };
    const { status, json } = await postWithModelText(JSON.stringify(rest));
    expect(status).toBe(502);
    expect(json).toEqual({ error: "invalid_plan" });
  });

  it("con dos días responde 502 invalid_plan", async () => {
    const { status, json } = await postWithModelText(JSON.stringify({ ...PLAN, days: PLAN.days.slice(0, 2) }));
    expect(status).toBe(502);
    expect(json).toEqual({ error: "invalid_plan" });
  });

  it("un día sin actividades responde 502 invalid_plan", async () => {
    const days = PLAN.days.map((d, i) => (i === 1 ? { ...d, activities: [] } : d));
    const { status, json } = await postWithModelText(JSON.stringify({ ...PLAN, days }));
    expect(status).toBe(502);
    expect(json).toEqual({ error: "invalid_plan" });
  });

  it("texto que no es JSON responde 502 invalid_plan", async () => {
    const { status, json } = await postWithModelText("Lo siento, no puedo ayudar con eso.");
    expect(status).toBe(502);
    expect(json).toEqual({ error: "invalid_plan" });
  });

  it("sin destino sigue respondiendo 400", async () => {
    const { status } = await postWithModelText(JSON.stringify(PLAN), {});
    expect(status).toBe(400);
  });
});
