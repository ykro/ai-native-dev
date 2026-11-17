# Judge-First sobre Rent My Gear
APP := rent-my-gear

.PHONY: instalar juez evidencia build aplicar-entrega volver-al-inicio resumen test all

instalar:
	cd $(APP) && npm ci

# El juez no se edita: si alguien lo tocó, la corrida no cuenta.
juez:
	@git diff --quiet HEAD -- $(APP)/juez $(APP)/vitest.juez.config.ts || \
		(echo "El juez cambió desde el último commit; la corrida no cuenta." && exit 1)
	cd $(APP) && npm run juez

# Evidencia de entrega, la misma que pide contrato.md: juez, suite completa y tipos.
evidencia: juez
	cd $(APP) && npm run test:run && npx tsc --noEmit

# Build de producción de la app (aparte de la evidencia del contrato).
build:
	cd $(APP) && npm run build

# Aplica el cambio que entregó el agente en la corrida grabada (logs/03-iterar.jsonl).
aplicar-entrega:
	patch -d $(APP) -p1 < entrega/cobertura.patch

# Regresa la app al estado inicial (juez en rojo).
volver-al-inicio:
	git checkout -- $(APP)/src && git clean -fdq -- $(APP)/src

resumen:
	@for f in logs/0*.jsonl; do python3 scripts/resumen_sesion.py $$f; echo; done

# Un test por fragmento de practica/ (necesita make instalar y el venv con pytest).
test:
	python3 -m pytest -v tests/test_practica.py

all: test
