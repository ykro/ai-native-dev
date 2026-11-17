"""Dos engines para el harness: Gemini en Vertex AI y uno grabado que repite una corrida real.

El grabado lee la traza de una sesión con Gemini (sesiones/<sesion>.jsonl) y devuelve, turno por turno,
las mismas tools y los mismos tokens. Las tools sí corren en tu máquina: el juez pasa de rojo a verde
de verdad, sin cuenta de Google Cloud."""
import json
import os
import time

SISTEMA = (
    "Eres un Coding Agent que trabaja en rent-my-gear, una app de Next.js con TypeScript. Las rutas son "
    "relativas a esa carpeta. Lee antes de editar. Para editar usa editar con un texto viejo que aparezca "
    "exactamente una vez. Si una tool devuelve ok=false, lee el codigo y la accion_sugerida y corrige el "
    "rumbo. Cuando termines, responde en texto sin pedir más tools."
)


def grabado(ruta, sesion):
    pasos = [t for t in map(json.loads, open(ruta, encoding="utf-8")) if t["sesion"] == sesion]
    pasos.reverse()

    def engine(messages, tools):
        t = pasos.pop()
        calls = [{"id": f"g{t['turno']}_{i}", **c} for i, c in enumerate(t["tool_calls"])]
        usage = {k: t[k] for k in ("input_tokens", "cached_tokens", "output_tokens", "thinking_tokens")}
        return {"tool_calls": calls, "text": t["text"], "usage": usage}

    return engine


def gemini(modelo="gemini-3.8-flash"):
    from google import genai
    from google.genai import types

    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
    client = genai.Client(http_options=types.HttpOptions(timeout=300_000))  # 5 min por turno

    def contents(messages):
        out, pend = [], []
        for m in messages:
            if m["role"] == "tool":
                pend.append(types.Part.from_function_response(name=m["name"], response=m["content"]))
            elif m["role"] == "user":
                if pend:
                    out.append(types.Content(role="user", parts=pend))
                    pend = []
                out.append(types.Content(role="user", parts=[types.Part.from_text(text=m["content"])]))
            else:
                if pend:
                    out.append(types.Content(role="user", parts=pend))
                    pend = []
                out.append(m["raw"])
        if pend:
            out.append(types.Content(role="user", parts=pend))
        return out

    def engine(messages, tools):
        config = types.GenerateContentConfig(
            system_instruction=SISTEMA,
            tools=[types.Tool(function_declarations=[
                {"name": t["name"], "description": t["description"], "parameters": t["input_schema"]} for t in tools])],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        for intento in range(5):
            try:
                resp = client.models.generate_content(model=modelo, contents=contents(messages), config=config)
                break
            except Exception as exc:  # noqa: BLE001
                if intento == 4 or not any(c in str(exc).lower() for c in ("429", "503", "500", "timeout", "timed out")):
                    raise
                time.sleep(5 * 2 ** intento)
        content = resp.candidates[0].content
        parts = content.parts or []
        calls = [{"id": f"c{len(messages)}_{i}", "name": p.function_call.name, "input": dict(p.function_call.args or {})}
                 for i, p in enumerate(parts) if getattr(p, "function_call", None)]
        text = "".join(p.text for p in parts if getattr(p, "text", None) and not getattr(p, "thought", False)).strip()
        g = lambda k: int(getattr(resp.usage_metadata, k, 0) or 0)  # noqa: E731
        usage = {"input_tokens": g("prompt_token_count"), "cached_tokens": g("cached_content_token_count"),
                 "output_tokens": g("candidates_token_count"), "thinking_tokens": g("thoughts_token_count")}
        return {"tool_calls": calls, "text": text, "usage": usage, "raw": content}

    return engine
