#!/usr/bin/env bash
# Smoke test. Usage: bash scripts/humo.sh <url|local> [proyecto]
#   url    base URL of a deployed project (home, health route and an example request with a time limit)
#   local  serves the production build of the project locally and runs the same three checks
set -uo pipefail
cd "$(dirname "$0")/.."
TARGET="${1:?url o local}"; PROJECT="${2:-}"
LIMIT=20
fail=0
check() { # name, curl args...
  local name="$1"; shift
  local code; code=$(curl -s -o /dev/null -m "$LIMIT" -w '%{http_code}' "$@" || echo 000)
  if [[ "$code" =~ ^2 ]]; then echo "OK    $name ($code)"; else echo "FALLA $name ($code)"; fail=1; fi
}
if [[ "$TARGET" == "local" ]]; then
  [[ -n "$PROJECT" ]] || { echo "con local hace falta el proyecto"; exit 2; }
  WT=".work/${PROJECT}-wt"; PORT=$((3100 + RANDOM % 500))
  SUB=""; [[ "$PROJECT" == "pawsmatch" ]] && SUB="app"
  # the working copy keeps no node_modules (the agents' runs remove the link); link the installed one for the build
  # Next (Turbopack) refuses a node_modules outside the project root, so it gets a copy-on-write clone instead of a link
  if [[ ! -e "$WT/$SUB/node_modules" && -d "proyectos/$PROJECT/$SUB/node_modules" ]]; then
    if [[ "$PROJECT" == "pawsmatch" ]]; then ln -s "$PWD/proyectos/$PROJECT/$SUB/node_modules" "$WT/$SUB/node_modules"
    else cp -Rc "proyectos/$PROJECT/$SUB/node_modules" "$WT/$SUB/node_modules"; fi
  fi
  [[ "$PROJECT" == "traderpulse" && ! -e "$WT/.venv" ]] && ln -s "$PWD/.venv" "$WT/.venv"
  case "$PROJECT" in
    pawsmatch) (cd "$WT/app" && npx vite build >/dev/null 2>&1) && { (cd "$WT/app" && exec npx vite preview --port "$PORT" >/dev/null 2>&1) & SERVER_PID=$!; } ;;
    travelens|rent-my-gear) (cd "$WT" && npx next build >/dev/null 2>&1) && { (cd "$WT" && exec npx next start -p "$PORT" >/dev/null 2>&1) & SERVER_PID=$!; } ;;
    traderpulse) { (cd "$WT" && GEMINI_API_KEY=test-key exec .venv/bin/python -m uvicorn backend.main:app --port "$PORT" >/dev/null 2>&1) & SERVER_PID=$!; } ;;
  esac
  for _ in $(seq 1 60); do curl -s -o /dev/null -m 2 "http://localhost:$PORT/" && break; sleep 1; done
  BASE="http://localhost:$PORT"
else
  BASE="${TARGET%/}"
fi
case "$PROJECT" in
  pawsmatch) HEALTH="/salud.json"; SAMPLE_ARGS=(-X GET "$BASE/") ;;
  travelens) HEALTH="/api/health"; SAMPLE_ARGS=(-X POST -H 'content-type: application/json' -d '{"destination":""}' "$BASE/api/ai-plan") ;;  # 400 is a controlled answer
  rent-my-gear) HEALTH="/api/health"; SAMPLE_ARGS=(-X GET "$BASE/") ;;
  traderpulse) HEALTH="/health"; SAMPLE_ARGS=(-X GET "$BASE/api/v1/gamification/status") ;;
  *) HEALTH="/health"; SAMPLE_ARGS=(-X GET "$BASE/") ;;
esac
check "pagina principal" "$BASE/"
check "ruta de salud" "$BASE$HEALTH"
if [[ "$PROJECT" == "travelens" ]]; then
  code=$(curl -s -o /dev/null -m "$LIMIT" -w '%{http_code}' "${SAMPLE_ARGS[@]}" || echo 000)
  [[ "$code" == "400" ]] && echo "OK    peticion de ejemplo (400 controlado en $LIMIT s)" || { echo "FALLA peticion de ejemplo ($code)"; fail=1; }
else
  check "peticion de ejemplo" "${SAMPLE_ARGS[@]}"
fi
if [[ "$TARGET" == "local" && -n "${SERVER_PID:-}" ]]; then pkill -P "$SERVER_PID" 2>/dev/null; kill "$SERVER_PID" 2>/dev/null; fi
exit $fail
