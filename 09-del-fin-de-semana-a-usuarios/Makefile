# Tema 09 · Del prototipo de fin de semana a usuarios
PY := .venv/bin/python
PROYECTOS := pawsmatch travelens rent-my-gear traderpulse

.PHONY: instalar pruebas antes cerrar costo tabla

instalar:
	uv venv .venv -q
	uv pip install -q --python $(PY) pytest -r proyectos/traderpulse/backend/requirements.txt
	cd proyectos/pawsmatch/app && npm ci
	cd proyectos/travelens && npm ci
	cd proyectos/rent-my-gear && npm ci

pruebas:
	$(PY) -m pytest tests -q

antes:
	for p in $(PROYECTOS); do $(PY) salida/juez_salida.py --proyecto $$p; done

cerrar:
	python3 scripts/cerrar_brechas.py --todos --paralelo

costo:
	$(PY) scripts/medir_tokens.py
	python3 scripts/costo_por_usuario.py

tabla:
	python3 scripts/tabla_cierre.py
