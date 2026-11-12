# Tema 03 · De localhost a Cloud Run con contratos tipados sobre TraderPulse
APP := traderpulse

.PHONY: instalar probar-backend compilar contrato juez-contrato juez-contenedor aplicar-entrega volver-al-inicio resumen

instalar:
	cd $(APP)/backend && uv sync
	cd $(APP)/frontend && npm ci

# Regenera el contrato OpenAPI desde los modelos del BFF y de ahí los tipos del frontend.
contrato:
	cd $(APP)/backend && uv run -q python scripts/exportar_openapi.py
	cd $(APP)/frontend && npm run -s tipos:api > /dev/null

probar-backend:
	cd $(APP)/backend && uv run -q pytest -q

# Compila el frontend contra los tipos generados; lista archivo y línea de cada uso desfasado.
compilar:
	cd $(APP)/frontend && node_modules/.bin/tsc --noEmit

juez-contrato:
	python3 juez/juez_contrato.py

# El juez de despliegue no se edita: si alguien lo tocó, la corrida no cuenta.
juez-contenedor:
	@git diff --quiet HEAD -- juez || (echo "El juez cambió desde el último commit; la corrida no cuenta." && exit 1)
	uv run --with pyyaml python juez/juez_contenedor.py

# Aplica lo que dejó la sesión contra el juez (logs/12-contra-el-juez.jsonl).
aplicar-entrega:
	patch -p1 < entrega/12-contra-el-juez.patch

# Regresa el repositorio a antes de los Dockerfiles (el juez de despliegue vuelve a quedar en rojo).
volver-al-inicio:
	rm -f $(APP)/backend/Dockerfile $(APP)/backend/.dockerignore $(APP)/frontend/Dockerfile $(APP)/frontend/.dockerignore
	rm -f gcp/*.yaml

resumen:
	@for f in logs/00-*.jsonl logs/1*.jsonl; do python3 scripts/resumen_sesion.py $$f; echo; done
