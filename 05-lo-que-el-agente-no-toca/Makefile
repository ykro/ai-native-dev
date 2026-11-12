# Tema 05 · Lo que el agente no puede tocar (Rent My Gear)
APP := rent-my-gear
TRABAJO ?= $(HOME)/ai-native-05

.PHONY: instalar canario juez juez-sin-guardas juez-vivo sesion-sin-guardas sesion-con-guardas resumen

instalar:
	cd $(APP) && npm ci

# Genera un canario nuevo y lo escribe en rent-my-gear/.env.local (valor falso).
canario:
	python3 scripts/canario.py

# Juez de las barreras contra el proyecto con guardas (sin red: registro simulado).
juez:
	python3 juez/juez_guardas.py --proyecto $(APP)

# El mismo juez contra una copia sin .claude/ y sin .npmrc (todo lo que bloquea sale en rojo).
juez-sin-guardas:
	@rm -rf $(TRABAJO)/juez-sin && mkdir -p $(TRABAJO)/juez-sin
	@rsync -a --exclude node_modules --exclude .claude --exclude .npmrc --exclude dependencias-permitidas.json $(APP)/ $(TRABAJO)/juez-sin/$(APP)/
	@python3 juez/juez_guardas.py --proyecto $(TRABAJO)/juez-sin/$(APP)

# Los casos de instalación contra el registro de verdad de npm (usa red; solo consulta).
juez-vivo:
	python3 juez/juez_guardas.py --proyecto $(APP) --registro real --casos 4,5,6,7,9

sesion-sin-guardas:
	python3 scripts/sesion.py sin 02-variables B2-sin-guardas-variables
	python3 scripts/sesion.py sin 01-paquete-inventado B1-sin-guardas-paquete

sesion-con-guardas:
	python3 scripts/sesion.py con 01-paquete-inventado D1-con-guardas-paquete
	python3 scripts/sesion.py con 02-variables D2-con-guardas-variables
	python3 scripts/sesion.py con 03-editar-el-juez D3-con-guardas-editar-juez
	python3 scripts/sesion.py con 04-comando-disfrazado D4-con-guardas-comando-disfrazado

# Tabla final: seis sesiones, bloqueos, preguntas y apariciones del canario; después el juez.
resumen:
	python3 scripts/resumen.py
	@echo
	python3 juez/juez_guardas.py --proyecto $(APP) | tail -3
	@grep -q "ignore-scripts=true" $(APP)/.npmrc && echo "npm: ignore-scripts=true (los scripts de instalación están desactivados)"
