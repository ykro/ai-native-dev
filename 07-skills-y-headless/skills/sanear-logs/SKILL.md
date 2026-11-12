---
name: sanear-logs
description: Quita rutas locales, usuario, hostname, correos y campos de la máquina de un log de sesión (Claude Code, Codex o AGI CLI) antes de publicarlo o mostrarlo en un video. Úsala cuando vayas a copiar un log .jsonl a un repo público, a una captura o a un artículo.
---

# Sanear logs

Un log de sesión trae la ruta completa donde corrió el agente, el nombre de usuario, a veces el hostname y la lista de plugins de la máquina. Nada de eso se publica.

## Pasos

1. Corre `python3 scripts/sanear.py <log> <salida> --raiz <carpeta-de-trabajo>=<alias>` por cada log. El alias es lo que se verá, por ejemplo `~/travelens-06`.
2. Corre `python3 scripts/sanear.py --verificar <salida>`. Si encuentra algo, devuelve código 1 y la línea; no publiques hasta que salga en cero.
3. Nunca edites el log a mano: si falta un reemplazo, agrega otra `--raiz` o `--ocultar` y vuelve a correr.

## Qué cambia

- La carpeta de trabajo y la carpeta personal pasan a su alias.
- El nombre de usuario, el hostname y los correos se reemplazan.
- En el evento de inicio de Claude Code se quitan `plugins`, `mcp_servers`, `slash_commands`, `agents`, `skills`, `memory_paths`, `session_id` y `uuid`.
