"""Suite de verificación determinista para el Harness mínimo y el inspector de trazas HTTP."""

from __future__ import annotations

import pathlib
import sys

import pytest

ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

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


def test_agent_loop_recovers_from_ambiguous_edit_and_passes_pytest() -> None:
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
