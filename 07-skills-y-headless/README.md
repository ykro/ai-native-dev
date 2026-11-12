# 07 · Empaquetar lo que repites con Skills y modo headless

Carpeta del monorepo público de **AI Native Dev**. Proyecto hilo: **PawsMatch**.

Una Skill (`agregar-mascota`) con un validador determinista como juez, y un script que lanza agentes en modo *headless* (`claude -p`) para agregar mascotas en lote, con y sin la Skill, y mide cada llamada con el mismo juez.

## Qué hay aquí

```text
07-skills-y-headless/
├── pawsmatch/                      # La app de la edición 2026 (React + Vite + Vitest), con npm test en verde
│   ├── app/src/data/pets.json      # 50 mascotas: id, nombre y bio de tres líneas
│   └── .claude/skills/agregar-mascota/
│       ├── SKILL.md                # 34 líneas: qué hace, cuándo usarla, pasos y límites
│       ├── references/formato-bio.md   # Tono y ejemplos; el agente solo lo abre al redactar
│       └── scripts/validar_mascotas.py # El juez: determinista, sin red, código de salida 0 o 1
├── tests/test_validar_mascotas.py  # Un archivo bueno y un archivo por regla rota (14 pruebas)
├── lote/
│   ├── mascotas-nuevas.csv         # Cinco filas: nombre y dos rasgos
│   ├── prompt-pegado.txt           # El párrafo largo que se pegaba antes de tener la Skill
│   ├── resultado-sin-skill.json    # Una fila por llamada: válida, turnos, duración, costo, errores
│   ├── resultado-con-skill.json
│   └── crudo-*/                    # JSON de salida de cada llamada a claude -p, saneado
├── scripts/
│   ├── agregar_en_lote.py          # El lote: --brazo sin-skill|con-skill --repeticiones N
│   ├── registrar_sesion.py         # Graba una sesión en stream-json, saneada
│   └── tabla_resultados.py         # Tabla de comparación
├── logs/
│   ├── pytest-rojo.txt, pytest-verde.txt   # El juez antes y después de escribir el validador
│   ├── con-skill-fila1.jsonl       # Una fila con la Skill: se carga en el turno 1, el validador corre en el turno 6
│   ├── sin-activar.jsonl           # Un pedido ajeno (color de un botón): la Skill no se carga
│   └── tabla.txt
├── inventario/inventario_skills.py # Cuenta líneas y descripciones de las Skills instaladas
└── skills/                         # Tres Skills de ejemplo reutilizables
```

## Cómo correrlo

```bash
make instalar
make pruebas                      # 14 pruebas del validador y la suite de PawsMatch
python3 scripts/agregar_en_lote.py --brazo sin-skill --repeticiones 3
python3 scripts/agregar_en_lote.py --brazo con-skill --repeticiones 3
python3 scripts/tabla_resultados.py
```

Requiere `claude` (probado con Claude Code 2.1.318) y sesión iniciada. Cada brazo hace 15 llamadas, aproximadamente 2 dólares por brazo con Sonnet.

## Cómo funciona el lote

Para cada repetición el script copia PawsMatch a una carpeta temporal (sin `.claude/skills` en el brazo `sin-skill`) y recorre las cinco filas del CSV en orden, de modo que los ids siguen creciendo. Por fila lanza:

```text
claude -p "<pedido>" --output-format json --max-turns 12 --model sonnet \
       --setting-sources project --max-budget-usd 1.00 \
       --allowedTools Read "Edit(app/src/data/pets.json)" [Skill "Bash(python3 <validador> *)"]
```

El brazo `sin-skill` recibe el párrafo pegado más el pedido y solo puede leer y editar el archivo de datos. El brazo `con-skill` recibe solo el pedido y además puede invocar la Skill y correr el validador. Todo lo que no esté en la lista falla, porque en modo headless nadie contesta permisos. Después de cada llamada el script corre el validador por su cuenta; si el archivo no pasa, o la mascota no quedó agregada, la fila es inválida y se revierte. El código de salida es 1 si alguna fila quedó inválida.

## Cifras de la corrida (Claude Code 2.1.318, Sonnet, 5 mascotas x 3 repeticiones por brazo)

| Brazo | Llamadas | Válidas | Turnos promedio | Segundos promedio | Dólares por mascota | Dólares totales |
|---|---|---|---|---|---|---|
| sin Skill | 15 | 12 | 6.4 | 28.7 | 0.133 | 1.99 |
| con Skill | 15 | 15 | 7.2 | 19.1 | 0.148 | 2.21 |

Las tres filas inválidas del brazo sin Skill no fallaron por el contenido de la biografía: el agente intentó editar el archivo de datos y la lista de permisos le negó la edición, así que la mascota no quedó agregada. No encontré la causa de que esa edición se negara en esas llamadas y no en las otras. En el brazo sin Skill, además, el agente intentó correr comandos de Bash que no estaban permitidos en las 15 llamadas; con la Skill, en ninguna.

Es una muestra pequeña para entender el mecanismo. No prueba que una Skill siempre mejore algo.

**Corrida inicial descartada.** La primera corrida dio 9 de 15 válidas sin Skill y 15 de 15 con Skill. Se descartó porque la carpeta temporal se creaba con la ruta `/var/...` y los agentes a veces usaban `/private/var/...`, que son la misma carpeta con dos escrituras, y las reglas de permisos podían tratarlas distinto. Se corrigió resolviendo la ruta real y se repitió completa; el archivo de esa corrida está en `lote/_corrida-inicial-descartada/`. La corrección redujo las ediciones denegadas de 6 a 3 pero no las eliminó.

## Costos

Las 30 llamadas de la corrida válida costaron 4.21 dólares según el campo `total_cost_usd` del JSON de salida de `claude -p`, que es una estimación del cliente y no una factura. La corrida inicial descartada costó otros 4.16 dólares, y las llamadas de diagnóstico y los registros de sesión cerca de 1 dólar más.

## Registros de sesión

- `logs/con-skill-fila1.jsonl`: el agente invoca la Skill en el turno 1, lee el archivo de datos y la guía de estilo, agrega la mascota y corre el validador en el turno 6, que pasa al primer intento.
- `logs/sin-activar.jsonl`: ante «cambia el color del botón de adoptar», el agente busca el botón y nunca invoca la Skill.

Los registros se sanearon: sin rutas locales, usuario ni equipo, y el evento inicial se reduce a los campos relevantes.
