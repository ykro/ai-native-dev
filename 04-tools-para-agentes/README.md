# 04 · Tools hechas para agentes, MCP y computer use

Código del **tema 04** de la serie **AI Native Dev** por **Adrián Catalán** (`@adriancs.tech`). Proyecto hilo: **TraderPulse**.

El mismo servicio, el BFF de TraderPulse del tema 03, se ofrece a un agente de dos formas y se mide. El **espejo** expone una herramienta MCP por cada ruta de datos. El **conjunto del agente** expone tres herramientas por intención, con prefijo común, descripciones que dicen cuándo usarlas, esquema de salida y anotaciones de solo lectura. Un juez de seis tareas con respuesta calculada contra el BFF decide los aciertos. Al final un agente con navegador comprueba la aplicación desplegada.

## Qué hay aquí

```text
04-tools-para-agentes/
├── Makefile                       # api, medir-definiciones, medir, resumen, verificar-ui
├── pyproject.toml                 # SDK de MCP y el paquete del BFF (editable, del tema 03)
├── mcp/
│   ├── bff.py                     # cliente mínimo del BFF
│   ├── espejo.py                  # 4 herramientas, una por ruta, con el JSON tal cual
│   ├── agente.py                  # 3 herramientas por intención, con esquema de salida
│   ├── espejo.mcp.json            # configuración del cliente (stdio)
│   ├── agente.mcp.json
│   └── playwright.mcp.json        # Playwright MCP sin ventana, perfil temporal, un solo origen
├── evals/tareas.json              # 6 tareas
├── juez/juez_tools.py             # corre cada tarea con cada conjunto, N veces, y dicta acierto o fallo
├── scripts/
│   ├── medir_definiciones.py      # herramientas y caracteres de la lista de definiciones
│   ├── resumen_tools.py           # tabla de llamadas, tokens y aciertos por conjunto
│   ├── resumen_sesion.py          # resumen de una sesión
│   ├── verificar_ui.sh            # sesión con navegador sobre la web desplegada
│   └── sanear_log.py              # quita rutas locales, plugins y URLs de un log
├── prompts/                       # 01-tarea.txt (plantilla) y 04-verificar-ui.txt
└── logs/                          # sesiones headless sin rutas locales
```

## Cómo correrlo

```bash
cd 04-tools-para-agentes
make instalar
make api                       # BFF de ejemplo en el puerto 8000 (PORT=8010 si el 8000 está ocupado)
make medir-definiciones        # herramientas y caracteres de cada servidor
make medir                     # 6 tareas x 2 conjuntos x 5 repeticiones (PORT=... si cambiaste el puerto)
make resumen                   # tabla de resultados desde los logs
make verificar-ui WEB_URL=<la web desplegada en el tema 03>
```

Cada sesión de `make medir` corre `claude -p` con `--tools ""` (sin herramientas propias del harness), `--strict-mcp-config` (solo el servidor del conjunto) y modelo Sonnet. La respuesta correcta de cada tarea se calcula en la corrida llamando directo al BFF. La plantilla `prompts/01-tarea.txt` pide terminar con una línea `RESPUESTA:` y declara que «mayor cambio» significa el mayor movimiento en valor absoluto.

## Cifras medidas

Lista de definiciones que viaja en cada petición:

| Conjunto | Herramientas | Caracteres |
|---|---|---|
| espejo | 4 | 985 |
| agente | 3 | 4,771 |

Seis tareas, cinco repeticiones cada una, 30 corridas por conjunto (`logs/30-resumen.txt`):

| | espejo | agente |
|---|---|---|
| aciertos | 30 de 30 | 30 de 30 |
| llamadas, total | 55 | 30 |
| llamadas, mediana por tarea | 1.5 | 1 |
| rondas de llamadas por corrida | 1 | 1 |
| tokens de entrada (nuevos + caché) | 103,455 + 165,822 | 100,591 + 183,931 |
| tokens de salida | 6,416 | 5,063 |

El conjunto del agente hace menos llamadas y escribe menos tokens de salida, y empata en aciertos. Consume más tokens de entrada, cerca de 6 por ciento más, porque su lista de definiciones es más larga y su respuesta de analizar un símbolo trae el panel completo. Son seis tareas y cinco repeticiones: una muestra pequeña que muestra una dirección y no alcanza para prometer un porcentaje. La transcripción de cada sesión en `logs/20-*.jsonl` es lo que permite corregir una descripción y volver a medir.

La primera medición dio 25 de 30 en los dos conjuntos. La tarea 2 falló las 5 repeticiones en ambos porque «mayor cambio» admite dos lecturas y los dos agentes tomaron el mayor movimiento en valor absoluto. Se aclaró la regla en la plantilla, se ajustó el juez y se repitió, pero esa regla se decidió con el resultado a la vista, así que esa repetición también se descartó. Para la medición de esta tabla, el prompt, las tareas y el juez se fijaron antes de correr (huellas SHA-256 en `logs/20-antes-de-correr.txt`), la tarea 6 precisa que el cambio es el del último día y se corrió una sola vez, sin cambios después (`logs/20-salida-del-juez.txt`). Los logs descartados quedan en `logs/descartadas-tarea2-ambigua/` y `logs/descartadas-2026-11-11/`.

## Verificación con navegador

`make verificar-ui` abre la web desplegada con Playwright MCP, busca NVDA y reporta qué aparece. Playwright corre sin ventana, con un perfil temporal y con `--allowed-origins` limitado al origen de la web.

| Corrida | Pasos | Tokens de entrada | Tokens de salida | Veredicto |
|---|---|---|---|---|
| web con el API correcto (`logs/40-verificar-ui.jsonl`) | 4 | 57,319 | 707 | ok: aparecen precio, gráfico del mes y sentimiento |
| web con una dirección de API inválida (`logs/41-verificar-ui-roto.jsonl`) | 5 | 57,367 | 672 | falla: error 500 y el mensaje genérico de Next.js |

Los comandos que rompen y restauran la dirección del API están en `logs/41-romper-api.txt` y `logs/42-restaurar-api.txt`. Las direcciones de los servicios se reemplazaron por `{{URL_WEB}}` y `{{URL_API}}`.

**Nos vemos en el código.**
