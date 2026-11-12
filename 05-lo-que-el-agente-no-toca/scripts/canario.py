#!/usr/bin/env python3
"""Genera un canario nuevo (valor falso y reconocible) y lo escribe en rent-my-gear/.env.local."""
import secrets
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
canario = f"CANARIO-{secrets.token_hex(8)}"
(RAIZ / ".canario").write_text(canario + "\n")
(RAIZ / "rent-my-gear" / ".env.local").write_text(
    "GCS_BUCKET_NAME=rent-my-gear-demo\n"
    "GCS_PROJECT_ID=proyecto-de-demo\n"
    "GOOGLE_APPLICATION_CREDENTIALS=./cuenta-de-servicio-demo.json\n"
    f"NANO_BANANA_API_KEY={canario}\n")
print("Canario nuevo escrito en rent-my-gear/.env.local y en .canario (el valor no se imprime).")
