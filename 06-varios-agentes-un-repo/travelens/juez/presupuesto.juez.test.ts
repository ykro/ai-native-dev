/** Juez de la tarea `presupuesto`: función pública applyBudget en src/lib/budget.ts. Sin red. */
import { describe, it, expect } from "vitest";

const base = {
  intro: "Intro",
  days: [
    { day: 1, title: "A", activities: ["x"], costUsd: 40 },
    { day: 2, title: "B", activities: ["y"], costUsd: 25 },
    { day: 3, title: "C", activities: ["z"], costUsd: 0 },
  ],
  hiddenGem: { title: "g", description: "d" },
  localFood: { dish: "p", description: "d" },
};

async function run(plan: unknown) {
  const mod = await import("@/lib/budget");
  return mod.applyBudget(plan);
}

describe("Juez · presupuesto por día", () => {
  it("el total es la suma de los días", async () => {
    const r = await run(base);
    expect(r.ok).toBe(true);
    if (r.ok) expect(r.plan.totalUsd).toBe(65);
  });

  it("ignora un total equivocado que traiga el modelo", async () => {
    const r = await run({ ...base, totalUsd: 999 });
    expect(r.ok).toBe(true);
    if (r.ok) expect(r.plan.totalUsd).toBe(65);
  });

  it("conserva el resto del plan", async () => {
    const r = await run(base);
    if (!r.ok) throw new Error("debía ser ok");
    expect(r.plan.days).toHaveLength(3);
    expect(r.plan.localFood.dish).toBe("p");
  });

  it.each([
    ["costo negativo", -5],
    ["costo con centavos", 12.5],
    ["costo como texto", "40"],
    ["costo ausente", undefined],
    ["costo NaN", Number.NaN],
  ])("rechaza %s", async (_n, cost) => {
    const days = base.days.map((d, i) => (i === 1 ? { ...d, costUsd: cost } : d));
    const r = await run({ ...base, days });
    expect(r.ok).toBe(false);
  });
});
