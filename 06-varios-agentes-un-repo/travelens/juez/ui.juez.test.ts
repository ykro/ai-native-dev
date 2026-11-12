/** Juez de la tarea `ui`: función pública requestPlan en src/lib/plan-client.ts, con fetch simulado. Sin red. */
import { describe, it, expect, vi, afterEach } from "vitest";

afterEach(() => vi.unstubAllGlobals());

const plan = { intro: "i", days: [], hiddenGem: {}, localFood: {}, totalUsd: 10 };

function stubFetch(response: { ok: boolean; status: number; body: unknown }) {
  const fn = vi.fn(async () => ({
    ok: response.ok,
    status: response.status,
    json: async () => response.body,
  }));
  vi.stubGlobal("fetch", fn);
  return fn;
}

describe("Juez · cliente del plan en la interfaz", () => {
  it("envía destino, contexto y días a /api/ai-plan", async () => {
    const fetchFn = stubFetch({ ok: true, status: 200, body: { plan } });
    const { requestPlan } = await import("@/lib/plan-client");
    await requestPlan({ destination: "Antigua", context: "Guatemala", days: 5 });
    const [url, init] = fetchFn.mock.calls[0] as unknown as [string, { method: string; body: string }];
    expect(url).toBe("/api/ai-plan");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).toEqual({ destination: "Antigua", context: "Guatemala", days: 5 });
  });

  it("devuelve el plan cuando llega con 200", async () => {
    stubFetch({ ok: true, status: 200, body: { plan } });
    const { requestPlan } = await import("@/lib/plan-client");
    expect(await requestPlan({ destination: "Antigua", days: 3 })).toEqual(plan);
  });

  it("devuelve null si el API responde 502 (plan que no se muestra)", async () => {
    stubFetch({ ok: false, status: 502, body: { error: "invalid_plan" } });
    const { requestPlan } = await import("@/lib/plan-client");
    expect(await requestPlan({ destination: "Antigua", days: 3 })).toBeNull();
  });

  it("devuelve null si fetch lanza, sin propagar la excepción", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => {
      throw new Error("red");
    }));
    vi.spyOn(console, "error").mockImplementation(() => {});
    const { requestPlan } = await import("@/lib/plan-client");
    expect(await requestPlan({ destination: "Antigua", days: 3 })).toBeNull();
  });

  it("si no se pide días, manda 3", async () => {
    const fetchFn = stubFetch({ ok: true, status: 200, body: { plan } });
    const { requestPlan } = await import("@/lib/plan-client");
    await requestPlan({ destination: "Antigua" });
    const [, init] = fetchFn.mock.calls[0] as unknown as [string, { body: string }];
    expect(JSON.parse(init.body).days).toBe(3);
  });
});
