#!/usr/bin/env bash
# Un agente con navegador comprueba la aplicación desplegada y entrega un veredicto.
# Uso (desde 04-tools-para-agentes/):  scripts/verificar_ui.sh <URL_WEB> <prefijo-del-log>
# El navegador (Playwright MCP) corre sin ventana, con un perfil temporal sin sesiones guardadas
# y solo puede pedir recursos del origen de la web. El log se guarda saneado en logs/.
set -euo pipefail
WEB_URL="${1:?falta la URL de la web}"; ARCHIVO="${2:-40-verificar-ui}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
ORIGEN="$(python3 -c 'import sys,urllib.parse as u; p=u.urlparse(sys.argv[1]); print(f"{p.scheme}://{p.netloc}")' "$WEB_URL")"
sed "s|{{ORIGEN_WEB}}|$ORIGEN|" "$RAIZ/mcp/playwright.mcp.json" > "$TMP/mcp.json"
PROMPT="$(sed "s|{URL_WEB}|$WEB_URL|" "$RAIZ/prompts/04-verificar-ui.txt")"
cd "$TMP"
claude -p "$PROMPT" --model claude-sonnet-5-5 --output-format stream-json --verbose --max-turns 20 \
  --mcp-config "$TMP/mcp.json" --strict-mcp-config --tools "" --allowedTools "mcp__playwright" \
  --disable-slash-commands --no-session-persistence --setting-sources project \
  > "$TMP/sesion.jsonl" 2> "$TMP/stderr.txt" || true
python3 "$RAIZ/scripts/sanear_log.py" "$TMP/sesion.jsonl" "$RAIZ/logs/$ARCHIVO.jsonl" \
  "$WEB_URL={{URL_WEB}}" "$ORIGEN={{URL_WEB}}" "${API_URL:-https://sin-api.invalid}={{URL_API}}" "$TMP=~/tmp"
python3 "$RAIZ/scripts/resumen_sesion.py" "$RAIZ/logs/$ARCHIVO.jsonl"
