---
name: resumen-de-sesion
description: Resume un log headless de Claude Code (claude -p --output-format stream-json) en turnos, herramientas usadas, intentos fallidos (bloqueados por permisos o fallidos al ejecutarse), corridas del juez, tokens y duración. Úsala para comparar corridas o para sacar las cifras que se narran en un video; nunca narres una cifra que no salga de aquí.
---

# Resumen de sesión

## Pasos

1. Corre `python3 scripts/resumen.py <log.jsonl> [<log.jsonl> ...]`.
2. Con `--json` devuelve los datos para otra herramienta; sin él imprime una tabla.
3. Si un campo no existe en el log, sale vacío. No lo estimes.
