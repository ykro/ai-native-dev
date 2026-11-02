#!/usr/bin/env python3
"""Harness mínimo de un Coding Agent con las 4 herramientas primitivas y su loop de ejecución."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess, sys
from typing import Any, Callable

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parents[1]
_VENV_BIN = str(pathlib.Path(sys.executable).parent)  # bin del interprete que corre el agente


def _resolve_safe_path(rel_path: str) -> pathlib.Path:
    """Resuelve una ruta relativa y garantiza que permanezca dentro de WORKSPACE_ROOT."""
    candidate = (WORKSPACE_ROOT / rel_path).resolve()
    if not candidate.is_relative_to(WORKSPACE_ROOT):
        raise ValueError(f"Ruta fuera del espacio de trabajo permitida -> {rel_path}")
    return candidate


def read_file(path: str, max_lines: int = 200) -> dict[str, Any]:
    """Lee un archivo del espacio de trabajo acotando la cantidad máxima de líneas devueltas."""
    target = _resolve_safe_path(path)
    if not target.exists():
        return {
            "ok": False,
            "codigo": "ARCHIVO_NO_ENCONTRADO",
            "accion_sugerida": "Verifica la ruta relativa con run_bash usando ls o find antes de leer",
        }
    lines = target.read_text(encoding="utf-8").splitlines()
    clipped = lines[:max_lines]
    return {
        "ok": True,
        "path": path,
        "total_lines": len(lines),
        "returned_lines": len(clipped),
        "content": "\n".join(clipped),
    }


def write_file(path: str, content: str, dry_run: bool = False) -> dict[str, Any]:
    """Escribe o sobrescribe un archivo completo dentro del espacio de trabajo."""
    target = _resolve_safe_path(path)
    if dry_run:
        return {"ok": True, "dry_run": True, "path": path, "bytes_to_write": len(content.encode("utf-8"))}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {"ok": True, "dry_run": False, "path": path, "bytes_written": len(content.encode("utf-8"))}

def edit_file(path: str, old_str: str, new_str: str, dry_run: bool = False) -> dict[str, Any]:
    """Reemplaza exactamente una ocurrencia única de texto dentro de un archivo."""
    target = _resolve_safe_path(path)
    if not target.exists():
        return {
            "ok": False,
            "codigo": "ARCHIVO_NO_ENCONTRADO",
            "accion_sugerida": "Usa read_file primero para confirmar la ruta y el contenido exacto",
        }
    text = target.read_text(encoding="utf-8")
    occurrences = text.count(old_str)
    if occurrences == 0:
        return {
            "ok": False,
            "codigo": "BLOQUE_NO_COINCIDE",
            "accion_sugerida": "Vuelve a leer las líneas cercanas con read_file e incluye 3 líneas de contexto exacto",
        }
    if occurrences > 1:
        return {
            "ok": False,
            "codigo": "BLOQUE_AMBIGUO",
            "coincidencias": occurrences,
            "accion_sugerida": "Amplía old_str con las funciones o líneas adyacentes para que la coincidencia sea única",
        }
    updated = text.replace(old_str, new_str, 1)
    if not dry_run: target.write_text(updated, encoding="utf-8")
    return {"ok": True, "dry_run": dry_run, "path": path, "replaced": 1}


def run_bash(command: str, timeout_sec: int = 15) -> dict[str, Any]:
    """Ejecuta un comando de verificación en terminal con límite de tiempo y salida acotada."""
    blocked = ("rm -rf /", "git push --force", "mkfs", "dd if=")
    if any(b in command for b in blocked):
        return {
            "ok": False,
            "codigo": "COMANDO_BLOQUEADO",
            "accion_sugerida": "Ejecuta únicamente comandos de inspección, compilación o pruebas dentro del workspace",
        }
    env = {**os.environ, "PYTHONPATH": str(WORKSPACE_ROOT), "PATH": f"{_VENV_BIN}:{os.environ.get('PATH', '')}"}
    proc = subprocess.run(command, shell=True, cwd=WORKSPACE_ROOT, env=env, capture_output=True, text=True, timeout=timeout_sec, check=False)
    return {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stdout": (proc.stdout or "")[-2000:],
        "stderr": (proc.stderr or "")[-2000:],
    }


TOOLS_SCHEMAS: list[dict[str, Any]] = [
    {"name": "read_file", "description": "Lee un archivo acotando max_lines.", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "max_lines": {"type": "integer", "default": 200}}, "required": ["path"]}},
    {"name": "write_file", "description": "Crea o sobrescribe un archivo en el workspace.", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}, "dry_run": {"type": "boolean"}}, "required": ["path", "content"]}},
    {"name": "edit_file", "description": "Reemplaza una coincidencia exacta y única de old_str por new_str.", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "old_str": {"type": "string"}, "new_str": {"type": "string"}}, "required": ["path", "old_str", "new_str"]}},
    {"name": "run_bash", "description": "Ejecuta un comando en terminal con timeout de 15s.", "input_schema": {"type": "object", "properties": {"command": {"type": "string"}, "timeout_sec": {"type": "integer", "default": 15}}, "required": ["command"]}},
]

TOOLS_REGISTRY: dict[str, Callable[..., dict[str, Any]]] = {
    "read_file": read_file, "write_file": write_file, "edit_file": edit_file, "run_bash": run_bash
}


def dispatch_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Despacha una llamada de herramienta solicitada por el Engine y devuelve un diccionario estructurado."""
    fn = TOOLS_REGISTRY.get(name)
    if fn is None:
        return {
            "ok": False,
            "codigo": "HERRAMIENTA_DESCONOCIDA",
            "accion_sugerida": f"Usa una de las 4 herramientas registradas ({', '.join(TOOLS_REGISTRY)})",
        }
    return fn(**arguments)



def run_agent_loop(
    prompt: str,
    engine_fn: Callable[[list[dict[str, Any]], list[dict[str, Any]]], dict[str, Any]],
    max_turns: int = 8,
) -> dict[str, Any]:
    """Ejecuta el ciclo principal del Coding Agent hasta que el Engine responde sin tool_calls."""
    messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
    for turn in range(1, max_turns + 1):
        response = engine_fn(messages, TOOLS_SCHEMAS)
        tool_calls = response.get("tool_calls") or []
        print(f"\n[TURN {turn}] reason={response.get('stop_reason', 'tool_use' if tool_calls else 'end_turn')}")
        if not tool_calls:
            final_text = response.get("text", "")
            print(f"[AGENT_FINAL] {final_text}")
            return {"ok": True, "turns": turn, "final_text": final_text, "messages": messages}
        messages.append({"role": "assistant", "tool_calls": tool_calls})
        for call in tool_calls:
            inp_s = {k: (v.splitlines()[0] + " ... (+8 líneas)" if isinstance(v, str) and "\n" in v else v) for k, v in call["input"].items()}
            print(f"  [TOOL_USE] {call['name']}({json.dumps(inp_s, ensure_ascii=False)})")
            result = dispatch_tool(call["name"], call["input"])
            preview = {k: (v if k not in ("content", "stdout") else f"<{len(str(v))} chars>") for k, v in result.items() if k != "accion_sugerida"}
            print(f"  [TOOL_RESULT] {json.dumps(preview, ensure_ascii=False)}")
            messages.append({"role": "tool", "name": call["name"], "tool_use_id": call["id"], "content": result})
    return {"ok": False, "turns": max_turns, "codigo": "MAX_TURNS_EXCEEDED", "messages": messages}


def _scripted_demo_engine(messages: list[dict[str, Any]], _tools: list[dict[str, Any]]) -> dict[str, Any]:
    """Engine determinista de 4 turnos para demostrar lectura, BLOQUE_AMBIGUO, edición con contexto y pytest."""
    turns = sum(1 for m in messages if m["role"] == "assistant")
    if turns == 0:
        return {"tool_calls": [{"id": "call_01", "name": "read_file", "input": {"path": "sandbox_app/catalog_filter.py"}}, {"id": "call_02", "name": "read_file", "input": {"path": "sandbox_app/test_catalog_filter.py"}}]}
    if turns == 1:
        return {"tool_calls": [{"id": "call_03", "name": "edit_file", "input": {"path": "sandbox_app/catalog_filter.py", "old_str": 'if item.get("active", True) and item.get("category") == category', "new_str": 'if item.get("active", True) and str(item.get("category", "")).strip().lower() == category.strip().lower()'}}]}
    if turns == 2:
        return {"tool_calls": [{"id": "call_04", "name": "edit_file", "input": {"path": "sandbox_app/catalog_filter.py", "old_str": 'def filter_by_category(items: list[dict[str, Any]], category: str) -> list[dict[str, Any]]:\n    """Filtra productos activos que coincidan con la categoría solicitada."""\n    if not items or not category.strip():\n        return []\n    return [\n        item\n        for item in items\n        if item.get("active", True) and item.get("category") == category\n    ]', "new_str": 'def filter_by_category(items: list[dict[str, Any]], category: str) -> list[dict[str, Any]]:\n    """Filtra productos activos que coincidan con la categoría solicitada."""\n    target_cat = category.strip().lower()\n    if not items or not target_cat:\n        return []\n    return [\n        item\n        for item in items\n        if item.get("active", True) and str(item.get("category", "")).strip().lower() == target_cat\n    ]'}}]}
    if turns == 3:
        return {"tool_calls": [{"id": "call_05", "name": "run_bash", "input": {"command": "pytest -q sandbox_app/test_catalog_filter.py"}}]}
    return {"stop_reason": "end_turn", "text": "Bug corregido en filter_by_category normalizando con .strip().lower(). Suite pytest en verde (exit_code=0)."}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--demo-primitives"
    if mode == "--demo-primitives":
        print("=== DEMO HARNESS · 4 PRIMITIVAS ===")
        print("1. read_file (ruta inexistente -> error como dato accionable):")
        print(json.dumps(dispatch_tool("read_file", {"path": "no-existe.py"}), indent=2, ensure_ascii=False))
        print("\n2. read_file (sandbox_app/catalog_filter.py con max_lines=10):")
        r = dispatch_tool("read_file", {"path": "sandbox_app/catalog_filter.py", "max_lines": 10})
        print(json.dumps({k: v for k, v in r.items() if k != "content"}, indent=2, ensure_ascii=False))
        print("\n3. run_bash (comando destructivo bloqueado):")
        print(json.dumps(dispatch_tool("run_bash", {"command": "rm -rf /"}), indent=2, ensure_ascii=False))
    elif mode == "--demo-loop":
        p = _resolve_safe_path("sandbox_app/catalog_filter.py")
        p.write_text(p.read_text("utf-8").replace("    target_cat = category.strip().lower()\n    if not items or not target_cat:", "    if not items or not category.strip():").replace('str(item.get("category", "")).strip().lower() == target_cat', 'item.get("category") == category'), "utf-8")
        print("=== DEMO AGENTIC LOOP · 4 TURNOS SOBRE SANDBOX_APP ===")
        run_agent_loop("Corrige el bug case-sensitive en filter_by_category y verifica con pytest.", _scripted_demo_engine)
