# Tema 01 · Judge-First sobre Rent My Gear
APP := rent-my-gear

.PHONY: instalar juez evidencia aplicar-entrega volver-al-inicio resumen

instalar:
	cd $(APP) && npm ci

# El juez no se edita: si alguien lo tocó, la corrida no cuenta.
juez:
	@git diff --quiet HEAD -- $(APP)/juez $(APP)/vitest.juez.config.ts || \
		(echo "El juez cambió desde el último commit; la corrida no cuenta." && exit 1)
	cd $(APP) && npm run juez

# Evidencia de entrega: juez, suite completa, tipos y build de producción.
evidencia: juez
	cd $(APP) && npm run test:run && npx tsc --noEmit && npm run build

# Aplica el cambio que entregó el agente en la corrida grabada (logs/03-iterar.jsonl).
aplicar-entrega:
	patch -d $(APP) -p1 < entrega/cobertura.patch

# Regresa la app al estado inicial (juez en rojo).
volver-al-inicio:
	git checkout -- $(APP)/src

resumen:
	@for f in logs/0*.jsonl; do python3 scripts/resumen_sesion.py $$f; echo; done
