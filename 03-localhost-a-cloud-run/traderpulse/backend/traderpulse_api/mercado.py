"""Datos de mercado de ejemplo. Deterministas para que pruebas y demos den lo mismo siempre."""

import json
from functools import lru_cache
from pathlib import Path

from .modelos import Cotizacion, Instrumento, PuntoHistorico

_DATOS = Path(__file__).parent / "datos" / "mercado.json"


@lru_cache
def _cargar() -> dict[str, dict]:
    datos = json.loads(_DATOS.read_text(encoding="utf-8"))
    return {i["simbolo"]: i for i in datos["instrumentos"]}


def normalizar(simbolo: str) -> str:
    return simbolo.strip().upper()


def existe(simbolo: str) -> bool:
    return normalizar(simbolo) in _cargar()


def buscar(texto: str = "") -> list[Instrumento]:
    q = texto.strip().lower()
    return [
        Instrumento(simbolo=s, nombre=i["nombre"])
        for s, i in _cargar().items()
        if not q or q in s.lower() or q in i["nombre"].lower()
    ]


def historico(simbolo: str) -> list[PuntoHistorico]:
    return [PuntoHistorico(**p) for p in _cargar()[normalizar(simbolo)]["historico"]]


def cotizacion(simbolo: str) -> Cotizacion:
    inst = _cargar()[normalizar(simbolo)]
    hist = inst["historico"]
    ultimo, anterior = hist[-1], hist[-2]
    cambio = (ultimo["cierre"] - anterior["cierre"]) / anterior["cierre"] * 100
    return Cotizacion(
        simbolo=inst["simbolo"],
        nombre=inst["nombre"],
        precio=ultimo["cierre"],
        cambio_pct=round(cambio, 2),
        volumen=inst["volumen"],
        fecha=ultimo["fecha"],
    )
