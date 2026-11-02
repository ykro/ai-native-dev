"""Resume un log de sesión headless de Claude Code (--output-format stream-json).

Cuenta turnos, llamadas a herramientas, intentos fallidos y tokens. Separa los
intentos que bloqueó el sistema de permisos de los que fallaron al ejecutarse.
No llama a ningún modelo; solo lee el log.

Uso:
    python3 scripts/resumen_sesion.py logs/03-iterar.jsonl [--json]
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


def summarize(path: Path) -> dict:
    tools: Counter[str] = Counter()
    failed = 0
    bash_cmds: list[tuple[str, str]] = []
    pending: dict[str, str] = {}
    failed_cmds: list[tuple[str, str]] = []
    result: dict = {}
    model = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        ev = json.loads(line)
        kind = ev.get("type")
        if kind == "system" and ev.get("subtype") == "init":
            model = ev.get("model", "")
        elif kind == "assistant":
            for block in ev.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    name = block.get("name", "?")
                    tools[name] += 1
                    label = name
                    if name == "Bash":
                        label = block.get("input", {}).get("command", "")
                        bash_cmds.append((block.get("id", ""), label))
                    pending[block.get("id", "")] = label
        elif kind == "user":
            content = ev.get("message", {}).get("content", [])
            if isinstance(content, list):
                for block in content:
                    if block.get("type") == "tool_result" and block.get("is_error"):
                        failed += 1
                        tid = block.get("tool_use_id", "")
                        failed_cmds.append((tid, pending.get(tid, "?")))
        elif kind == "result":
            result = ev
    denied_ids = {d.get("tool_use_id") for d in result.get("permission_denials", [])}
    denied = [label for tid, label in failed_cmds if tid in denied_ids]
    errors = [label for tid, label in failed_cmds if tid not in denied_ids]
    judge_runs = [c for tid, c in bash_cmds if "npm run juez" in c and tid not in denied_ids]
    usage = result.get("usage", {})
    fresh_in = usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0)
    cached_in = usage.get("cache_read_input_tokens", 0)
    out = usage.get("output_tokens", 0)
    return {
        "log": path.name,
        "model": model,
        "turns": result.get("num_turns"),
        "tool_calls": sum(tools.values()),
        "tools": dict(tools.most_common()),
        "failed_tool_results": failed,
        "denied_by_permissions": denied,
        "failed_on_execution": errors,
        "judge_runs": len(judge_runs),
        "bash_commands": [c for _, c in bash_cmds],
        "input_tokens_fresh": fresh_in,
        "input_tokens_cached": cached_in,
        "output_tokens": out,
        "total_tokens": fresh_in + cached_in + out,
        "duration_s": round(result.get("duration_ms", 0) / 1000, 1),
        "cost_usd": round(result.get("total_cost_usd", 0.0), 4),
        "is_error": result.get("is_error"),
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    data = summarize(Path(argv[1]))
    if "--json" in argv:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print(f"log                {data['log']}  ({data['model']})")
    print(f"turnos             {data['turns']}")
    print(f"herramientas       {data['tool_calls']}  {data['tools']}")
    print(f"intentos fallidos  {data['failed_tool_results']}"
          f"  (bloqueados por permisos {len(data['denied_by_permissions'])},"
          f" fallaron al ejecutarse {len(data['failed_on_execution'])})")
    for cmd in data["failed_on_execution"]:
        print(f"   - {cmd.splitlines()[0][:90] if cmd else '?'}")
    print(f"corridas del juez  {data['judge_runs']}")
    print(f"tokens entrada     {data['input_tokens_fresh']:,} nuevos + {data['input_tokens_cached']:,} desde caché")
    print(f"tokens salida      {data['output_tokens']:,}")
    print(f"duración           {data['duration_s']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
