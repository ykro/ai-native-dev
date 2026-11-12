"""Juez de herramientas: corre cada tarea con cada conjunto, N veces, y dicta acierto o fallo.

- La respuesta correcta se calcula en cada corrida contra el BFF de ejemplo; no está escrita a mano.
- Cada tarea se repite --reps veces: un modelo puede acertar una vez por suerte.
- El agente solo dispone de las herramientas MCP del conjunto que se mide: sin herramientas
  propias del harness (--tools ""), sin otros servidores (--strict-mcp-config).

Uso (desde 04-tools-para-agentes/, con el BFF corriendo):
    uv run python juez/juez_tools.py --reps 3
    uv run python juez/juez_tools.py --reps 3 --bff http://127.0.0.1:8010 --jobs 4
Escribe logs/20-<conjunto>-t<tarea>-r<rep>.jsonl (saneados) y logs/20-resultados.json.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
from sanear_log import sanear  # noqa: E402

CONJUNTOS = ["espejo", "agente"]
CATEGORIAS = ["alcista", "bajista", "neutral"]
MODELO = "claude-sonnet-5-5"
TOLERANCIA = 0.006


def esperado(bff: str) -> dict[int, dict]:
    """Calcula la respuesta correcta de cada tarea llamando directo al BFF."""
    def get(ruta: str):
        return httpx.get(f"{bff}{ruta}", timeout=20).json()

    cot = {s: get(f"/api/v1/cotizaciones/{s}") for s in ("AAPL", "MSFT", "NVDA")}
    hist_aapl = get("/api/v1/historico/AAPL")
    mejor = max(hist_aapl, key=lambda p: p["cierre"])
    return {
        1: {"numero": cot["NVDA"]["precio"]},
        # «Mayor cambio» se declara en el prompt: el mayor movimiento en valor absoluto, suba o baje.
        2: {"simbolo": max(cot, key=lambda s: abs(cot[s]["cambio_pct"]))},
        3: {"categoria": get("/api/v1/sentimiento/TSLA")["sentimiento"]},
        4: {"simbolo": next(i["simbolo"] for i in get("/api/v1/instrumentos?q=alphabet"))},
        5: {"numero": mejor["cierre"], "fecha": mejor["fecha"]},
        6: {"numero": cot["MSFT"]["precio"], "cambio": cot["MSFT"]["cambio_pct"],
            "categoria": get("/api/v1/sentimiento/MSFT")["sentimiento"]},
    }


def numeros(texto: str) -> list[float]:
    return [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", texto.replace(",", ""))]


def hay(valor: float, texto: str) -> bool:
    return any(abs(n - valor) < TOLERANCIA for n in numeros(texto))


def juzgar(tarea: dict, esp: dict, respuesta: str, simbolos: list[str]) -> tuple[bool, str]:
    lineas = [ln for ln in respuesta.strip().splitlines() if ln.startswith("RESPUESTA:")]
    if not lineas or not respuesta.strip().splitlines()[-1].startswith("RESPUESTA:"):
        return False, "la última línea no es RESPUESTA:"
    linea = lineas[-1].removeprefix("RESPUESTA:").strip()
    categorias = [c for c in CATEGORIAS if c in linea.lower()]
    tipo = tarea["tipo"]
    if tipo == "numero":
        return hay(esp["numero"], linea), f"esperaba {esp['numero']}"
    if tipo == "simbolo":
        nombrados = [s for s in simbolos if re.search(rf"\b{s}\b", linea)]
        return nombrados == [esp["simbolo"]], f"esperaba {esp['simbolo']}, nombró {nombrados}"
    if tipo == "categoria":
        return categorias == [esp["categoria"]], f"esperaba {esp['categoria']}, dijo {categorias}"
    if tipo == "maximo":
        return hay(esp["numero"], linea) and esp["fecha"] in linea, f"esperaba {esp['numero']} el {esp['fecha']}"
    ok = hay(esp["numero"], linea) and hay(esp["cambio"], linea) and categorias == [esp["categoria"]]
    return ok, f"esperaba {esp['numero']}, {esp['cambio']}, {esp['categoria']}"


def correr(args, conjunto: str, tarea: dict, rep: int, esp: dict, simbolos: list[str]) -> dict:
    nombre = f"{args.salida}-{conjunto}-t{tarea['id']}-r{rep}"
    with tempfile.TemporaryDirectory() as tmp:
        config = json.loads((RAIZ / "mcp" / f"{conjunto}.mcp.json").read_text())
        srv = config["mcpServers"]["traderpulse"]
        srv["args"] = ["run", "--project", str(RAIZ), "--quiet", "python", str(RAIZ / "mcp" / f"{conjunto}.py")]
        srv["env"] = {"BFF_URL": args.bff}
        cfg = Path(tmp) / "mcp.json"
        cfg.write_text(json.dumps(config))
        prompt = (RAIZ / "prompts" / "01-tarea.txt").read_text().replace("{pregunta}", tarea["pregunta"])
        crudo = Path(tmp) / "sesion.jsonl"
        with crudo.open("w") as salida:
            subprocess.run(
                ["claude", "-p", prompt, "--model", MODELO, "--output-format", "stream-json",
                 "--verbose", "--max-turns", str(args.max_turns), "--mcp-config", str(cfg),
                 "--strict-mcp-config", "--tools", "", "--allowedTools", "mcp__traderpulse",
                 "--disable-slash-commands", "--no-session-persistence",
                 "--setting-sources", "project"],
                cwd=tmp, stdout=salida, stderr=subprocess.DEVNULL, text=True,
            )
        respuesta, costo = "", 0.0
        for linea in crudo.read_text().splitlines():
            ev = json.loads(linea) if linea.strip() else {}
            if ev.get("type") == "result":
                respuesta, costo = ev.get("result") or "", ev.get("total_cost_usd", 0.0)
        sanear(crudo, RAIZ / "logs" / f"{nombre}.jsonl", {tmp: "~/tmp"})
    ok, detalle = juzgar(tarea, esp, respuesta, simbolos)
    print(f"{'ACIERTA' if ok else 'FALLA  '} {conjunto:<6} tarea {tarea['id']} rep {rep}  ({detalle})", flush=True)
    return {"log": f"{nombre}.jsonl", "conjunto": conjunto, "tarea": tarea["id"], "rep": rep,
            "acierta": ok, "detalle": detalle, "respuesta": respuesta.strip().splitlines()[-1:] or [""],
            "costo_usd": costo}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--bff", default="http://127.0.0.1:8000")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--max-turns", type=int, default=12)
    ap.add_argument("--conjuntos", nargs="*", default=CONJUNTOS)
    ap.add_argument("--tareas", nargs="*", type=int, help="solo estos números de tarea")
    ap.add_argument("--salida", default="20", help="prefijo de los logs (por defecto 20)")
    args = ap.parse_args()

    tareas = [t for t in json.loads((RAIZ / "evals" / "tareas.json").read_text())
              if not args.tareas or t["id"] in args.tareas]
    esp = esperado(args.bff)
    simbolos = [i["simbolo"] for i in httpx.get(f"{args.bff}/api/v1/instrumentos", timeout=20).json()]
    print(f"respuestas correctas calculadas contra el BFF: {json.dumps(esp, ensure_ascii=False)}")
    (RAIZ / "logs").mkdir(exist_ok=True)
    trabajos = [(c, t, r) for c in args.conjuntos for t in tareas for r in range(1, args.reps + 1)]
    with ThreadPoolExecutor(args.jobs) as pool:
        resultados = list(pool.map(lambda x: correr(args, x[0], x[1], x[2], esp[x[1]["id"]], simbolos), trabajos))
    resultados.sort(key=lambda r: r["log"])
    (RAIZ / "logs" / f"{args.salida}-resultados.json").write_text(
        json.dumps({"reps": args.reps, "esperado": esp, "corridas": resultados}, ensure_ascii=False, indent=2) + "\n")
    for c in args.conjuntos:
        mios = [r for r in resultados if r["conjunto"] == c]
        print(f"{c}: {sum(r['acierta'] for r in mios)} aciertos de {len(mios)} corridas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
