#!/usr/bin/env python3
"""Launches the read-only reviewer (claude -p) on a branch and writes revision/hallazgos-agente.json."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sanitize(text: str, worktree: Path) -> str:
    for p in {str(worktree), str(worktree.resolve())}:
        text = text.replace(p, "~/traderpulse")
    text = re.sub(r"/Users/[^/\"\s]+", "~", text)
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rama", required=True)
    parser.add_argument("--repo", default=str(ROOT / ".work/repo"))
    parser.add_argument("--informe", default="revision/informe.json")
    parser.add_argument("--salida", default="revision/hallazgos-agente.json")
    parser.add_argument("--log", default="logs/revisor-agente.jsonl")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--max-turns", type=int, default=20)
    args = parser.parse_args()

    repo = Path(args.repo)
    worktree = ROOT / ".work/wt-revisor"
    shutil.rmtree(worktree, ignore_errors=True)
    subprocess.run(["git", "worktree", "prune"], cwd=repo, check=True)
    subprocess.run(["git", "worktree", "add", "--detach", str(worktree), args.rama], cwd=repo, check=True, capture_output=True)
    informe = json.loads((ROOT / args.informe).read_text(encoding="utf-8"))
    for stage in informe["etapas"].values():  # keep the prompt short: the detail stays in the file
        stage.pop("detalle", None)
    prompt = (ROOT / "prompts/02-revisar.txt").read_text(encoding="utf-8")
    prompt = prompt.replace("{CONTRATO}", (ROOT / "contrato.md").read_text(encoding="utf-8"))
    prompt = prompt.replace("{INFORME}", json.dumps(informe, ensure_ascii=False, indent=1))
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose", "--max-turns", str(args.max_turns),
           "--model", args.model, "--setting-sources", "project", "--max-budget-usd", "2.00",
           "--allowedTools", "Read", "Glob", "Grep", "Bash(git diff *)", "Bash(git log *)", "Bash(git show *)"]
    t0 = time.time()
    run = subprocess.run(cmd, cwd=worktree, capture_output=True, text=True)
    wall = round(time.time() - t0, 1)
    events = [json.loads(l) for l in run.stdout.splitlines() if l.strip()]
    for e in events:
        if e.get("type") == "system" and e.get("subtype") == "init":
            e.clear(); e.update({"type": "system", "subtype": "init"})
    log = ROOT / args.log
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("\n".join(sanitize(json.dumps(e, ensure_ascii=False), worktree) for e in events) + "\n", encoding="utf-8")
    result = next((e for e in reversed(events) if e.get("type") == "result"), {})
    text = result.get("result", "")
    match = re.search(r"\{.*\}", text, re.S)
    try:
        parsed = json.loads(match.group(0)) if match else {}
    except json.JSONDecodeError:
        parsed = {"error": "la respuesta no era JSON", "texto": text}
    parsed["_medicion"] = {"turnos": result.get("num_turns"), "duracion_ms": result.get("duration_ms"),
                           "segundos_de_reloj": wall, "costo_usd": result.get("total_cost_usd"), "subtype": result.get("subtype")}
    out = ROOT / args.salida
    out.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=repo, check=True)
    print(f"Hallazgos: {len(parsed.get('hallazgos', []))}; escrito en {args.salida}; costo {parsed['_medicion']['costo_usd']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
