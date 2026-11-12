"""El contrato. Estos modelos generan el OpenAPI que el frontend convierte en tipos."""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class Instrumento(BaseModel):
    simbolo: str = Field(examples=["AAPL"])
    nombre: str = Field(examples=["Apple"])


class Cotizacion(BaseModel):
    simbolo: str
    nombre: str
    precio: float = Field(description="Último cierre en dólares.")
    cambio_pct: float = Field(
        description="Cambio contra el cierre anterior, en puntos porcentuales."
    )
    volumen: int = Field(ge=0)
    fecha: date


class PuntoHistorico(BaseModel):
    fecha: date
    cierre: float


class Sentimiento(StrEnum):
    alcista = "alcista"
    bajista = "bajista"
    neutral = "neutral"


class AnalisisSentimiento(BaseModel):
    simbolo: str
    sentimiento: Sentimiento
    justificacion: str = Field(max_length=400)
    fuente: str = Field(description="Modelo que generó el análisis, o 'ejemplo'.")


class Panel(BaseModel):
    """Todo lo que la pantalla de un símbolo necesita, en una sola respuesta."""

    cotizacion: Cotizacion
    historico: list[PuntoHistorico]
    sentimiento: AnalisisSentimiento


class ErrorApi(BaseModel):
    codigo: str = Field(examples=["simbolo_desconocido"])
    mensaje: str


class Salud(BaseModel):
    estado: str = "ok"
    version: str
