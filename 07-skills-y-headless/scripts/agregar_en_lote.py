#!/usr/bin/env python3
"""Adds the pets of lote/mascotas-nuevas.csv to PawsMatch with one headless agent per row.

The script owns the loop: it decides how many rows exist, how many turns each agent may spend and
which tools it may use. After every call it ignores what the agent says and runs the judge itself.

Arms:
  sin-skill  copy of PawsMatch without .claude/skills; the agent receives the pasted paragraph.
  con-skill  copy of PawsMatch with the agregar-mascota Skill; the agent receives a one-line request.

Each repetition starts from a fresh copy; the rows of a repetition run in order on that copy, so ids
keep growing. A row that fails the judge is rolled back before the next one.

Usage:
    python3 scripts/agregar_en_lote.py --brazo sin-skill --repeticiones 3
    python3 scripts/agregar_en_lote.py --brazo con-skill --repeticiones 3
Exit code: 0 if every row is valid, 1 otherwise.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAWSMATCH = ROOT / "pawsmatch"
VALIDATOR = PAWSMATCH / ".claude/skills/agregar-mascota/scripts/validar_mascotas.py"
PETS_REL = "app/src/data/pets.json"
VALIDATOR_REL = ".claude/skills/agregar-mascota/scripts/validar_mascotas.py"
CSV_PATH = ROOT / "lote/mascotas-nuevas.csv"
PASTED_PROMPT = ROOT / "lote/prompt-pegado.txt"

# The script, not the agent, decides what the agent can touch. Anything outside this list is denied
# because nobody answers permission prompts in headless mode.
TOOLS_BASE = ["Read", f"Edit({PETS_REL})"]
TOOLS_SKILL = ["Skill", f"Bash(python3 {VALIDATOR_REL} *)"]


def build_request(row: dict[str, str]) -> str:
    return (
        f"Agrega una mascota nueva llamada {row['nombre']}. "
        f"Sus rasgos de personalidad son: {row['rasgo1']} y {row['rasgo2']}."
    )


def build_prompt(arm: str, row: dict[str, str]) -> str:
    request = build_request(row)
    if arm == "sin-skill":
        return PASTED_PROMPT.read_text(encoding="utf-8").strip() + "\n\n" + request
    return request


def make_workdir(arm: str) -> Path:
    # resolve(): on macOS /var is a symlink to /private/var; the permission rules must see one single spelling of the path
    work = Path(tempfile.mkdtemp(prefix="pawsmatch-lote-")).resolve()
    ignore = ["node_modules", "dist"] + ([".claude"] if arm == "sin-skill" else [])
    shutil.copytree(PAWSMATCH, work / "pawsmatch", ignore=shutil.ignore_patterns(*ignore), symlinks=True)
    return work / "pawsmatch"


def judge(pets_file: Path) -> tuple[int, str]:
    run = subprocess.run([sys.executable, str(VALIDATOR), str(pets_file)], capture_output=True, text=True)
    return run.returncode, run.stdout.strip()


def call_agent(arm: str, prompt: str, cwd: Path, max_turns: int, model: str) -> tuple[dict, int]:
    tools = TOOLS_BASE + (TOOLS_SKILL if arm == "con-skill" else [])
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--max-turns", str(max_turns),
        "--model", model,
        "--setting-sources", "project",
        "--max-budget-usd", "1.00",
        "--allowedTools", *tools,
    ]
    run = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    try:
        output = json.loads(run.stdout)
    except json.JSONDecodeError:
        output = {"is_error": True, "result": run.stdout[-500:] + run.stderr[-500:]}
    return output, run.returncode


def denials(output: dict) -> dict[str, int]:
    """Counts the tool calls the permission list denied, by tool name."""
    counts: dict[str, int] = {}
    for item in output.get("permission_denials") or []:
        counts[item.get("tool_name", "?")] = counts.get(item.get("tool_name", "?"), 0) + 1
    return counts


def failure_reason(code: int, message: str, added: int, denied: dict[str, int]) -> list[str]:
    if code != 0:
        return [l.strip("- ").strip() for l in message.splitlines()[1:]] or [message]
    if added != 1:
        reason = "la mascota no quedó en el archivo (el archivo sigue válido pero sin la fila nueva)"
        if denied.get("Edit"):
            reason += f"; la edición fue denegada por la lista de permisos ({denied['Edit']} vez/veces)"
        return [reason]
    return []


def average(values: list[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def reannotate(arm: str) -> int:
    path = ROOT / f"lote/resultado-{arm}.json"
    summary = json.loads(path.read_text(encoding="utf-8"))
    for row in summary["filas"]:
        output = json.loads((ROOT / f"lote/crudo-{arm}/rep{row['repeticion']}-fila{row['fila']}.json").read_text(encoding="utf-8"))
        row["denegaciones_de_permiso"] = denials(output)
        if not row["valido"]:
            row["errores"] = failure_reason(row["codigo_validador"], "", 0 if row["codigo_validador"] == 0 else 1, denials(output))
            row["revertida"] = True
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Anotado {path.name}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--brazo", choices=["sin-skill", "con-skill"], required=True)
    parser.add_argument("--repeticiones", type=int, default=3)
    parser.add_argument("--max-turns", type=int, default=12)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--reanotar", action="store_true", help="refill motives and denials in an existing resultado from lote/crudo-*")
    args = parser.parse_args()
    if args.reanotar:
        return reannotate(args.brazo)

    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    raw_dir = ROOT / f"lote/crudo-{args.brazo}"
    raw_dir.mkdir(parents=True, exist_ok=True)
    version = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()

    results: list[dict] = []
    for rep in range(1, args.repeticiones + 1):
        cwd = make_workdir(args.brazo)
        pets_file = cwd / PETS_REL
        for index, row in enumerate(rows, start=1):
            snapshot = pets_file.read_text(encoding="utf-8")
            output, exit_code = call_agent(args.brazo, build_prompt(args.brazo, row), cwd, args.max_turns, args.model)
            (raw_dir / f"rep{rep}-fila{index}.json").write_text(
                json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
            code, message = judge(pets_file)
            added = [p for p in json.loads(pets_file.read_text(encoding="utf-8")) if p.get("name") == row["nombre"]] \
                if code == 0 else []
            rolled_back = code != 0 or len(added) != 1
            if rolled_back:
                pets_file.write_text(snapshot, encoding="utf-8")
            record = {
                "repeticion": rep,
                "fila": index,
                "nombre": row["nombre"],
                "valido": code == 0 and len(added) == 1,
                "codigo_validador": code,
                "errores": failure_reason(code, message, len(added), denials(output)),
                "denegaciones_de_permiso": denials(output),
                "revertida": rolled_back,
                "turnos": output.get("num_turns"),
                "duracion_ms": output.get("duration_ms"),
                "costo_usd": output.get("total_cost_usd"),
                "subtype": output.get("subtype"),
                "codigo_salida_claude": exit_code,
            }
            results.append(record)
            print(f"[{args.brazo}] rep {rep} fila {index} {row['nombre']}: "
                  f"{'valida' if record['valido'] else 'INVALIDA'} turnos={record['turnos']} "
                  f"costo={record['costo_usd']}", flush=True)
        shutil.rmtree(cwd.parent, ignore_errors=True)

    valid = [r for r in results if r["valido"]]
    summary = {
        "brazo": args.brazo,
        "claude_version": version,
        "modelo": args.model,
        "max_turns": args.max_turns,
        "repeticiones": args.repeticiones,
        "llamadas": len(results),
        "validas": len(valid),
        "turnos_promedio": average([r["turnos"] for r in results if r["turnos"] is not None]),
        "segundos_promedio": average([r["duracion_ms"] / 1000 for r in results if r["duracion_ms"] is not None]),
        "costo_promedio_usd": average([r["costo_usd"] for r in results if r["costo_usd"] is not None]),
        "costo_total_usd": round(sum(r["costo_usd"] or 0 for r in results), 4),
        "filas": results,
    }
    out = ROOT / f"lote/resultado-{args.brazo}.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{summary['validas']}/{summary['llamadas']} válidas. Resultado en {out.relative_to(ROOT)}")
    return 0 if len(valid) == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
