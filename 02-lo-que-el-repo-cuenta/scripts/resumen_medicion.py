"""Resume los logs de sesión headless (stream JSON de Codex) de la medición antes vs. después.

Cuenta pasos del modelo, comandos de terminal ejecutados, comandos fallidos (exit != 0),
archivos modificados, tokens de entrada (nuevos y desde caché), tokens de salida y duración.
No realiza llamadas de red ni depende de ningún modelo externo.

Uso:
    python3 scripts/resumen_medicion.py medicion/logs/01-antes.jsonl medicion/logs/02-despues.jsonl [--json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def summarize(path: Path) -> dict:
    steps = 0
    commands: list[tuple[int, str]] = []
    failed_commands: list[tuple[int, str]] = []
    file_changes = 0
    messages = 0
    input_tokens = 0
    cached_tokens = 0
    output_tokens = 0
    duration_s = 0.0
    model = "codex-headless"

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        ev = json.loads(line)
        kind = ev.get("type")
        if kind == "session.meta":
            model = ev.get("model", model)
            duration_s = float(ev.get("duration_s", 0.0))
        elif kind == "turn.completed":
            usage = ev.get("usage", {})
            input_tokens += usage.get("input_tokens", 0)
            cached_tokens += usage.get("cached_input_tokens", 0)
            output_tokens += usage.get("output_tokens", 0)
            if "duration_s" in ev:
                duration_s = float(ev["duration_s"])
        elif kind == "item.completed":
            steps += 1
            item = ev.get("item", {})
            itype = item.get("type")
            if itype == "command_execution":
                cmd = item.get("command", "")
                if cmd.startswith("/bin/zsh -lc "):
                    cmd = cmd[len("/bin/zsh -lc "):].strip("'\"")
                exit_code = int(item.get("exit_code") or 0)
                commands.append((exit_code, cmd))
                if exit_code != 0:
                    failed_commands.append((exit_code, cmd))
            elif itype == "file_change":
                file_changes += len(item.get("changes", []))
            elif itype == "agent_message":
                messages += 1

    fresh_tokens = max(0, input_tokens - cached_tokens)
    return {
        "log": path.name,
        "model": model,
        "steps": steps,
        "commands_total": len(commands),
        "failed_commands_count": len(failed_commands),
        "failed_commands": [cmd for _, cmd in failed_commands],
        "commands": [{"exit_code": ec, "command": cmd} for ec, cmd in commands],
        "file_changes": file_changes,
        "messages": messages,
        "input_tokens_total": input_tokens,
        "input_tokens_fresh": fresh_tokens,
        "input_tokens_cached": cached_tokens,
        "output_tokens": output_tokens,
        "duration_s": round(duration_s, 1),
    }


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv[1:] if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 2
    rows = [summarize(p) for p in paths]
    if "--json" in argv:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    for r in rows:
        print(f"log                   {r['log']}")
        print(f"pasos del agente      {r['steps']}  (comandos {r['commands_total']}, ediciones {r['file_changes']}, mensajes {r['messages']})")
        print(f"comandos fallidos     {r['failed_commands_count']}")
        for cmd in r["failed_commands"]:
            print(f"   - {cmd.splitlines()[0][:90]}")
        print(f"tokens de entrada     {r['input_tokens_total']:,}  ({r['input_tokens_fresh']:,} nuevos + {r['input_tokens_cached']:,} desde caché)")
        print(f"tokens de salida      {r['output_tokens']:,}")
        print(f"duración              {r['duration_s']} s")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
