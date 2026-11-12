#!/usr/bin/env python3
"""Builds medicion/tabla.md: one row per project (before/after score, review findings, estimate vs clock, own minutes, turns, dollars)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ["pawsmatch", "travelens", "rent-my-gear", "traderpulse"]
estimates = (ROOT / "medicion/estimacion-previa.md").read_text(encoding="utf-8")


def estimate(project_label: str) -> str:
    m = re.search(rf"^\|\s*{re.escape(project_label)}\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", estimates, re.M)
    return f"{m.group(1)} h / {m.group(2)} min" if m and "por completar" not in m.group(0) else "pendiente del autor"


labels = {"pawsmatch": "PawsMatch", "travelens": "TraveLens", "rent-my-gear": "Rent My Gear", "traderpulse": "TraderPulse"}
rows = ["| Proyecto | Antes | Después | Hallazgos de la revisión | Estimación previa | Reloj medido | Minutos propios | Turnos | Dólares |",
        "|---|---|---|---|---|---|---|---|---|"]
for p in PROJECTS:
    m = json.loads((ROOT / f"medicion/{p}.json").read_text(encoding="utf-8"))
    rev_path = ROOT / f"medicion/{p}-revision.json"
    findings = "sin revisión"
    if rev_path.exists():
        rev = json.loads(rev_path.read_text(encoding="utf-8"))
        findings = str(len(rev["agente_revisor"].get("hallazgos", [])))
    clock = f"{m['segundos_de_reloj'] / 60:.1f} min"
    rows.append(f"| {labels[p]} | {m['antes']['aprobadas']}/{m['antes']['aplicadas']} | {m['despues']['aprobadas']}/{m['despues']['aplicadas']} | "
                f"{findings} | {estimate(labels[p])} | {clock} | sin cronómetro | {m['turnos']} | {m['costo_usd_reportado']:.2f} |")
(ROOT / "medicion/tabla.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
print("\n".join(rows))
