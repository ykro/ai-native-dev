#!/usr/bin/env python3
"""Clean fixing session: from pr/rsi-y-noticias creates pr/defendida with a headless agent.

The session only gets the contract, the judge (read-only copy in _juez) and the review report.
Writes defensa/defensa.patch, defensa/medicion.json and logs/defensa.jsonl (sanitized).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT / ".work/repo"
WT = ROOT / ".work/wt-defensa"


def git(*args, cwd=REPO, check=True):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=check).stdout


def main() -> int:
    shutil.rmtree(WT, ignore_errors=True)
    git("worktree", "prune")
    git("branch", "-D", "pr/defendida", check=False)
    git("worktree", "add", "-b", "pr/defendida", str(WT), "pr/rsi-y-noticias")
    shutil.copytree(ROOT / "juez", WT / "_juez", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(ROOT / "contrato.md", WT / "contrato.md")
    shutil.copy(ROOT / "revision/informe.json", WT / "informe.json")
    (WT / ".venv").symlink_to(ROOT / ".venv")
    prompt = (ROOT / "prompts/03-defender.txt").read_text(encoding="utf-8")
    py = ".venv/bin/python -m pytest *"
    edits = ["backend/services/ai_service.py", "backend/services/indicators.py", "backend/requirements.txt",
             "docker-compose.yml", "backend/tests/test_api.py"]
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose", "--max-turns", "40", "--model", "sonnet",
           "--setting-sources", "project", "--max-budget-usd", "3.00", "--allowedTools",
           "Read", "Glob", "Grep", *[f"Edit({p})" for p in edits], "Write(backend/tests/test_sentiment_defense.py)",
           f"Bash({py})"]
    t0 = time.time()
    run = subprocess.run(cmd, cwd=WT, capture_output=True, text=True)
    wall = round(time.time() - t0, 1)
    events = [json.loads(l) for l in run.stdout.splitlines() if l.strip()]
    for e in events:
        if e.get("type") == "system" and e.get("subtype") == "init":
            e.clear(); e.update({"type": "system", "subtype": "init"})
    def clean(t):
        for p in {str(WT), str(WT.resolve())}:
            t = t.replace(p, "~/traderpulse")
        return re.sub(r"/Users/[^/\"\s]+", "~", t)
    (ROOT / "logs/defensa.jsonl").write_text("\n".join(clean(json.dumps(e, ensure_ascii=False)) for e in events) + "\n", encoding="utf-8")
    result = next((e for e in reversed(events) if e.get("type") == "result"), {})
    (WT / ".venv").unlink()
    shutil.rmtree(WT / "_juez"); (WT / "contrato.md").unlink(); (WT / "informe.json").unlink()
    git("add", "-A", cwd=WT)
    git("-c", "user.name=demo", "-c", "user.email=demo@example.com", "commit", "-qm", "Defensa: titulares como datos, esquema estricto y RSI definido", cwd=WT)
    (ROOT / "defensa").mkdir(exist_ok=True)
    (ROOT / "defensa/defensa.patch").write_text(git("diff", "pr/rsi-y-noticias..pr/defendida"), encoding="utf-8")
    medicion = {"turnos": result.get("num_turns"), "duracion_ms": result.get("duration_ms"), "segundos_de_reloj": wall,
                "costo_usd": result.get("total_cost_usd"), "subtype": result.get("subtype"),
                "reporte_del_agente": clean(result.get("result", ""))}
    (ROOT / "defensa/medicion.json").write_text(json.dumps(medicion, ensure_ascii=False, indent=2), encoding="utf-8")
    git("worktree", "remove", "--force", str(WT))
    print(json.dumps({k: v for k, v in medicion.items() if k != "reporte_del_agente"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
