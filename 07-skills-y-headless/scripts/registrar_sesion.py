#!/usr/bin/env python3
"""Records one headless session as stream-json, sanitized, and prints which Skill it loaded.

Usage:
    python3 scripts/registrar_sesion.py --fila 1 --salida logs/con-skill-fila1.jsonl
    python3 scripts/registrar_sesion.py --pedido "Cambia el color del botón..." --salida logs/sin-activar.jsonl

The session runs on a fresh copy of PawsMatch with the agregar-mascota Skill installed. The log keeps
every assistant and tool event; the large `init` event is reduced to the fields that matter.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agregar_en_lote as lote  # noqa: E402

ROOT = lote.ROOT


def sanitize(text: str, secrets: list[str]) -> str:
    for secret in sorted(set(filter(None, secrets)), key=len, reverse=True):
        text = text.replace(secret, "~")
    text = re.sub(r"(?:/private)?/var/folders/[^\"\s]+?/pawsmatch-lote-\w+/pawsmatch", "~/pawsmatch", text)
    text = re.sub(r"/Users/[^/\"\s]+", "~", text)
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fila", type=int, help="CSV row (1-based); builds the add-a-pet request")
    parser.add_argument("--pedido", help="free-form request, for the session that must not load the Skill")
    parser.add_argument("--salida", required=True)
    parser.add_argument("--brazo", choices=["sin-skill", "con-skill"], default="con-skill")
    parser.add_argument("--max-turns", type=int, default=12)
    parser.add_argument("--model", default="sonnet")
    args = parser.parse_args()

    rows = list(csv.DictReader(lote.CSV_PATH.open(encoding="utf-8")))
    prompt = lote.build_request(rows[args.fila - 1]) if args.fila else args.pedido
    cwd = lote.make_workdir(args.brazo)
    tools = lote.TOOLS_BASE + (lote.TOOLS_SKILL if args.brazo == "con-skill" else []) + (["Edit(app/src/**)"] if args.pedido else [])
    if args.fila and args.brazo == "sin-skill":
        prompt = lote.build_prompt("sin-skill", rows[args.fila - 1])
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
           "--max-turns", str(args.max_turns), "--model", args.model, "--setting-sources", "project",
           "--max-budget-usd", "1.00", "--allowedTools", *tools]
    run = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    secrets = [str(Path.home()), os.environ.get("USER", ""), socket.gethostname()]
    out_lines, skill_turn, validator_turns, turn = [], None, [], 0
    for line in run.stdout.splitlines():
        event = json.loads(line)
        event_skills = event.get("skills", [])
        if event.get("type") == "system" and event.get("subtype") != "init":
            continue  # keep only init; other system events carry the full command list of the machine
        if event.get("type") == "system" and event.get("subtype") == "init":
            event = {k: event.get(k) for k in ("type", "subtype", "model", "permissionMode", "claude_code_version")}
            event["agregar_mascota_instalada"] = "agregar-mascota" in json.dumps(event_skills)
        if event.get("type") == "assistant":
            turn += 1
            for block in event["message"].get("content", []):
                if block.get("type") == "tool_use":
                    if block["name"] == "Skill" and skill_turn is None:
                        skill_turn = turn
                    if block["name"] == "Bash" and "validar_mascotas" in json.dumps(block["input"]):
                        validator_turns.append(turn)
        out_lines.append(sanitize(json.dumps(event, ensure_ascii=False), secrets))
    out = ROOT / args.salida
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    shutil.rmtree(cwd.parent, ignore_errors=True)
    print(json.dumps({"salida": args.salida, "eventos": len(out_lines), "turnos_asistente": turn,
                      "turno_carga_skill": skill_turn, "turnos_validador": validator_turns}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
