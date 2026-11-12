"""Sentimiento del símbolo. 'ejemplo' es determinista; 'vertex' llama a Gemini en Vertex AI."""

import logging
from functools import lru_cache

from .config import ajustes
from .mercado import cotizacion, historico
from .modelos import AnalisisSentimiento, Sentimiento


def _por_tendencia(simbolo: str) -> AnalisisSentimiento:
    hist = historico(simbolo)
    variacion = (hist[-1].cierre - hist[0].cierre) / hist[0].cierre * 100
    if variacion > 2:
        valor = Sentimiento.alcista
    elif variacion < -2:
        valor = Sentimiento.bajista
    else:
        valor = Sentimiento.neutral
    return AnalisisSentimiento(
        simbolo=simbolo,
        sentimiento=valor,
        justificacion=f"En el mes el cierre se movió {variacion:+.1f} %.",
        fuente="ejemplo",
    )


@lru_cache(maxsize=64)
def _con_gemini(simbolo: str) -> AnalisisSentimiento:
    from google import genai
    from google.genai import types

    a = ajustes()
    cliente = genai.Client(
        vertexai=True, project=a.google_cloud_project or None, location=a.google_cloud_location
    )
    datos = {
        "cotizacion": cotizacion(simbolo).model_dump(mode="json"),
        "cierres": [p.cierre for p in historico(simbolo)],
    }
    respuesta = cliente.models.generate_content(
        model=a.modelo_gemini,
        contents=(
            "Eres analista financiero. Con estos datos de un mes, da el sentimiento del "
            "símbolo y una justificación de máximo dos oraciones en español.\n"
            f"{datos}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AnalisisSentimiento,
        ),
    )
    analisis = AnalisisSentimiento.model_validate_json(respuesta.text)
    return analisis.model_copy(update={"simbolo": simbolo, "fuente": a.modelo_gemini})


def analizar(simbolo: str) -> AnalisisSentimiento:
    if ajustes().sentimiento_fuente == "vertex":
        try:
            return _con_gemini(simbolo)
        except Exception:
            logging.getLogger(__name__).exception("Gemini falló; uso la tendencia")
            return _por_tendencia(simbolo)
    return _por_tendencia(simbolo)
