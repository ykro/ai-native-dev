#!/usr/bin/env python3
"""Cost of one request and a scenario table, from medicion/tokens-por-peticion-*.jsonl and salida/precios.json.

The scenario assumptions are printed on screen on purpose: they are assumptions, not measurements.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
prices = json.loads((ROOT / "salida/precios.json").read_text(encoding="utf-8"))
model = prices["modelos"]["gemini-3.8-flash"]
REQUESTS_PER_PERSON_PER_DAY = [3, 10]
PEOPLE = [100, 1000]
DAYS = 30

summary = {"tarifa": {"modelo": "gemini-3.8-flash", "fecha_de_consulta": prices["fecha_de_consulta"],
                      "entrada_por_millon": model["entrada"], "salida_por_millon": model["salida"], "url": model["url_oficial"]},
           "supuestos": {"peticiones_por_persona_al_dia": REQUESTS_PER_PERSON_PER_DAY, "personas": PEOPLE, "dias": DAYS},
           "proyectos": {}}
print(f"Tarifa de {summary['tarifa']['modelo']} consultada el {prices['fecha_de_consulta']}: "
      f"{model['entrada']} USD entrada y {model['salida']} USD salida por millón de tokens ({model['url_oficial']})")
print(f"SUPUESTOS (no son mediciones): {REQUESTS_PER_PERSON_PER_DAY} peticiones por persona al día, {PEOPLE} personas, {DAYS} días\n")
for path in sorted((ROOT / "medicion").glob("tokens-por-peticion-*.jsonl")):
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    project = rows[0]["proyecto"]
    tin = sum(r["tokens_entrada"] for r in rows) / len(rows)
    tout = sum(r["tokens_salida"] for r in rows) / len(rows)
    cost = (tin * model["entrada"] + tout * model["salida"]) / 1e6
    scenarios = []
    for people in PEOPLE:
        for rpd in REQUESTS_PER_PERSON_PER_DAY:
            scenarios.append({"personas": people, "peticiones_por_persona_al_dia": rpd, "costo_mensual_usd": round(cost * people * rpd * DAYS, 2)})
    summary["proyectos"][project] = {"peticiones_medidas": len(rows), "tokens_entrada_promedio": round(tin, 1),
                                     "tokens_salida_promedio": round(tout, 1), "costo_por_peticion_usd": round(cost, 6), "escenarios": scenarios}
    print(f"{project}: {len(rows)} peticiones medidas; entrada {tin:.0f} tokens y salida {tout:.0f} tokens en promedio; "
          f"{cost:.6f} USD por petición")
    print(f"  {'personas':>9} {'pet./persona/día':>17} {'USD al mes':>11}")
    for s in scenarios:
        print(f"  {s['personas']:>9} {s['peticiones_por_persona_al_dia']:>17} {s['costo_mensual_usd']:>11.2f}")
(ROOT / "medicion/costo-por-usuario.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
