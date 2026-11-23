"""Compara las trazas reales antes y después de preparar el repositorio."""
import json
import pathlib
import sys

LOGS = ("medicion/logs/01-antes.jsonl", "medicion/logs/02-despues.jsonl")


def resumir_traza(ruta):
    pasos, fallidos, entrada, salida, seg = 0, [], 0, 0, 0.0
    for linea in pathlib.Path(ruta).read_text(encoding="utf-8").splitlines():
        ev = json.loads(linea)
        if ev.get("type") == "session.meta":
            seg = float(ev.get("duration_s", 0.0))
        elif ev.get("type") == "turn.completed":
            u = ev.get("usage", {})
            entrada += u.get("input_tokens", 0)
            salida += u.get("output_tokens", 0)
        elif ev.get("type") == "item.completed":
            pasos += 1
            it = ev.get("item", {})
            es_fallo = it.get("type") == "command_execution" and it.get("exit_code")
            if es_fallo:
                raw = it.get("command", "").removeprefix("/bin/zsh -lc ")
                primera = raw.strip("'\"").splitlines()[0]
                fallidos.append((int(it["exit_code"]), primera))
    return {"log": pathlib.Path(ruta).name, "pasos": pasos, "fallidos": fallidos,
            "entrada": entrada, "salida": salida, "segundos": round(seg, 1)}


if __name__ == "__main__":
    filas = [resumir_traza(p) for p in LOGS]
    cols = f"{'corrida':18} {'pasos':>5} {'fallos':>6} {'entrada':>9} {'tiempo':>7}"
    print(cols)
    for r in filas:
        print(f"{r['log']:18} {r['pasos']:5} {len(r['fallidos']):6} "
              f"{r['entrada']:9,} {r['segundos']:6.1f}s")
    if "--fallos" in sys.argv:
        for code, cmd in filas[0]["fallidos"]:
            print(f"  exit={code}  {cmd}")
