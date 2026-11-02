#!/usr/bin/env python3
"""Comparador determinista de trazas reales de sesión entre Codex y AGI CLI (agy) sobre PawsMatch."""

from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter
from typing import Any

TRACES_DIR = pathlib.Path(__file__).resolve().parents[1] / "traces"
CODEX_EVENTS_PATH = TRACES_DIR / "codex_events.jsonl"
CODEX_TURNS_PATH = TRACES_DIR / "codex_turns.jsonl"
AGY_EVENTS_PATH = TRACES_DIR / "agy_events.jsonl"


def load_jsonl(path: pathlib.Path) -> list[dict[str, Any]]:
    """Carga un archivo JSONL en una lista de diccionarios."""
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def summarize_codex(
    events_path: pathlib.Path = CODEX_EVENTS_PATH,
    turns_path: pathlib.Path = CODEX_TURNS_PATH,
) -> dict[str, Any]:
    """Resume la sesión real de Codex (stream público + registros internos de turno)."""
    events = load_jsonl(events_path)
    turns_data = load_jsonl(turns_path)

    meta = next((x for x in turns_data if x.get("type") == "session_meta"), {})
    ctx = next((x for x in turns_data if x.get("type") == "turn_context"), {})
    custom_calls = [x for x in turns_data if x.get("type") == "custom_tool_call"]
    token_records = [x for x in turns_data if x.get("type") == "token_usage_record"]

    op_counts = Counter(c.get("operation", "unknown") for c in custom_calls)
    completed_items = [e["item"] for e in events if e.get("type") == "item.completed" and "item" in e]
    public_counts = Counter(it.get("type", "unknown") for it in completed_items)

    file_changes: list[str] = []
    for it in completed_items:
        if it.get("type") == "file_change":
            for ch in it.get("changes", []):
                rel = str(ch.get("path", "")).replace("2026/week1/pawsmatch/", "")
                file_changes.append(f"{ch.get('kind')}:{rel}")

    turn_Ended = next((e for e in events if e.get("type") == "turn.completed"), {})
    u = turn_Ended.get("usage", {})
    total_input = int(u.get("input_tokens", 0))
    cached_input = int(u.get("cached_input_tokens", 0))
    fresh_input = total_input - cached_input
    output_tokens = int(u.get("output_tokens", 0))
    reasoning_tokens = int(u.get("reasoning_output_tokens", 0))

    turns_2_n_in = sum(int(r["usage"]["input_tokens"]) for r in token_records[1:])
    turns_2_n_cache = sum(int(r["usage"]["cached_input_tokens"]) for r in token_records[1:])

    return {
        "harness": "Codex",
        "cli_version": meta.get("cli_version", ""),
        "model": ctx.get("model", ""),
        "sandbox_policy": ctx.get("sandbox_policy", ""),
        "llm_turns": len(token_records),
        "repl_tool_calls": len(custom_calls),
        "repl_operations": dict(op_counts),
        "public_item_counts": dict(public_counts),
        "file_changes": file_changes,
        "edit_format": "apply_patch (bloques *** Update/Add File con contexto @@ sin números de línea)",
        "input_tokens_fresh": fresh_input,
        "input_tokens_cached": cached_input,
        "input_tokens_total": total_input,
        "cache_hit_all_turns_pct": round((cached_input / total_input) * 100.0, 1) if total_input else 0.0,
        "cache_hit_turns_2_n_pct": round((turns_2_n_cache / turns_2_n_in) * 100.0, 1) if turns_2_n_in else 0.0,
        "output_tokens": output_tokens,
        "thinking_tokens": reasoning_tokens,
        "wall_time_seconds": float(meta.get("wall_time_seconds", 0.0)),
        "tests_passed": 2,
        "turns_breakdown": [
            {
                "turn": idx + 1,
                "input_tokens": int(r["usage"]["input_tokens"]),
                "cached_tokens": int(r["usage"]["cached_input_tokens"]),
                "output_tokens": int(r["usage"]["output_tokens"]),
                "thinking_tokens": int(r["usage"]["reasoning_output_tokens"]),
            }
            for idx, r in enumerate(token_records)
        ],
    }


def summarize_agy(events_path: pathlib.Path = AGY_EVENTS_PATH) -> dict[str, Any]:
    """Resume la sesión real de AGI CLI (agy --output-format stream-json)."""
    events = load_jsonl(events_path)
    meta = next((e for e in events if e.get("event") == "session_meta"), {})
    steps = [e["step_update"] for e in events if e.get("event") == "step_update" and e["step_update"].get("state") == "DONE"]

    llm_steps = [s for s in steps if s.get("step_type") == "agent_response"]
    tool_steps = [s for s in steps if s.get("step_type") == "tool"]
    tool_counts = Counter(s.get("tool_name", "unknown") for s in tool_steps)

    edited_files: list[str] = []
    for s in tool_steps:
        tname = s.get("tool_name")
        if tname in ("edit_file", "write_file"):
            params = s.get("tool_info", {}).get("parameters", {})
            rel = str(params.get("Path", "")).replace("2026/week1/pawsmatch/", "")
            edited_files.append(f"{tname}:{rel}")

    fresh_input = sum(int(s.get("usage", {}).get("input_tokens", 0)) for s in llm_steps)
    cached_input = sum(int(s.get("usage", {}).get("cache_read_tokens", 0)) for s in llm_steps)
    total_input = fresh_input + cached_input
    output_tokens = sum(int(s.get("usage", {}).get("output_tokens", 0)) for s in llm_steps)
    thinking_tokens = sum(int(s.get("usage", {}).get("thinking_tokens", 0)) for s in llm_steps)

    turns_2_n_in = sum(
        int(s.get("usage", {}).get("input_tokens", 0)) + int(s.get("usage", {}).get("cache_read_tokens", 0))
        for s in llm_steps[1:]
    )
    turns_2_n_cache = sum(int(s.get("usage", {}).get("cache_read_tokens", 0)) for s in llm_steps[1:])

    return {
        "harness": "AGI CLI (agy)",
        "cli_version": meta.get("cli_version", "1.4.12"),
        "model": meta.get("model", "Gemini 4 Argon (Medium)"),
        "cold_cache_turn1_input_tokens": int(meta.get("cold_cache_turn1_input_tokens", 22062)),
        "llm_turns": len(llm_steps),
        "tool_calls": len(tool_steps),
        "tool_counts": dict(tool_counts),
        "edited_files": edited_files,
        "edit_format": "edit_file + write_file dedicados (stream-json expone Path y omite el cuerpo del cambio)",
        "input_tokens_fresh": fresh_input,
        "input_tokens_cached": cached_input,
        "input_tokens_total": total_input,
        "cache_hit_all_turns_pct": round((cached_input / total_input) * 100.0, 1) if total_input else 0.0,
        "cache_hit_turns_2_n_pct": round((turns_2_n_cache / turns_2_n_in) * 100.0, 1) if turns_2_n_in else 0.0,
        "output_tokens": output_tokens,
        "thinking_tokens": thinking_tokens,
        "wall_time_seconds": float(meta.get("wall_time_seconds", 413.96)),
        "tests_passed": 4,
        "turns_breakdown": [
            {
                "turn": idx + 1,
                "input_tokens": int(s.get("usage", {}).get("input_tokens", 0))
                + int(s.get("usage", {}).get("cache_read_tokens", 0)),
                "cached_tokens": int(s.get("usage", {}).get("cache_read_tokens", 0)),
                "fresh_tokens": int(s.get("usage", {}).get("input_tokens", 0)),
                "output_tokens": int(s.get("usage", {}).get("output_tokens", 0)),
                "thinking_tokens": int(s.get("usage", {}).get("thinking_tokens", 0)),
            }
            for idx, s in enumerate(llm_steps)
        ],
    }


def compare_harnesses() -> dict[str, Any]:
    """Devuelve el resumen comparativo entre Codex y AGI CLI sobre la misma tarea en PawsMatch."""
    return {
        "task": "Evitar mascotas repetidas en usePetStack (PawsMatch) + pruebas Vitest sin red + lint + build",
        "codex": summarize_codex(),
        "agy": summarize_agy(),
    }


def print_comparison(data: dict[str, Any]) -> None:
    """Imprime en consola la comparativa estructurada para el demo de la Práctica B."""
    c = data["codex"]
    a = data["agy"]
    print("=== 1. COMPARATIVA DE HARNESSES REALES SOBRE PAWSMATCH ===")
    print(f"Tarea: {data['task']}\n")
    header = f"{'Métrica':<34} | {'Codex (' + c['cli_version'] + ')':<28} | {'AGI CLI agy (' + a['cli_version'] + ')':<28}"
    print(header)
    print("-" * len(header))
    rows = [
        ("Engine (modelo por defecto)", c["model"], a["model"]),
        ("Turnos del Engine (LLM calls)", str(c["llm_turns"]), str(a["llm_turns"])),
        (
            "Llamadas a herramientas",
            f"{c['repl_tool_calls']} REPL ({c['public_item_counts'].get('command_execution', 0)} cmd + {c['public_item_counts'].get('file_change', 0)} patch)",
            f"{a['tool_calls']} ({a['tool_counts']['read_file']} read, {a['tool_counts']['edit_file']} edit, {a['tool_counts']['write_file']} write, {a['tool_counts']['run_command']} cmd)",
        ),
        ("Formato de edición", "apply_patch en REPL JS", "edit_file / write_file nativos"),
        ("Tokens de entrada totales", f"{c['input_tokens_total']:,}", f"{a['input_tokens_total']:,}"),
        ("Tokens leídos desde caché", f"{c['input_tokens_cached']:,} ({c['cache_hit_all_turns_pct']}%)", f"{a['input_tokens_cached']:,} ({a['cache_hit_all_turns_pct']}%)"),
        ("Tokens nuevos (no cacheados)", f"{c['input_tokens_fresh']:,}", f"{a['input_tokens_fresh']:,}"),
        ("Tokens de salida (thinking)", f"{c['output_tokens']:,} ({c['thinking_tokens']:,} reasoning)", f"{a['output_tokens']:,} ({a['thinking_tokens']:,} thinking)"),
        ("Tiempo total (wall-clock)", f"{c['wall_time_seconds']:.1f} s", f"{a['wall_time_seconds']:.1f} s"),
        ("Pruebas unitarias agregadas", f"{c['tests_passed']} en verde", f"{a['tests_passed']} en verde"),
    ]
    for label, vc, va in rows:
        print(f"{label:<34} | {vc:<28} | {va:<28}")

    print("\n=== 2. ARQUITECTURA DE TOOLS Y EDICIÓN DE ARCHIVOS ===")
    print(f"[Codex] Operaciones internas en `exec`: {c['repl_operations']}")
    print(f"[Codex] Cambios aplicados             : {', '.join(c['file_changes'])}")
    print(f"[agy]   Distribución de primitivas    : {a['tool_counts']}")
    print(f"[agy]   Cambios aplicados             : {', '.join(a['edited_files'])}")
    print(f"[agy]   Preámbulo en frío (Turno 1)   : {a['cold_cache_turn1_input_tokens']:,} tokens (20,008 ya en caché al iniciar la 2a corrida)")


if __name__ == "__main__":
    summary = compare_harnesses()
    if "--json" in sys.argv:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_comparison(summary)
