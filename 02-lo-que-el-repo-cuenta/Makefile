# Tema 02 · Lo que el repo le cuenta al agente (TraveLens)
APP := travelens

.PHONY: instalar check juez evidencia resumen volver-al-inicio aplicar-entrega

instalar:
	cd $(APP) && npm ci

# Corre los tres comandos únicos de verificación documentados en AGENTS.md
check:
	cd $(APP) && npm run typecheck && npm run lint && npm run test:run

# Ejecuta el juez oculto (7 pruebas sobre POST /api/ai-plan y GeminiService)
juez:
	cd $(APP) && npm run juez

# Evidencia completa: comandos de AGENTS.md + juez oculto + build de producción
evidencia: check juez
	cd $(APP) && npm run build

# Muestra la tabla comparativa de los logs reales antes vs. después
resumen:
	@python3 scripts/resumen_medicion.py medicion/logs/01-antes.jsonl medicion/logs/02-despues.jsonl

# Regresa gemini.ts y route.ts al estado previo al encargo (juez en rojo: 5 fallan)
volver-al-inicio:
	cp medicion/antes/gemini.inicial.ts $(APP)/src/services/gemini.ts
	cp medicion/antes/route.inicial.ts $(APP)/src/app/api/ai-plan/route.ts
	cp medicion/antes/gemini.inicial.test.ts $(APP)/src/services/gemini.test.ts
	cp medicion/antes/route.inicial.test.ts $(APP)/src/app/api/ai-plan/route.test.ts

# Vuelve a aplicar el cambio entregado por el agente en la corrida después
aplicar-entrega:
	patch -d $(APP) -p1 < medicion/entrega.patch
