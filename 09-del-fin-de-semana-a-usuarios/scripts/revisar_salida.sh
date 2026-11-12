#!/usr/bin/env bash
# Clean read-only review of branch salida/<project>. Usage: bash scripts/revisar_salida.sh traderpulse
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 scripts/_revisar_salida.py --proyecto "${1:?proyecto}"
