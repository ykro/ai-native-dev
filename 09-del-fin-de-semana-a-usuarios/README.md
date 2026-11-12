# 09 · Del prototipo de fin de semana a usuarios

Carpeta del monorepo público de **AI Native Dev**. Proyecto hilo: **los cuatro** (PawsMatch, TraveLens, Rent My Gear y TraderPulse).

Un juez de salida con siete promesas a un usuario, cuatro agentes *headless* que cierran las brechas en paralelo (cada uno en su copia y su `worktree`), una revisión con sesión limpia de solo lectura, el costo de cada sesión y de cada petición al modelo, y una prueba de humo. No es una fábrica: son cuatro encargos explícitos y una persona que decide al final.

## Qué hay aquí

```text
09-del-fin-de-semana-a-usuarios/
├── proyectos/                    # Los cuatro proyectos en su estado inicial (copias de las carpetas de los temas 01, 02, 07 y 08)
├── salida/
│   ├── juez_salida.py            # --proyecto <nombre> [--ruta] [--json]; sale con 1 si falla algo aplicable
│   ├── perfiles/*.json           # Qué comprobaciones aplican a cada proyecto y su comando
│   ├── buscar_secretos.py        # Expresiones regulares, sin dependencias
│   ├── precios.json              # Tarifa por millón de tokens, URL oficial y fecha de consulta
│   └── skills/salida-a-usuarios/SKILL.md   # 45 líneas: cómo cerrar una brecha con Judge-First
├── scripts/
│   ├── cerrar_brechas.py         # Copia + worktree + juez antes + agente + juez después + medición
│   ├── revisar_salida.sh         # Revisión: juez, archivos prohibidos, aserciones quitadas, dependencias nuevas y agente revisor
│   ├── medir_tokens.py           # Tokens reales de una petición (TraveLens y TraderPulse) contra Vertex AI
│   ├── costo_por_usuario.py      # Costo por petición y escenarios con supuestos impresos
│   ├── tabla_cierre.py           # medicion/tabla.md
│   └── humo.sh                   # Prueba de humo: URL desplegada o build local
├── medicion/
│   ├── estimacion-previa.md      # PENDIENTE: la completa el autor antes de grabar
│   ├── intervenciones.md         # Registro de intervenciones del autor (esta corrida no tuvo)
│   ├── <proyecto>-antes.json, -despues.json, <proyecto>.json, <proyecto>.patch, <proyecto>-revision.json
│   ├── tokens-por-peticion-*.jsonl, costo-por-usuario.json, corrida.json, tabla.md
├── prompts/revisar-salida.txt
├── logs/                         # cerrar-<proyecto>.jsonl (stream-json saneado) y salidas de los scripts
└── tests/test_juez_salida.py     # Escáner de secretos y comprobación del README
```

## Las siete comprobaciones

1 comando único de verificación en verde, 2 sin secretos versionados y `.env` ignorado, 3 auditoría de dependencias de producción sin hallazgos altos (`npm audit` o `pip-audit`), 4 prueba de tiempo agotado y respuesta rota del modelo, 5 tope de salida del modelo y límite de peticiones por cliente con prueba, 6 registros sin datos personales y ruta de salud con prueba, 7 sección «Cómo volver atrás» en el README. PawsMatch no llama al modelo, así que 4 y 5 se marcan N/A con su razón y su ruta de salud es un archivo estático con prueba.

El juez declara sus comprobaciones débiles: la 7 solo comprueba que la sección y un comando existen, y la parte de datos personales de la 6 depende de la prueba que escribe el propio proyecto. Las pruebas se encuentran por una etiqueta en el nombre (`modelo-timeout`, `limite-peticiones`, `salud`...), que la Skill documenta.

## Cómo correrlo

```bash
make instalar && make pruebas
make antes                                  # puntaje inicial
python3 scripts/cerrar_brechas.py --todos --paralelo
for p in pawsmatch travelens rent-my-gear traderpulse; do bash scripts/revisar_salida.sh $p; done
GOOGLE_CLOUD_PROJECT=<tu-proyecto> .venv/bin/python scripts/medir_tokens.py
python3 scripts/costo_por_usuario.py && python3 scripts/tabla_cierre.py
bash scripts/humo.sh local <proyecto>       # o: bash scripts/humo.sh https://<url> <proyecto>
```

Los agentes usan `claude -p` (Claude Code 2.1.318, Sonnet) con permisos explícitos: leer, editar, escribir y correr los comandos de verificación del proyecto; sin Git, sin leer ni editar archivos `.env` y sin tocar `salida/`. Ningún servicio se despliega: la prueba de humo corre contra el build de producción local.

## Cifras de la corrida (2026-11-11)

| Proyecto | Antes | Después | Turnos | Reloj del agente | Dólares (tarifa) | Diff |
|---|---|---|---|---|---|---|
| PawsMatch | 2/5 | 5/5 | 38 | 97 s | 0.30 | 10 archivos, +104 -4 |
| TraveLens | 3/7 | 7/7 | 30 | 105 s | 0.28 | 9 archivos, +144 -6 |
| Rent My Gear | 3/7 | 7/7 | 34 | 171 s | 0.39 | 12 archivos, +282 -10 |
| TraderPulse | 3/7 | 7/7 | 21 | 87 s | 0.24 | 6 archivos, +200 -18 |

- Reloj total de la corrida en paralelo: 304.5 s (incluye el juez antes y después). Suma de los cuatro agentes: 459.5 s.
- Tokens de las cuatro sesiones: 3,431,297 de entrada (104 sin caché, 193,135 de escritura de caché y 3,238,058 de lectura de caché) y 40,069 de salida. Dólares con la tarifa de `salida/precios.json`: 1.21. El campo `total_cost_usd` del JSON de salida de `claude -p` suma 1.50; es una estimación del cliente.
- Revisión (cuatro sesiones de solo lectura): 5, 7, 7 y 6 hallazgos; ninguna dependencia nueva, ninguna aserción quitada, ningún archivo prohibido tocado. Costo de las cuatro revisiones: 0.61 dólares.
- Tokens por petición al modelo (`gemini-3.8-flash`, Vertex AI, tarifa del 2026-11-11 de 0.75 USD de entrada y 3.75 USD de salida por millón): TraveLens 190 de entrada y 1,534 de salida, 0.0059 USD por petición; TraderPulse 125 y 504, 0.0020 USD. La salida incluye los tokens de razonamiento del modelo, que son la mayor parte. Cada una es el promedio de tres peticiones.
- Escenarios (suposiciones, no mediciones): 3 y 10 peticiones por persona al día, 100 y 1,000 personas, 30 días. TraderPulse de 17.85 a 595.12 USD al mes; TraveLens de 53.06 a 1,768.58.
- Prueba de humo contra el build de producción local: los cuatro pasan sus tres comprobaciones. La petición de ejemplo no llama al modelo (TraveLens: petición vacía con 400 controlado; TraderPulse: ruta de gamificación).

## Lo que esta corrida no midió

- **Estimación previa y minutos propios.** `medicion/estimacion-previa.md` espera la estimación del autor, y debe hacerse commit antes de la primera corrida real para que la fecha sea evidencia. Los minutos propios no existen: el agente que preparó esta carpeta ejecutó todo sin cronómetro.
- Los topes de salida que los agentes configuraron (por ejemplo 256 tokens en TraderPulse y 2048 en TraveLens) pueden cortar respuestas válidas, porque el razonamiento del modelo cuenta dentro del tope. Dos revisiones lo señalaron y las mediciones de tokens lo confirman (TraderPulse usa 504 tokens de salida en promedio).
- Una primera corrida de `cerrar_brechas.py` se interrumpió porque un proceso huérfano de una corrida anterior escribía en una carpeta de trabajo; se repitió completa desde cero. Los datos de esta carpeta vienen de la repetición.
