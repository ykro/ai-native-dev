#!/usr/bin/env python3
"""Engine real para el loop de mini_agent.py: Gemini vía Vertex AI (google-genai, credenciales ADC).

El Harness (mini_agent.py) no sabe nada del proveedor: llama a engine_fn(messages, tools) y recibe
{"tool_calls": [...]} o {"text": ...}. Este adaptador traduce ese formato al de Gemini, guarda la
respuesta original del modelo (lleva las firmas de pensamiento que Gemini exige de vuelta) y anota
el uso de tokens de cada vuelta, incluidos los tokens servidos desde caché.
"""

from __future__ import annotations

import json
import os
import pathlib
import time
from typing import Any, Callable

SYSTEM_PROMPT = (
    "Eres un Coding Agent que trabaja dentro de un repositorio con cuatro herramientas: read_file, "
    "write_file, edit_file y run_bash. Lee antes de editar. Para editar usa edit_file con un old_str "
    "que aparezca exactamente una vez en el archivo. Si una herramienta devuelve ok=false, lee el "
    "codigo de error y la accion sugerida y corrige el rumbo. Verifica con pytest antes de terminar; "
    "en cuanto pytest pase con exit_code=0, no ejecutes git status ni git diff y responde de inmediato "
    "con un resumen de una o dos líneas, sin llamar más herramientas."
)


def to_function_declarations(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convierte los esquemas del Harness (input_schema) al formato de Gemini (parameters)."""
    return [{"name": t["name"], "description": t["description"], "parameters": t["input_schema"]} for t in tools]


def to_contents(messages: list[dict[str, Any]], types: Any) -> list[Any]:
    """Traduce el historial del Harness a la lista de contents de Gemini."""
    contents: list[Any] = []
    pending: list[Any] = []
    for m in messages:
        if m["role"] == "tool":
            pending.append(types.Part.from_function_response(name=m["name"], response=m["content"]))
            continue
        if pending:
            contents.append(types.Content(role="user", parts=pending))
            pending = []
        if m["role"] == "user":
            contents.append(types.Content(role="user", parts=[types.Part.from_text(text=m["content"])]))
        elif m["role"] == "assistant":
            contents.append(m["raw"])  # respuesta original del modelo, con sus firmas
    if pending:
        contents.append(types.Content(role="user", parts=pending))
    return contents


def usage_of(meta: Any) -> dict[str, int]:
    """Extrae del usage_metadata de Gemini los contadores que compara el video."""
    g = lambda k: int(getattr(meta, k, 0) or 0)  # noqa: E731
    return {
        "input_tokens": g("prompt_token_count"),
        "cached_tokens": g("cached_content_token_count"),
        "output_tokens": g("candidates_token_count"),
        "thinking_tokens": g("thoughts_token_count"),
    }


def make_gemini_engine(
    model: str = "gemini-3.8-flash",
    trace_path: str | None = None,
    client: Any = None,
    types: Any = None,
) -> Callable[[list[dict[str, Any]], list[dict[str, Any]]], dict[str, Any]]:
    """Crea un engine_fn compatible con run_agent_loop. client/types se inyectan en los tests."""
    if client is None or types is None:
        from google import genai
        from google.genai import types as gtypes

        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
        client, types = genai.Client(), gtypes
    trace = pathlib.Path(trace_path) if trace_path else None
    if trace:
        trace.parent.mkdir(parents=True, exist_ok=True)
        trace.write_text("", encoding="utf-8")

    def engine(messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[types.Tool(function_declarations=to_function_declarations(tools))],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        t0 = time.perf_counter()
        for attempt in range(4):  # 429 de cuota: espera y reintenta, igual que un Harness de verdad
            try:
                resp = client.models.generate_content(model=model, contents=to_contents(messages, types), config=config)
                break
            except Exception as exc:  # noqa: BLE001
                if "429" not in str(exc) or attempt == 3:
                    raise
                time.sleep(5 * 2**attempt)
        elapsed = round(time.perf_counter() - t0, 2)
        content = resp.candidates[0].content
        calls = [p.function_call for p in (content.parts or []) if getattr(p, "function_call", None)]
        tool_calls = [
            {"id": f"call_{len(messages):02d}_{i}", "name": c.name, "input": dict(c.args or {})} for i, c in enumerate(calls)
        ]
        text = "".join(p.text for p in (content.parts or []) if getattr(p, "text", None) and not getattr(p, "thought", False))
        usage = usage_of(resp.usage_metadata)
        if trace:
            with trace.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"messages_sent": len(messages), "tool_calls": [c["name"] for c in tool_calls],
                                    "seconds": elapsed, **usage}, ensure_ascii=False) + "\n")
        out: dict[str, Any] = {"raw": content, "usage": usage, "seconds": elapsed}
        if tool_calls:
            out["tool_calls"] = tool_calls
        else:
            out.update(stop_reason="end_turn", text=text.strip())
        return out

    return engine
