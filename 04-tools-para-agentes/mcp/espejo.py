"""Servidor MCP espejo: una herramienta por ruta de datos del BFF, con la respuesta tal cual.

Es la primera idea que se le ocurre a cualquiera: reflejar el API. Cada herramienta lleva el
nombre de su ruta, una descripción de una línea y devuelve el texto del JSON.
"""
from mcp.server.mcpserver import MCPServer

from bff import get

servidor = MCPServer("traderpulse")


@servidor.tool(structured_output=False)
def buscarInstrumentos(q: str = "") -> str:
    """GET /api/v1/instrumentos. Lista instrumentos que coinciden con q."""
    return get("/api/v1/instrumentos", q=q).text


@servidor.tool(structured_output=False)
def cotizacion(simbolo: str) -> str:
    """GET /api/v1/cotizaciones/{simbolo}. Cotización de un símbolo."""
    return get(f"/api/v1/cotizaciones/{simbolo}").text


@servidor.tool(structured_output=False)
def historico(simbolo: str) -> str:
    """GET /api/v1/historico/{simbolo}. Cierres diarios de un símbolo."""
    return get(f"/api/v1/historico/{simbolo}").text


@servidor.tool(structured_output=False)
def sentimiento(simbolo: str) -> str:
    """GET /api/v1/sentimiento/{simbolo}. Sentimiento de un símbolo."""
    return get(f"/api/v1/sentimiento/{simbolo}").text


if __name__ == "__main__":
    servidor.run("stdio")
