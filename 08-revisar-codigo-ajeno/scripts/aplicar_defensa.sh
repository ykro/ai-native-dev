#!/usr/bin/env bash
# Recreates the branch pr/defendida from defensa/defensa.patch (on top of pr/rsi-y-noticias).
set -euo pipefail
cd "$(dirname "$0")/../.work/repo"
git branch -D pr/defendida 2>/dev/null || true
git checkout -q -b pr/defendida pr/rsi-y-noticias
git apply ../../defensa/defensa.patch
git add -A
git -c user.name=demo -c user.email=demo@example.com commit -qm "Defensa: titulares como datos, esquema estricto y RSI definido"
git checkout -q main
echo "Rama pr/defendida creada"
