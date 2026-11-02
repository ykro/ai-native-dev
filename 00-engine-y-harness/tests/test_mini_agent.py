"""Suite de verificación determinista para el Harness mínimo y el inspector de trazas HTTP."""

from __future__ import annotations

import pathlib
import shutil
import sys

import pytest

ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import src.mini_agent as mini_agent  # noqa: E402
from src.http_trace_inspector import load_trace, summarize_trace  # noqa: E402
from src.mini_agent import (  # noqa: E402
    _resolve_safe_path,
    _scripted_demo_engine,
    dispatch_tool,
    edit_file,
    read_file,
    run_agent_loop,
    run_bash,
    write_file,
)


def test_resolve_safe_path_blocks_traversal() -> None:
    with pytest.raises(ValueError, match="Ruta fuera del espacio de trabajo"):
        _resolve_safe_path("../../etc/passwd")


def test_read_file_missing_returns_actionable_dict() -> None:
    res = read_file("ruta/inexistente.py")
    assert res["ok"] is False
    assert res["codigo"] == "ARCHIVO_NO_ENCONTRADO"
    assert "accion_sugerida" in res


def test_read_file_respects_max_lines() -> None:
    res = read_file("sandbox_app/catalog_filter.py", max_lines=5)
    assert res["ok"] is True
    assert res["returned_lines"] == 5
    assert res["total_lines"] > 5


def test_write_and_edit_file_uniqueness_contracts() -> None:
    rel = "sandbox_app/_tmp_test_target.py"
    target = _resolve_safe_path(rel)
    try:
        w = write_file(rel, "def a():\n    return []\n\ndef b():\n    return []\n")
        assert w["ok"] is True

        no_match = edit_file(rel, "return None", "return []")
        assert no_match["ok"] is False
        assert no_match["codigo"] == "BLOQUE_NO_COINCIDE"

        ambiguous = edit_file(rel, "return []", "return [1]")
        assert ambiguous["ok"] is False
        assert ambiguous["codigo"] == "BLOQUE_AMBIGUO"
        assert ambiguous["coincidencias"] == 2

        unique = edit_file(rel, "def a():\n    return []", "def a():\n    return [1]")
        assert unique["ok"] is True
        assert unique["replaced"] == 1
    finally:
        if target.exists():
            target.unlink()


def test_run_bash_blocks_destructive_commands() -> None:
    res = run_bash("rm -rf /")
    assert res["ok"] is False
    assert res["codigo"] == "COMANDO_BLOQUEADO"


def test_agent_loop_recovers_from_ambiguous_edit_and_passes_pytest(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # El loop corre sobre una copia: así correr pytest dentro del repo nunca toca sandbox_app/ real.
    shutil.copytree(ROOT_DIR / "sandbox_app", tmp_path / "sandbox_app", ignore=shutil.ignore_patterns("__pycache__"))
    monkeypatch.setattr(mini_agent, "WORKSPACE_ROOT", tmp_path)
    catalog_path = _resolve_safe_path("sandbox_app/catalog_filter.py")
    raw = catalog_path.read_text(encoding="utf-8")
    buggy = raw.replace(
        "    target_cat = category.strip().lower()\n    if not items or not target_cat:",
        "    if not items or not category.strip():",
    ).replace(
        'str(item.get("category", "")).strip().lower() == target_cat',
        'item.get("category") == category',
    )
    catalog_path.write_text(buggy, encoding="utf-8")

    loop_res = run_agent_loop(
        "Corrige el bug case-sensitive en filter_by_category y verifica con pytest.",
        _scripted_demo_engine,
    )
    assert loop_res["ok"] is True
    assert loop_res["turns"] == 5

    tool_msgs = [m for m in loop_res["messages"] if m["role"] == "tool"]
    codes = [m["content"].get("codigo") for m in tool_msgs if not m["content"].get("ok")]
    assert "BLOQUE_AMBIGUO" in codes
    assert any(m["name"] == "run_bash" and m["content"].get("exit_code") == 0 for m in tool_msgs)


def test_http_trace_inspector_metrics() -> None:
    trace = load_trace()
    summary = summarize_trace(trace)
    assert summary["user_prompt_tokens"] == 20
    assert summary["preamble_tokens"] == 12420
    assert summary["cache_hit_ratio_turns_2_5_pct"] > 92.0
    assert dispatch_tool("unknown_tool", {})["codigo"] == "HERRAMIENTA_DESCONOCIDA"


def test_gemini_engine_adapter_and_trace_record() -> None:
    from src.gemini_engine import to_function_declarations, usage_of
    from src.harness_trace_compare import load_jsonl
    from src.mini_agent import TOOLS_SCHEMAS

    decls = to_function_declarations(TOOLS_SCHEMAS)
    assert [d["name"] for d in decls] == ["read_file", "write_file", "edit_file", "run_bash"]
    assert all("parameters" in d for d in decls)

    class _DummyMeta:
        prompt_token_count = 956
        cached_content_token_count = 0
        candidates_token_count = 24
        thoughts_token_count = 27

    assert usage_of(_DummyMeta()) == {
        "input_tokens": 956,
        "cached_tokens": 0,
        "output_tokens": 24,
        "thinking_tokens": 27,
    }

    gemini_rows = load_jsonl(ROOT_DIR / "traces" / "gemini_run.jsonl")
    assert len(gemini_rows) >= 6
    tools_used = [t for r in gemini_rows for t in r.get("tool_calls", [])]
    assert "read_file" in tools_used
    assert "edit_file" in tools_used
    assert "run_bash" in tools_used


def test_harness_trace_compare_and_sanitization() -> None:
    from src.harness_trace_compare import compare_harnesses

    comp = compare_harnesses()
    codex = comp["codex"]
    agy = comp["agy"]

    assert codex["model"] == "gpt-6-luna"
    assert codex["llm_turns"] == 9
    assert codex["repl_tool_calls"] == 8
    assert codex["repl_operations"] == {"exec_command": 3, "apply_patch": 4, "exec_command_parallel": 1}
    assert codex["input_tokens_total"] == 215273
    assert codex["input_tokens_cached"] == 186752
    assert codex["cache_hit_all_turns_pct"] == 86.8
    assert codex["output_tokens"] == 2614
    assert codex["thinking_tokens"] == 479

    assert agy["model"] == "Gemini 4 Argon (Medium)"
    assert agy["llm_turns"] == 19
    assert agy["tool_calls"] == 25
    assert agy["tool_counts"] == {"read_file": 10, "run_command": 12, "edit_file": 2, "write_file": 1}
    assert agy["input_tokens_fresh"] == 55615
    assert agy["input_tokens_cached"] == 730575
    assert agy["input_tokens_total"] == 786190
    assert agy["cache_hit_all_turns_pct"] == 92.9
    assert agy["output_tokens"] == 18330
    assert agy["thinking_tokens"] == 12931

    # Ningún archivo de trazas puede contener rutas personales ni identificadores locales
    forbidden = ("/Users/", "/private/tmp", "ykro", "aacs85", "claude-501", "ai-experiments")
    for trace_file in (ROOT_DIR / "traces").glob("*"):
        text = trace_file.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"Encontrado '{token}' en {trace_file.name}"
