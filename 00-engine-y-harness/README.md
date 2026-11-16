# 00 · Lo que pasa cuando le pides algo a un Coding Agent

Código ejecutable del **Tema 00** de la serie **AI Native Dev** por **Adrián Catalán** (`@adriancs.tech`).

- **YouTube** · [Video de Teoría](https://youtu.be/L7MwTArreqw) · [Video de Práctica](https://youtu.be/tFTEsbVYQvE) · [Playlist AI Native Dev](https://www.youtube.com/playlist?list=PLADgjqdtJ3Bc)
- **Substack** · [Gemini 4 Argon trabajando en auditar, construir y deployear código](https://ykro1.substack.com/p/gemini-4-argon-trabajando-en-auditar) · [Cómo delegarle un proyecto a un agente de IA sin perder el control](https://ykro1.substack.com/p/delegar-a-un-agente)

Este paquete cubre las dos prácticas del tema:

- **Práctica A · Construir el Coding Agent mínimo**: implementación desde cero en Python puro (`src/mini_agent.py`) de las cuatro primitivas (`read_file`, `write_file`, `edit_file`, `run_bash`), sus contratos de error como datos accionables (`BLOQUE_AMBIGUO`, `BLOQUE_NO_COINCIDE`, `ARCHIVO_NO_ENCONTRADO`, `COMANDO_BLOQUEADO`), el adaptador para un *Engine* real en Vertex AI (`src/gemini_engine.py`) y el inspector de *payload* HTTP y *Prompt Caching* (`src/http_trace_inspector.py`).
- **Práctica B · La misma tarea en Harnesses reales (`Codex` y `AGI CLI`)**: comparación directa sobre **PawsMatch** (`2026/week1/pawsmatch`, evitando mascotas repetidas en `usePetStack` con pruebas en Vitest) ejecutada en modo *headless* con **Codex** (`0.166.0-alpha.5.1`, modelo `gpt-6-luna`) y **AGI CLI** (`agy 1.4.12`, modelo `Gemini 4 Argon (Medium)`), auditando sus trazas reales de sesión (`src/harness_trace_compare.py`).

## Práctica: escribe tu propio agente mínimo

La carpeta `practica/` tiene los fragmentos que se escriben en el video de práctica, en este orden. Cada uno tiene su test en `tests/test_practica.py`.

| Archivo | Qué hace |
|---|---|
| `practica/herramientas.py` | Dos tools (`read_file`, `run_bash`) que devuelven un diccionario, también cuando fallan |
| `practica/editar.py` | `edit_file` con reemplazo exacto: se niega si el texto aparece cero o más de una vez |
| `practica/editar_roto.py` | El error a propósito: pedir un cambio sobre un texto que aparece dos veces (`BLOQUE_AMBIGUO`) |
| `practica/agente.py` | El loop: pedir el siguiente paso al engine, ejecutar la tool y repetir; imprime cuánto crece cada turno |
| `practica/agente_gemini.py` | El mismo loop con Gemini en Vertex AI como engine (necesita `gcloud auth application-default login` y `GOOGLE_CLOUD_PROJECT`) |

```bash
git clone https://github.com/ykro/ai-native-dev.git
cd ai-native-dev/00-engine-y-harness
python3 -m venv .venv && source .venv/bin/activate
pip install pytest google-genai

python -m practica.herramientas
python -m practica.editar_roto     # BLOQUE_AMBIGUO
python -m practica.editar          # con contexto: un solo reemplazo
python -m practica.agente
python -m practica.agente_gemini   # opcional, llama a Gemini
make all
```

## Estructura del Paquete

```text
00-engine-y-harness/
├── Makefile                        # Atajos para correr las prácticas, el comparador y pytest
├── README.md                       # Guía rápida de ejecución
├── src/
│   ├── mini_agent.py               # Harness mínimo: 4 primitivas + dispatch_tool + run_agent_loop
│   ├── gemini_engine.py            # Adaptador de Engine real (Gemini en Vertex AI con google-genai)
│   ├── http_trace_inspector.py     # Analizador de preámbulo oculto y Prompt Caching en 5 turnos
│   └── harness_trace_compare.py    # Comparador de trazas reales entre Codex y AGI CLI (agy)
├── practica/                       # Fragmentos del video de práctica (agente mínimo paso a paso)
├── sandbox_app/
│   ├── catalog_filter.py           # Módulo de catálogo usado como objetivo en la Práctica A
│   └── test_catalog_filter.py      # Suite pytest de verificación cerrada
├── traces/
│   ├── session_5_turns.json        # Traza HTTP de ejemplo de 5 turnos con desglose de preámbulo
│   ├── gemini_run.jsonl            # Traza real de mini_agent.py con gemini-3.8-flash
│   ├── codex_events.jsonl          # Stream JSON real de Codex resolviendo el reto en PawsMatch
│   ├── codex_turns.jsonl           # Registros de turno, apply_patch y tokens de la sesión de Codex
│   └── agy_events.jsonl            # Stream JSON real de AGI CLI (agy) sobre la misma tarea
└── tests/
    ├── test_mini_agent.py          # Suite pytest determinista del Harness, adaptador y comparador
    └── test_practica.py            # Un test por cada fragmento de practica/
```

## Ejecución Rápida

```bash
cd 00-engine-y-harness

# 1. Práctica A: probar las 4 primitivas y sus contratos de error como datos
python3 src/mini_agent.py --demo-primitives

# 2. Práctica A: ejecutar el loop determinista de 4 turnos (lectura -> BLOQUE_AMBIGUO -> edición -> pytest)
python3 src/mini_agent.py --demo-loop

# 3. Práctica A (opcional con credenciales ADC): correr el loop contra Gemini en Vertex AI
python3 src/mini_agent.py --demo-loop --engine gemini

# 4. Práctica A: inspeccionar el desglose de preámbulo y Prompt Caching
python3 src/http_trace_inspector.py

# 5. Práctica B: comparar las trazas reales de Codex y AGI CLI (agy) sobre PawsMatch
python3 src/harness_trace_compare.py

# 6. Correr toda la suite de pruebas (17 tests)
python3 -m pytest -v tests/test_mini_agent.py tests/test_practica.py sandbox_app/test_catalog_filter.py
```

**Nos vemos en el código.**
