# Tema 07 · Una Skill, un juez y un lote con agentes headless
PY := .venv/bin/python

.PHONY: instalar pruebas lote-sin-skill lote-con-skill tabla

instalar:
	uv venv .venv -q && uv pip install -q --python $(PY) pytest
	cd pawsmatch/app && npm ci

pruebas:
	$(PY) -m pytest tests/test_validar_mascotas.py -q
	cd pawsmatch/app && npm test

lote-sin-skill:
	python3 scripts/agregar_en_lote.py --brazo sin-skill --repeticiones 3

lote-con-skill:
	python3 scripts/agregar_en_lote.py --brazo con-skill --repeticiones 3

tabla:
	python3 scripts/tabla_resultados.py
