"""El loop de un Coding Agent: pedir un paso, ejecutar la tool, repetir."""
import json

from practica.herramientas import TOOLS

PLAN = [  # lo que respondería un engine, turno por turno
    [{"name": "read_file",
      "input": {"path": "sandbox_app/catalog_filter.py", "max_lines": 20}}],
    [{"name": "run_bash",
      "input": {"command": "python -m pytest -q sandbox_app"}}],
    [],  # sin tool calls: el engine terminó
]


def engine(messages):
    return PLAN[sum(m["role"] == "assistant" for m in messages)]


def correr(tarea, engine, max_turns=8):
    messages = [{"role": "user", "content": tarea}]
    for turno in range(1, max_turns + 1):
        enviado = len(json.dumps(messages, ensure_ascii=False))
        print(f"turno {turno}: le mando {enviado} caracteres")
        calls = engine(messages)
        if not calls:
            return messages
        messages.append({"role": "assistant", "tool_calls": calls})
        for c in calls:
            r = TOOLS[c["name"]](**c["input"])
            print(f"  {c['name']} -> ok={r['ok']}")
            messages.append({"role": "tool", "name": c["name"], "content": r})
    return messages


if __name__ == "__main__":
    correr("¿Pasan los tests del catálogo?", engine)
