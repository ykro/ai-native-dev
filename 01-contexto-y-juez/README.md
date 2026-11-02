# 01 · Sesiones largas, contexto limpio y un juez antes del código

Código del **tema 01** de la serie **AI Native Dev** por **Adrián Catalán** (`@adriancs.tech`). Proyecto hilo: **Rent My Gear** (Next.js 16, React 19, Tailwind 4, Zod 4, Vitest 5).

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
├── entrega/cobertura.patch            # El cambio que entregó el agente
└── scripts/resumen_sesion.py          # Turnos, herramientas, intentos fallidos y tokens de un log
```

## Cómo correrlo

```bash
cd 01-contexto-y-juez
make instalar
make juez               # 5 pruebas en rojo: la cobertura no existe todavía
make aplicar-entrega    # aplica el cambio que hizo el agente
make evidencia          # juez 5/5, suite completa, tipos y build
make volver-al-inicio   # regresa src/ al estado inicial
make resumen            # cifras de las tres sesiones grabadas
```

## Cómo se grabaron las sesiones

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
