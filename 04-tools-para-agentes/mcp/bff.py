"""Cliente mínimo del BFF de TraderPulse, compartido por los dos servidores MCP."""
from __future__ import annotations

import os

import httpx

BFF_URL = os.environ.get("BFF_URL", "http://127.0.0.1:8000")
TOKEN = os.environ.get("TRADERPULSE_TOKEN", "")


def get(ruta: str, **params: str) -> httpx.Response:
    """GET contra el BFF. Devuelve la respuesta tal cual, sin recortar nada."""
    headers = {"X-TraderPulse-Token": TOKEN} if TOKEN else {}
    return httpx.get(f"{BFF_URL}{ruta}", params=params or None, headers=headers, timeout=20)
