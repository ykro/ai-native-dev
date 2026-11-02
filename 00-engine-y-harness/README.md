# 00 · Lo que pasa cuando le pides algo a un Coding Agent

Código ejecutable del **Tema 00** de la serie **AI Native Dev** por **Adrián Catalán** (`@adriancs.tech`).

Este paquete construye desde cero un **Harness mínimo de Coding Agent** en Python puro (`src/mini_agent.py`) para demostrar cómo operan las 4 herramientas primitivas (`read_file`, `write_file`, `edit_file`, `run_bash`), cómo se devuelven los errores como datos accionables (`BLOQUE_AMBIGUO`, `ARCHIVO_NO_ENCONTRADO`) y cómo impacta el preámbulo oculto en la economía de *tokens* y *Prompt Caching* (`src/http_trace_inspector.py`).

## Estructura del Paquete

```text
00-engine-y-harness/
├── Makefile                        # Atajos para correr los demos, el inspector y pytest
├── README.md                       # Guía rápida de ejecución
├── src/
│   ├── mini_agent.py               # Harness (<180 líneas): 4 primitivas + dispatch_tool + run_agent_loop
│   └── http_trace_inspector.py     # Analizador de payload HTTP, preámbulo y Prompt Caching en 5 turnos
├── sandbox_app/
│   ├── catalog_filter.py           # Módulo de catálogo usado como objetivo de reparación
│   └── test_catalog_filter.py      # Suite pytest de verificación cerrada
├── traces/
│   └── session_5_turns.json        # Traza HTTP representativa de 5 turnos (reconstrucción armada a mano)
└── tests/
    └── test_mini_agent.py          # Pruebas deterministas del Harness y del inspector
```

> **Sobre la traza.** `traces/session_5_turns.json` es una reconstrucción representativa de una sesión de cinco turnos, armada a mano con la forma de las peticiones de un *Harness* a su *Engine*; sus cifras son ilustrativas. Y el demo del *loop* usa un *Engine* guionizado y determinista (no llama a ningún modelo) para que la corrida sea reproducible; el *loop* y las cuatro herramientas sí son reales.

## Ejecución Rápida

```bash
cd 00-engine-y-harness

# 1. Probar las 4 primitivas y sus contratos de error como datos
python3 src/mini_agent.py --demo-primitives

# 2. Ejecutar el loop completo de 4 turnos (lectura -> BLOQUE_AMBIGUO -> edición con contexto -> pytest)
python3 src/mini_agent.py --demo-loop

# 3. Inspeccionar el payload HTTP y la tabla de Token Economics / Prompt Caching
python3 src/http_trace_inspector.py

# 4. Correr toda la suite de pruebas
pytest -v tests/test_mini_agent.py sandbox_app/test_catalog_filter.py
```

**Nos vemos en el código.**
