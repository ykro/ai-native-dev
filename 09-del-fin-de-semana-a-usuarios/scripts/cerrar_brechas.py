#!/usr/bin/env python3
"""Closes the gaps of the exit judge with one headless agent per project.

For each project: working copy outside the series folder (.work/), a git repo with a worktree on branch
salida/<project>, judge "before", headless agent with explicit permissions and the Skill, judge "after", and
medicion/<project>.json with wall-clock seconds, turns, tokens, dollars and the diff stat.

Usage: python3 scripts/cerrar_brechas.py --todos --paralelo
       python3 scripts/cerrar_brechas.py --proyecto traderpulse
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / ".work"
PROJECTS = ["pawsmatch", "travelens", "rent-my-gear", "traderpulse"]
JS_SUBDIR = {"pawsmatch": "app", "travelens": "", "rent-my-gear": "", "traderpulse": ""}
NPM_TOOLS = ["Bash(npm run *)", "Bash(npm test*)", "Bash(npx vitest*)", "Bash(npx tsc*)", "Bash(npx eslint*)", "Bash(npm audit*)"]
PY_TOOLS = ["Bash(.venv/bin/python -m pytest *)", "Bash(GEMINI_API_KEY=test-key .venv/bin/python -m pytest *)"]
DENY = ["Read(**/.env*)", "Edit(**/.env*)", "Write(**/.env*)", "Bash(git *)", "Edit(BRECHAS.md)", "Edit(.claude/**)"]

PROMPT = """Usa la Skill salida-a-usuarios. El proyecto es {proyecto}. El juez de salida revisa siete promesas a un usuario y hoy falla en esto (copia en BRECHAS.md):

{brechas}

Cierra las brechas que fallan, una por una, con la disciplina de la Skill: primero la prueba que las captura, luego el código. Las comprobaciones que dicen N/A no aplican y no se tocan. {extra}Termina con el reporte de la Skill."""

EXTRA = {
    "pawsmatch": "La app es una SPA de Vite en la carpeta app/; el README del proyecto está en la raíz. ",
    "travelens": "El modelo se llama desde src/services/gemini.ts. Las rutas de la API están en src/app/api/. ",
    "rent-my-gear": "El modelo de imágenes se llama desde src/services/imageService.ts, expuesto en src/app/api/generate-image/route.ts. ",
    "traderpulse": "El README que revisa el juez es backend/README.md. Las pruebas se corren con `GEMINI_API_KEY=test-key .venv/bin/python -m pytest backend/tests -q` desde la raíz. ",
}


def sh(*args, cwd, check=True):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=check).stdout


def judge(project: str, folder: Path) -> dict:
    out = subprocess.run([sys.executable, str(ROOT / "salida/juez_salida.py"), "--proyecto", project, "--ruta", str(folder), "--json"],
                         capture_output=True, text=True)
    return json.loads(out.stdout)


def prepare(project: str) -> tuple[Path, Path]:
    base, wt = WORK / project, WORK / f"{project}-wt"
    shutil.rmtree(base, ignore_errors=True); shutil.rmtree(wt, ignore_errors=True)
    shutil.copytree(ROOT / "proyectos" / project, base, symlinks=True, ignore=shutil.ignore_patterns("node_modules", ".next", "__pycache__", ".venv"))
    sh("git", "init", "-q", "-b", "main", cwd=base)
    sh("git", "add", "-A", cwd=base)
    sh("git", "-c", "user.name=demo", "-c", "user.email=demo@example.com", "commit", "-qm", f"base {project}", cwd=base)
    sh("git", "worktree", "add", "-q", "-b", f"salida/{project}", str(wt), cwd=base)
    nm_src = ROOT / "proyectos" / project / JS_SUBDIR[project] / "node_modules"
    if nm_src.exists():
        (wt / JS_SUBDIR[project] / "node_modules").symlink_to(nm_src)
    if project == "traderpulse":
        (wt / ".venv").symlink_to(ROOT / ".venv")
    skill_dst = wt / ".claude/skills/salida-a-usuarios"
    skill_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / "salida/skills/salida-a-usuarios", skill_dst)
    return base, wt


def brechas_text(result: dict) -> str:
    lines = []
    for cid, d in result["detalle"].items():
        lines.append(f"- {cid}. {d['nombre']}: {'OK' if d['ok'] else 'FALLA'} — {d['motivo']}")
    lines += [f"- {n['id']}. {n['nombre']}: N/A — {n['razon']}" for n in result["no_aplica"]]
    return "\n".join(lines)


def sanitize(text: str, wt: Path) -> str:
    for p in sorted({str(wt), str(wt.resolve())}, key=len, reverse=True):
        text = text.replace(p, "~/proyecto")
    return re.sub(r"/Users/[^/\"\s]+", "~", text)


def price(usage: dict, prices: dict) -> float:
    p = prices["modelos"]["claude-sonnet-5-5"]
    return round((usage.get("input_tokens", 0) * p["entrada"] + usage.get("output_tokens", 0) * p["salida"]
                  + usage.get("cache_creation_input_tokens", 0) * p["escritura_cache_5m"]
                  + usage.get("cache_read_input_tokens", 0) * p["lectura_cache"]) / 1e6, 4)


def close_gaps(project: str, max_turns: int, budget: float) -> dict:
    base, wt = prepare(project)
    before = judge(project, wt)
    (ROOT / "medicion").mkdir(exist_ok=True)
    (ROOT / f"medicion/{project}-antes.json").write_text(json.dumps(before, ensure_ascii=False, indent=2), encoding="utf-8")
    (wt / "BRECHAS.md").write_text("# Brechas según el juez de salida\n\n" + brechas_text(before) + "\n", encoding="utf-8")
    tools = ["Read", "Glob", "Grep", "Edit", "Write", *(PY_TOOLS if project == "traderpulse" else NPM_TOOLS)]
    cmd = ["claude", "-p", PROMPT.format(proyecto=project, brechas=brechas_text(before), extra=EXTRA[project]),
           "--output-format", "stream-json", "--verbose", "--max-turns", str(max_turns), "--model", "sonnet",
           "--setting-sources", "project", "--max-budget-usd", str(budget),
           "--allowedTools", *tools, "--disallowedTools", *DENY]
    t0 = time.time()
    run = subprocess.run(cmd, cwd=wt, capture_output=True, text=True)
    seconds = round(time.time() - t0, 1)
    events = [json.loads(l) for l in run.stdout.splitlines() if l.strip()]
    kept = []
    for e in events:
        if e.get("type") == "system":
            if e.get("subtype") != "init":
                continue
            e = {"type": "system", "subtype": "init", "model": e.get("model"), "claude_code_version": e.get("claude_code_version")}
        kept.append(sanitize(json.dumps(e, ensure_ascii=False), wt))
    (ROOT / f"logs/cerrar-{project}.jsonl").write_text("\n".join(kept) + "\n", encoding="utf-8")
    result = next((e for e in reversed(events) if e.get("type") == "result"), {})
    after = judge(project, wt)
    (ROOT / f"medicion/{project}-despues.json").write_text(json.dumps(after, ensure_ascii=False, indent=2), encoding="utf-8")
    for link in (wt / JS_SUBDIR[project] / "node_modules", wt / ".venv"):
        if link.is_symlink():
            link.unlink()
    (wt / "BRECHAS.md").unlink(missing_ok=True)
    shutil.rmtree(wt / ".claude", ignore_errors=True)
    sh("git", "add", "-A", cwd=wt)
    sh("git", "-c", "user.name=demo", "-c", "user.email=demo@example.com", "commit", "-qm", f"salida {project}", "--allow-empty", cwd=wt)
    stat = sh("git", "diff", "--shortstat", "main", f"salida/{project}", cwd=base).strip()
    files = sh("git", "diff", "--name-only", "main", f"salida/{project}", cwd=base).split()
    (ROOT / f"medicion/{project}.patch").write_text(sh("git", "diff", "main", f"salida/{project}", cwd=base), encoding="utf-8")
    prices = json.loads((ROOT / "salida/precios.json").read_text(encoding="utf-8"))
    usage = result.get("usage", {})
    record = {
        "proyecto": project, "segundos_de_reloj": seconds, "turnos": result.get("num_turns"),
        "subtype": result.get("subtype"), "tokens": {k: usage.get(k, 0) for k in
            ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")},
        "costo_usd_reportado": result.get("total_cost_usd"), "costo_usd_con_tarifa": price(usage, prices),
        "tarifa_consultada": prices["fecha_de_consulta"],
        "antes": {"aplicadas": before["aplicadas"], "aprobadas": before["aprobadas"], "falladas": before["falladas"]},
        "despues": {"aplicadas": after["aplicadas"], "aprobadas": after["aprobadas"], "falladas": after["falladas"]},
        "diff": {"resumen": stat, "archivos": files},
        "reporte_del_agente": sanitize(result.get("result", ""), wt),
    }
    (ROOT / f"medicion/{project}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[{project}] {before['aprobadas']}/{before['aplicadas']} -> {after['aprobadas']}/{after['aplicadas']} "
          f"en {seconds}s, {record['turnos']} turnos, ${record['costo_usd_reportado']}", flush=True)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--todos", action="store_true")
    parser.add_argument("--proyecto", choices=PROJECTS)
    parser.add_argument("--paralelo", action="store_true")
    parser.add_argument("--max-turns", type=int, default=80)
    parser.add_argument("--presupuesto-usd", type=float, default=8.0)
    args = parser.parse_args()
    selected = PROJECTS if args.todos else [args.proyecto]
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=len(selected) if args.paralelo else 1) as pool:
        records = list(pool.map(lambda p: close_gaps(p, args.max_turns, args.presupuesto_usd), selected))
    total = round(time.time() - t0, 1)
    (ROOT / "medicion/corrida.json").write_text(json.dumps({
        "paralelo": args.paralelo, "segundos_de_reloj_total": total,
        "segundos_sumados": round(sum(r["segundos_de_reloj"] for r in records), 1),
        "costo_usd_reportado_total": round(sum(r["costo_usd_reportado"] or 0 for r in records), 4),
        "costo_usd_con_tarifa_total": round(sum(r["costo_usd_con_tarifa"] for r in records), 4)}, indent=2), encoding="utf-8")
    print(f"Total de reloj: {total}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
