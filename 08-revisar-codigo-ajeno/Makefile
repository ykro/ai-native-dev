# Tema 08 · Revisar código que no escribiste (TraderPulse)
PY := .venv/bin/python
export GEMINI_API_KEY ?= test-key-no-real-calls

.PHONY: instalar pruebas juez pruebas-pr

instalar:
	uv venv .venv -q
	uv pip install -q --python $(PY) -r traderpulse/backend/requirements.txt

# Pruebas de la base (la copia de la edición 2026, sin cambios).
pruebas:
	cd traderpulse && ../$(PY) -m pytest backend/tests -q

# El juez se escribe antes de ver el cambio; sobre la base debe fallar.
juez:
	$(PY) -m pytest juez -q

# Pruebas propias del PR, corridas en la rama pr/rsi-y-noticias (requiere scripts/crear_pr.sh).
pruebas-pr:
	cd .work/repo && git checkout -q pr/rsi-y-noticias && ../../$(PY) -m pytest backend/tests -q; cd .work/repo && git checkout -q main
