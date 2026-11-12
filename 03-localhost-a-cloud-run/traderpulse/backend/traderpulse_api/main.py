"""TraderPulse BFF. Cada ruta declara su respuesta y sus errores con un modelo tipado."""

import secrets
from importlib.metadata import version

from fastapi import Depends, FastAPI, Header, Query
from fastapi.responses import JSONResponse

from . import mercado, sentimiento
from .config import ajustes
from .modelos import (
    AnalisisSentimiento,
    Cotizacion,
    ErrorApi,
    Instrumento,
    Panel,
    PuntoHistorico,
    Salud,
)

VERSION = version("traderpulse-api")


class ErrorDeApi(Exception):
    def __init__(self, estado: int, codigo: str, mensaje: str):
        self.estado, self.codigo, self.mensaje = estado, codigo, mensaje


def verificar_token(x_traderpulse_token: str = Header(default="")) -> None:
    esperado = ajustes().traderpulse_token
    if esperado and not secrets.compare_digest(x_traderpulse_token, esperado):
        raise ErrorDeApi(401, "token_invalido", "Falta el token del frontend o no coincide.")


def simbolo_valido(simbolo: str) -> str:
    if not mercado.existe(simbolo):
        raise ErrorDeApi(404, "simbolo_desconocido", f"No hay datos para '{simbolo}'.")
    return mercado.normalizar(simbolo)


ERRORES = {
    401: {"model": ErrorApi, "description": "Token ausente o incorrecto."},
    404: {"model": ErrorApi, "description": "El símbolo no existe."},
}

app = FastAPI(
    title="TraderPulse BFF",
    version=VERSION,
    description="API que sirve a la pantalla de TraderPulse. Datos de mercado de ejemplo.",
)


@app.exception_handler(ErrorDeApi)
async def _error_de_api(_, exc: ErrorDeApi) -> JSONResponse:
    cuerpo = ErrorApi(codigo=exc.codigo, mensaje=exc.mensaje)
    return JSONResponse(status_code=exc.estado, content=cuerpo.model_dump())


@app.get("/salud", response_model=Salud, operation_id="salud", tags=["sistema"])
def salud() -> Salud:
    return Salud(version=VERSION)


api = [Depends(verificar_token)]


@app.get(
    "/api/v1/instrumentos",
    response_model=list[Instrumento],
    responses={401: ERRORES[401]},
    operation_id="buscarInstrumentos",
    dependencies=api,
    tags=["mercado"],
)
def buscar_instrumentos(q: str = Query(default="", max_length=40)) -> list[Instrumento]:
    return mercado.buscar(q)


@app.get(
    "/api/v1/panel/{simbolo}",
    response_model=Panel,
    responses=ERRORES,
    operation_id="panel",
    dependencies=api,
    tags=["pantalla"],
)
def panel(simbolo: str = Depends(simbolo_valido)) -> Panel:
    return Panel(
        cotizacion=mercado.cotizacion(simbolo),
        historico=mercado.historico(simbolo),
        sentimiento=sentimiento.analizar(simbolo),
    )


@app.get(
    "/api/v1/cotizaciones/{simbolo}",
    response_model=Cotizacion,
    responses=ERRORES,
    operation_id="cotizacion",
    dependencies=api,
    tags=["mercado"],
)
def obtener_cotizacion(simbolo: str = Depends(simbolo_valido)) -> Cotizacion:
    return mercado.cotizacion(simbolo)


@app.get(
    "/api/v1/historico/{simbolo}",
    response_model=list[PuntoHistorico],
    responses=ERRORES,
    operation_id="historico",
    dependencies=api,
    tags=["mercado"],
)
def obtener_historico(simbolo: str = Depends(simbolo_valido)) -> list[PuntoHistorico]:
    return mercado.historico(simbolo)


@app.get(
    "/api/v1/sentimiento/{simbolo}",
    response_model=AnalisisSentimiento,
    responses=ERRORES,
    operation_id="sentimiento",
    dependencies=api,
    tags=["mercado"],
)
def obtener_sentimiento(simbolo: str = Depends(simbolo_valido)) -> AnalisisSentimiento:
    return sentimiento.analizar(simbolo)
