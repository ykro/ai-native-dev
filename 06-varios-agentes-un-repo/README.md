# 06 · Varios agentes sobre el mismo repo

Código del **tema 06** de la serie **AI Native Dev** por **Adrián Catalán** (`@adriancs.tech`). Proyecto hilo: **TraveLens** (Next.js 16, React 19, Zod 4, Vitest 5).

Un agente reparte el pedido de un sprint en encargos con su juez, varios agentes construyen en paralelo, cada uno en su propio `git worktree`, y un integrador con contexto limpio fusiona las ramas y corre todos los jueces. Entre la construcción y la integración, un script que no usa ningún modelo mide qué chocó.

## Qué hay aquí

```text
06-varios-agentes-un-repo/
├── pedido.md                  # El pedido de producto (tres cambios, sin decir cómo implementarlos)
├── travelens/                 # La app del tema 02, más los cuatro jueces que escribió el agente que reparte
│   └── juez/                  # ai-plan (tema 02) + api, descarga, presupuesto y ui (rojos hasta aplicar el parche)
├── orquestador/
│   ├── orquestar.py           # preparar, repartir, congelar, construir, medir, integrar, exportar
│   └── test_orquestar.py      # 17 pruebas del orquestador (git en carpetas temporales)
├── prompts/                   # Las tres instrucciones: 01-repartir, 02-construir, 03-integrar
├── reparto/tareas.json        # El reparto que devolvió el agente (revisado por una persona)
├── entrega/                   # Un parche por encargo y integracion.patch (todo junto, sobre el reparto)
├── logs/                      # Sesiones de Claude Code en headless (saneadas) y las mediciones en JSON
└── scripts/resumen_sesion.py  # Turnos, herramientas, intentos bloqueados y tokens de un log
```

## Cómo correrlo

```bash
cd 06-varios-agentes-un-repo
(cd travelens && npm ci && npm run check && npm run juez)   # base: el juez del tema 02 en verde
uv run --with pytest python -m pytest orquestador/test_orquestar.py   # el orquestador se prueba solo

T=~/travelens-06                                    # repo de trabajo, fuera del monorepo
python3 orquestador/orquestar.py preparar  --trabajo $T
python3 orquestador/orquestar.py repartir  --trabajo $T   # agente que reparte
# revisión humana de $T/reparto/tareas.json y de los jueces en $T/travelens/juez/
python3 orquestador/orquestar.py congelar  --trabajo $T
python3 orquestador/orquestar.py construir --trabajo $T   # un worktree y un agente por encargo, por olas
python3 orquestador/orquestar.py medir     --trabajo $T   # sin modelo: fusiones por pares, secuencia y jueces
python3 orquestador/orquestar.py integrar  --trabajo $T   # integrador con contexto limpio
python3 orquestador/orquestar.py exportar  --trabajo $T   # parches, reparto y logs saneados a esta carpeta
for f in logs/*.jsonl; do python3 scripts/resumen_sesion.py $f; done
```

Para ver el resultado sin gastar créditos, aplica el parche y corre los jueces:

```bash
patch -p1 < entrega/integracion.patch                         # desde esta carpeta
(cd travelens && npm run check && npm run juez)               # 45 pruebas y 38 pruebas de juez en verde
```

## Cómo se grabaron las sesiones

- Herramienta: Claude Code `2.1.318` en modo headless (`claude -p ... --output-format stream-json --verbose`), modelo `claude-sonnet-5-5`.
- Cada papel tiene sus permisos: el que reparte solo escribe `reparto/` y los jueces; los constructores editan código y corren comandos de verificación, pero no tocan `juez/`, no instalan paquetes y no usan Git; el integrador usa `git merge`, `git add` y `git commit`, y no toca `juez/`. Todos corren con `--max-turns 40` y `--max-budget-usd 6`, y con las lecturas de `~/.ssh`, `~/.aws`, `~/.config`, `~/.claude`, `~/.gnupg` y de cualquier `.env` negadas.
- Los logs se exportan saneados (rutas de la laptop fuera, campos de configuración del `init` fuera).

## Cifras de la corrida (una sola, no es un promedio)

| Qué | Valor |
|---|---|
| Encargos del reparto | 4 (`presupuesto`, `descarga`, `api`, `ui`), 3 olas |
| Archivos asignados a más de un encargo | 0 |
| Juez de cada encargo en su rama | presupuesto 8/8, descarga 3/3, api 15/15, ui 5/5; `npm run check` en verde en las cuatro |
| Tiempo de reloj de la construcción | 231.2 s |
| Suma de lo que tardó cada agente | 250.8 s (el paralelismo compró unos 20 s: la API y la interfaz dependían de otros encargos, así que solo la primera ola corrió en paralelo) |
| Archivos tocados fuera de lo asignado | 0 en los cuatro |
| Fusiones por pares | 6 pares, 0 chocaron |
| Fusión en secuencia | limpia |
| Regresiones al juntar todo | 1: `ai-plan.juez` (el del tema 02) aprueba 5 de 7 pruebas |
| Integrador | 5 commits propios (4 fusiones y 1 resolución), 5 jueces con 38 pruebas de 38 y `npm run check` en verde |

La regresión es un choque de significado y no de texto. El pedido pide que cada día traiga costo y que el juez del tema 02, que manda planes sin costo, siga en verde. El agente que reparte lo avisó en sus riesgos. Antes de congelar, la persona que revisó quitó del juez de la API el caso que exigía rechazar un día sin costo. Aun así, al juntar las ramas la API rechazaba los planes sin costo del juez anterior. El integrador resolvió contando como cero un día sin costo.

| Sesión | Turnos | Herramientas | Bloqueados por permisos | Tokens de entrada (nuevos + caché) | Tokens de salida | Segundos | Costo (USD) |
|---|---|---|---|---|---|---|---|
| Reparto | 28 | 27 | 6 | 47,344 + 862,509 | 23,388 | 175.5 | 0.51 |
| Constructor `presupuesto` | 13 | 12 | 3 | 18,568 + 305,158 | 3,937 | 44.6 | 0.14 |
| Constructor `descarga` | 11 | 10 | 3 | 16,417 + 258,330 | 3,403 | 41.9 | 0.13 |
| Constructor `api` | 25 | 24 | 2 | 30,648 + 443,134 | 9,889 | 79.3 | 0.27 |
| Constructor `ui` | 25 | 24 | 4 | 27,648 + 490,581 | 8,100 | 81.1 | 0.24 |
| Integrador | 25 | 24 | 5 | 34,139 + 959,301 | 6,359 | 162.3 | 0.30 |
| **Total** | | | | | | | **1.58** |

El costo es el `total_cost_usd` que reporta Claude Code en cada sesión (estimado por el cliente a la tarifa que él conoce), no una consulta de la tarifa publicada el día de grabar. Antes de narrar un costo en voz conviene contrastarlo con la tarifa del modelo ese día.

## Notas de la corrida

- `medir` comparaba cada rama contra `reparto` aunque la rama hubiera arrancado de `base/<id>` con las ramas de sus dependencias. Eso hacía que `api` y `ui` parecieran tocar archivos de otros encargos. Ahora compara contra el punto de partida real de cada rama (`desde_de`, con prueba).
- Las sesiones headless con `--permission-mode acceptEdits` rechazan los comandos compuestos y los que usan variables; esos rechazos son los «bloqueados por permisos» de la tabla.
