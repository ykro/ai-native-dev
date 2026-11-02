import { describe, it, expect, vi, beforeEach } from "vitest";
import { VALID_ITINERARY_FIXTURE } from "./__fixtures__/itinerary.fixture";

const generateContent = vi.fn();

vi.mock("@google/genai", () => ({
  GoogleGenAI: class {
    models = { generateContent };
  },
}));

describe("GeminiService.generateTravelPlan", () => {
  beforeEach(() => {
    generateContent.mockReset();
    process.env.GOOGLE_GENAI_API_KEY = "test-key";
    vi.spyOn(console, "error").mockImplementation(() => {});
  });

  it("devuelve el plan cuando el modelo responde JSON válido", async () => {
    generateContent.mockResolvedValue({ text: JSON.stringify(VALID_ITINERARY_FIXTURE) });
    const { GeminiService } = await import("./gemini");
    const plan = await GeminiService.generateTravelPlan("Antigua");
    expect(plan?.days).toHaveLength(3);
    expect(generateContent).toHaveBeenCalledOnce();
  });

  it("devuelve null si falta la API key", async () => {
    delete process.env.GOOGLE_GENAI_API_KEY;
    const { GeminiService } = await import("./gemini");
    expect(await GeminiService.generateTravelPlan("Antigua")).toBeNull();
    expect(generateContent).not.toHaveBeenCalled();
  });
});
