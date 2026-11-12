#!/usr/bin/env python3
"""Prints the comparison table of lote/resultado-sin-skill.json and lote/resultado-con-skill.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
arms = {a: json.loads((ROOT / f"lote/resultado-{a}.json").read_text(encoding="utf-8")) for a in ("sin-skill", "con-skill")}

print(f"{'brazo':<10} {'llamadas':>8} {'válidas':>8} {'turnos':>7} {'segundos':>9} {'USD/mascota':>12} {'USD total':>10}")
for name, r in arms.items():
    print(f"{name:<10} {r['llamadas']:>8} {r['validas']:>8} {r['turnos_promedio']:>7.1f} "
          f"{r['segundos_promedio']:>9.1f} {r['costo_promedio_usd']:>12.4f} {r['costo_total_usd']:>10.4f}")
for name, r in arms.items():
    bad = [f for f in r["filas"] if not f["valido"]]
    if bad:
        print(f"\nFallas de {name}:")
        for f in bad:
            print(f"  rep {f['repeticion']} fila {f['fila']} ({f['nombre']}): {'; '.join(f['errores'])}")
