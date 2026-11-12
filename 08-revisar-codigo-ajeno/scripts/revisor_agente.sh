#!/usr/bin/env bash
# Headless reviewer agent: clean session, read-only. Usage: bash scripts/revisor_agente.sh pr/rsi-y-noticias
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 scripts/_revisor_agente.py --rama "${1:?rama}"
