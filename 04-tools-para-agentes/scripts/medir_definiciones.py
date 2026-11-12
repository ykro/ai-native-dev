"""Mide la lista de definiciones de herramientas que un servidor MCP entrega al cliente.

Arranca el servidor de la configuración dada, pide la lista de herramientas y cuenta cuántas
son y cuántos caracteres ocupa esa lista en JSON compacto (nombre, descripción, esquema de
entrada, esquema de salida y anotaciones). Es lo que viaja en cada petición del agente.

Uso (desde 04-tools-para-agentes/):  uv run python scripts/medir_definiciones.py mcp/espejo.mcp.json
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def listar(config: Path) -> list[dict]:
    srv = next(iter(json.loads(config.read_text())["mcpServers"].values()))
    params = StdioServerParameters(command=srv["command"], args=srv["args"], env=srv.get("env"))
    async with stdio_client(params) as (leer, escribir):
        async with ClientSession(leer, escribir) as sesion:
            await sesion.initialize()
            herramientas = (await sesion.list_tools()).tools
    return [h.model_dump(mode="json", by_alias=True, exclude_none=True) for h in herramientas]


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    herramientas = asyncio.run(listar(Path(sys.argv[1])))
    texto = json.dumps(herramientas, ensure_ascii=False, separators=(",", ":"))
    print(f"servidor     {Path(sys.argv[1]).name.removesuffix('.mcp.json')}")
    for h in herramientas:
        print(f"  {h['name']:<36} {len(json.dumps(h, ensure_ascii=False, separators=(',', ':'))):>5} caracteres")
    print(f"herramientas {len(herramientas)}")
    print(f"caracteres   {len(texto)}")
    if "--json" in sys.argv:
        print(json.dumps({"herramientas": len(herramientas), "caracteres": len(texto)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
