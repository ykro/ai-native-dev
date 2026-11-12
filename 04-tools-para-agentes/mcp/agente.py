"""Servidor MCP hecho para el agente: tres herramientas por intención, no una por ruta.

Las fuentes de datos son las del espejo. Cambia el diseño: cada herramienta responde una
pregunta completa, comparte el prefijo del producto, explica cuándo usarla y cuándo no,
declara como esquema de salida el mismo modelo Pydantic que usa el BFF para su contrato y
lleva anotaciones de solo lectura. Ninguna recorta ni resume lo que devuelve el BFF.
"""
from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations
from traderpulse_api.modelos import Cotizacion, Instrumento, Panel

from bff import get

servidor = MCPServer("traderpulse")

SOLO_LECTURA = ToolAnnotations(
    readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False
)


def _ok(r, simbolo: str = ""):
    if r.status_code == 404:
        raise ValueError(f"'{simbolo}' no es un símbolo conocido. Usa traderpulse_buscar_instrumento.")
    r.raise_for_status()
    return r.json()


@servidor.tool(annotations=SOLO_LECTURA)
def traderpulse_buscar_instrumento(consulta: str) -> list[Instrumento]:
    """Busca instrumentos de TraderPulse por nombre de empresa o por símbolo.

    Úsala cuando solo tienes el nombre de una empresa y necesitas su símbolo, o para ver qué
    instrumentos existen. No sirve para precios ni sentimiento: con un símbolo ya conocido
    usa traderpulse_analizar_simbolo.
    """
    return [Instrumento(**i) for i in _ok(get("/api/v1/instrumentos", q=consulta))]


@servidor.tool(annotations=SOLO_LECTURA)
def traderpulse_analizar_simbolo(simbolo: str) -> Panel:
    """Analiza un símbolo de punta a punta: cotización, histórico de cierres y sentimiento.

    Úsala para cualquier pregunta sobre un solo símbolo (precio, cambio, mejor o peor cierre,
    sentimiento). Responde todo en una sola llamada. Si necesitas varios símbolos usa
    traderpulse_comparar_simbolos en lugar de repetir esta herramienta.
    """
    return Panel(**_ok(get(f"/api/v1/panel/{simbolo}"), simbolo))


@servidor.tool(annotations=SOLO_LECTURA)
def traderpulse_comparar_simbolos(simbolos: list[str]) -> list[Cotizacion]:
    """Devuelve la cotización y el cambio porcentual de varios símbolos en una sola llamada.

    Úsala para comparar, ordenar o elegir entre dos o más símbolos. No incluye histórico ni
    sentimiento: para eso usa traderpulse_analizar_simbolo sobre el símbolo elegido.
    """
    return [Cotizacion(**_ok(get(f"/api/v1/cotizaciones/{s}"), s)) for s in simbolos]


if __name__ == "__main__":
    servidor.run("stdio")
