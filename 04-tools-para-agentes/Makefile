# Tema 04 · Tools hechas para agentes sobre TraderPulse
BACK := ../03-localhost-a-cloud-run/traderpulse/backend
PORT ?= 8000
REPS ?= 5

.PHONY: instalar api medir-definiciones medir resumen verificar-ui

instalar:
	cd $(BACK) && uv sync
	uv sync

# BFF de ejemplo (datos deterministas, sin token) en una terminal aparte.
api:
	cd $(BACK) && uv run uvicorn traderpulse_api.main:app --port $(PORT)

# Captura A: cuántas herramientas y cuántos caracteres entrega cada servidor.
medir-definiciones:
	uv run python scripts/medir_definiciones.py mcp/espejo.mcp.json
	uv run python scripts/medir_definiciones.py mcp/agente.mcp.json

# Captura B: 6 tareas x 2 conjuntos x REPS repeticiones. Cada sesión queda en logs/20-*.jsonl.
medir:
	uv run python juez/juez_tools.py --reps $(REPS) --bff http://127.0.0.1:$(PORT)

# Captura C: tabla de resultados a partir de los logs guardados.
resumen:
	python3 scripts/resumen_tools.py

# Captura D: un agente con navegador comprueba la aplicación desplegada del tema 03.
# Uso: make verificar-ui WEB_URL=https://... [ARCHIVO=40-verificar-ui]
verificar-ui:
	@test -n "$(WEB_URL)" || (echo "Falta WEB_URL (la dirección de la web desplegada en el tema 03)." && exit 1)
	scripts/verificar_ui.sh "$(WEB_URL)" "$(or $(ARCHIVO),40-verificar-ui)"
