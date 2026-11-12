#!/usr/bin/env bash
# Despliega TraderPulse en Cloud Run (API primero, después la web con la dirección del API).
# Uso (desde 03-localhost-a-cloud-run/):  PROJECT_ID=... REGION=us-central1 scripts/desplegar.sh
# Los servicios quedan con min-instances 0. El token se genera aquí y solo vive en Secret Manager.
set -euo pipefail
: "${PROJECT_ID:?define PROJECT_ID}" "${REGION:=us-central1}"
export PROJECT_ID REGION TAG="${TAG:-v1}"
REPO="$REGION-docker.pkg.dev/$PROJECT_ID/traderpulse"
TMP="$(mktemp -d)"
ahora() { date +%s; }
paso() { printf '\n== %s\n' "$*"; }

paso "APIs"
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com cloudbuild.googleapis.com
paso "registro de imágenes"
gcloud artifacts repositories describe traderpulse --location "$REGION" >/dev/null 2>&1 ||
  gcloud artifacts repositories create traderpulse --repository-format=docker --location="$REGION"
paso "secreto con un valor aleatorio (no se imprime)"
# Sin salto de línea al final: con `openssl rand` directo el secreto queda con "\n" y el BFF rechaza el token.
gcloud secrets describe traderpulse-token >/dev/null 2>&1 ||
  printf %s "$(openssl rand -hex 24)" | gcloud secrets create traderpulse-token --data-file=-
paso "cuentas de servicio y permiso de lectura del secreto"
for cuenta in traderpulse-api traderpulse-web; do
  gcloud iam service-accounts describe "$cuenta@$PROJECT_ID.iam.gserviceaccount.com" >/dev/null 2>&1 ||
    gcloud iam service-accounts create "$cuenta"
  gcloud secrets add-iam-policy-binding traderpulse-token \
    --member="serviceAccount:$cuenta@$PROJECT_ID.iam.gserviceaccount.com" \
    --role=roles/secretmanager.secretAccessor --condition=None >/dev/null
done

INICIO=$(ahora)
echo "INICIO_DESPLIEGUE $INICIO"
paso "construir y subir las imágenes con Cloud Build"
gcloud builds submit traderpulse/backend --tag "$REPO/api:$TAG" --quiet
gcloud builds submit traderpulse/frontend --tag "$REPO/web:$TAG" --quiet
paso "servicio del API"
envsubst '${PROJECT_ID} ${REGION} ${TAG}' < gcp/api.servicio.yaml > "$TMP/api.yaml"
gcloud run services replace "$TMP/api.yaml" --region "$REGION"
gcloud run services add-iam-policy-binding traderpulse-api --region "$REGION" \
  --member=allUsers --role=roles/run.invoker >/dev/null
API_URL=$(gcloud run services describe traderpulse-api --region "$REGION" --format='value(status.url)')
export API_URL
paso "servicio de la web con la dirección del API"
envsubst '${PROJECT_ID} ${REGION} ${TAG} ${API_URL}' < gcp/web.servicio.yaml > "$TMP/web.yaml"
gcloud run services replace "$TMP/web.yaml" --region "$REGION"
gcloud run services add-iam-policy-binding traderpulse-web --region "$REGION" \
  --member=allUsers --role=roles/run.invoker >/dev/null
WEB_URL=$(gcloud run services describe traderpulse-web --region "$REGION" --format='value(status.url)')

paso "esperar a que ambos servicios respondan"
for url in "$API_URL/salud" "$WEB_URL/"; do
  until [ "$(curl -s -o /dev/null -w '%{http_code}' "$url")" = "200" ]; do sleep 2; done
done
FIN=$(ahora)
echo "FIN_DESPLIEGUE $FIN"
echo "DURACION_DESPLIEGUE_S $((FIN - INICIO))"
rm -rf "$TMP"
