# Lo que el repo le cuenta al agente

Código ejecutable de **Lo que el repo le cuenta al agente**, de la serie **AI Native Dev** por **Adrián Catalán** (`@adriancs.tech`). Proyecto hilo: **TraveLens** (Next.js 16, React 19, Tailwind 4, Zod 4, Vitest 5 y `@google/genai`).

Este repositorio mide qué cambia en el trabajo de un *Coding Agent* en modo *headless* cuando el proyecto pasa de no tener comandos de prueba ni fronteras tipadas a exponer comandos únicos no interactivos (`npm run typecheck`, `npm run lint`, `npm run test:run`), esquemas con Zod (`src/services/schemas.ts`), datos semilla deterministas (`src/services/__fixtures__/itinerary.fixture.ts`) y un archivo `AGENTS.md` de una página (31 líneas, importado desde `CLAUDE.md` con `@AGENTS.md`). También muestra por qué `AGENTS.md` es contexto y cuándo necesitas una compuerta ejecutable.

## Qué hay aquí

```text
02-lo-que-el-repo-cuenta/
├── AGENTS.md                                  # Guía operativa de 31 líneas en 4 bloques
├── Makefile                                   # Atajos de verificación, juez, resumen y tests
├── practica/                                  # Fragmentos del video de práctica
├── tests/test_practica.py                     # Pruebas de cada fragmento y cada «prueba esto»
├── travelens/
│   ├── AGENTS.md                              # Fuente de verdad del repositorio (31 líneas)
│   ├── CLAUDE.md                              # Importa @AGENTS.md
│   ├── vitest.config.ts                       # Suite unitaria rápida sin red
│   ├── vitest.juez.config.ts                  # Config del juez externo
│   ├── juez/ai-plan.juez.test.ts              # Juez ejecutable (7 pruebas sobre /api/ai-plan)
│   └── src/
│       ├── app/api/ai-plan/
│       │   ├── route.ts                       # Endpoint validado (200 válido, 400 sin destino, 502 invalid_plan)
│       │   └── route.test.ts                  # Pruebas unitarias de la ruta
│       └── services/
│           ├── schemas.ts                     # ItineraryResponseSchema con Zod
│           ├── __fixtures__/
│           │   └── itinerary.fixture.ts       # Datos semilla deterministas para pruebas sin red
│           ├── gemini.ts                      # Cliente de Gemini entregado por el agente (type guard manual)
│           └── gemini.test.ts                 # Pruebas unitarias del servicio con SDK simulado
├── medicion/
│   ├── prompts/encargo.txt                    # El mismo encargo ejecutado antes y después
│   ├── juez/ai-plan.juez.test.ts              # Copia de respaldo del juez externo
│   ├── antes/                                 # Estado previo al encargo y CLAUDE.inflado.md (260 líneas)
│   ├── despues.patch                          # Diff de preparación del repositorio
│   ├── entrega.patch                          # Diff entregado por el agente sobre el repositorio preparado
│   ├── logs/
│   │   ├── 01-antes.jsonl                     # Traza headless antes de preparar el repositorio
│   │   └── 02-despues.jsonl                   # Traza headless después de preparar el repositorio
│   └── resumen.json                           # Cifras extraídas de ambos logs
└── scripts/resumen_medicion.py                # Resume pasos, comandos fallidos, tokens y duración
```

## Práctica

La carpeta `practica/` contiene los cinco archivos que se escriben y se corren en el video de práctica. Todos corren en local sin cuentas de nube y cada uno tiene su prueba en `tests/test_practica.py`.

| Archivo | Qué hace |
|---|---|
| `practica/comando_colgado_roto.py` | Reproduce cómo un comando en modo *watch* cuelga la tool de terminal del agente hasta agotar el *timeout* (`TIMEOUT`) |
| `practica/auditar_comandos.py` | Audita `package.json` antes y después, y corre los tres comandos no interactivos (`typecheck`, `lint`, `test:run`) |
| `practica/verificar_agents_md.py` | Compara `CLAUDE.inflado.md` (260 líneas, comando roto) contra `AGENTS.md` (31 líneas, `@AGENTS.md`) y verifica que cada comando y ruta citada existan |
| `practica/compuerta_frontera.py` | Compuerta ejecutable sobre `src/services/` que detecta que `gemini.ts` validó con un *type guard* manual sin importar `schemas.ts` aunque `AGENTS.md` pedía Zod y el juez daba 7 de 7 |
| `practica/comparar_corridas.py` | Lee `01-antes.jsonl` y `02-despues.jsonl` e imprime la tabla comparativa y los comandos fallidos (`--fallos`) |

Necesitas Python 3.11 o más nuevo y Node 22 o más nuevo.

```bash
git clone https://github.com/ykro/ai-native-dev.git
cd ai-native-dev/02-lo-que-el-repo-cuenta
python3 -m venv .venv && source .venv/bin/activate
pip install pytest
make instalar
make check
make juez

python -m practica.comando_colgado_roto
python -m practica.auditar_comandos
python -m practica.verificar_agents_md
python -m practica.compuerta_frontera
python -m practica.comparar_corridas
python -m practica.comparar_corridas --fallos
make all
```

## Cómo explorar la entrega grabada

```bash
cd 02-lo-que-el-repo-cuenta
make instalar
make check              # npm run typecheck && npm run lint && npm run test:run (12 pruebas)
make juez               # 7 de 7 pruebas del juez en verde
make resumen            # compara 01-antes.jsonl contra 02-despues.jsonl
make volver-al-inicio   # regresa gemini.ts y route.ts al estado previo (5 fallas en el juez)
make aplicar-entrega    # vuelve a aplicar el cambio entregado por el agente
```

## Resultado de la medición antes contra después

Mismo encargo (`medicion/prompts/encargo.txt`) y mismo juez externo (`juez/ai-plan.juez.test.ts`, 7 pruebas) corridos en modo *headless* sin intervención humana:

| Métrica | Antes (`01-antes.jsonl`) | Después (`02-despues.jsonl`) | Cambio |
|---|---|---|---|
| **Pasos del agente** | 23 (12 comandos, 7 ediciones) | 10 (5 comandos, 4 ediciones) | −57 % |
| **Comandos fallidos en terminal** | 4 (`npm run verify:all`, `npm test`, `npm run build`, `npx tsc --noEmit`) | 0 | 4 → 0 |
| **Tokens de entrada** | 408,027 (23,259 nuevos + 384,768 desde caché) | 201,000 (14,248 nuevos + 186,752 desde caché) | −51 % |
| **Tokens de salida** | 4,037 | 1,910 | −53 % |
| **Duración total** | 140.0 s | 27.0 s | 5.2× más rápido |
| **Juez externo (`npm run juez`)** | 7 / 7 | 7 / 7 | Misma calidad verificada |

**Nos vemos en el código.**
