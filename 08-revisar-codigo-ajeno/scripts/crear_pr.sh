#!/usr/bin/env bash
# Builds the throwaway repo .work/repo: commit "main" with the base copy and branch
# pr/rsi-y-noticias created from pr/rsi-y-noticias.patch. Safe to run again (rebuilds from scratch).
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf .work/repo
mkdir -p .work/repo
cp -R traderpulse/. .work/repo/
find .work/repo -name __pycache__ -prune -exec rm -rf {} + 
cd .work/repo
git init -q -b main
git add -A
git -c user.name=demo -c user.email=demo@example.com commit -qm "base: TraderPulse backend 2026"
git checkout -q -b pr/rsi-y-noticias
git apply ../../pr/rsi-y-noticias.patch
git add -A
git -c user.name=demo -c user.email=demo@example.com commit -qm "RSI de 14 dias y titulares en el analisis de sentimiento"
git checkout -q main
echo "Rama pr/rsi-y-noticias creada en .work/repo"
git log --oneline --all
