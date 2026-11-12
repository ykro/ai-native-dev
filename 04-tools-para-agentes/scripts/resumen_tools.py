"""Tabla de resultados por conjunto de herramientas, calculada solo con los logs guardados.

Lee logs/20-resultados.json (aciertos, dictados por el juez) y cada log stream-json
(llamadas a herramientas, rondas, turnos, tokens, costo). No llama a ningún modelo.

Una ronda es una respuesta del modelo que pide una o más herramientas: una vuelta del loop.
Los turnos son el num_turns que reporta el harness, que cuenta cada llamada por separado.

Uso (desde 04-tools-para-agentes/):  python3 scripts/resumen_tools.py [--json]
"""
from __future__ import annotations

import json
import statistics as st
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LOGS = RAIZ / "logs"


def leer(log: Path) -> dict:
    llamadas, rondas, final = 0, set(), {}
    for linea in log.read_text(encoding="utf-8").splitlines():
        ev = json.loads(linea)
        if ev.get("type") == "assistant":
            usos = sum(1 for b in ev["message"]["content"] if b.get("type") == "tool_use")
            llamadas += usos
            if usos:
                rondas.add(ev["message"].get("id"))
        elif ev.get("type") == "result":
            final = ev
    u = final.get("usage", {})
    return {
        "llamadas": llamadas,
        "rondas": len(rondas),
        "turnos": final.get("num_turns", 0),
        "entrada_nueva": u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0),
        "entrada_cache": u.get("cache_read_input_tokens", 0),
        "salida": u.get("output_tokens", 0),
        "costo": final.get("total_cost_usd", 0.0),
    }


def cargar(archivo: str = "20-resultados.json") -> list[dict]:
    corridas = json.loads((LOGS / archivo).read_text(encoding="utf-8"))["corridas"]
    for c in corridas:
        c.update(leer(LOGS / c["log"]))
    return corridas


def resumir(corridas: list[dict]) -> dict:
    out: dict = {"conjuntos": {}}
    for conjunto in sorted({c["conjunto"] for c in corridas}):
        mios = [c for c in corridas if c["conjunto"] == conjunto]
        por_tarea = {}
        for t in sorted({c["tarea"] for c in mios}):
            ts = [c for c in mios if c["tarea"] == t]
            por_tarea[t] = {
                "corridas": len(ts),
                "aciertos": sum(c["acierta"] for c in ts),
                "llamadas_mediana": st.median(c["llamadas"] for c in ts),
                "turnos_mediana": st.median(c["turnos"] for c in ts),
                "entrada_media": round(st.mean(c["entrada_nueva"] + c["entrada_cache"] for c in ts)),
                "salida_media": round(st.mean(c["salida"] for c in ts)),
            }
        out["conjuntos"][conjunto] = {
            "corridas": len(mios),
            "aciertos": sum(c["acierta"] for c in mios),
            "llamadas_mediana_por_tarea": st.median(v["llamadas_mediana"] for v in por_tarea.values()),
            "llamadas_mediana_por_corrida": st.median(c["llamadas"] for c in mios),
            "llamadas_total": sum(c["llamadas"] for c in mios),
            "rondas_maximo": max(c["rondas"] for c in mios),
            "turnos_mediana": st.median(c["turnos"] for c in mios),
            "entrada_nueva": sum(c["entrada_nueva"] for c in mios),
            "entrada_cache": sum(c["entrada_cache"] for c in mios),
            "salida": sum(c["salida"] for c in mios),
            "costo_usd": round(sum(c["costo"] for c in mios), 4),
            "mas_llamadas": max(mios, key=lambda c: (c["llamadas"], c["log"]))["log"],
            "por_tarea": por_tarea,
        }
    return out


def main() -> int:
    r = resumir(cargar())
    if "--json" in sys.argv:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0
    cs = r["conjuntos"]
    print(f"{'':<40}" + "".join(f"{c:>14}" for c in cs))
    filas = [
        ("corridas", "corridas"), ("aciertos", "aciertos"),
        ("llamadas, mediana por tarea", "llamadas_mediana_por_tarea"),
        ("llamadas, total", "llamadas_total"),
        ("rondas de llamadas, máximo por corrida", "rondas_maximo"),
        ("turnos del harness, mediana", "turnos_mediana"),
        ("tokens de entrada nuevos", "entrada_nueva"), ("tokens de entrada desde caché", "entrada_cache"),
        ("tokens de salida", "salida"), ("costo USD", "costo_usd"),
    ]
    for etiqueta, clave in filas:
        print(f"{etiqueta:<40}" + "".join(f"{v[clave]:>14,}" if isinstance(v[clave], int) else f"{v[clave]:>14}" for v in cs.values()))
    print("\ndetalle por tarea (llamadas mediana · aciertos/corridas · tokens de entrada y de salida, media por corrida)")
    tareas = sorted({t for v in cs.values() for t in v["por_tarea"]})
    for t in tareas:
        celdas = []
        for v in cs.values():
            d = v["por_tarea"][t]
            celdas.append(f"{d['llamadas_mediana']:>4} · {d['aciertos']}/{d['corridas']} · {d['entrada_media']:>6,} · {d['salida_media']:>5,}")
        print(f"  tarea {t}   " + "   |   ".join(f"{c}: {x}" for c, x in zip(cs, celdas)))
    print("\nsesión con más llamadas por conjunto: " + ", ".join(f"{c} {v['mas_llamadas']}" for c, v in cs.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
