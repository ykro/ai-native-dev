# Contrato de despliegue · TraderPulse en Cloud Run

## Qué cambia
- Un Dockerfile y un .dockerignore en traderpulse/backend y en traderpulse/frontend.
- gcp/api.servicio.yaml y gcp/web.servicio.yaml (servicios de Cloud Run, formato Knative).
- El frontend lee API_URL y TRADERPULSE_TOKEN al arrancar; el token sale de Secret Manager.

## Qué no se toca
- juez/, el código de traderpulse/*/src y traderpulse_api/, y el contrato OpenAPI.

## Quién decide
- `uv run --with pyyaml python juez/juez_contenedor.py` en 23 de 23.
