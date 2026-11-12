# 03 · De localhost a Cloud Run con contratos tipados

Código del **tema 03** de la serie **AI Native Dev** por **Adrián Catalán** (`@adriancs.tech`). Proyecto hilo: **TraderPulse**.

Un BFF en FastAPI y un frontend en Next.js comparten un contrato OpenAPI. Un juez compara el contrato con los modelos y con los tipos del frontend. Otro juez examina las imágenes de contenedor y la configuración de Cloud Run antes de pedirle a un agente que escriba los Dockerfiles. Al final la aplicación corre en [Cloud Run](https://cloud.google.com/run/docs) con el token en [Secret Manager](https://cloud.google.com/secret-manager/docs).

## Qué hay aquí

```text
03-localhost-a-cloud-run/
├── Makefile
├── despliegue.md                  # Contrato de despliegue: qué cambia, qué no se toca, quién decide
├── traderpulse/
│   ├── backend/                   # BFF FastAPI; los modelos Pydantic son el contrato (+ Dockerfile)
│   ├── frontend/                  # Next.js 16; los tipos salen del contrato (+ Dockerfile)
│   └── contrato/openapi.json      # Contrato publicado, generado desde el BFF
├── juez/
│   ├── juez_contrato.py           # 3 verificaciones: contrato, tipos y compilación del frontend
│   └── juez_contenedor.py         # 23 verificaciones: 2 imágenes y 2 definiciones de servicio (no se edita)
├── gcp/                           # api.servicio.yaml y web.servicio.yaml (Knative, con variables)
├── prompts/                       # Los tres encargos que se le dan al agente
├── scripts/
│   ├── resumen_sesion.py          # Turnos, herramientas, intentos fallidos y tokens de un log
│   ├── sanear_log.py              # Quita rutas locales y plugins de un log antes de publicarlo
│   └── desplegar.sh               # El despliegue completo a Cloud Run
├── entrega/                       # Lo que dejó cada sesión del agente, como parche
└── logs/                          # Sesiones headless y salidas de los jueces
```

## Cómo correrlo

Requisitos: Docker en marcha, `uv`, Node 24 y, para desplegar, `gcloud` con un proyecto con facturación.

```bash
cd 03-localhost-a-cloud-run
make instalar
make juez-contrato            # 3 de 3
make volver-al-inicio         # quita los Dockerfiles y los YAML que dejó el agente
make juez-contenedor          # 0 de 23: sin Dockerfiles todo falla
make aplicar-entrega          # aplica lo que dejó la sesión contra el juez
make juez-contenedor          # 23 de 23
PROJECT_ID=<tu-proyecto> REGION=us-central1 scripts/desplegar.sh
make resumen                  # cifras de las tres sesiones grabadas
```

`scripts/desplegar.sh` deja los dos servicios con `min-instances` en 0, genera el token al momento y lo guarda en Secret Manager. El token nunca pasa por un archivo del repositorio. Crea el secreto sin salto de línea al final (`printf %s`). Con `openssl rand` directo hacia `gcloud secrets create`, el secreto queda con un `\n` y el BFF rechaza el token con 401.

## Cómo se grabaron las sesiones

Claude Code en modo headless (`claude -p ... --output-format stream-json --verbose`), modelo Sonnet, una corrida por sesión, en una copia limpia del repositorio. Las sesiones de despliegue no tienen acceso a `gcloud`, y ninguna puede escribir dentro de `juez/`.

| Sesión | Qué recibe | Turnos | Duración | Corridas del juez | Resultado |
|---|---|---|---|---|---|
| `00-contrato` | renombrar `cambio_pct` a `variacion_pct`; el compilador señala lo que falta | 28 | 64 s | 1 | `tsc` entregó 3 errores; juez del contrato 3 de 3 |
| `11-una-linea` | una línea: prepara TraderPulse para Cloud Run | 20 | 62 s | 0 | juez de despliegue 22 de 23 |
| `12-contra-el-juez` | contrato de despliegue y juez | 21 | 209 s | 2 (0 de 23, después 23 de 23) | 23 de 23 |

La única verificación que falló en la sesión de una línea es «web · tiene startup probe HTTP»: el agente declaró una prueba de arranque que solo abre una conexión al puerto. Los tokens de cada sesión salen de `make resumen`.

## Verificaciones medidas

- Captura A, `logs/01-contrato-verde.txt`: juez del contrato 3 de 3.
- Captura B, `logs/02-contrato-rojo.txt`: tras renombrar el campo en el backend y regenerar el contrato, las pruebas del backend pasan (7) y el juez falla en la compilación con 3 errores: `src/app/page.tsx` (líneas 52 y 63) y `tests/contrato.test.ts` (línea 15).
- Captura D, `logs/10-juez-rojo.txt`: juez de despliegue sin Dockerfiles, 0 de 23.
- Captura E, `logs/11-una-linea-juez.txt`: 22 de 23.
- Captura F, `logs/12-juez-verde.txt`: 23 de 23 sobre el repositorio con la entrega aplicada.
- Despliegue, `logs/20-despliegue.txt`: 241 segundos desde la primera construcción con Cloud Build hasta que los dos servicios respondieron 200.
- Prueba de humo, `logs/21-humo.txt`: el API sin token responde 401, con token responde 200 y la web devuelve el precio de NVDA.
- `logs/20-despliegue-primer-intento.txt` y `logs/21-humo-primer-intento.txt` guardan un primer despliegue con el secreto creado con salto de línea al final: los dos servicios respondían 200 y la prueba de humo devolvía 401 con el token correcto.

Los identificadores del proyecto de nube y las direcciones de los servicios se reemplazaron por `{{PROJECT_ID}}`, `{{PROJECT_NUMBER}}`, `{{URL_API}}` y `{{URL_WEB}}` en los logs.

## Servicios

`traderpulse-api` y `traderpulse-web` en Cloud Run, región `us-central1`, `min-instances` en 0 y 5 instancias como máximo. Cada uno usa su propia cuenta de servicio con un solo permiso, leer el secreto del token. El API es público y lo protege el token que comparten los dos servicios.

**Nos vemos en el código.**
