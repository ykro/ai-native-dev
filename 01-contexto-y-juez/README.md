# Sesiones largas, contexto limpio y un juez antes del código

Código ejecutable de **Sesiones largas, contexto limpio y un juez antes del código**, de la serie **AI Native Dev** por **Adrián Catalán** (`@adriancs.tech`). Proyecto hilo: **Rent My Gear** (Next.js 16, React 19, Tailwind 4, Zod 4, Vitest 5).

- **Lecturas relacionadas en Substack** · [Cómo delegarle un proyecto a un agente de IA sin perder el control](https://ykro1.substack.com/p/delegar-a-un-agente) · [Primero la spec](https://ykro1.substack.com/p/primero-la-spec)

El demo agrega una cobertura por daños por categoría con **Judge-First**: primero se escribe un juez ejecutable que hoy falla, el agente mapea el repo sin editar, se acuerda un contrato corto y una sesión limpia itera contra el juez hasta entregar con evidencia.

## Qué hay aquí

```text
01-contexto-y-juez/
├── Makefile
├── rent-my-gear/
│   ├── juez/cobertura.juez.test.tsx   # El juez, escrito antes que el código (no se edita)
│   ├── vitest.juez.config.ts          # Config del juez, separada de la suite normal
│   ├── contrato.md                    # Contrato corto acordado después del mapa
│   └── src/                           # La app en su estado inicial (juez en rojo)
├── prompts/                           # Las tres instrucciones de la demo
│   ├── 01-directo.txt                 # Una línea, sin juez (para comparar)
│   ├── 02-mapa.txt                    # Sesión de solo lectura que devuelve un mapa
│   └── 03-iterar.txt                  # Sesión limpia que itera contra el juez
├── logs/                              # Logs reales de Claude Code en modo headless
├── practica/                          # Fragmentos del video de práctica, el harness y el engine
├── sesiones/                          # Sesiones grabadas con Gemini (para --grabada y contexto.py)
├── tests/test_practica.py             # Un test por fragmento de practica/
├── entrega/cobertura.patch            # El cambio que entregó el agente
└── scripts/resumen_sesion.py          # Turnos, herramientas, intentos fallidos y tokens de un log
```

## Práctica: un juez, tres sesiones y el contexto que se llena

La carpeta `practica/` tiene los fragmentos que se escriben en el video de práctica, en este orden. Cada uno tiene su test en `tests/test_practica.py`. El harness es el loop del tema «Lo que pasa cuando le pides algo a un Coding Agent» con tools para Rent My Gear (`practica/harness.py`) y Gemini en Vertex AI como engine (`practica/motor.py`).

| Archivo | Qué hace |
|---|---|
| `practica/juez.py` | El juez como tool: corre sus pruebas y regresa cuántas pasan y la primera línea de cada falla |
| `practica/permisos.py` | Las reglas del harness: en la sesión directa el agente no ve el juez ni el contrato, el mapa es de solo lectura y nadie edita el juez |
| `practica/sesion.py` | Lanza una sesión: `directo` (una línea y correcciones en la misma sesión), `mapa` (solo lectura) o `limpia` (contrato y juez, historia vacía) |
| `practica/contexto.py` | Lee la traza de una sesión y dibuja cuántos tokens de entrada carga cada turno |

Las sesiones grabadas están en `sesiones/` (una línea por turno: tokens y tools que pidió Gemini). Con `--grabada`, el harness repite esas respuestas del modelo sin cuenta de Google Cloud, pero las tools corren de verdad en tu máquina: el juez pasa de rojo a verde en tu copia de Rent My Gear. Sin `--grabada`, la sesión llama a Gemini y guarda su traza en `sesiones/tuya-<sesion>.jsonl`.

Necesitas Python 3.11 o más nuevo y Node 20 o más nuevo.

```bash
git clone https://github.com/ykro/ai-native-dev.git
cd ai-native-dev/01-contexto-y-juez
python3 -m venv .venv && source .venv/bin/activate
pip install pytest google-genai
make instalar
make juez                                   # 5 pruebas en rojo

python -m practica.juez                     # el mismo rojo, en un diccionario corto
python -m practica.permisos

# Opcional, llama a Gemini en Vertex AI (la forma de usar Gemini desde un proyecto de Google Cloud)
gcloud auth application-default login
gcloud services enable aiplatform.googleapis.com
export GOOGLE_CLOUD_PROJECT=tu-proyecto
python -m practica.sesion directo           # sin cuenta: agrega --grabada
python -m practica.contexto sesiones/directo.jsonl   # mi corrida; la tuya queda en sesiones/tuya-directo.jsonl
make volver-al-inicio
python -m practica.sesion mapa
python -m practica.sesion limpia            # el juez pasa de rojo a verde
python -m practica.contexto sesiones/directo.jsonl sesiones/limpia.jsonl
make evidencia
make volver-al-inicio
make all
```

## Cómo correrlo

```bash
cd 01-contexto-y-juez
make instalar
make juez               # 5 pruebas en rojo: la cobertura no existe todavía
make aplicar-entrega    # aplica el cambio que hizo el agente
make evidencia          # juez 5/5, suite completa y tipos (make build: build de producción)
make volver-al-inicio   # regresa src/ al estado inicial
make resumen            # cifras de las tres sesiones grabadas
```

## Cómo se grabaron las sesiones de `logs/` (Claude Code)

Con Claude Code en modo headless (`claude -p ... --output-format stream-json --verbose`), modelo Sonnet, una corrida por sesión:

| Sesión | Herramientas permitidas | Turnos | Intentos fallidos | Juez |
|---|---|---|---|---|
| `01-directo` (sin juez) | leer, editar, `npm`/`npx` | 21 | 1 (permiso) | 0 de 5 al evaluarlo después; 3 de 5 con los nombres traducidos |
| `02-mapa` | solo leer | 12 | 0 | lo lee y resume lo que exige |
| `03-iterar` (sesión limpia, contrato + juez) | leer, editar, `npm`/`npx`; sin escritura en `juez/` | 26 | 4 (permisos) | rojo al inicio, 5 de 5 al final |

Las cifras exactas de tokens y duración salen de `make resumen`. Los logs se publicaron sin rutas locales ni la lista de plugins de la máquina donde se grabaron.

## El modelo de imágenes

La app genera fotos de producto con Gemini (`@google/genai`, modelo `gemini-3.1-flash-image-preview`) cuando un equipo no tiene imagen. El demo de este tema no lo necesita: el juez y las pruebas no llaman a ningún modelo.

**Nos vemos en el código.**
