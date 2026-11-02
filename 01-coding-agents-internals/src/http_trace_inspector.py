#!/usr/bin/env python3
"""Inspector de trazas HTTP y economía de tokens (Prompt Caching) para un Coding Agent."""

from __future__ import annotations

import json
import pathlib
from typing import Any

TRACE_PATH = pathlib.Path(__file__).resolve().parents[1] / "traces" / "session_5_turns.json"


def load_trace(path: pathlib.Path = TRACE_PATH) -> dict[str, Any]:
    """Carga el archivo JSON de la traza HTTP."""
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_trace(trace: dict[str, Any]) -> dict[str, Any]:
    """Calcula métricas agregadas de preámbulo, lectura de caché y ahorro de tokens."""
    preamble = trace["preamble_breakdown"]["total_preamble_tokens"]
    prompt_tokens = trace["user_prompt"]["tokens"]
    total_fresh_input = sum(t["usage"]["input_tokens"] + t["usage"]["cache_creation_input_tokens"] for t in trace["turns"])
    total_cache_read = sum(t["usage"]["cache_read_input_tokens"] for t in trace["turns"])
    total_output = sum(t["usage"]["output_tokens"] for t in trace["turns"])
    turns_2_to_5_total = sum(
        t["usage"]["input_tokens"] + t["usage"]["cache_creation_input_tokens"] + t["usage"]["cache_read_input_tokens"]
        for t in trace["turns"][1:]
    )
    cache_hit_ratio = (total_cache_read / turns_2_to_5_total) * 100.0 if turns_2_to_5_total else 0.0
    return {
        "user_prompt_tokens": prompt_tokens,
        "preamble_tokens": preamble,
        "preamble_to_prompt_ratio": round(preamble / prompt_tokens, 1),
        "total_fresh_input_tokens": total_fresh_input,
        "total_cache_read_tokens": total_cache_read,
        "total_output_tokens": total_output,
        "cache_hit_ratio_turns_2_5_pct": round(cache_hit_ratio, 1),
    }


def print_report(trace: dict[str, Any]) -> None:
    """Imprime en consola el desglose del payload HTTP y la tabla de Token Economics."""
    pb = trace["preamble_breakdown"]
    summary = summarize_trace(trace)
    print("=== 1. DISECCIÓN DEL PAYLOAD HTTP (TURNO 1) ===")
    print(f"Prompt del usuario : \"{trace['user_prompt']['text']}\" ({summary['user_prompt_tokens']} tokens)")
    print(f"Preámbulo oculto   : {summary['preamble_tokens']:,} tokens ({summary['preamble_to_prompt_ratio']}x el mensaje del usuario)")
    print(f"  - System operational rules : {pb['system_operational_rules_tokens']:,} tokens")
    print(f"  - Tools JSON Schemas       : {pb['tools_json_schemas_tokens']:,} tokens")
    print(f"  - Memoria AGENTS.md        : {pb['agents_md_memory_tokens']:,} tokens")
    print(f"  - Snapshot de Git status   : {pb['git_workspace_snapshot_tokens']:,} tokens")

    print("\n=== 2. TOKEN ECONOMICS & PROMPT CACHING (5 TURNOS) ===")
    print(f"{'Turno':<6} | {'Input Nuevo':>11} | {'Cache Create':>12} | {'Cache Read':>11} | {'Output':>7} | {'Latencia':>8} | {'Acción'}")
    print("-" * 98)
    for t in trace["turns"]:
        u = t["usage"]
        print(
            f"T{t['turn']:<5} | {u['input_tokens']:>11,} | {u['cache_creation_input_tokens']:>12,} | "
            f"{u['cache_read_input_tokens']:>11,} | {u['output_tokens']:>7,} | {t['latency_ms']:>6}ms | {t['action']}"
        )
    print("-" * 98)
    print(
        f"Tasa de acierto de Prompt Cache (Turnos 2..5): {summary['cache_hit_ratio_turns_2_5_pct']}% "
        f"(Cache Read acumulado: {summary['total_cache_read_tokens']:,} tokens)"
    )

    print("\n=== 3. SIMULACIÓN DE ANTIPATRONES DE CONTEXTO ===")
    ap = trace["anti_patterns_simulation"]
    print(f"[!] Volcado bash sin recorte (8,000 líneas) : +{ap['unclipped_bash_dump_8000_lines']['extra_tokens_per_turn']:,} tokens/turno -> {ap['unclipped_bash_dump_8000_lines']['impact']}")
    print(f"[!] Mutar el prefijo system en cada turno   : cache_read={ap['mutating_system_prefix_each_turn']['cache_read_input_tokens']} -> {ap['mutating_system_prefix_each_turn']['impact']}")


if __name__ == "__main__":
    print_report(load_trace())
