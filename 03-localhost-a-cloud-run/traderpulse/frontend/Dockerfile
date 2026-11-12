FROM node:24-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# API_URL y TRADERPULSE_TOKEN se leen al arrancar, no aquí.
RUN npm run build

FROM node:24-slim
ENV NODE_ENV=production HOSTNAME=0.0.0.0 NEXT_TELEMETRY_DISABLED=1
WORKDIR /app
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
USER 10001
# exec: node recibe SIGTERM como PID 1. Next lee PORT del entorno.
CMD ["node", "server.js"]
