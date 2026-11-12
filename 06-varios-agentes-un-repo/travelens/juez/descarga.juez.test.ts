/** Juez de la tarea `descarga`: funciones públicas de src/lib/itinerary-markdown.ts. Sin red. */
import { describe, it, expect, vi, afterEach } from "vitest";

const plan = {
  intro: "Intro",
  days: [
    { day: 1, title: "Centro", activities: ["Arco", "Catedral"], costUsd: 30 },
    { day: 2, title: "Volcanes", activities: ["Pacaya"], costUsd: 50 },
  ],
  hiddenGem: { title: "Cerro", description: "Vista" },
  localFood: { dish: "Pepián", description: "Recado" },
  totalUsd: 80,
};

afterEach(() => vi.unstubAllGlobals());

describe("Juez · descargar itinerario", () => {
  it("el nombre de archivo no lleva espacios ni acentos", async () => {
    const { itineraryFilename } = await import("@/lib/itinerary-markdown");
    expect(itineraryFilename("Antigua Guatemala")).toBe("antigua-guatemala.md");
    expect(itineraryFilename("Quetzaltenango Ciudad Éxito")).toBe("quetzaltenango-ciudad-exito.md");
    expect(itineraryFilename("  Panajachel  ")).toBe("panajachel.md");
  });

  it("el markdown trae destino como título, un encabezado por día y actividades en lista", async () => {
    const { itineraryToMarkdown } = await import("@/lib/itinerary-markdown");
    const md = itineraryToMarkdown("Antigua Guatemala", plan);
    const lines = md.split("\n");
    expect(lines[0]).toBe("# Antigua Guatemala");
    expect(lines.filter((l) => /^## /.test(l) && /Día [12]/.test(l))).toHaveLength(2);
    expect(md).toMatch(/^- Arco$/m);
    expect(md).toMatch(/^- Catedral$/m);
    expect(md).toMatch(/^- Pacaya$/m);
  });

  it("downloadItinerary entrega un Blob markdown con el nombre correcto", async () => {
    const click = vi.fn();
    const anchor = { href: "", download: "", click };
    const createObjectURL = vi.fn(() => "blob:fake");
    vi.stubGlobal("document", {
      createElement: vi.fn(() => anchor),
      body: { appendChild: vi.fn(), removeChild: vi.fn() },
    });
    vi.stubGlobal("URL", Object.assign(URL, { createObjectURL, revokeObjectURL: vi.fn() }));
    const { downloadItinerary } = await import("@/lib/itinerary-markdown");
    downloadItinerary("Antigua Guatemala", plan);
    expect(click).toHaveBeenCalledOnce();
    expect(anchor.download).toBe("antigua-guatemala.md");
    const blob = (createObjectURL.mock.calls as unknown as [Blob][])[0][0];
    expect(blob.type).toContain("markdown");
  });
});
